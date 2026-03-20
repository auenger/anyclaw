"""Session Command Handlers - /new, /reset, /clear."""

from __future__ import annotations

import os
from typing import Optional

from anyclaw.commands.base import CommandHandler, CommandResult
from anyclaw.commands.context import CommandContext


class NewCommandHandler(CommandHandler):
    """Handle /new command - create a new session.

    Usage:
        /new              - Create new session
        /new <message>    - Create new session with first message
    """

    @property
    def description(self) -> str:
        return "创建新会话"

    @property
    def aliases(self) -> list[str]:
        return ["new"]

    async def execute(
        self,
        args: Optional[str],
        context: CommandContext,
    ) -> CommandResult:
        """Execute /new command.

        Args:
            args: Optional first message for the new session.
            context: Execution context.

        Returns:
            CommandResult with new session confirmation.
        """
        # Get session manager from context
        session_manager = context.session_manager

        if session_manager is None:
            return CommandResult.success("✅ 新会话已创建")

        # Create new session
        try:
            # Generate new session key
            import uuid

            new_session_id = str(uuid.uuid4())[:8]
            new_session_key = f"{context.user_id}:{context.chat_id}:{new_session_id}"

            # Store the new session key in context for the caller to use
            context.set("new_session_key", new_session_key)

            # If there's a first message, store it for processing
            if args and args.strip():
                context.set("first_message", args.strip())
                return CommandResult.success(
                    f"✅ 新会话已创建\n\n你的消息: {args.strip()}"
                )

            return CommandResult.success("✅ 新会话已创建")

        except Exception as e:
            return CommandResult.fail(f"创建新会话失败: {e}")


class ResetCommandHandler(CommandHandler):
    """Handle /reset command - reset current session.

    Usage:
        /reset    - Clear session history, keep config
    """

    @property
    def description(self) -> str:
        return "重置当前会话"

    @property
    def aliases(self) -> list[str]:
        return ["reset"]

    async def execute(
        self,
        args: Optional[str],
        context: CommandContext,
    ) -> CommandResult:
        """Execute /reset command.

        Args:
            args: Ignored.
            context: Execution context.

        Returns:
            CommandResult with reset confirmation.
        """
        # Get session manager from context
        session_manager = context.session_manager

        if session_manager is None:
            return CommandResult.success("✅ 会话已重置")

        # Reset session
        try:
            if context.session_key:
                # Clear history but keep session
                context.set("reset_session", True)
                return CommandResult.success("✅ 会话已重置，历史消息已清空")

            return CommandResult.success("✅ 会话已重置")

        except Exception as e:
            return CommandResult.fail(f"重置会话失败: {e}")


class ClearCommandHandler(CommandHandler):
    """Handle /clear command - clear terminal screen.

    Usage:
        /clear    - Clear terminal (CLI only)

    Note:
        This command only works in CLI channel.
        In other channels, it returns a friendly message.
    """

    @property
    def description(self) -> str:
        return "清屏（仅 CLI）"

    @property
    def aliases(self) -> list[str]:
        return ["clear"]

    async def execute(
        self,
        args: Optional[str],
        context: CommandContext,
    ) -> CommandResult:
        """Execute /clear command.

        Args:
            args: Ignored.
            context: Execution context.

        Returns:
            CommandResult with clear action.
        """
        # Only works in CLI
        if not context.is_cli:
            return CommandResult.success(
                "💡 /clear 命令仅在命令行界面有效。\n"
                "在其他渠道中，可以使用 /reset 重置会话。"
            )

        # Clear terminal
        try:
            # ANSI escape code to clear screen
            os.system("clear" if os.name == "posix" else "cls")
            return CommandResult.success("")  # Empty reply, screen is cleared

        except Exception as e:
            return CommandResult.fail(f"清屏失败: {e}")
