"""测试 LLM 响应韧性增强功能"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio


class TestEmptyResponseDetection:
    """测试空响应检测与恢复"""

    @pytest.mark.asyncio
    async def test_empty_response_triggers_retry(self):
        """空响应应触发重试"""
        from anyclaw.agent.loop import AgentLoop

        # 模拟响应序列：空响应 -> 有效响应
        mock_response_1 = MagicMock()
        mock_response_1.choices = [MagicMock()]
        mock_response_1.choices[0].message.content = None
        mock_response_1.choices[0].message.tool_calls = None

        mock_response_2 = MagicMock()
        mock_response_2.choices = [MagicMock()]
        mock_response_2.choices[0].message.content = "有效响应"
        mock_response_2.choices[0].message.tool_calls = None

        loop = AgentLoop(enable_tools=False)
        loop.tools = MagicMock()
        loop.tools.get_definitions = MagicMock(return_value=[])

        with patch.object(loop, "_call_llm_with_tools", new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = [mock_response_1, mock_response_2]

            result = await loop._run_with_tools([{"role": "user", "content": "test"}])

            # 应该调用两次（空响应重试一次）
            assert mock_call.call_count == 2
            assert result == "有效响应"

    @pytest.mark.asyncio
    async def test_empty_response_max_retries(self):
        """达到最大重试次数应返回错误提示"""
        from anyclaw.agent.loop import AgentLoop
        from anyclaw.config.settings import settings

        # 模拟连续空响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_response.choices[0].message.tool_calls = None

        loop = AgentLoop(enable_tools=False)
        loop.tools = MagicMock()
        loop.tools.get_definitions = MagicMock(return_value=[])

        max_retries = settings.llm_empty_response_retry + 1  # 包括首次尝试

        with patch.object(loop, "_call_llm_with_tools", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await loop._run_with_tools([{"role": "user", "content": "test"}])

            # 应该调用 max_retries 次
            assert mock_call.call_count == max_retries
            assert "异常" in result or "重试" in result

    @pytest.mark.asyncio
    async def test_non_empty_response_no_retry(self):
        """非空响应不应触发重试"""
        from anyclaw.agent.loop import AgentLoop

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "正常响应"
        mock_response.choices[0].message.tool_calls = None

        loop = AgentLoop(enable_tools=False)
        loop.tools = MagicMock()
        loop.tools.get_definitions = MagicMock(return_value=[])

        with patch.object(loop, "_call_llm_with_tools", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_response

            result = await loop._run_with_tools([{"role": "user", "content": "test"}])

            # 应该只调用一次
            assert mock_call.call_count == 1
            assert result == "正常响应"


class TestLLMResponseDetailLogging:
    """测试 LLM 响应详情日志"""

    def test_log_llm_response_detail_with_content(self):
        """有内容时应正确记录日志"""
        from anyclaw.agent.loop import AgentLoop

        loop = AgentLoop(enable_tools=False)

        mock_response = MagicMock()
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.total_tokens = 150
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].finish_reason = "stop"
        mock_response.choices[0].message.content = "测试内容"
        mock_response.choices[0].message.tool_calls = None

        with patch("anyclaw.agent.loop.logger") as mock_logger:
            loop._log_llm_response_detail(mock_response, mock_response.choices[0].message)

            # 应该调用 debug 日志
            mock_logger.debug.assert_called_once()

    def test_log_llm_response_detail_empty_triggers_warning(self):
        """空响应应触发警告日志"""
        from anyclaw.agent.loop import AgentLoop

        loop = AgentLoop(enable_tools=False)

        mock_response = MagicMock()
        mock_response.usage = None
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].finish_reason = "stop"
        mock_response.choices[0].message.content = None
        mock_response.choices[0].message.tool_calls = None

        with patch("anyclaw.agent.loop.logger") as mock_logger:
            loop._log_llm_response_detail(mock_response, mock_response.choices[0].message)

            # 应该调用 warning 日志
            mock_logger.warning.assert_called_once()


class TestLLMResilienceConfig:
    """测试 LLM 韧性配置"""

    def test_config_defaults(self):
        """测试默认配置值"""
        from anyclaw.config.settings import Settings

        # 使用默认值创建
        s = Settings()

        assert s.llm_max_retries == 3
        assert s.llm_retry_delay == 1.0
        assert s.llm_empty_response_retry == 2
        assert s.llm_log_response_detail == False

    def test_config_validation(self):
        """测试配置验证"""
        from anyclaw.config.settings import Settings
        from pydantic import ValidationError

        # 测试边界值
        s = Settings(
            llm_max_retries=10,
            llm_retry_delay=30.0,
            llm_empty_response_retry=5,
        )
        assert s.llm_max_retries == 10

        # 测试超出范围
        with pytest.raises(ValidationError):
            Settings(llm_max_retries=11)  # 超过 max 10

        with pytest.raises(ValidationError):
            Settings(llm_empty_response_retry=6)  # 超过 max 5


class TestToolCallsPreserved:
    """测试 tool_calls 不被空响应处理干扰"""

    @pytest.mark.asyncio
    async def test_tool_calls_not_affected_by_empty_check(self):
        """有 tool_calls 时不应触发空响应重试"""
        from anyclaw.agent.loop import AgentLoop

        # 模拟有 tool_calls 的响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None  # content 可能为空
        mock_response.choices[0].message.tool_calls = [MagicMock()]
        mock_response.choices[0].message.tool_calls[0].id = "call_123"
        mock_response.choices[0].message.tool_calls[0].function.name = "test_tool"
        mock_response.choices[0].message.tool_calls[0].function.arguments = '{"arg": "value"}'

        # 模拟工具执行
        mock_tool_result = MagicMock()
        mock_tool_result.choices = [MagicMock()]
        mock_tool_result.choices[0].message.content = "工具执行结果"
        mock_tool_result.choices[0].message.tool_calls = None

        loop = AgentLoop(enable_tools=True)
        loop.tools = MagicMock()
        loop.tools.get_definitions = MagicMock(return_value=[])
        loop.tools.execute = AsyncMock(return_value="执行成功")

        with patch.object(loop, "_call_llm_with_tools", new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = [mock_response, mock_tool_result]

            result = await loop._run_with_tools([{"role": "user", "content": "test"}])

            # 应该执行工具，而不是触发空响应重试
            loop.tools.execute.assert_called_once()
