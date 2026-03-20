"""Agent 主处理循环"""

import asyncio
import json
import logging
import re
import time
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Optional, Dict, List, Any, AsyncGenerator, Callable, Awaitable

# 优化 litellm 性能
import litellm
litellm.drop_params = True
litellm.set_verbose = False
litellm.suppress_debug_info = True  # 禁用 "Give Feedback / Get Help" 提示

from litellm import acompletion

from anyclaw.config.settings import settings
from anyclaw.skills.models import SkillDefinition
from anyclaw.tools.registry import ToolRegistry
from anyclaw.tools.shell import ExecTool
from anyclaw.tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool
from anyclaw.tools.memory import SaveMemoryTool, UpdatePersonaTool
from anyclaw.bus.events import OutboundMessage  # 新增导入
from anyclaw.security.sanitizers import ContentSanitizer
from anyclaw.security.validators import ValidationError
from .history import ConversationHistory
from .context import ContextBuilder

logger = logging.getLogger(__name__)


class AgentLoop:
    """Agent 主处理循环"""

    _TOOL_RESULT_MAX_CHARS = 16_000

    def __init__(
        self,
        enable_tools: bool = True,
        workspace: Optional[Path] = None,
        enable_session_manager: bool = True,  # 新增：是否启用 SessionManager
        enable_message_tool: bool = True,  # 新增：是否启用 MessageTool
        enable_archive: bool = True,  # 新增：是否启用会话归档
    ):
        self.history = ConversationHistory(max_length=10)
        self.skills: Dict[str, SkillDefinition] = {}
        self.enable_tools = enable_tools
        self.enable_message_tool = enable_message_tool  # 新增
        self.enable_archive = enable_archive
        self.workspace = workspace or Path.cwd()
        self._message_tool: Optional["MessageTool"] = None  # 新增：MessageTool 实例
        self._session_key: str = "default"  # 当前会话 key

        # SessionManager（可选）
        self.session_manager: Optional["SessionManager"] = None
        if enable_session_manager:
            from anyclaw.session.manager import SessionManager, SessionManagerConfig

            # 检查是否启用 SessionManager
            session_enabled = getattr(settings, 'session_enabled', True)

            if session_enabled:
                session_config = SessionManagerConfig(
                    workspace=self.workspace,
                    sessions_dir=self.workspace / settings.sessions_dir,
                    max_history_messages=getattr(settings, 'max_history_messages', 500),
                    enable_persistence=getattr(settings, 'enable_session_persistence', True),
                    enable_memory_cache=getattr(settings, 'enable_session_cache', True)
                )
                try:
                    from anyclaw.session.manager import SessionManager
                    self.session_manager = SessionManager(session_config)
                    logger.info("SessionManager enabled")
                except ImportError as e:
                    logger.warning(f"Failed to initialize SessionManager: {e}")
                    self.session_manager = None
            else:
                logger.debug("SessionManager disabled")

        # SessionArchiveManager（会话归档）
        self.archive_manager: Optional["SessionArchiveManager"] = None
        if enable_archive:
            try:
                from anyclaw.session.archive import SessionArchiveManager, ArchiveConfig
                archive_config = ArchiveConfig(
                    enable_archive=getattr(settings, 'enable_session_archive', True),
                    retention_days=getattr(settings, 'session_retention_days', 30),
                )
                self.archive_manager = SessionArchiveManager(archive_config)
                logger.debug("SessionArchiveManager enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize SessionArchiveManager: {e}")
                self.archive_manager = None

        # MCP 连接管理
        self._mcp_stack: Optional[AsyncExitStack] = None

        # 初始化 Tool Registry
        self.tools = ToolRegistry()
        if enable_tools:
            self._register_default_tools()

    def _register_default_tools(self) -> None:
        """注册默认工具"""
        self.tools.register(ExecTool(
            working_dir=str(self.workspace),
            timeout=settings.tool_timeout if hasattr(settings, 'tool_timeout') else 60,
        ))
        self.tools.register(ReadFileTool(workspace=self.workspace))
        self.tools.register(WriteFileTool(
            workspace=self.workspace,
            restrict_to_workspace=settings.restrict_to_workspace,
        ))
        # 添加 list_dir 超时配置
        list_dir_timeout = getattr(settings, 'list_dir_timeout', 30)  # 默认 30 秒
        list_dir_max_entries = getattr(settings, 'list_dir_max_entries', 200)  # 默认 200 条
        self.tools.register(ListDirTool(
            workspace=self.workspace,
            timeout=list_dir_timeout,
            max_entries=list_dir_max_entries
        ))

        # 记忆工具
        self.tools.register(SaveMemoryTool(workspace_path=str(self.workspace)))
        self.tools.register(UpdatePersonaTool(workspace_path=str(self.workspace)))

        # 新增：MessageTool（如果启用）
        if self.enable_message_tool:
            from anyclaw.agent.tools.message import MessageTool
            self._message_tool = MessageTool()
            self.tools.register(self._message_tool)

    async def connect_mcp_servers(self) -> None:
        """连接配置的 MCP Server 并注册工具

        必须在使用前调用此方法来建立 MCP 连接。
        使用 close_mcp_servers() 来清理连接。
        """
        if self._mcp_stack is not None:
            return  # 已经连接

        mcp_servers = settings.mcp_servers
        if not mcp_servers:
            return  # 没有配置 MCP servers

        self._mcp_stack = AsyncExitStack()
        await self._mcp_stack.__aenter__()

        try:
            from anyclaw.tools.mcp import connect_mcp_servers
            await connect_mcp_servers(mcp_servers, self.tools, self._mcp_stack)
            logger.info("MCP servers connected")
        except Exception as e:
            logger.error("Failed to connect MCP servers: %s", e)
            await self._mcp_stack.aclose()
            self._mcp_stack = None
            raise

    async def close_mcp_servers(self) -> None:
        """关闭 MCP Server 连接"""
        if self._mcp_stack is not None:
            await self._mcp_stack.aclose()
            self._mcp_stack = None
            logger.info("MCP servers disconnected")

    async def __aenter__(self):
        """支持 async context manager"""
        await self.connect_mcp_servers()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """支持 async context manager"""
        await self.close_mcp_servers()
        return False

    def set_skills(self, skills: Dict[str, SkillDefinition]) -> None:
        """设置可用技能（兼容旧接口）"""
        self.skills = skills

    # ==================== 会话归档方法 ====================

    def start_archive_session(
        self,
        channel: str = "cli",
        channel_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        开始归档会话

        Args:
            channel: 渠道类型（cli/feishu/discord）
            channel_id: 渠道 ID

        Returns:
            会话 ID，如果归档未启用则返回 None
        """
        if not self.archive_manager:
            return None

        version = getattr(settings, 'version', 'unknown')
        return self.archive_manager.start_session(
            cwd=self.workspace,
            channel=channel,
            channel_id=channel_id,
            version=version,
        )

    def end_archive_session(self) -> None:
        """结束归档会话"""
        if self.archive_manager:
            self.archive_manager.end_session()

    def set_session_key(self, key: str) -> None:
        """设置当前会话 key"""
        self._session_key = key

    def _get_skills_info(self) -> List[Dict[str, Any]]:
        """获取技能信息列表"""
        return [
            {"name": name, "description": skill.description}
            for name, skill in self.skills.items()
        ]

    # SessionManager 适配器方法
    def get_session(self, key: str) -> Optional["Session"]:
        """获取会话（优先使用 SessionManager，向后兼容 History）"""
        if self.session_manager:
            return self.session_manager.get_or_create(key)
        # 向后兼容：使用 history
        return self.history

    def add_message(self, key: str, role: str, content: Optional[str] = None, **kwargs) -> None:
        """添加消息到会话（适配器模式）"""
        if self.session_manager:
            return self.session_manager.add_message(key, role, content, **kwargs)
        # 向后兼容
        return self.history.add(role, content)

    def get_conversation_history(self, key: str, max_messages: int = None) -> List[Dict[str, Any]]:
        """获取会话历史（适配器模式）"""
        if self.session_manager:
            return self.session_manager.get_history(key, max_messages)
        # 向后兼容
        return self.history.get_messages(max_messages)

    # MessageTool 适配器方法
    def set_message_callback(self, callback: Callable[[OutboundMessage], Awaitable[None]]) -> None:
        """设置 MessageTool 的发送回调（由 Channel 调用）"""
        if self._message_tool:
            self._message_tool.set_send_callback(callback)

    def set_message_context(self, channel: str, chat_id: str, message_id: Optional[str] = None) -> None:
        """设置 MessageTool 的上下文（由 Channel 调用）"""
        if self._message_tool:
            self._message_tool.set_context(channel, chat_id, message_id)

    def message_sent_in_turn(self) -> bool:
        """检查当前回合是否通过 MessageTool 发送过消息"""
        if self._message_tool:
            return self._message_tool._sent_in_turn
        return False

    def start_turn(self) -> None:
        """开始新回合（重置发送跟踪）"""
        if self._message_tool:
            self._message_tool.start_turn()

    def set_spawn_context(self, channel: str, chat_id: str) -> None:
        """设置 SpawnTool 的上下文（由 Channel 调用）"""
        if self._spawn_tool and hasattr(self._spawn_tool, "set_context"):
            self._spawn_tool.set_context(channel, chat_id)

    async def process(self, user_input: str) -> str:
        """处理用户输入"""
        # 清理和验证用户输入
        try:
            user_input = ContentSanitizer.sanitize_message(user_input)
        except ValueError as e:
            return f"错误: {e}"

        self.history.add_user_message(user_input)

        # 记录用户消息到归档
        if self.archive_manager:
            self.archive_manager.record_user_message(user_input)

        context_builder = ContextBuilder(
            self.history,
            self._get_skills_info(),
            workspace=self.workspace,
        )
        messages = context_builder.build()

        if self.enable_tools:
            response = await self._run_with_tools(messages)
        else:
            response = await self._call_llm(messages)

        self.history.add_assistant_message(response)

        # 记录助手消息到归档
        if self.archive_manager:
            self.archive_manager.record_assistant_message(
                response,
                model=settings.llm_model,
            )

        return response

    async def process_stream(self, user_input: str) -> AsyncGenerator[str, None]:
        """流式处理用户输入"""
        # 清理和验证用户输入
        try:
            user_input = ContentSanitizer.sanitize_message(user_input)
        except ValueError as e:
            yield f"错误: {e}"
            return

        self.history.add_user_message(user_input)

        # 记录用户消息到归档
        if self.archive_manager:
            self.archive_manager.record_user_message(user_input)

        context_builder = ContextBuilder(
            self.history,
            self._get_skills_info(),
            workspace=self.workspace,
        )
        messages = context_builder.build()

        full_response = []

        try:
            if self.enable_tools:
                async for chunk in self._stream_with_tools(messages):
                    full_response.append(chunk)
                    yield chunk
            else:
                async for chunk in self._stream_llm(messages):
                    full_response.append(chunk)
                    yield chunk
        except Exception as e:
            error_msg = f"[错误: {str(e)}]"
            full_response.append(error_msg)
            yield error_msg

        response_text = "".join(full_response)
        self.history.add_assistant_message(response_text)

        # 记录助手消息到归档
        if self.archive_manager:
            self.archive_manager.record_assistant_message(
                response_text,
                model=settings.llm_model,
            )

    async def _stream_with_tools(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """流式处理（支持 tool calling）"""
        # 暂时使用非流式处理 tool calling
        response = await self._run_with_tools(messages)
        yield response

    async def _stream_llm(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        """流式调用 LLM"""
        kwargs = self._get_llm_kwargs(settings.llm_model)
        kwargs["model"] = settings.llm_model
        kwargs["messages"] = messages
        kwargs["temperature"] = settings.llm_temperature
        kwargs["max_tokens"] = settings.llm_max_tokens
        kwargs["timeout"] = settings.llm_timeout
        kwargs["stream"] = True

        response = await acompletion(**kwargs)

        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content

    async def _run_with_tools(
        self,
        messages: List[Dict[str, Any]],
        max_iterations: int = 10,
        on_progress: Optional[Callable[[str, bool], Awaitable[None]]] = None,
    ) -> str:
        """运行带 tool calling 的循环"""
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # 获取工具定义
            tool_defs = self.tools.get_definitions()

            # 调用 LLM
            response = await self._call_llm_with_tools(messages, tool_defs)

            message = response.choices[0].message

            # 检查是否有 tool calls
            if not hasattr(message, 'tool_calls') or not message.tool_calls:
                return message.content or ""

            # 处理 tool calls
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": self._format_tool_calls(message.tool_calls)
            })

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                # 记录工具调用到归档
                call_id = None
                if self.archive_manager:
                    call_id = self.archive_manager.record_tool_call(tool_name, arguments)

                # 显示进度
                if on_progress:
                    hint = self._tool_hint(tool_name, arguments)
                    await on_progress(hint, tool_hint=True)

                # 执行工具
                start_time = time.time()
                try:
                    result = await self.tools.execute(tool_name, arguments)
                    success = True
                except Exception as e:
                    result = f"Error: {e}"
                    success = False
                duration_ms = int((time.time() - start_time) * 1000)

                # 记录工具结果到归档
                if self.archive_manager and call_id:
                    self.archive_manager.record_tool_result(
                        call_id,
                        result[:self._TOOL_RESULT_MAX_CHARS],
                        duration_ms=duration_ms,
                        success=success,
                    )

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result[:self._TOOL_RESULT_MAX_CHARS]
                })

        return "达到最大迭代次数"

    def _tool_hint(self, name: str, args: Dict[str, Any]) -> str:
        """生成工具调用提示"""
        val = next(iter(args.values()), None) if args else None
        if isinstance(val, str) and len(val) > 40:
            return f'{name}("{val[:40]}…")'
        elif isinstance(val, str):
            return f'{name}("{val}")'
        else:
            return name

    def _normalize_model_name(self, model: str) -> str:
        """规范化模型名称

        对于 ZAI provider：
        - zai/glm-4.7 -> openai/glm-4.7 (使用 OpenAI 兼容接口)
        - glm-4.7 -> openai/glm-4.7

        对于其他 provider：
        - 如果没有前缀，根据 provider 添加对应前缀
        """
        # ZAI 特殊处理：使用 OpenAI 兼容接口
        if model.startswith("zai/"):
            # zai/glm-4.7 -> openai/glm-4.7
            return model.replace("zai/", "openai/", 1)

        # 如果已经有前缀，直接返回
        if "/" in model:
            return model

        # 根据配置的 provider 添加前缀
        provider = settings.llm_provider
        provider_prefix_map = {
            "openai": "openai",
            "anthropic": "anthropic",
            "zai": "openai",  # ZAI 使用 OpenAI 兼容接口
            "deepseek": "deepseek",
            "openrouter": "openrouter",
            "ollama": "ollama",
        }

        prefix = provider_prefix_map.get(provider, "openai")
        return f"{prefix}/{model}"

    async def _call_llm(self, messages: list) -> str:
        """调用 LLM（无 tools）"""
        model = self._normalize_model_name(settings.llm_model)
        kwargs = self._get_llm_kwargs(model)

        # 处理模型名覆盖
        actual_model = kwargs.pop("_model_override", model)

        kwargs["model"] = actual_model
        kwargs["messages"] = messages
        kwargs["temperature"] = settings.llm_temperature
        kwargs["max_tokens"] = settings.llm_max_tokens
        kwargs["timeout"] = settings.llm_timeout

        response = await acompletion(**kwargs)
        return response.choices[0].message.content

    async def _call_llm_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ):
        """调用 LLM（带 tools）"""
        model = self._normalize_model_name(settings.llm_model)
        kwargs = self._get_llm_kwargs(model)

        # 处理模型名覆盖
        actual_model = kwargs.pop("_model_override", model)

        kwargs["model"] = actual_model
        kwargs["messages"] = messages
        kwargs["temperature"] = settings.llm_temperature
        kwargs["max_tokens"] = settings.llm_max_tokens
        kwargs["timeout"] = settings.llm_timeout

        if tools:
            kwargs["tools"] = tools

        return await acompletion(**kwargs)

    def _get_llm_kwargs(self, model: str) -> Dict[str, Any]:
        """获取 LLM 调用的额外参数"""
        kwargs: Dict[str, Any] = {}

        # ZAI Provider (使用 OpenAI 兼容接口)
        if model.startswith("openai/") and settings.llm_provider == "zai":
            from anyclaw.providers.zai import get_zai_provider
            provider = get_zai_provider()
            if provider.is_configured():
                kwargs.update(provider.get_completion_kwargs(model))
            return kwargs

        # ZAI Provider (旧格式)
        if model.startswith("zai/"):
            from anyclaw.providers.zai import get_zai_provider
            provider = get_zai_provider()
            if provider.is_configured():
                kwargs.update(provider.get_completion_kwargs(model))
            return kwargs

        # OpenAI
        if model.startswith("openai/"):
            api_key = settings.get_api_key("openai")
            if api_key:
                kwargs["api_key"] = api_key
            return kwargs

        # Anthropic
        if model.startswith("anthropic/"):
            api_key = settings.get_api_key("anthropic")
            if api_key:
                kwargs["api_key"] = api_key
            return kwargs

        # DeepSeek
        if model.startswith("deepseek/"):
            api_key = settings.get_api_key("deepseek")
            if api_key:
                kwargs["api_key"] = api_key
                kwargs["api_base"] = "https://api.deepseek.com/v1"
            return kwargs

        return kwargs

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
