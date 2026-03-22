"""Agent 主处理循环"""

import asyncio
import json
import logging
import time
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any, AsyncGenerator, Awaitable, Callable, Dict, List, Optional

# 优化 litellm 性能
import litellm

litellm.drop_params = True
litellm.set_verbose = False
litellm.suppress_debug_info = True  # 禁用 "Give Feedback / Get Help" 提示
# 重试配置（将在 Settings 加载后更新）
litellm.num_retries = 3  # 默认值，后续会根据 settings 更新

from litellm import acompletion

from anyclaw.bus.events import OutboundMessage  # 新增导入
from anyclaw.config.settings import settings
from anyclaw.config.settings import settings as global_settings
from anyclaw.cron.service import CronService
from anyclaw.cron.tool import CronTool
from anyclaw.security.path import create_path_guard_from_settings
from anyclaw.security.sanitizers import ContentSanitizer
from anyclaw.skills.models import SkillDefinition
from anyclaw.tools.filesystem import ListDirTool, ReadFileTool, WriteFileTool
from anyclaw.tools.memory import SaveMemoryTool, UpdatePersonaTool
from anyclaw.tools.registry import ToolRegistry
from anyclaw.tools.search import SearchFilesTool
from anyclaw.tools.shell import ExecTool

from .context import ContextBuilder
from .history import ConversationHistory
from .logger import get_agent_logger
from .summary import (
    IterationSummaryCollector,
    IterationSummaryGenerator,
)

