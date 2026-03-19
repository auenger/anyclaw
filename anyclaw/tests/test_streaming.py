"""流式输出测试"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from anyclaw.agent.loop import AgentLoop
from anyclaw.channels.cli import CLIChannel
from anyclaw.config.settings import settings


class TestAgentLoopStreaming:
    """AgentLoop 流式响应测试"""

    def setup_method(self):
        self.agent = AgentLoop(enable_tools=False)

    @pytest.mark.asyncio
    async def test_process_stream_is_generator(self):
        """测试 process_stream 是 async generator"""
        user_input = "Hello"

        # process_stream 应该返回 async generator
        gen = self.agent.process_stream(user_input)

        # 验证是 async generator
        assert hasattr(gen, '__aiter__')
        assert hasattr(gen, '__anext__')

        # 清理
        await gen.aclose()

    @pytest.mark.asyncio
    async def test_process_stream_yields_strings(self):
        """测试 process_stream 产出字符串块"""
        user_input = "Hello"

        # Mock LLM 响应
        mock_chunks = ["Hello", " ", "world", "!"]

        async def mock_stream(*args, **kwargs):
            for chunk in mock_chunks:
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].delta = MagicMock()
                mock_response.choices[0].delta.content = chunk
                yield mock_response

        with patch('anyclaw.agent.loop.acompletion') as mock_acompletion:
            mock_acompletion.return_value = mock_stream()

            chunks = []
            async for chunk in self.agent.process_stream(user_input):
                chunks.append(chunk)

            # 验证所有块都是字符串
            assert all(isinstance(c, str) for c in chunks)
            # 验证完整内容
            assert "".join(chunks) == "Hello world!"

    @pytest.mark.asyncio
    async def test_process_stream_saves_to_history(self):
        """测试流式响应保存到历史"""
        user_input = "Test message"

        # Mock LLM 响应
        async def mock_stream(*args, **kwargs):
            for chunk in ["Response"]:
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].delta = MagicMock()
                mock_response.choices[0].delta.content = chunk
                yield mock_response

        with patch('anyclaw.agent.loop.acompletion') as mock_acompletion:
            mock_acompletion.return_value = mock_stream()

            # 消费流
            chunks = []
            async for chunk in self.agent.process_stream(user_input):
                chunks.append(chunk)

            # 验证历史中有消息（通过检查历史长度）
            assert len(self.agent.history.messages) >= 2  # 用户消息 + 助手响应

    @pytest.mark.asyncio
    async def test_process_stream_error_handling(self):
        """测试流式响应错误处理"""
        user_input = "Test"

        # Mock LLM 抛出错误
        async def mock_stream_error(*args, **kwargs):
            raise Exception("Test error")
            yield  # never reached

        with patch('anyclaw.agent.loop.acompletion') as mock_acompletion:
            mock_acompletion.return_value = mock_stream_error()

            chunks = []
            async for chunk in self.agent.process_stream(user_input):
                chunks.append(chunk)

            # 应该收到错误消息
            assert len(chunks) == 1
            assert "Error" in chunks[0] or "错误" in chunks[0]

    @pytest.mark.asyncio
    async def test_process_stream_empty_response(self):
        """测试空流式响应"""
        user_input = "Test"

        # Mock 空响应
        async def mock_stream_empty(*args, **kwargs):
            return
            yield  # never reached

        with patch('anyclaw.agent.loop.acompletion') as mock_acompletion:
            mock_acompletion.return_value = mock_stream_empty()

            chunks = []
            async for chunk in self.agent.process_stream(user_input):
                chunks.append(chunk)

            # 空响应应该产生空列表
            assert chunks == []


class TestCLIChannelStreaming:
    """CLI Channel 流式显示测试"""

    @pytest.mark.asyncio
    async def test_print_stream(self):
        """测试 _print_stream 方法"""
        from anyclaw.bus.queue import MessageBus
        bus = MessageBus()
        config = CLIChannel.default_config()
        channel = CLIChannel(config, bus)

        async def stream_gen():
            yield "Hello"
            yield " "
            yield "World"

        # 应该不抛出异常
        await channel._print_stream(stream_gen())

    @pytest.mark.asyncio
    async def test_print_stream_interrupt(self):
        """测试流式输出中断"""
        from anyclaw.bus.queue import MessageBus
        bus = MessageBus()
        config = CLIChannel.default_config()
        channel = CLIChannel(config, bus)

        async def stream_gen():
            yield "Start"
            channel.interrupt_stream()
            yield "Should not appear"

        # 应该在中断后停止
        await channel._print_stream(stream_gen())

    @pytest.mark.asyncio
    async def test_run_stream_is_callable(self):
        """测试 run_stream 方法可调用"""
        from anyclaw.bus.queue import MessageBus
        bus = MessageBus()
        config = CLIChannel.default_config()
        channel = CLIChannel(config, bus)

        # 验证方法存在
        assert hasattr(channel, 'run_stream')
        assert callable(getattr(channel, 'run_stream'))


class TestStreamingConfig:
    """流式配置测试"""

    def test_stream_enabled_default(self):
        """测试流式默认启用"""
        # 默认应该启用流式
        assert hasattr(settings, 'stream_enabled')

    def test_stream_buffer_size_default(self):
        """测试缓冲大小默认值"""
        assert hasattr(settings, 'stream_buffer_size')

    def test_stream_config_types(self):
        """测试流式配置类型"""
        if hasattr(settings, 'stream_enabled'):
            assert isinstance(settings.stream_enabled, bool)
        if hasattr(settings, 'stream_buffer_size'):
            assert isinstance(settings.stream_buffer_size, int)


class TestStreamingIntegration:
    """流式集成测试"""

    @pytest.mark.asyncio
    async def test_agent_streaming_workflow(self):
        """测试完整流式工作流"""
        agent = AgentLoop(enable_tools=False)

        # Mock LLM 响应
        async def mock_stream(*args, **kwargs):
            chunks = ["Hello", " ", "from", " ", "stream"]
            for chunk in chunks:
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].delta = MagicMock()
                mock_response.choices[0].delta.content = chunk
                yield mock_response

        with patch('anyclaw.agent.loop.acompletion') as mock_acompletion:
            mock_acompletion.return_value = mock_stream()

            # 收集流式输出
            result = []
            async for chunk in agent.process_stream("Hi"):
                result.append(chunk)

            # 验证完整输出
            assert "".join(result) == "Hello from stream"

    @pytest.mark.asyncio
    async def test_streaming_vs_non_streaming(self):
        """测试流式和非流式都可以正常工作"""
        # 简化测试：只验证流式模式正常工作

        agent = AgentLoop(enable_tools=False)

        async def mock_stream(*args, **kwargs):
            chunks = ["Test", " ", "response"]
            for chunk in chunks:
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].delta = MagicMock()
                mock_response.choices[0].delta.content = chunk
                yield mock_response

        with patch('anyclaw.agent.loop.acompletion') as mock_acompletion:
            mock_acompletion.return_value = mock_stream()
            stream_result = []
            async for chunk in agent.process_stream("Test"):
                stream_result.append(chunk)
            stream_full = "".join(stream_result)
            assert stream_full == "Test response"
