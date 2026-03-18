"""Agent 主处理循环"""
import asyncio
from typing import Optional, Dict, List
from litellm import acompletion
from anyclaw.config.settings import settings
from anyclaw.skills.models import SkillDefinition
from .history import ConversationHistory
from .context import ContextBuilder
from .tool_loop import ToolCallingLoop


class AgentLoop:
    """Agent 主处理循环"""

    def __init__(self, enable_tools: bool = True):
        self.history = ConversationHistory(max_length=10)
        self.skills: Dict[str, SkillDefinition] = {}
        self.enable_tools = enable_tools
        self.tool_loop: Optional[ToolCallingLoop] = None

    def set_skills(self, skills: Dict[str, SkillDefinition]) -> None:
        """设置可用技能"""
        self.skills = skills
        if self.enable_tools and skills:
            self.tool_loop = ToolCallingLoop(
                skills=skills,
                history=self.history,
                max_iterations=settings.tool_max_iterations
            )

    async def process(self, user_input: str) -> str:
        """处理用户输入"""
        # 1. 添加用户消息到历史
        self.history.add_user_message(user_input)

        # 2. 构建上下文
        context_builder = ContextBuilder(self.history, self._get_skills_info())
        messages = context_builder.build()

        # 3. 调用 LLM（支持 tool calling）
        if self.enable_tools and self.tool_loop and self.skills:
            response = await self.tool_loop.process_with_tools(
                messages,
                settings.llm_model
            )
        else:
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

    def _get_skills_info(self) -> List[Dict[str, str]]:
        """获取技能信息列表"""
        return [
            {"name": skill.name, "description": skill.description}
            for skill in self.skills.values()
            if skill.eligible
        ]
