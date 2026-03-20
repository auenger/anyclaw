"""Compact Command Handler - /compact for context compression."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from anyclaw.commands.base import CommandHandler, CommandResult
from anyclaw.commands.context import CommandContext

if TYPE_CHECKING:
    from anyclaw.agent.history import ConversationHistory


class CompactCommandHandler(CommandHandler):
    """Handle /compact command - compress conversation context.

    Usage:
        /compact                  - Compress with default settings
        /compact <instructions>   - Compress with custom instructions
    """

    @property
    def description(self) -> str:
        return "压缩上下文"

    @property
    def aliases(self) -> list[str]:
        return ["compress"]

    async def execute(
        self,
        args: Optional[str],
        context: CommandContext,
    ) -> CommandResult:
        """Execute /compact command.

        Args:
            args: Optional compression instructions.
            context: Execution context.

        Returns:
            CommandResult with compression result.
        """
        # Get conversation history from context
        history: ConversationHistory | None = context.get("history")

        if history is None:
            return CommandResult.success(
                "⚠️ 无法压缩：没有找到对话历史。\n"
                "请确保在活跃的会话中使用此命令。"
            )

        # Check if there's enough history to compress
        message_count = len(history.messages) if hasattr(history, "messages") else 0

        if message_count < 5:
            return CommandResult.success(
                f"💡 当前消息数量较少 ({message_count} 条)，无需压缩。\n"
                "当消息数量超过 10 条时，压缩会更加有效。"
            )

        try:
            # Get token count before compression
            tokens_before = self._estimate_tokens(history)

            # Perform compression
            custom_instructions = args.strip() if args else None

            if hasattr(history, "compress"):
                if custom_instructions:
                    await history.compress(instructions=custom_instructions)
                else:
                    await history.compress()
            else:
                return CommandResult.fail("压缩功能不可用")

            # Get token count after compression
            tokens_after = self._estimate_tokens(history)

            # Calculate reduction
            reduction = tokens_before - tokens_after
            reduction_pct = (reduction / tokens_before * 100) if tokens_before > 0 else 0

            return CommandResult.success(
                f"⚙️ 上下文已压缩\n"
                f"   {tokens_before:,} → {tokens_after:,} tokens (-{reduction_pct:.1f}%)"
            )

        except Exception as e:
            return CommandResult.fail(f"压缩失败: {e}")

    def _estimate_tokens(self, history: ConversationHistory) -> int:
        """Estimate token count from history.

        Args:
            history: Conversation history.

        Returns:
            Estimated token count.
        """
        if hasattr(history, "token_count"):
            return history.token_count

        # Rough estimate: ~4 chars per token
        total_chars = 0
        if hasattr(history, "messages"):
            for msg in history.messages:
                content = getattr(msg, "content", "") or ""
                total_chars += len(content)

        return total_chars // 4
