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
            # 获取模型特定的调用参数
            kwargs = self._get_llm_kwargs(settings.llm_model)
            kwargs["model"] = settings.llm_model
            kwargs["messages"] = messages
            kwargs["temperature"] = settings.llm_temperature
            kwargs["max_tokens"] = settings.llm_max_tokens
            kwargs["timeout"] = settings.llm_timeout

            response = await acompletion(**kwargs)

            return response.choices[0].message.content

        except Exception as e:
            return f"Error: {str(e)}"

    def _get_llm_kwargs(self, model: str) -> Dict:
        """
        获取 LLM 调用的额外参数

        支持模型前缀路由到正确的 provider:
        - zai/* -> ZAI Provider
        - openai/* 或 gpt-* -> OpenAI
        - anthropic/* 或 claude-* -> Anthropic
        """
        kwargs: Dict = {}

        # ZAI Provider
        if model.startswith("zai/"):
            from anyclaw.providers.zai import get_zai_provider
            provider = get_zai_provider()
            if provider.is_configured():
                kwargs.update(provider.get_completion_kwargs(model))
            return kwargs

        # OpenAI
        if model.startswith("openai/") or model.startswith("gpt"):
            if settings.openai_api_key:
                kwargs["api_key"] = settings.openai_api_key
            return kwargs

        # Anthropic
        if model.startswith("anthropic/") or model.startswith("claude"):
            if settings.anthropic_api_key:
                kwargs["api_key"] = settings.anthropic_api_key
            return kwargs

        # 默认使用 OpenAI API Key
        if settings.openai_api_key:
            kwargs["api_key"] = settings.openai_api_key

        return kwargs

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

    # ========== 流式输出支持 ==========

    async def process_stream(self, user_input: str):
        """流式处理用户输入（async generator）

        Args:
            user_input: 用户输入文本

        Yields:
            str: 响应内容块
        """
        # 1. 添加用户消息到历史
        self.history.add_user_message(user_input)

        # 2. 构建上下文
        context_builder = ContextBuilder(self.history, self._get_skills_info())
        messages = context_builder.build()

        # 3. 流式调用 LLM
        full_response = []

        try:
            if self.enable_tools and self.tool_loop and self.skills:
                # Tool Calling 流式
                async for chunk in self._stream_with_tools(messages):
                    full_response.append(chunk)
                    yield chunk
            else:
                # 普通流式
                async for chunk in self._stream_llm(messages):
                    full_response.append(chunk)
                    yield chunk

        except Exception as e:
            error_msg = f"[Stream Error: {str(e)}]"
            full_response.append(error_msg)
            yield error_msg

        # 4. 保存完整响应到历史
        self.history.add_assistant_message("".join(full_response))

    async def _stream_llm(self, messages: list):
        """流式调用 LLM

        Args:
            messages: 消息列表

        Yields:
            str: 响应内容块
        """
        try:
            kwargs = self._get_llm_kwargs(settings.llm_model)
            kwargs["model"] = settings.llm_model
            kwargs["messages"] = messages
            kwargs["temperature"] = settings.llm_temperature
            kwargs["max_tokens"] = settings.llm_max_tokens
            kwargs["timeout"] = settings.llm_timeout
            kwargs["stream"] = True  # 启用流式

            response = await acompletion(**kwargs)

            async for chunk in response:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content

        except Exception as e:
            yield f"[Error: {str(e)}]"

    async def _stream_with_tools(self, messages: list):
        """Tool Calling 流式处理

        Args:
            messages: 消息列表

        Yields:
            str: 响应内容块
        """
        # 简化实现：先流式获取响应，然后处理工具调用
        # 完整的 Tool Calling 流式需要更复杂的实现

        iteration = 0
        current_messages = list(messages)

        while iteration < settings.tool_max_iterations:
            # 流式获取响应
            response_text = []

            async for chunk in self._stream_llm(current_messages):
                response_text.append(chunk)
                yield chunk

            full_response = "".join(response_text)

            # 检查是否需要调用工具
            # 这里简化处理，直接返回响应
            # 完整实现需要解析响应中的工具调用
            break

    async def process_with_stream_fallback(self, user_input: str) -> str:
        """带回退的流式处理（如果不支持流式则回退到普通模式）

        Args:
            user_input: 用户输入文本

        Returns:
            str: 完整响应
        """
        if not settings.stream_enabled:
            return await self.process(user_input)

        # 收集流式输出
        chunks = []
        async for chunk in self.process_stream(user_input):
            chunks.append(chunk)

        return "".join(chunks)
