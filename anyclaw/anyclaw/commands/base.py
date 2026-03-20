"""Command Handler Base - Base class for command handlers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from anyclaw.commands.context import CommandContext


@dataclass
class CommandResult:
    """Result of command execution.

    Attributes:
        handled: Whether the command was handled (stops normal message processing).
        reply: Optional reply message to send back.
        error: Optional error message if command failed.
        continue_session: Whether to continue the session (for /new, /reset).
    """

    handled: bool = True
    """Whether the command was handled."""

    reply: Optional[str] = None
    """Reply message to send back to user."""

    error: Optional[str] = None
    """Error message if command failed."""

    continue_session: bool = True
    """Whether to continue the session after command."""

    @classmethod
    def success(cls, reply: Optional[str] = None) -> "CommandResult":
        """Create a successful result.

        Args:
            reply: Optional reply message.

        Returns:
            CommandResult with handled=True.
        """
        return cls(handled=True, reply=reply)

    @classmethod
    def fail(cls, error: str) -> "CommandResult":
        """Create a failed result.

        Args:
            error: Error message.

        Returns:
            CommandResult with handled=True and error set.
        """
        return cls(handled=True, error=error)

    @classmethod
    def not_handled(cls) -> "CommandResult":
        """Create a not-handled result.

        Returns:
            CommandResult with handled=False.
        """
        return cls(handled=False)

    @classmethod
    def new_session(cls, reply: Optional[str] = None) -> "CommandResult":
        """Create a result that triggers a new session.

        Args:
            reply: Optional reply message.

        Returns:
            CommandResult with continue_session=False.
        """
        return cls(handled=True, reply=reply, continue_session=False)


class CommandHandler(ABC):
    """Base class for command handlers.

    Subclasses must implement the execute() method.
    """

    @property
    def name(self) -> str:
        """Command name (derived from class name).

        Returns:
            Command name in lowercase with 'handler' suffix removed.
        """
        class_name = self.__class__.__name__
        if class_name.endswith("Handler"):
            return class_name[:-7].lower()
        return class_name.lower()

    @property
    def description(self) -> str:
        """Command description for help text.

        Override this in subclasses to provide a description.

        Returns:
            Description string.
        """
        return ""

    @property
    def aliases(self) -> list[str]:
        """Command aliases.

        Override this in subclasses to provide aliases.

        Returns:
            List of alias names.
        """
        return []

    @abstractmethod
    async def execute(
        self,
        args: Optional[str],
        context: CommandContext,
    ) -> CommandResult:
        """Execute the command.

        Args:
            args: Command arguments (may be None).
            context: Execution context with session, config, etc.

        Returns:
            CommandResult indicating success/failure and any reply.
        """
        pass

    def validate_args(self, args: Optional[str]) -> Optional[str]:
        """Validate command arguments.

        Override this to provide argument validation.

        Args:
            args: Command arguments to validate.

        Returns:
            Error message if validation fails, None if valid.
        """
        return None