logger = logging.getLogger(__name__)
agent_logger = get_agent_logger()


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

        # CronService（定时任务）
        self._cron_service: Optional[CronService] = None
        self._cron_tool: Optional[CronTool] = None

        # 任务中断机制
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._abort_flags: Dict[str, bool] = {}

        # SessionManager（可选）
        self.session_manager: Optional["SessionManager"] = None
        if enable_session_manager:
            from anyclaw.session.manager import SessionManager, SessionManagerConfig

            # 检查是否启用 SessionManager
            session_enabled = getattr(settings, "session_enabled", True)

            if session_enabled:
                session_config = SessionManagerConfig(
                    workspace=self.workspace,
                    sessions_dir=self.workspace / settings.sessions_dir,
                    max_history_messages=getattr(settings, "max_history_messages", 500),
                    enable_persistence=getattr(settings, "enable_session_persistence", True),
                    enable_memory_cache=getattr(settings, "enable_session_cache", True),
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
                from anyclaw.session.archive import ArchiveConfig, SessionArchiveManager

                archive_config = ArchiveConfig(
                    enable_archive=getattr(settings, "enable_session_archive", True),
                    retention_days=getattr(settings, "session_retention_days", 30),
                )
                self.archive_manager = SessionArchiveManager(archive_config)
                logger.debug("SessionArchiveManager enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize SessionArchiveManager: {e}")
                self.archive_manager = None

        # MCP 连接管理
        self._mcp_stack: Optional[AsyncExitStack] = None

        # CronService 初始化（定时任务服务）
        cron_store_path = self.workspace / ".anyclaw" / "cron_jobs.json"
        self._cron_service = CronService(cron_store_path)

        # 初始化 Tool Registry
        self.tools = ToolRegistry()
        if enable_tools:
            self._register_default_tools()

    def _register_default_tools(self) -> None:
        """注册默认工具"""
        # 创建 path_guard（自动处理 allow_all_access）
        path_guard = create_path_guard_from_settings(self.workspace)

        # ExecTool 支持 session cwd
        # Note: session 将在运行时动态获取，初始化时传入 None
        self.tools.register(
            ExecTool(
                working_dir=str(self.workspace),
                timeout=settings.tool_timeout if hasattr(settings, "tool_timeout") else 60,
                session=None,  # session 在运行时通过 get_current_session() 获取
            )
        )

        # 文件工具传递 path_guard
        self.tools.register(
            ReadFileTool(
                workspace=self.workspace,
                path_guard=path_guard,
            )
        )
        self.tools.register(
            WriteFileTool(
                workspace=self.workspace,
                restrict_to_workspace=settings.restrict_to_workspace,
                path_guard=path_guard,
            )
        )

        # 添加 list_dir 超时配置
        list_dir_timeout = getattr(settings, "list_dir_timeout", 30)  # 默认 30 秒
        list_dir_max_entries = getattr(settings, "list_dir_max_entries", 200)  # 默认 200 条
        self.tools.register(
            ListDirTool(
                workspace=self.workspace,
                timeout=list_dir_timeout,
                max_entries=list_dir_max_entries,
                path_guard=path_guard,
            )
        )

        # 记忆工具
        self.tools.register(SaveMemoryTool(workspace_path=str(self.workspace)))
        self.tools.register(UpdatePersonaTool(workspace_path=str(self.workspace)))

        # 新增：MessageTool（如果启用）
        if self.enable_message_tool:
            from anyclaw.agent.tools.message import MessageTool

            self._message_tool = MessageTool()
            self.tools.register(self._message_tool)

        # 智能文件搜索工具
        self.tools.register(
            SearchFilesTool(
                workspace=self.workspace,
                timeout=getattr(settings, "search_timeout", 5.0),
                max_depth=getattr(settings, "search_max_depth", 3),
                max_results=getattr(settings, "search_max_results", 50),
            )
        )

        # CronTool（定时任务）
        if self._cron_service:
            self._cron_tool = CronTool(self._cron_service)
            self.tools.register(self._cron_tool)

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

    # ==================== CronService 生命周期管理 ====================

    async def start_cron_service(self) -> None:
        """启动 CronService

        应该在 Channel 启动时调用。
        """
        if self._cron_service:
            await self._cron_service.start()
            logger.info("CronService started")

    async def stop_cron_service(self) -> None:
        """停止 CronService

        应该在 Channel 关闭时调用。
        """
        if self._cron_service:
            self._cron_service.stop()
            logger.info("CronService stopped")

    def set_cron_context(self, channel: str, chat_id: str) -> None:
        """设置 CronTool 的上下文

        由 Channel 调用，用于设置定时任务消息的投递目标。

        Args:
            channel: 频道名称（如 "cli", "feishu", "discord"）
            chat_id: 会话 ID
        """
        if self._cron_tool:
            self._cron_tool.set_context(channel, chat_id)
            logger.debug(f"CronTool context set: channel={channel}, chat_id={chat_id}")

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

    # ==================== 任务中断机制 ====================

    def register_task(self, session_key: str, task: asyncio.Task) -> None:
        """注册活动任务

        Args:
            session_key: 会话标识
            task: asyncio.Task 实例
        """
        self._active_tasks[session_key] = task
        self._abort_flags[session_key] = False
        logger.debug(f"Task registered: {session_key}")

    def unregister_task(self, session_key: str) -> None:
        """取消注册任务

        Args:
            session_key: 会话标识
        """
        if session_key in self._active_tasks:
            del self._active_tasks[session_key]
        if session_key in self._abort_flags:
            del self._abort_flags[session_key]
        logger.debug(f"Task unregistered: {session_key}")

    def request_abort(self, session_key: str = "default") -> bool:
        """请求中断任务

        Args:
            session_key: 会话标识，默认 "default"

        Returns:
            是否成功请求中断（有活动任务时返回 True）
        """
        if session_key not in self._active_tasks:
            logger.debug(f"No active task to abort: {session_key}")
            return False

        task = self._active_tasks.get(session_key)
        if task and not task.done():
            self._abort_flags[session_key] = True
            task.cancel()
            logger.info(f"Abort requested for task: {session_key}")
            return True

        return False

    def is_abort_requested(self, session_key: str = "default") -> bool:
        """检查是否请求了中断

        Args:
            session_key: 会话标识

        Returns:
            是否请求了中断
        """
        return self._abort_flags.get(session_key, False)

    def has_active_task(self, session_key: str = "default") -> bool:
        """检查是否有活动任务

        Args:
            session_key: 会话标识

        Returns:
            是否有活动任务
        """
        task = self._active_tasks.get(session_key)
        return task is not None and not task.done()

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

        version = getattr(settings, "version", "unknown")
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
            {"name": name, "description": skill.description} for name, skill in self.skills.items()
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

    def set_message_context(
        self, channel: str, chat_id: str, message_id: Optional[str] = None
    ) -> None:
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

        # 记录用户输入
        agent_logger.log_user_input(user_input)

        self.history.add_user_message(user_input)

        # 记录用户消息到 session_manager
        if self.session_manager and self._session_key:
            self.session_manager.add_message(
                self._session_key,
                "user",
                content=user_input,
            )

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
            response = await self._run_with_tools(messages, session_key=self._session_key)
        else:
            response = await self._call_llm(messages)

        self.history.add_assistant_message(response)

        # 记录助手响应（检查是否是迭代摘要)
        is_summary = "迭代摘要" in response or "工作进度汇报" in response
        agent_logger.log_assistant_response(response, settings.llm_model, is_summary=is_summary)

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

        # 记录用户消息到 session_manager
        if self.session_manager and self._session_key:
            self.session_manager.add_message(
                self._session_key,
                "user",
                content=user_input,
            )

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
        response = await self._run_with_tools(messages, session_key=self._session_key)
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
        session_key: str = "default",
    ) -> str:
        """运行带 tool calling 的循环

        Args:
            messages: 对话消息列表
            max_iterations: 最大迭代次数
            on_progress: 进度回调
            session_key: 会话标识，用于中断检测
        """
        iteration = 0
        empty_response_count = 0  # 空响应计数器

        # 初始化迭代摘要收集器
        summary_collector = IterationSummaryCollector()

        # 更新 LiteLLM 重试配置
        litellm.num_retries = settings.llm_max_retries

        # 🔍 详细日志：开始处理
        logger.info(f"[Agent] 🚀 开始处理任务: session_key={session_key}, "
                    f"history_len={len(messages)}, max_iterations={max_iterations}")

        while iteration < max_iterations:
            # 检查中断标志
            if self._abort_flags.get(session_key, False):
                logger.info(f"Task aborted by user: {session_key}")
                self._abort_flags[session_key] = False  # 清除标志
                return "⏹️ 任务已被用户中断"

            iteration += 1

            # 获取工具定义
            tool_defs = self.tools.get_definitions()

            # 🔍 详细日志：LLM 调用前
            logger.info(f"[Agent] 📡 LLM 调用: iteration={iteration}/{max_iterations}, "
                        f"tools_count={len(tool_defs) if tool_defs else 0}")

            # 调用 LLM
            llm_start = time.time()
            response = await self._call_llm_with_tools(messages, tool_defs)
            llm_duration = time.time() - llm_start

            # 🔍 详细日志：LLM 调用后
            has_tool_calls = hasattr(response.choices[0].message, "tool_calls") and response.choices[0].message.tool_calls
            tool_calls_count = len(response.choices[0].message.tool_calls) if has_tool_calls else 0
            logger.info(f"[Agent] ✅ LLM 响应: iteration={iteration}, "
                        f"duration={llm_duration:.2f}s, "
                        f"has_content={bool(response.choices[0].message.content)}, "
                        f"tool_calls={tool_calls_count}")

            message = response.choices[0].message

            # 记录 LLM 响应详情（可选）
            if settings.llm_log_response_detail:
                self._log_llm_response_detail(response, message)

            # 检查是否有 tool calls
            if not hasattr(message, "tool_calls") or not message.tool_calls:
                content = message.content or ""

                # 空响应检测与恢复
                if not content:
                    empty_response_count += 1
                    logger.warning(
                        f"LLM returned empty content (attempt {empty_response_count}/"
                        f"{settings.llm_empty_response_retry + 1})"
                    )

                    if empty_response_count <= settings.llm_empty_response_retry:
                        # 追加提示消息，重新请求
                        messages.append({"role": "user", "content": "请继续完成任务。"})
                        continue  # 继续循环，重新调用 LLM
                    else:
                        # 达到最大重试次数
                        logger.error("Max empty response retries reached")
                        return "抱歉，模型响应异常，请稍后重试。"

                return content

            # 处理 tool calls
            formatted_tool_calls = self._format_tool_calls(message.tool_calls)
            messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": formatted_tool_calls,
                }
            )

            # 记录 assistant 消息（包含 tool_calls）到 session
            if self.session_manager:
                self.session_manager.add_message(
                    self._session_key,
                    "assistant",
                    content=message.content,
                    tool_calls=formatted_tool_calls,
                )

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                # 🔍 详细日志：工具调用前
                logger.info(f"[Agent] 🔧 工具调用: tool={tool_name}, "
                            f"args_preview={str(arguments)[:100]}{'...' if len(str(arguments)) > 100 else ''}")

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
                    agent_logger.log_error(f"Tool {tool_name}", e)
                duration_ms = int((time.time() - start_time) * 1000)

                # 🔍 详细日志：工具调用后
                result_preview = result[:100] if result else "empty"
                logger.info(f"[Agent] ✅ 工具完成: tool={tool_name}, "
                            f"duration={duration_ms}ms, success={success}, "
                            f"result_preview={result_preview}{'...' if len(result) > 100 else ''}")

                # 记录到迭代摘要收集器
                summary_collector.record_tool_call(
                    name=tool_name,
                    arguments=arguments,
                    result=result,
                    duration_ms=duration_ms,
                    success=success,
                )

                # 记录工具调用日志
                agent_logger.log_tool_call(tool_name, arguments, result, duration_ms)

                # 记录工具结果到归档
                if self.archive_manager and call_id:
                    self.archive_manager.record_tool_result(
                        call_id,
                        result[: self._TOOL_RESULT_MAX_CHARS],
                        duration_ms=duration_ms,
                        success=success,
                    )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result[: self._TOOL_RESULT_MAX_CHARS],
                    }
                )

                # 记录 tool 结果到 session
                if self.session_manager:
                    self.session_manager.add_message(
                        self._session_key,
                        "tool",
                        content=result[: self._TOOL_RESULT_MAX_CHARS],
                        tool_call_id=tool_call.id,
                        name=tool_name,
                    )

        # 达到最大迭代次数，生成智能汇报
        logger.info(f"[Agent] 📊 达到最大迭代次数 {max_iterations}，生成进度汇报...")
        summary = await self._generate_iteration_summary(summary_collector, messages, max_iterations)
        logger.info(f"[Agent] ✅ 进度汇报生成完成: len={len(summary)}")
        return summary

    async def _generate_iteration_summary(
        self,
        collector: IterationSummaryCollector,
        messages: List[Dict[str, Any]],
        max_iterations: int,
    ) -> str:
        """生成迭代限制智能汇报"""
        # 检查是否启用智能汇报
        enabled = getattr(global_settings, "iteration_summary_enabled", True)
        max_tokens = getattr(global_settings, "iteration_summary_max_tokens", 1000)

        generator = IterationSummaryGenerator(enabled=enabled, max_tokens=max_tokens)
        return await generator.generate(collector, messages, max_iterations)

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
            formatted.append(
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
            )
        return formatted

    def _log_llm_response_detail(self, response, message) -> None:
        """记录 LLM 响应详情（DEBUG 级别）

        Args:
            response: LLM 响应对象
            message: 响应消息对象
        """
        has_content = bool(message.content)
        has_tool_calls = hasattr(message, "tool_calls") and bool(message.tool_calls)
        tool_calls_count = len(message.tool_calls) if has_tool_calls else 0

        # 提取 usage 信息
        usage = None
        if hasattr(response, "usage") and response.usage:
            usage = {
                "prompt": getattr(response.usage, "prompt_tokens", "?"),
                "completion": getattr(response.usage, "completion_tokens", "?"),
                "total": getattr(response.usage, "total_tokens", "?"),
            }

        # 提取 finish_reason
        finish_reason = (
            getattr(response.choices[0], "finish_reason", None) if response.choices else None
        )

        logger.debug(
            f"[LLM] Response detail: model={settings.llm_model}, "
            f"content={has_content}, tool_calls={has_tool_calls}({tool_calls_count}), "
            f"usage={usage}, finish_reason={finish_reason}"
        )

        # 如果是空响应，记录更详细的信息
        if not has_content and not has_tool_calls:
            logger.warning(
                f"[LLM] Empty response detected: finish_reason={finish_reason}, "
                f"response_type={type(response).__name__}"
            )
