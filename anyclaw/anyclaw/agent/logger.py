"""Agent 日志工具 - 分级详细的对话日志

日志级别：
- CONVERSATION: 用户输入和助手响应
- TOOL_CALL: 工具调用（名称、参数、结果）
- LLM_RESPONSE: LLM 返回详情

使用方式：
    from anyclaw.agent.logger import AgentLogger
    logger = AgentLogger()

    logger.log_user_input("你好")
    logger.log_assistant_response("你好！")
    logger.log_tool_call("shell", {"cmd": "ls"}, "file1\nfile2")
    logger.log_llm_response("glm-4.7", 150, 0.5)
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

# 创建自定义日志级别
CONVERSATION = 15  #介于 DEBUG 和 INFO 之间
TOOL_CALL = 16

logging.addLevelName(CONVERSATION, "CONVERSATION")
logging.addLevelName(TOOL_CALL, "TOOL")


class AgentLogger:
    """Agent 专用日志器"""

    def __init__(self, name: str = "anyclaw.agent"):
        self.logger = logging.getLogger(name)
        self._session_id: Optional[str] = None
        self._channel: Optional[str] = None

    def set_context(self, session_id: str, channel: str = "cli") -> None:
        """设置日志上下文"""
        self._session_id = session_id
        self._channel = channel

    def log_user_input(self, content: str) -> None:
        """记录用户输入"""
        self.logger.log(
            CONVERSATION,
            f"[USER] {self._truncate(content, 200)}"
        )

    def log_assistant_response(self, content: str, model: str = None, is_summary: bool = False) -> None:
        """记录助手响应

        Args:
            content: 响应内容
            model: 模型名称
            is_summary: 是否是迭代摘要（显示更多内容）
        """
        model_info = f" ({model})" if model else ""

        if not content:
            self.logger.log(CONVERSATION, f"[ASSISTANT]{model_info} (empty)")
            return

        # 对于迭代摘要，显示更多内容（最多 2000 字符)
        if is_summary:
            if len(content) > 2000:
                truncated = content[:2000] + "..."
                self.logger.log(CONVERSATION, f"[ASSISTANT]{model_info}\n{truncated}")
            else:
                self.logger.log(CONVERSATION, f"[ASSISTANT]{model_info}\n{content}")
        else:
            # 普通响应，最多显示 300 字符
            self.logger.log(
                CONVERSATION,
                f"[ASSISTANT]{model_info} {self._truncate(content, 300)}"
            )

    def log_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        result: str,
        duration_ms: float = None
    ) -> None:
        """记录工具调用"""
        args_str = json.dumps(arguments, ensure_ascii=False, indent=None)
        if len(args_str) > 100:
            args_str = args_str[:100] + "..."

        result_preview = self._truncate(result, 150)

        duration_info = f" [{duration_ms:.0f}ms]" if duration_ms else ""

        self.logger.log(
            TOOL_CALL,
            f"[TOOL] {tool_name}{duration_info}\n"
            f"       args: {args_str}\n"
            f"       result: {result_preview}"
        )

    def log_skill_call(
        self,
        skill_name: str,
        kwargs: Dict[str, Any],
        result: str,
        duration_ms: float = None
    ) -> None:
        """记录技能调用"""
        return self.log_tool_call(f"skill:{skill_name}", kwargs, result, duration_ms)

    def log_llm_request(
        self,
        model: str,
        message_count: int,
        tools_count: int = 0
    ) -> None:
        """记录 LLM 请求"""
        tools_info = f", {tools_count} tools" if tools_count > 0 else ""
        self.logger.debug(
            f"[LLM] Request: model={model}, messages={message_count}{tools_info}"
        )

    def log_llm_response(
        self,
        model: str,
        response_preview: str,
        tool_calls_count: int = 0,
        usage: Dict[str, int] = None
    ) -> None:
        """记录 LLM 响应"""
        preview = self._truncate(response_preview, 100)
        tools_info = f", {tool_calls_count} tool_calls" if tool_calls_count > 0 else ""
        usage_info = ""
        if usage:
            usage_info = f", tokens: {usage.get('prompt', '?')}/{usage.get('completion', '?')}"

        self.logger.debug(
            f"[LLM] Response: {preview}{tools_info}{usage_info}"
        )

    def log_session_event(self, event: str, details: str = None) -> None:
        """记录会话事件"""
        details_info = f" - {details}" if details else ""
        self.logger.info(f"[SESSION] {event}{details_info}")

    def log_error(self, context: str, error: Exception) -> None:
        """记录错误"""
        self.logger.error(f"[ERROR] {context}: {type(error).__name__}: {error}")

    def _truncate(self, text: str, max_len: int) -> str:
        """截断文本"""
        if not text:
            return "(empty)"
        text = text.replace("\n", "\\n")
        if len(text) > max_len:
            return text[:max_len] + "..."
        return text


# 全局实例
_agent_logger: Optional[AgentLogger] = None


def get_agent_logger() -> AgentLogger:
    """获取全局 Agent 日志器"""
    global _agent_logger
    if _agent_logger is None:
        _agent_logger = AgentLogger()
    return _agent_logger
