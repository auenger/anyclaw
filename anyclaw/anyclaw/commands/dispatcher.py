"""Command Dispatcher - Dispatch commands to appropriate handlers."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from anyclaw.commands.base import CommandHandler, CommandResult
from anyclaw.commands.context import CommandContext
from anyclaw.commands.parser import CommandParser, ParsedCommand
from anyclaw.commands.permission import PermissionConfig, PermissionManager
from anyclaw.commands.registry import CommandRegistry

if TYPE_CHECKING:
    from anyclaw.config.settings import Settings


logger = logging.getLogger(__name__)


class CommandDispatcher:
    """Dispatch user commands to appropriate handlers.

    Integrates:
    - CommandParser: Parse user input
    - CommandRegistry: Find handlers
    - PermissionManager: Check permissions

    Example:
        dispatcher = CommandDispatcher()
        dispatcher.register("help", HelpHandler(), aliases=["?"], description="Show help")

        result = await dispatcher.dispatch("/help", context)
        if result.handled and result.reply:
            print(result.reply)
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        permission_config: Optional[PermissionConfig] = None,
    ) -> None:
        """Initialize dispatcher.

        Args:
            settings: Application settings for permission config.
            permission_config: Explicit permission config (overrides settings).
        """
        self.parser = CommandParser()
        self.registry = CommandRegistry()

        # Initialize permission manager
        if permission_config:
            perm_config = permission_config
        elif settings:
            perm_config = PermissionConfig.from_settings(settings)
        else:
            perm_config = PermissionConfig()
        self.permissions = PermissionManager(perm_config)

    def register(
        self,
        name: str,
        handler: CommandHandler,
        aliases: Optional[list[str]] = None,
        description: Optional[str] = None,
    ) -> None:
        """Register a command handler.

        Args:
            name: Primary command name.
            handler: Command handler instance.
            aliases: Optional list of aliases.
            description: Optional description for help.
        """
        # Use handler's properties if not specified
        if aliases is None:
            aliases = handler.aliases
        if description is None:
            description = handler.description

        self.registry.register(name, handler, aliases, description)
        logger.debug(f"Registered command: /{name}" + (f" (aliases: {aliases})" if aliases else ""))

    async def dispatch(
        self,
        text: str,
        context: CommandContext,
    ) -> CommandResult:
        """Dispatch user input to command handler.

        Args:
            text: User input text.
            context: Execution context.

        Returns:
            CommandResult from handler or not_handled result.
        """
        # Parse the input
        parsed = self.parser.parse(text)

        if parsed is None:
            # Not a command
            return CommandResult.not_handled()

        # Find handler
        handler = self.registry.get(parsed.name)

        if handler is None:
            # Unknown command - not handled, treat as normal message
            logger.debug(f"Unknown command: /{parsed.name}")
            return CommandResult.not_handled()

        # Get primary command name for permission check
        primary_name = self.registry.get_primary_name(parsed.name) or parsed.name

        # Check permission
        if not self.permissions.check_permission(primary_name, context.user_id):
            error_msg = self.permissions.get_permission_error(primary_name)
            return CommandResult.fail(error_msg)

        # Execute handler
        try:
            logger.debug(f"Executing command: /{parsed.name} (args: {parsed.args})")
            result = await handler.execute(parsed.args, context)
            return result

        except Exception as e:
            logger.error(f"Command execution failed: /{parsed.name} - {e}")
            return CommandResult.fail(f"命令执行失败: {e}")

    def is_command(self, text: str) -> bool:
        """Check if text is a command.

        Args:
            text: User input text.

        Returns:
            True if text is a command.
        """
        return self.parser.is_command(text)

    def get_help_text(self) -> str:
        """Get help text for all registered commands.

        Returns:
            Formatted help text.
        """
        return self.registry.get_help_text()

    def list_commands(self) -> list[str]:
        """List all registered commands.

        Returns:
            List of command names.
        """
        return self.registry.list_commands()

    def get_handler(self, name: str) -> Optional[CommandHandler]:
        """Get handler for a command.

        Args:
            name: Command name or alias.

        Returns:
            CommandHandler if found, None otherwise.
        """
        return self.registry.get(name)
