"""Special Commands System for AnyClaw.

This module provides a command framework for handling special commands
that users can input during conversations (e.g., /new, /stop, /help).

Usage:
    from anyclaw.commands import CommandDispatcher, CommandContext

    dispatcher = CommandDispatcher(config)
    result = await dispatcher.dispatch("/help", context)
"""

from anyclaw.commands.context import CommandContext
from anyclaw.commands.dispatcher import CommandDispatcher
from anyclaw.commands.parser import CommandParser, ParsedCommand
from anyclaw.commands.registry import CommandRegistry
from anyclaw.commands.base import CommandHandler, CommandResult
from anyclaw.commands.permission import PermissionManager

__all__ = [
    "CommandDispatcher",
    "CommandContext",
    "CommandParser",
    "ParsedCommand",
    "CommandRegistry",
    "CommandHandler",
    "CommandResult",
    "PermissionManager",
]
