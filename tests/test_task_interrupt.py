"""测试任务即时中断机制"""

import asyncio
import pytest

from anyclaw.agent.loop import AgentLoop


class TestAgentLoopInterrupt:
    """测试 AgentLoop 中断机制"""

    @pytest.fixture
    def agent_loop(self, tmp_path):
        """创建 AgentLoop 实例"""
        return AgentLoop(
            workspace=tmp_path,
            enable_tools=False,  # 简化测试
            enable_session_manager=False,
            enable_archive=False,
        )

    def test_active_tasks_initially_empty(self, agent_loop):
        """测试 _active_tasks 初始为空"""
        assert agent_loop._active_tasks == {}
        assert agent_loop._abort_flags == {}

    @pytest.mark.asyncio
    async def test_register_task(self, agent_loop):
        """测试任务注册"""
        async def dummy_coro():
            await asyncio.sleep(10)

        task = asyncio.create_task(dummy_coro())
        agent_loop.register_task("test", task)

        assert "test" in agent_loop._active_tasks
        assert agent_loop._active_tasks["test"] is task
        assert agent_loop._abort_flags["test"] is False

        # 清理
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_unregister_task(self, agent_loop):
        """测试任务取消注册"""
        async def dummy_coro():
            await asyncio.sleep(10)

        task = asyncio.create_task(dummy_coro())
        agent_loop.register_task("test", task)
        agent_loop.unregister_task("test")

        assert "test" not in agent_loop._active_tasks
        assert "test" not in agent_loop._abort_flags

        # 清理
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_request_abort_sets_flag(self, agent_loop):
        """测试请求中断设置标志"""
        async def dummy_coro():
            await asyncio.sleep(10)

        task = asyncio.create_task(dummy_coro())
        agent_loop.register_task("test", task)

        result = agent_loop.request_abort("test")

        assert result is True
        assert agent_loop._abort_flags["test"] is True

        # 等待任务被取消
        try:
            await task
        except asyncio.CancelledError:
            pass

    def test_request_abort_no_task(self, agent_loop):
        """测试没有任务时请求中断"""
        result = agent_loop.request_abort("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_request_abort_completed_task(self, agent_loop):
        """测试已完成任务请求中断"""
        async def quick_coro():
            return "done"

        task = asyncio.create_task(quick_coro())
        await asyncio.sleep(0)  # 让任务完成

        agent_loop.register_task("test", task)
        result = agent_loop.request_abort("test")

        assert result is False  # 已完成的任务无法中断

    def test_is_abort_requested(self, agent_loop):
        """测试中断标志检查"""
        assert agent_loop.is_abort_requested("test") is False

        agent_loop._abort_flags["test"] = True
        assert agent_loop.is_abort_requested("test") is True

    @pytest.mark.asyncio
    async def test_has_active_task(self, agent_loop):
        """测试活动任务检查"""
        assert agent_loop.has_active_task("test") is False

        async def dummy_coro():
            await asyncio.sleep(10)

        task = asyncio.create_task(dummy_coro())
        agent_loop.register_task("test", task)

        assert agent_loop.has_active_task("test") is True

        # 取消任务
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert agent_loop.has_active_task("test") is False

    @pytest.mark.asyncio
    async def test_run_with_tools_respects_abort_flag(self, agent_loop):
        """测试 _run_with_tools 检查中断标志"""
        # 设置中断标志
        agent_loop._abort_flags["default"] = True

        # 调用 _run_with_tools
        result = await agent_loop._run_with_tools(
            messages=[{"role": "user", "content": "test"}],
            session_key="default",
        )

        assert "中断" in result or "interrupted" in result.lower()


class TestCLIChannelInterrupt:
    """测试 CLIChannel 中断支持"""

    @pytest.fixture
    def cli_channel(self):
        """创建 CLIChannel 实例"""
        from anyclaw.bus.queue import MessageBus
        from anyclaw.channels.cli import CLIChannel, CLIConfig

        bus = MessageBus()
        config = CLIConfig({"agent_name": "TestAgent"})
        return CLIChannel(config, bus)

    def test_set_agent_loop(self, cli_channel):
        """测试设置 AgentLoop 引用"""
        mock_agent_loop = object()
        cli_channel.set_agent_loop(mock_agent_loop)

        assert cli_channel._agent_loop is mock_agent_loop

    def test_agent_loop_initially_none(self, cli_channel):
        """测试 _agent_loop 初始为 None"""
        assert cli_channel._agent_loop is None

    @pytest.mark.asyncio
    async def test_handle_stop_direct_no_agent_loop(self, cli_channel):
        """测试没有 agent_loop 时的 _handle_stop_direct"""
        # 应该不会抛出异常
        await cli_channel._handle_stop_direct()

    @pytest.mark.asyncio
    async def test_handle_stop_direct_with_agent_loop(self, cli_channel):
        """测试有 agent_loop 时的 _handle_stop_direct"""
        class MockAgentLoop:
            def has_active_task(self, key):
                return True

            def request_abort(self, key):
                return True

        cli_channel.set_agent_loop(MockAgentLoop())
        await cli_channel._handle_stop_direct()  # 应该成功

    @pytest.mark.asyncio
    async def test_handle_stop_direct_no_active_task(self, cli_channel):
        """测试没有活动任务时的 _handle_stop_direct"""
        class MockAgentLoop:
            def has_active_task(self, key):
                return False

        cli_channel.set_agent_loop(MockAgentLoop())
        await cli_channel._handle_stop_direct()  # 应该成功


class TestStopCommandHandlerUpdate:
    """测试 StopCommandHandler 更新"""

    @pytest.mark.asyncio
    async def test_stop_with_new_abort_mechanism(self):
        """测试使用新的中断机制"""
        from anyclaw.commands.handlers.task import StopCommandHandler
        from anyclaw.commands.context import CommandContext

        class MockAgentLoop:
            def has_active_task(self, key):
                return True

            def request_abort(self, key):
                return True

        handler = StopCommandHandler()
        context = CommandContext(
            user_id="test",
            chat_id="test",
            agent_loop=MockAgentLoop(),
        )

        result = await handler.execute(None, context)
        assert result.handled is True

    @pytest.mark.asyncio
    async def test_stop_no_active_task(self):
        """测试没有活动任务时的停止"""
        from anyclaw.commands.handlers.task import StopCommandHandler
        from anyclaw.commands.context import CommandContext

        class MockAgentLoop:
            def has_active_task(self, key):
                return False

        handler = StopCommandHandler()
        context = CommandContext(
            user_id="test",
            chat_id="test",
            agent_loop=MockAgentLoop(),
        )

        result = await handler.execute(None, context)
        assert "没有" in result.reply

    @pytest.mark.asyncio
    async def test_stop_backward_compatible(self):
        """测试向后兼容（使用旧的 is_running/abort）"""
        from anyclaw.commands.handlers.task import StopCommandHandler
        from anyclaw.commands.context import CommandContext

        class OldStyleAgentLoop:
            is_running = True

            async def abort(self):
                pass

        handler = StopCommandHandler()
        context = CommandContext(
            user_id="test",
            chat_id="test",
            agent_loop=OldStyleAgentLoop(),
        )

        result = await handler.execute(None, context)
        assert result.handled is True
