"""Session Command Handler - /session for session lifecycle management."""

from __future__ import annotations

import re
from typing import Optional

from anyclaw.commands.base import CommandHandler, CommandResult
from anyclaw.commands.context import CommandContext


class SessionCommandHandler(CommandHandler):
    """Handle /session command - manage session lifecycle.

    Usage:
        /session                     - Show current session settings
        /session idle <duration>     - Set idle timeout (e.g., "24h", "30m", "off")
        /session max-age <duration>  - Set max age (e.g., "7d", "24h", "off")

    Duration formats:
        - "30m" = 30 minutes
        - "2h" = 2 hours
        - "1d" = 1 day
        - "off" = disable
    """

    @property
    def description(self) -> str:
        return "会话生命周期管理"

    @property
    def aliases(self) -> list[str]:
        return ["sess"]

    async def execute(
        self,
        args: Optional[str],
        context: CommandContext,
    ) -> CommandResult:
        """Execute /session command.

        Args:
            args: Optional subcommand and arguments.
            context: Execution context.

        Returns:
            CommandResult with session info or setting result.
        """
        # CLI channel shows hint that this is mainly for IM
        if context.is_cli:
            if not args or not args.strip():
                return CommandResult.success(
                    "💡 `/session` 命令主要用于 IM 渠道（Discord、飞书等）\n"
                    "用于设置会话的空闲超时和最大存活时间。\n\n"
                    "在 CLI 中，会话会一直保持活跃。"
                )

        # No args - show current settings
        if not args or not args.strip():
            return self._show_settings(context)

        # Parse subcommand
        parts = args.strip().split(maxsplit=1)
        subcommand = parts[0].lower()

        if subcommand == "idle":
            if len(parts) < 2:
                return CommandResult.success("用法: /session idle <时长>\n示例: 24h, 30m, off")
            return self._set_idle_timeout(parts[1], context)

        elif subcommand == "max-age" or subcommand == "maxage":
            if len(parts) < 2:
                return CommandResult.success("用法: /session max-age <时长>\n示例: 7d, 24h, off")
            return self._set_max_age(parts[1], context)

        else:
            return CommandResult.success(
                f"❌ 未知子命令: {subcommand}\n"
                "可用子命令: idle, max-age"
            )

    def _show_settings(self, context: CommandContext) -> CommandResult:
        """Show current session lifecycle settings.

        Args:
            context: Execution context.

        Returns:
            CommandResult with settings info.
        """
        # Get current settings from context
        idle_timeout = context.get("session_idle_timeout", "未设置")
        max_age = context.get("session_max_age", "未设置")

        lines = [
            "⏱️ **会话生命周期设置**",
            "",
            f"**空闲超时**: {idle_timeout}",
            f"**最大存活**: {max_age}",
            "",
            "**设置命令**:",
            "  /session idle <时长>     - 设置空闲超时",
            "  /session max-age <时长>  - 设置最大存活",
            "",
            "**时长格式**: 30m, 2h, 1d, off (禁用)",
        ]

        return CommandResult.success("\n".join(lines))

    def _set_idle_timeout(self, duration: str, context: CommandContext) -> CommandResult:
        """Set idle timeout.

        Args:
            duration: Duration string or "off".
            context: Execution context.

        Returns:
            CommandResult with setting result.
        """
        if duration.lower() == "off":
            context.set("session_idle_timeout", None)
            return CommandResult.success("✅ 空闲超时已禁用")

        parsed = self._parse_duration(duration)
        if parsed is None:
            return CommandResult.success(
                f"❌ 无效的时长格式: {duration}\n"
                "支持的格式: 30m, 2h, 1d"
            )

        # Format for display
        display = self._format_duration(parsed)
        context.set("session_idle_timeout", parsed)

        return CommandResult.success(f"✅ 空闲超时已设置为 {display}")

    def _set_max_age(self, duration: str, context: CommandContext) -> CommandResult:
        """Set max age.

        Args:
            duration: Duration string or "off".
            context: Execution context.

        Returns:
            CommandResult with setting result.
        """
        if duration.lower() == "off":
            context.set("session_max_age", None)
            return CommandResult.success("✅ 最大存活时间已禁用")

        parsed = self._parse_duration(duration)
        if parsed is None:
            return CommandResult.success(
                f"❌ 无效的时长格式: {duration}\n"
                "支持的格式: 30m, 2h, 1d"
            )

        # Format for display
        display = self._format_duration(parsed)
        context.set("session_max_age", parsed)

        return CommandResult.success(f"✅ 最大存活时间已设置为 {display}")

    def _parse_duration(self, duration: str) -> int | None:
        """Parse duration string to seconds.

        Args:
            duration: Duration string (e.g., "30m", "2h", "1d").

        Returns:
            Duration in seconds, or None if invalid.
        """
        pattern = r"^(\d+)(m|h|d)$"
        match = re.match(pattern, duration.lower())

        if not match:
            return None

        value = int(match.group(1))
        unit = match.group(2)

        if unit == "m":
            return value * 60
        elif unit == "h":
            return value * 3600
        elif unit == "d":
            return value * 86400

        return None

    def _format_duration(self, seconds: int) -> str:
        """Format seconds to human-readable duration.

        Args:
            seconds: Duration in seconds.

        Returns:
            Human-readable string.
        """
        if seconds >= 86400:
            return f"{seconds // 86400}d"
        elif seconds >= 3600:
            return f"{seconds // 3600}h"
        elif seconds >= 60:
            return f"{seconds // 60}m"
        else:
            return f"{seconds}s"
