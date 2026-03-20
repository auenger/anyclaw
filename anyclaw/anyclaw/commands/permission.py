"""Permission Manager - Fine-grained command permission control."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Optional, Union

if TYPE_CHECKING:
    from anyclaw.config.settings import Settings


# Permission types
PermissionLevel = Union[Literal["*"], Literal["admin"], list[str]]


@dataclass
class PermissionConfig:
    """Permission configuration for commands.

    Attributes:
        default: Default permission level for all commands.
        commands: Per-command permission overrides.
        admins: List of admin user IDs.
    """

    default: PermissionLevel = "*"
    """Default permission: '*' = everyone, 'admin' = admins only, or list of user IDs."""

    commands: dict[str, PermissionLevel] = None
    """Per-command permission overrides."""

    admins: list[str] = None
    """List of admin user IDs."""

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.commands is None:
            self.commands = {}
        if self.admins is None:
            self.admins = []

    @classmethod
    def from_settings(cls, settings: Optional[Settings]) -> PermissionConfig:
        """Create PermissionConfig from application settings.

        Args:
            settings: Application settings.

        Returns:
            PermissionConfig instance.
        """
        if settings is None:
            return cls()

        # Try to get commands config from settings
        commands_config = getattr(settings, "commands", None)
        if commands_config is None:
            return cls()

        permissions = getattr(commands_config, "permissions", None)
        if permissions is None:
            return cls()

        return cls(
            default=getattr(permissions, "default", "*") or "*",
            commands=dict(getattr(permissions, "commands", {}) or {}),
            admins=list(getattr(permissions, "admins", []) or []),
        )


class PermissionManager:
    """Manages command permissions.

    Supports fine-grained permission control per command:
    - "*" = everyone can use
    - "admin" = only admins
    - ["user1", "user2"] = specific users

    Default behavior: all commands are available to everyone.
    """

    def __init__(self, config: Optional[PermissionConfig] = None) -> None:
        """Initialize permission manager.

        Args:
            config: Permission configuration.
        """
        self.config = config or PermissionConfig()

    def check_permission(self, command: str, user_id: str) -> bool:
        """Check if user has permission to use command.

        Args:
            command: Command name (case-insensitive).
            user_id: User ID to check.

        Returns:
            True if user has permission, False otherwise.
        """
        command_lower = command.lower()

        # Get permission level for this command
        level = self.config.commands.get(command_lower, self.config.default)

        return self._check_level(level, user_id)

    def _check_level(self, level: PermissionLevel, user_id: str) -> bool:
        """Check if user matches permission level.

        Args:
            level: Permission level to check.
            user_id: User ID to check.

        Returns:
            True if user has permission.
        """
        if level == "*":
            # Everyone has permission
            return True

        if level == "admin":
            # Only admins
            return user_id in self.config.admins

        if isinstance(level, list):
            # Specific user list
            return user_id in level

        # Unknown level, default to allow
        return True

    def get_permission_error(self, command: str) -> str:
        """Get error message for permission denied.

        Args:
            command: Command name.

        Returns:
            Error message string.
        """
        return f"⛔ 你没有权限使用 /{command} 命令"

    def is_admin(self, user_id: str) -> bool:
        """Check if user is an admin.

        Args:
            user_id: User ID to check.

        Returns:
            True if user is admin.
        """
        return user_id in self.config.admins

    def get_command_permission(self, command: str) -> PermissionLevel:
        """Get the permission level for a command.

        Args:
            command: Command name.

        Returns:
            Permission level for the command.
        """
        return self.config.commands.get(command.lower(), self.config.default)
