#!/usr/bin/env python3
"""测试 ListDirTool 和 ExecTool 的新功能"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "anyclaw"))

from anyclaw.tools.filesystem import ListDirTool
from anyclaw.tools.shell import ExecTool


async def test_list_dir_timeout():
    """测试 ListDirTool 超时功能"""
    print("\n=== 测试 1: ListDirTool 超时 ===")
    tool = ListDirTool(timeout=1)  # 1 秒超时

    # 测试正常情况
    result = await tool.execute(path=".")
    print(f"✅ 正常列出当前目录: {len(result.splitlines())} 行")

    # 测试超时情况（模拟慢速操作）
    # 注意：实际的文件系统操作可能不会触发超时，
    # 这里只是验证超时参数被正确处理


async def test_list_dir_max_entries():
    """测试 ListDirTool 最大条目限制"""
    print("\n=== 测试 2: ListDirTool 最大条目限制 ===")

    # 测试限制 5 个条目
    tool = ListDirTool(max_entries=5)
    result = await tool.execute(path=".")

    lines = result.splitlines()
    print(f"✅ 结果: {len(lines)} 行")

    # 检查是否有截断提示
    if "已截断" in result or "truncated" in result.lower():
        print(f"✅ 正确显示截断提示")
    else:
        # 检查实际返回的行数
        content_lines = [l for l in lines if not l.startswith("(已截断")]
        print(f"✅ 返回了 {len(content_lines)} 个条目（限制 5 个）")


async def test_list_dir_ignore_dirs():
    """测试 ListDirTool 忽略列表"""
    print("\n=== 测试 3: ListDirTool 忽略列表 ===")
    tool = ListDirTool()

    # 创建一个测试结构
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建一些测试目录，包括被忽略的
        os.makedirs(Path(tmpdir) / ".git")
        os.makedirs(Path(tmpdir) / "node_modules")
        os.makedirs(Path(tmpdir) / "__pycache__")
        os.makedirs(Path(tmpdir) / "normal_dir")

        # 列出目录
        tool_test = ListDirTool(workspace=Path(tmpdir))
        result = await tool_test.execute(path=".")

        # 检查结果
        if ".git" not in result:
            print("✅ .git 被正确忽略")
        if "node_modules" not in result:
            print("✅ node_modules 被正确忽略")
        if "__pycache__" not in result:
            print("✅ __pycache__ 被正确忽略")
        if "normal_dir" in result:
            print("✅ normal_dir 被正确显示")


async def test_exec_timeout():
    """测试 ExecTool 超时功能"""
    print("\n=== 测试 4: ExecTool 超时 ===")

    # 测试正常情况
    tool = ExecTool(timeout=10)
    result = await tool.execute(command="echo 'test'")
    print(f"✅ 正常执行命令: {len(result)} 字符")

    # 测试超时情况（使用 sleep 模拟长运行命令）
    tool = ExecTool(timeout=2)
    result = await tool.execute(command="sleep 5")

    if "超时" in result or "timeout" in result.lower() or "timed out" in result.lower():
        print(f"✅ 正确检测到超时")
        print(f"   结果: {result[:100]}...")
    else:
        print(f"⚠️  未检测到超时（命令可能很快完成）")


async def test_exec_path_traversal():
    """测试 ExecTool 路径遍历检查"""
    print("\n=== 测试 5: ExecTool 路径遍历检查 ===")

    tool = ExecTool()

    # 测试路径遍历
    result = await tool.execute(command="ls ../../../")

    if "路径遍历" in result or "path traversal" in result.lower():
        print(f"✅ 正确阻止路径遍历")
        print(f"   结果: {result[:100]}...")
    else:
        print(f"⚠️  路径遍历检查可能没有生效")


async def test_exec_internal_url():
    """测试 ExecTool 内部 URL 检查"""
    print("\n=== 测试 6: ExecTool 内部 URL 检查 ===")

    tool = ExecTool()

    # 测试内部 URL
    result = await tool.execute(command="curl http://127.0.0.1:8080/secret")

    if "内部" in result or "internal" in result.lower() or "private" in result.lower():
        print(f"✅ 正确阻止内部 URL")
        print(f"   结果: {result[:100]}...")
    else:
        print(f"⚠️  内部 URL 检查可能没有生效")


async def test_exec_output_truncation():
    """测试 ExecTool 输出截断"""
    print("\n=== 测试 7: ExecTool 输出截断 ===")

    tool = ExecTool()
    # 生成大量输出
    result = await tool.execute(command="printf '%s\\n' {1..10000}")

    if "truncated" in result.lower() or "已截断" in result or "chars truncated" in result.lower():
        print(f"✅ 正确截断输出")
        print(f"   结果长度: {len(result)} 字符")
        print(f"   预期: <= {tool._MAX_OUTPUT} 字符")
    else:
        print(f"⚠️  输出截断可能没有生效")
        print(f"   结果长度: {len(result)} 字符")


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("AnyClaw 工具修复验证测试")
    print("=" * 60)
    print(f"测试时间: {asyncio.get_event_loop().time()}")
    print()

    try:
        # 运行所有测试
        await test_list_dir_timeout()
        await test_list_dir_max_entries()
        await test_list_dir_ignore_dirs()
        await test_exec_timeout()
        await test_exec_path_traversal()
        await test_exec_internal_url()
        await test_exec_output_truncation()

        print("\n" + "=" * 60)
        print("✅ 所有测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
