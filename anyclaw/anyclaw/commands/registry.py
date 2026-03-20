"""Command Registry - Register and manage command handlers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from anyclaw.commands.base import CommandHandler


class CommandRegistry:
    """Registry for command handlers.

    Manages registration and lookup of command handlers.
    Supports command aliases for alternative command names.

    Example:
        registry = CommandRegistry()
        registry.register("help", HelpHandler())
        registry.register("?", HelpHandler(), alias=True)
        handler = registry.get("help")
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        # Primary command -> handler
        self._handlers: dict[str, CommandHandler] = {}
        # Alias -> primary command name
        self._aliases: dict[str, str] = {}
        # Command descriptions for help
        self._descriptions: dict[str, str] = {}

    def register(
        self,
        name: str,
        handler: CommandHandler,
        aliases: Optional[list[str]] = None,
        description: Optional[str] = None,
    ) -> None:
        """Register a command handler.

        Args:
            name: Primary command name (case-insensitive).
            handler: The command handler instance.
            aliases: Optional list of alternative names.
            description: Optional description for help text.
        """
        name_lower = name.lower()

        self._handlers[name_lower] = handler

        if description:
            self._descriptions[name_lower] = description

        if aliases:
            for alias in aliases:
                self._aliases[alias.lower()] = name_lower

    def get(self, name: str) -> Optional[CommandHandler]:
        """Get handler for a command name or alias.

        Args:
            name: Command name or alias (case-insensitive).

        Returns:
            CommandHandler if found, None otherwise.
        """
        name_lower = name.lower()

        # Check if it's a primary command
        if name_lower in self._handlers:
            return self._handlers[name_lower]

        # Check if it's an alias
        if name_lower in self._aliases:
            primary = self._aliases[name_lower]
            return self._handlers.get(primary)

        return None

    def get_primary_name(self, name: str) -> Optional[str]:
        """Get the primary command name for a command or alias.

        Args:
            name: Command name or alias.

        Returns:
            Primary command name if found, None otherwise.
        """
        name_lower = name.lower()

        if name_lower in self._handlers:
            return name_lower

        if name_lower in self._aliases:
            return self._aliases[name_lower]

        return None

    def get_description(self, name: str) -> Optional[str]:
        """Get description for a command.

        Args:
            name: Command name.

        Returns:
            Description if available, None otherwise.
        """
        primary = self.get_primary_name(name)
        if primary:
            return self._descriptions.get(primary)
        return None

    def list_commands(self) -> list[str]:
        """List all registered primary commands.

        Returns:
            List of command names sorted alphabetically.
        """
        return sorted(self._handlers.keys())

    def list_all_commands_with_aliases(self) -> dict[str, list[str]]:
        """List all commands with their aliases.

        Returns:
            Dict mapping primary command name to list of aliases.
        """
        result: dict[str, list[str]] = {}

        for cmd in self._handlers:
            result[cmd] = []

        for alias, primary in self._aliases.items():
            if primary in result:
                result[primary].append(alias)

        return result

    def get_help_text(self) -> str:
        """Generate help text for all commands.

        Returns:
            Formatted help text string.
        """
        lines = ["Available commands:"]

        commands_with_aliases = self.list_all_commands_with_aliases()

        for cmd in sorted(commands_with_aliases.keys()):
            desc = self._descriptions.get(cmd, "")
            aliases = commands_with_aliases[cmd]

            if aliases:
                alias_str = ", /".join(aliases)
                line = f"  /{cmd} (/{alias_str})"
            else:
                line = f"  /{cmd}"

            if desc:
                line += f" - {desc}"

            lines.append(line)

        return "\n".join(lines)

    def unregister(self, name: str) -> bool:
        """Unregister a command and its aliases.

        Args:
            name: Command name to unregister.

        Returns:
            True if command was unregistered, False if not found.
        """
        name_lower = name.lower()

        if name_lower not in self._handlers:
            return False

        del self._handlers[name_lower]
        self._descriptions.pop(name_lower, None)

        # Remove all aliases pointing to this command
        aliases_to_remove = [
            alias for alias, primary in self._aliases.items() if primary == name_lower
        ]
        for alias in aliases_to_remove:
            del self._aliases[alias]

        return True
