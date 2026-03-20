"""Info Command Handlers - /help, /status, /version."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from anyclaw.commands.base import CommandHandler, CommandResult
from anyclaw.commands.context import CommandContext

if TYPE_CHECKING:
    pass


class HelpCommandHandler(CommandHandler):
    """Handle /help command - show help information.

    Usage:
        /help     - Show all available commands
        /?        - Same as /help (alias)
    """

    @property
    def description(self) -> str:
        return "显示帮助信息"

    @property
    def aliases(self) -> list[str]:
        return ["?", "h"]

    async def execute(
        self,
        args: Optional[str],
        context: CommandContext,
    ) -> CommandResult:
        """Execute /help command.

        Args:
            args: Ignored.
            context: Execution context.

        Returns:
            CommandResult with help text.
        """
        # Build help text
        lines = [
            "📖 **AnyClaw 命令帮助**",
            "",
            "**会话控制**",
            "  /new [message]  - 创建新会话",
            "  /reset          - 重置当前会话",
            "  /clear          - 清屏（仅 CLI）",
            "",
            "**任务控制**",
            "  /stop           - 停止当前任务",
            "  /abort          - 同 /stop",
            "",
            "**信息查询**",
            "  /help, /?       - 显示帮助",
            "  /status         - 显示会话状态",
            "  /version        - 显示版本号",
            "",
            "**高级命令**（需要 Advanced 特性）",
            "  /compact        - 压缩上下文",
            "  /model [name]   - 查看/切换模型",
            "  /agent [name]   - 查看/切换 Agent",
            "",
            "💡 提示: 输入以 / 开头的消息会被识别为命令",
        ]

        return CommandResult.success("\n".join(lines))


class StatusCommandHandler(CommandHandler):
    """Handle /status command - show session status.

    Usage:
        /status    - Show current session status
    """

    @property
    def description(self) -> str:
        return "显示会话状态"

    @property
    def aliases(self) -> list[str]:
        return ["info"]

    async def execute(
        self,
        args: Optional[str],
        context: CommandContext,
    ) -> CommandResult:
        """Execute /status command.

        Args:
            args: Ignored.
            context: Execution context.

        Returns:
            CommandResult with status information.
        """
        lines = ["📊 **会话状态**", ""]

        # Basic info
        lines.append(f"**渠道**: {context.channel_type}")
        lines.append(f"**用户 ID**: {context.user_id}")
        lines.append(f"**聊天 ID**: {context.chat_id}")

        # Session info
        if context.session_key:
            lines.append(f"**会话 Key**: {context.session_key}")
        if context.session_id:
            lines.append(f"**会话 ID**: {context.session_id}")

        # Model info
        if context.config:
            config = context.config
            if hasattr(config, "llm") and hasattr(config.llm, "model"):
                lines.append(f"**模型**: {config.llm.model}")
            if hasattr(config, "llm") and hasattr(config.llm, "provider"):
                lines.append(f"**Provider**: {config.llm.provider}")

        # Message count (if available)
        message_count = context.get("message_count", "N/A")
        lines.append(f"**消息数量**: {message_count}")

        # Token usage (if available)
        token_usage = context.get("token_usage")
        if token_usage:
            lines.append(f"**Token 使用**: {token_usage}")

        return CommandResult.success("\n".join(lines))


class VersionCommandHandler(CommandHandler):
    """Handle /version command - show version.

    Usage:
        /version    - Show AnyClaw version
    """

    @property
    def description(self) -> str:
        return "显示版本号"

    @property
    def aliases(self) -> list[str]:
        return ["v", "ver"]

    async def execute(
        self,
        args: Optional[str],
        context: CommandContext,
    ) -> CommandResult:
        """Execute /version command.

        Args:
            args: Ignored.
            context: Execution context.

        Returns:
            CommandResult with version info.
        """
        try:
            from anyclaw import __version__

            version = __version__
        except ImportError:
            version = "unknown"

        lines = [
            "📦 **AnyClaw 版本信息**",
            "",
            f"**版本**: {version}",
            "**框架**: Python 3.11+",
        ]

        return CommandResult.success("\n".join(lines))
