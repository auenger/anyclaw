"""上下文构建器"""
from typing import List, Dict
from anyclaw.config.settings import settings
from .history import ConversationHistory


class ContextBuilder:
    """上下文构建器"""

    def __init__(self, history: ConversationHistory, skills_info: List[Dict]):
        self.history = history
        self.skills_info = skills_info

    def build(self) -> List[Dict]:
        """构建完整上下文"""
        context = []

        # 1. 系统提示词
        system_prompt = self._build_system_prompt()
        context.append({"role": "system", "content": system_prompt})

        # 2. 历史对话
        context.extend(self.history.get_history())

        return context

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        base_prompt = settings.get_system_prompt()

        # 添加技能信息
        if self.skills_info:
            skills_desc = "\n\nYou have access to these skills:\n"
            for skill in self.skills_info:
                skills_desc += f"- {skill['name']}: {skill['description']}\n"
            base_prompt += skills_desc

        return base_prompt
