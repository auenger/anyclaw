"""Agent 主处理循环"""
import asyncio
from typing import Optional
from litellm import acompletion
from anyclaw.config.settings import settings
from .history import ConversationHistory
from .context import ContextBuilder


class AgentLoop:
    """Agent 主处理循环"""

    def __init__(self):
        self.history = ConversationHistory(max_length=10)
        self.skills_info = []

    async def process(self, user_input: str) -> str:
        """处理用户输入"""
        # 1. 添加用户消息到历史
        self.history.add_user_message(user_input)

        # 2. 构建上下文
        context_builder = ContextBuilder(self.history, self.skills_info)
        messages = context_builder.build()

        # 3. 调用 LLM
        response = await self._call_llm(messages)

        # 4. 添加助手响应到历史
        self.history.add_assistant_message(response)

        return response

    async def _call_llm(self, messages: list) -> str:
        """调用 LLM"""
        try:
            response = await acompletion(
                model=settings.llm_model,
                messages=messages,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout,
                api_key=settings.openai_api_key,
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error: {str(e)}"

    def clear_history(self) -> None:
        """清空对话历史"""
        self.history.clear()

    def set_skills(self, skills_info: list) -> None:
        """设置可用技能"""
        self.skills_info = skills_info
