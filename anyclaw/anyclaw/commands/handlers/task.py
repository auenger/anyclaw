"""Task Command Handlers - /stop, /abort."""

from __future__ import annotations

from typing import Optional

from anyclaw.commands.base import CommandHandler, CommandResult
from anyclaw.commands.context import CommandContext


class StopCommandHandler(CommandHandler):
    """Handle /stop command - stop current task.

    Usage:
        /stop     - Stop current LLM call or tool execution
        /abort    - Same as /stop (alias)

    This command aborts:
    - Ongoing LLM generation
    - Running tool calls
    - Active skill execution
    """

    @property
    def description(self) -> str:
        return "停止当前任务"

    @property
    def aliases(self) -> list[str]:
        return ["stop", "abort"]

    async def execute(
        self,
        args: Optional[str],
        context: CommandContext,
    ) -> CommandResult:
        """Execute /stop command.

        Args:
            args: Ignored.
            context: Execution context.

        Returns:
            CommandResult with stop confirmation.
        """
        # Get agent loop from context
        agent_loop = context.agent_loop

        if agent_loop is None:
            return CommandResult.success("⏹️ 没有正在执行的任务")

        # Check if there's an active task
        if not hasattr(agent_loop, "is_running") or not agent_loop.is_running:
            return CommandResult.success("⏹️ 没有正在执行的任务")

        # Abort the task
        try:
            # Call abort method on agent loop
            if hasattr(agent_loop, "abort"):
                await agent_loop.abort()
                return CommandResult.success("⏹️ 任务已停止")
            else:
                return CommandResult.success("⏹️ 没有可停止的任务")

        except Exception as e:
            return CommandResult.fail(f"停止任务失败: {e}")


class AbortCommandHandler(CommandHandler):
    """Handle /abort command - alias for /stop.

    This is a separate handler for the /abort alias,
    but it just delegates to StopCommandHandler.
    """

    @property
    def description(self) -> str:
        return "中止当前任务"

    @property
    def aliases(self) -> list[str]:
        return ["abort"]

    async def execute(
        self,
        args: Optional[str],
        context: CommandContext,
    ) -> CommandResult:
        """Execute /abort command.

        Args:
            args: Ignored.
            context: Execution context.

        Returns:
            CommandResult from StopCommandHandler.
        """
        stop_handler = StopCommandHandler()
        return await stop_handler.execute(args, context)
