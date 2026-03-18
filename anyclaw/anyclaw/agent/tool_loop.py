"""Tool Calling 主循环 - 处理 LLM 返回的 tool_calls"""
import json
from typing import List, Dict, Any, Optional
from litellm import acompletion

from ..skills.models import SkillDefinition
from ..skills.executor import ToolExecutor
from ..skills.converter import skills_to_tools
from .history import ConversationHistory
from ..config.settings import settings


class ToolCallingLoop:
    """Tool Calling 主循环"""

    def __init__(
        self,
        skills: Dict[str, SkillDefinition],
        history: ConversationHistory,
        max_iterations: int = 10
    ):
        """
        初始化 Tool Calling 循环

        Args:
            skills: 可用 skills 字典
            history: 对话历史
            max_iterations: 最大迭代次数
        """
        self.skills = skills
        self.history = history
        self.max_iterations = max_iterations
        self.executor = ToolExecutor(
            timeout=settings.tool_timeout if hasattr(settings, 'tool_timeout') else 60
        )

    async def process_with_tools(
        self,
        messages: List[Dict[str, Any]],
        model: str
    ) -> str:
        """
        处理消息，支持 tool calling

        Args:
            messages: 消息列表
            model: LLM 模型

        Returns:
            最终响应
        """
        # 生成 tools 定义
        tools = skills_to_tools(list(self.skills.values()))

        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            # 调用 LLM
            response = await self._call_llm_with_tools(messages, model, tools if tools else None)

            message = response.choices[0].message

            # 检查是否有 tool calls
            if not hasattr(message, 'tool_calls') or not message.tool_calls:
                # 没有 tool calls，返回最终响应
                return message.content or ""

            # 处理 tool calls
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": self._format_tool_calls(message.tool_calls)
            })

            # 执行每个 tool call
            for tool_call in message.tool_calls:
                result = await self._execute_tool_call(tool_call)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

        # 达到最大迭代次数
        return "Error: Maximum tool calling iterations reached"

    async def _call_llm_with_tools(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        tools: Optional[List[Dict[str, Any]]] = None
    ):
        """调用 LLM（带 tools）"""
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens,
            "timeout": settings.llm_timeout,
        }

        if tools:
            kwargs["tools"] = tools

        # 根据配置添加 API key
        if settings.openai_api_key:
            kwargs["api_key"] = settings.openai_api_key

        return await acompletion(**kwargs)

    def _format_tool_calls(self, tool_calls) -> List[Dict[str, Any]]:
        """格式化 tool calls 为消息格式"""
        formatted = []
        for tc in tool_calls:
            formatted.append({
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            })
        return formatted

    async def _execute_tool_call(self, tool_call) -> str:
        """执行单个 tool call"""
        try:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            return await self.executor.execute_tool_call(
                tool_name,
                arguments,
                self.skills
            )

        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON arguments - {e}"
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"
