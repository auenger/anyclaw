"""MCP Tool 包装器 - 将 MCP Server Tool 包装为 AnyClaw Tool"""

import asyncio
import logging
from typing import Any, Dict

from anyclaw.tools.base import Tool

logger = logging.getLogger(__name__)


class MCPToolWrapper(Tool):
    """将单个 MCP Server Tool 包装为 AnyClaw Tool

    工具名称格式: mcp_{server_name}_{original_name}
    """

    def __init__(
        self,
        session,
        server_name: str,
        tool_def,
        tool_timeout: int = 30
    ):
        """
        Args:
            session: MCP ClientSession 实例
            server_name: MCP Server 名称
            tool_def: MCP Tool 定义对象
            tool_timeout: 工具调用超时时间（秒）
        """
        self._session = session
        self._server_name = server_name
        self._original_name = tool_def.name
        self._name = f"mcp_{server_name}_{tool_def.name}"
        self._description = tool_def.description or tool_def.name
        self._parameters = tool_def.inputSchema or {"type": "object", "properties": {}}
        self._tool_timeout = tool_timeout

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def parameters(self) -> Dict[str, Any]:
        return self._parameters

    async def execute(self, **kwargs: Any) -> str:
        """执行 MCP Tool

        Returns:
            执行结果字符串
        """
        from mcp import types

        try:
            result = await asyncio.wait_for(
                self._session.call_tool(self._original_name, arguments=kwargs),
                timeout=self._tool_timeout,
            )
        except asyncio.TimeoutError:
            logger.warning(
                "MCP tool '%s' timed out after %ss",
                self._name, self._tool_timeout
            )
            return f"(MCP tool call timed out after {self._tool_timeout}s)"
        except asyncio.CancelledError:
            # MCP SDK 的 anyio cancel scopes 可能在超时/失败时泄露 CancelledError
            # 只有当我们的任务被外部取消时才重新抛出（例如 /stop）
            task = asyncio.current_task()

            # Python 3.11+ has task.cancelling() method that returns the count of
            # cancel requests. If > 0, it's an external cancellation.
            # For Python 3.9-3.10, we don't have a reliable way to distinguish,
            # so we always re-raise to be safe (user cancellation is more important)
            if task is not None and hasattr(task, 'cancelling'):
                # Python 3.11+: can distinguish external vs internal cancellation
                if task.cancelling() == 0:
                    # Internal cancellation from MCP SDK
                    logger.warning(
                        "MCP tool '%s' was cancelled by server/SDK",
                        self._name
                    )
                    return "(MCP tool call was cancelled)"

            # For Python 3.9-3.10 or external cancellation: re-raise
            raise
        except Exception as exc:
            logger.exception(
                "MCP tool '%s' failed: %s: %s",
                self._name, type(exc).__name__, exc
            )
            return f"(MCP tool call failed: {type(exc).__name__})"

        # 格式化结果
        parts = []
        for block in result.content:
            if isinstance(block, types.TextContent):
                parts.append(block.text)
            else:
                parts.append(str(block))

        return "\n".join(parts) or "(no output)"
