"""Command Context - Execution context for command handlers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from anyclaw.channels.base import BaseChannel
    from anyclaw.config.settings import Settings
    from anyclaw.session.manager import SessionManager
    from anyclaw.agent.loop import AgentLoop


@dataclass
class CommandContext:
    """Context passed to command handlers during execution.

    Contains all the information needed for a command to execute,
    including session state, configuration, and channel information.
    """

    # User identification
    user_id: str
    """Unique identifier for the user who sent the command."""

    chat_id: str
    """Unique identifier for the chat/conversation."""

    # Channel information
    channel: Optional[BaseChannel] = None
    """The channel through which the command was received."""

    channel_type: str = "cli"
    """Type of channel: 'cli', 'discord', 'feishu', etc."""

    # Session information
    session_key: Optional[str] = None
    """Current session key."""

    session_id: Optional[str] = None
    """Current session ID."""

    # Configuration
    config: Optional[Settings] = None
    """Application settings."""

    # Managers (for commands that need them)
    session_manager: Optional[SessionManager] = None
    """Session manager for creating/resetting sessions."""

    agent_loop: Optional[AgentLoop] = None
    """Current agent loop for abort operations."""

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional context-specific data."""

    @property
    def is_cli(self) -> bool:
        """Check if command is from CLI channel."""
        return self.channel_type == "cli"

    @property
    def is_discord(self) -> bool:
        """Check if command is from Discord channel."""
        return self.channel_type == "discord"

    @property
    def is_feishu(self) -> bool:
        """Check if command is from Feishu channel."""
        return self.channel_type == "feishu"

    @property
    def is_im_channel(self) -> bool:
        """Check if command is from an IM channel (Discord/Feishu/etc)."""
        return self.channel_type in ("discord", "feishu", "telegram", "slack")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from metadata.

        Args:
            key: Metadata key.
            default: Default value if key not found.

        Returns:
            Value from metadata or default.
        """
        return self.metadata.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a value in metadata.

        Args:
            key: Metadata key.
            value: Value to set.
        """
        self.metadata[key] = value
