"""Command Parser - Parse user input for special commands."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedCommand:
    """Represents a parsed command from user input."""

    name: str
    """The command name (lowercase, without /)."""

    args: Optional[str]
    """The command arguments (may be None)."""

    raw: str
    """The original raw input string."""

    @property
    def has_args(self) -> bool:
        """Check if command has arguments."""
        return self.args is not None and self.args.strip() != ""


class CommandParser:
    """Parse user input to detect and extract special commands.

    Commands are detected by a leading '/' character.
    Command names are case-insensitive.

    Examples:
        "/help" -> ParsedCommand(name="help", args=None)
        "/new hello world" -> ParsedCommand(name="new", args="hello world")
        "/MODEL glm-4" -> ParsedCommand(name="model", args="glm-4")
        "hello" -> None (not a command)
    """

    # Pattern to match command: /command-name followed by optional space and args
    # Allows optional leading whitespace, colon or space as separator
    COMMAND_PATTERN = re.compile(r"^\s*/([a-zA-Z][a-zA-Z0-9_-]*)(?:[\s:]+(.*))?$")

    @classmethod
    def parse(cls, text: str) -> Optional[ParsedCommand]:
        """Parse text to extract command if present.

        Args:
            text: The user input text to parse.

        Returns:
            ParsedCommand if text is a command, None otherwise.
        """
        if not text:
            return None

        # Quick check: must contain / somewhere
        if "/" not in text:
            return None

        # Use regex to parse command
        match = cls.COMMAND_PATTERN.match(text)
        if not match:
            return None

        name = match.group(1).lower()
        args = match.group(2)

        return ParsedCommand(
            name=name,
            args=args,
            raw=text,
        )

    @classmethod
    def is_command(cls, text: str) -> bool:
        """Check if text is a command.

        Args:
            text: The user input text to check.

        Returns:
            True if text is a command, False otherwise.
        """
        return cls.parse(text) is not None
