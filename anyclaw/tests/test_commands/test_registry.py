"""Tests for command registry."""

import pytest

from anyclaw.commands.registry import CommandRegistry
from anyclaw.commands.base import CommandHandler, CommandResult
from anyclaw.commands.context import CommandContext


class MockHandler(CommandHandler):
    """Mock handler for testing."""

    def __init__(self, name: str = "mock"):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def execute(self, args, context):
        return CommandResult.success(f"Executed {self._name}")


class TestCommandRegistry:
    """Test CommandRegistry class."""

    def test_register_and_get(self) -> None:
        """Register and retrieve handler."""
        registry = CommandRegistry()
        handler = MockHandler("test")

        registry.register("test", handler)

        result = registry.get("test")
        assert result is handler

    def test_get_case_insensitive(self) -> None:
        """Registry is case-insensitive."""
        registry = CommandRegistry()
        handler = MockHandler()

        registry.register("Help", handler)

        assert registry.get("help") is handler
        assert registry.get("HELP") is handler
        assert registry.get("HeLp") is handler

    def test_get_unknown(self) -> None:
        """Get returns None for unknown command."""
        registry = CommandRegistry()
        assert registry.get("unknown") is None

    def test_register_with_aliases(self) -> None:
        """Register command with aliases."""
        registry = CommandRegistry()
        handler = MockHandler()

        registry.register("help", handler, aliases=["?", "h"])

        assert registry.get("help") is handler
        assert registry.get("?") is handler
        assert registry.get("h") is handler

    def test_register_with_description(self) -> None:
        """Register command with description."""
        registry = CommandRegistry()
        handler = MockHandler()

        registry.register("help", handler, description="Show help")

        assert registry.get_description("help") == "Show help"

    def test_list_commands(self) -> None:
        """List registered commands."""
        registry = CommandRegistry()

        registry.register("help", MockHandler())
        registry.register("new", MockHandler())
        registry.register("abort", MockHandler())

        commands = registry.list_commands()
        assert "help" in commands
        assert "new" in commands
        assert "abort" in commands
        # Should be sorted
        assert commands == sorted(commands)

    def test_list_all_commands_with_aliases(self) -> None:
        """List commands with their aliases."""
        registry = CommandRegistry()

        registry.register("help", MockHandler(), aliases=["?", "h"])
        registry.register("new", MockHandler())

        result = registry.list_all_commands_with_aliases()

        assert "help" in result
        assert "?" in result["help"]
        assert "h" in result["help"]
        assert "new" in result
        assert result["new"] == []

    def test_get_help_text(self) -> None:
        """Generate help text."""
        registry = CommandRegistry()

        registry.register("help", MockHandler(), description="Show help")
        registry.register("new", MockHandler(), aliases=["n"], description="New session")

        help_text = registry.get_help_text()

        assert "Available commands:" in help_text
        assert "/help" in help_text
        assert "Show help" in help_text
        assert "/new" in help_text
        assert "/n" in help_text

    def test_unregister(self) -> None:
        """Unregister command."""
        registry = CommandRegistry()
        handler = MockHandler()

        registry.register("test", handler)
        assert registry.get("test") is handler

        result = registry.unregister("test")
        assert result is True
        assert registry.get("test") is None

    def test_unregister_with_aliases(self) -> None:
        """Unregister command removes aliases."""
        registry = CommandRegistry()
        handler = MockHandler()

        registry.register("help", handler, aliases=["?"])

        registry.unregister("help")

        assert registry.get("help") is None
        assert registry.get("?") is None

    def test_unregister_unknown(self) -> None:
        """Unregister unknown command returns False."""
        registry = CommandRegistry()
        assert registry.unregister("unknown") is False

    def test_get_primary_name(self) -> None:
        """Get primary name from command or alias."""
        registry = CommandRegistry()
        handler = MockHandler()

        registry.register("help", handler, aliases=["?"])

        assert registry.get_primary_name("help") == "help"
        assert registry.get_primary_name("?") == "help"
        assert registry.get_primary_name("unknown") is None
