"""ExecTool cd 命令检测和会话集成测试"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from anyclaw.tools.shell import ExecTool
from anyclaw.session.models import Session


class TestDetectCdCommand:
    """cd 命令检测测试"""

    def test_detect_absolute_path_cd(self):
        """检测绝对路径 cd"""
        tool = ExecTool()

        with tempfile.TemporaryDirectory() as tmpdir:
            resolved = str(Path(tmpdir).resolve())
            new_cwd = tool._detect_cd_command(f"cd {tmpdir}", os.getcwd())
            assert new_cwd == resolved

    def test_detect_relative_path_cd(self):
        """检测相对路径 cd（相对于当前 cwd）"""
        tool = ExecTool()

        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建子目录
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()

            new_cwd = tool._detect_cd_command("cd subdir", tmpdir)
            assert new_cwd == str(subdir.resolve())

    def test_detect_cd_with_command(self):
        """检测 cd && cmd 组合命令"""
        tool = ExecTool()

        with tempfile.TemporaryDirectory() as tmpdir:
            resolved = str(Path(tmpdir).resolve())
            new_cwd = tool._detect_cd_command(f"cd {tmpdir} && ls", os.getcwd())
            assert new_cwd == resolved

    def test_detect_cd_with_semicolon(self):
        """检测 cd ; cmd 组合命令"""
        tool = ExecTool()

        with tempfile.TemporaryDirectory() as tmpdir:
            resolved = str(Path(tmpdir).resolve())
            new_cwd = tool._detect_cd_command(f"cd {tmpdir} ; ls", os.getcwd())
            assert new_cwd == resolved

    def test_no_cd_command(self):
        """非 cd 命令返回 None"""
        tool = ExecTool()

        assert tool._detect_cd_command("ls -la", os.getcwd()) is None
        assert tool._detect_cd_command("cat file.txt", os.getcwd()) is None
        assert tool._detect_cd_command("echo hello", os.getcwd()) is None

    def test_invalid_path_cd(self):
        """无效路径 cd 返回 None"""
        tool = ExecTool()

        new_cwd = tool._detect_cd_command("cd /nonexistent/path/12345", os.getcwd())
        assert new_cwd is None

    def test_file_path_cd(self):
        """文件路径 cd 返回 None（必须是目录）"""
        tool = ExecTool()

        with tempfile.NamedTemporaryFile() as tmpfile:
            new_cwd = tool._detect_cd_command(f"cd {tmpfile.name}", os.getcwd())
            assert new_cwd is None

    def test_cd_with_quotes(self):
        """带引号的 cd 命令"""
        tool = ExecTool()

        with tempfile.TemporaryDirectory() as tmpdir:
            resolved = str(Path(tmpdir).resolve())
            new_cwd = tool._detect_cd_command(f'cd "{tmpdir}"', os.getcwd())
            assert new_cwd == resolved

    def test_cd_home_directory(self):
        """cd ~ 解析到 home 目录"""
        tool = ExecTool()

        # 使用 cd ~ && cmd 格式，因为正则要求 cd 后有分隔符
        new_cwd = tool._detect_cd_command("cd ~ && pwd", os.getcwd())
        assert new_cwd == str(Path.home())


class TestExecToolSessionIntegration:
    """ExecTool 会话集成测试"""

    @pytest.mark.asyncio
    async def test_session_cwd_as_default(self):
        """session.cwd 作为默认工作目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = Session(key="test:123")
            session.set_cwd(tmpdir)

            tool = ExecTool(session=session)

            # 执行 pwd 命令验证工作目录
            result = await tool.execute("pwd")
            assert tmpdir in result or str(Path(tmpdir).resolve()) in result

    @pytest.mark.asyncio
    async def test_working_dir_param_priority(self):
        """working_dir 参数优先于 session.cwd"""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                session = Session(key="test:123")
                session.set_cwd(tmpdir1)

                tool = ExecTool(session=session)

                # 参数优先
                result = await tool.execute("pwd", working_dir=tmpdir2)
                assert tmpdir2 in result or str(Path(tmpdir2).resolve()) in result

    @pytest.mark.asyncio
    async def test_no_session_behavior_unchanged(self):
        """无 session 时行为不变"""
        tool = ExecTool()

        # 应该使用 os.getcwd()
        result = await tool.execute("pwd")
        assert os.getcwd() in result or str(Path.cwd().resolve()) in result

    @pytest.mark.asyncio
    async def test_cd_updates_session_cwd(self):
        """cd 命令更新 session.cwd"""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = Session(key="test:123")
            original_cwd = session.get_cwd()

            tool = ExecTool(session=session)

            # 执行 cd 命令
            await tool.execute(f"cd {tmpdir}")

            # session.cwd 应该更新
            assert session.get_cwd() == str(Path(tmpdir).resolve())
            assert session.get_cwd() != original_cwd

    @pytest.mark.asyncio
    async def test_cd_invalid_path_no_update(self):
        """cd 无效路径不更新 session.cwd"""
        session = Session(key="test:123")
        original_cwd = session.get_cwd()

        tool = ExecTool(session=session)

        # 执行 cd 到无效路径
        await tool.execute("cd /nonexistent/path/12345")

        # session.cwd 不应该更新
        assert session.get_cwd() == original_cwd

    @pytest.mark.asyncio
    async def test_working_dir_priority_order(self):
        """工作目录优先级: 参数 > session.cwd > self.working_dir > os.getcwd()"""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                with tempfile.TemporaryDirectory() as tmpdir3:
                    session = Session(key="test:123")
                    session.set_cwd(tmpdir1)

                    # working_dir 设置为 tmpdir2
                    tool = ExecTool(working_dir=tmpdir2, session=session)

                    # 不带参数：session.cwd > working_dir
                    result = await tool.execute("pwd")
                    # session.cwd 应该优先
                    assert str(Path(tmpdir1).resolve()) in result

                    # 带参数：参数优先
                    result = await tool.execute("pwd", working_dir=tmpdir3)
                    assert str(Path(tmpdir3).resolve()) in result
