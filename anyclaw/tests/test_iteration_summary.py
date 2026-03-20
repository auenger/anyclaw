"""迭代限制智能汇报测试

测试 IterationSummaryCollector 和 IterationSummaryGenerator
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from anyclaw.agent.summary import (
    ToolCallRecord,
    IterationStatistics,
    IterationSummaryCollector,
    IterationSummaryGenerator,
    get_summary_collector,
    reset_summary_collector,
)


class TestToolCallRecord:
    """测试 ToolCallRecord"""

    def test_create_record(self):
        """测试创建记录"""
        record = ToolCallRecord(
            name="read_file",
            arguments={"path": "/test/file.txt"},
            result_summary="File content...",
            duration_ms=100,
            success=True,
        )
        assert record.name == "read_file"
        assert record.arguments == {"path": "/test/file.txt"}
        assert record.success is True
        assert record.duration_ms == 100

    def test_to_dict(self):
        """测试转换为字典"""
        record = ToolCallRecord(
            name="exec",
            arguments={"command": "ls"},
            result_summary="file1\nfile2",
            duration_ms=50,
            success=True,
        )
        d = record.to_dict()
        assert d["name"] == "exec"
        assert d["arguments"] == {"command": "ls"}
        assert d["success"] is True


class TestIterationSummaryCollector:
    """测试 IterationSummaryCollector"""

    def setup_method(self):
        """每个测试前重置收集器"""
        self.collector = IterationSummaryCollector()

    def test_record_tool_call(self):
        """测试记录工具调用"""
        self.collector.record_tool_call(
            name="read_file",
            arguments={"path": "/test.txt"},
            result="Content",
            duration_ms=100,
            success=True,
        )
        assert self.collector.has_tool_calls() is True

    def test_result_truncation(self):
        """测试结果截断"""
        long_result = "x" * 500
        self.collector.record_tool_call(
            name="test",
            arguments={},
            result=long_result,
            duration_ms=10,
            success=True,
        )
        timeline = self.collector.get_tool_call_timeline()
        assert len(timeline[0]["result_summary"]) < len(long_result)
        assert "..." in timeline[0]["result_summary"]

    def test_collect_statistics(self):
        """测试收集统计信息"""
        # 记录多个工具调用
        self.collector.record_tool_call("read_file", {"path": "a.txt"}, "OK", 100, True)
        self.collector.record_tool_call("write_file", {"path": "b.txt"}, "OK", 150, True)
        self.collector.record_tool_call("exec", {"cmd": "test"}, "Error", 50, False)

        stats = self.collector.collect_statistics()
        assert stats.total_calls == 3
        assert stats.successful_calls == 2
        assert stats.failed_calls == 1
        assert stats.total_duration_ms == 300
        assert "read_file" in stats.unique_tools
        assert "write_file" in stats.unique_tools
        assert "exec" in stats.unique_tools

    def test_loop_detection(self):
        """测试循环检测"""
        # 同一个工具调用多次
        for i in range(4):
            self.collector.record_tool_call(
                "read_file",
                {"path": "/same/path.txt"},
                "Content",
                10,
                True,
            )

        stats = self.collector.collect_statistics()
        assert len(stats.detected_loops) > 0
        assert stats.detected_loops[0]["tool"] == "read_file"
        assert stats.detected_loops[0]["count"] >= 3

    def test_get_tool_call_timeline(self):
        """测试获取工具调用时间线"""
        self.collector.record_tool_call("tool1", {}, "r1", 10, True)
        self.collector.record_tool_call("tool2", {}, "r2", 20, True)

        timeline = self.collector.get_tool_call_timeline()
        assert len(timeline) == 2
        assert timeline[0]["name"] == "tool1"
        assert timeline[1]["name"] == "tool2"

    def test_clear(self):
        """测试清空记录"""
        self.collector.record_tool_call("test", {}, "result", 10, True)
        assert self.collector.has_tool_calls() is True

        self.collector.clear()
        assert self.collector.has_tool_calls() is False


class TestIterationSummaryGenerator:
    """测试 IterationSummaryGenerator"""

    def setup_method(self):
        """每个测试前创建生成器"""
        self.generator = IterationSummaryGenerator(enabled=True, max_tokens=500)
        self.collector = IterationSummaryCollector()

    def test_disabled_generator(self):
        """测试禁用的生成器"""
        generator = IterationSummaryGenerator(enabled=False)
        result = await_if_needed(generator.generate(self.collector, [], 10))
        assert result == "达到最大迭代次数"

    def test_simple_summary_no_tool_calls(self):
        """测试无工具调用时的简化汇报"""
        messages = [{"role": "user", "content": "测试请求"}]
        result = await_if_needed(self.generator.generate(self.collector, messages, 10))
        assert "10 次迭代限制" in result
        assert "没有执行任何工具操作" in result

    def test_extract_user_request(self):
        """测试提取用户请求"""
        messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "用户请求内容"},
            {"role": "assistant", "content": "响应"},
        ]
        request = self.generator._extract_user_request(messages)
        assert request == "用户请求内容"

    def test_format_arguments(self):
        """测试格式化参数"""
        args = {"path": "/test/file.txt", "mode": "read"}
        formatted = self.generator._format_arguments(args)
        assert "path=/test/file.txt" in formatted
        assert "mode=read" in formatted

    def test_format_arguments_truncation(self):
        """测试参数截断"""
        args = {"long_value": "x" * 100}
        formatted = self.generator._format_arguments(args)
        assert len(formatted) < 100

    @pytest.mark.asyncio
    async def test_fallback_summary(self):
        """测试降级汇报"""
        self.collector.record_tool_call("read_file", {"path": "a.txt"}, "OK", 100, True)
        self.collector.record_tool_call("exec", {"cmd": "fail"}, "Error", 50, False)

        result = self.generator._generate_fallback_summary(self.collector, 10)
        assert "10 次迭代限制" in result
        assert "成功 1 次" in result
        assert "失败 1 次" in result


class TestGlobalFunctions:
    """测试全局函数"""

    def test_get_summary_collector(self):
        """测试获取全局收集器"""
        reset_summary_collector()
        collector1 = get_summary_collector()
        collector2 = get_summary_collector()
        assert collector1 is collector2

    def test_reset_summary_collector(self):
        """测试重置全局收集器"""
        collector = get_summary_collector()
        collector.record_tool_call("test", {}, "result", 10, True)

        reset_summary_collector()
        new_collector = get_summary_collector()
        assert new_collector.has_tool_calls() is False


def await_if_needed(coro):
    """辅助函数：如果需要则运行协程"""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None:
        # 已经在事件循环中，使用 run_until_complete 会失败
        # 所以创建一个新任务并等待
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()
    else:
        return asyncio.run(coro)


class TestIntegration:
    """集成测试"""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """测试完整工作流"""
        # 创建收集器并记录多个工具调用
        collector = IterationSummaryCollector()
        collector.record_tool_call("read_file", {"path": "test.txt"}, "Content", 100, True)
        collector.record_tool_call("write_file", {"path": "out.txt"}, "Written", 150, True)
        collector.record_tool_call("exec", {"cmd": "test"}, "Error", 50, False)

        # 收集统计
        stats = collector.collect_statistics()
        assert stats.total_calls == 3
        assert stats.successful_calls == 2
        assert stats.failed_calls == 1

        # 生成汇报
        generator = IterationSummaryGenerator(enabled=True, max_tokens=500)
        messages = [{"role": "user", "content": "测试任务"}]

        # 由于 LLM 调用可能失败，测试降级汇报
        result = generator._generate_fallback_summary(collector, 10)
        assert "迭代限制" in result
        assert "3 次工具调用" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
