"""Tests for command parser."""

import pytest

from anyclaw.commands.parser import CommandParser, ParsedCommand


class TestCommandParser:
    """Test CommandParser class."""

    def test_parse_simple_command(self) -> None:
        """Parse simple command without args."""
        result = CommandParser.parse("/help")

        assert result is not None
        assert result.name == "help"
        assert result.args is None
        assert result.raw == "/help"

    def test_parse_command_with_args(self) -> None:
        """Parse command with arguments."""
        result = CommandParser.parse("/new hello world")

        assert result is not None
        assert result.name == "new"
        assert result.args == "hello world"

    def test_parse_command_case_insensitive(self) -> None:
        """Command names are case-insensitive."""
        result = CommandParser.parse("/HELP")

        assert result is not None
        assert result.name == "help"

        result = CommandParser.parse("/NeW")
        assert result is not None
        assert result.name == "new"

    def test_parse_command_with_hyphen(self) -> None:
        """Parse command with hyphen in name."""
        result = CommandParser.parse("/max-age 7d")

        assert result is not None
        assert result.name == "max-age"
        assert result.args == "7d"

    def test_parse_command_with_underscore(self) -> None:
        """Parse command with underscore in name."""
        result = CommandParser.parse("/test_cmd arg")

        assert result is not None
        assert result.name == "test_cmd"
        assert result.args == "arg"

    def test_not_a_command(self) -> None:
        """Non-command text returns None."""
        assert CommandParser.parse("hello") is None
        assert CommandParser.parse("") is None
        assert CommandParser.parse("  ") is None
        assert CommandParser.parse("/ not a command") is None

    def test_command_with_colon(self) -> None:
        """Parse command with colon separator."""
        # Commands can use colon or space as separator
        result = CommandParser.parse("/compact: keep important")

        assert result is not None
        assert result.name == "compact"
        # Colon is treated as part of args
        assert "keep important" in result.args

    def test_is_command(self) -> None:
        """Test is_command helper."""
        assert CommandParser.is_command("/help") is True
        assert CommandParser.is_command("/new test") is True
        assert CommandParser.is_command("hello") is False
        assert CommandParser.is_command("") is False

    def test_command_with_leading_spaces(self) -> None:
        """Parse command with leading spaces."""
        result = CommandParser.parse("  /help")

        assert result is not None
        assert result.name == "help"

    def test_command_with_empty_args(self) -> None:
        """Parse command with empty args."""
        result = CommandParser.parse("/new   ")

        assert result is not None
        assert result.name == "new"
        # Empty args should be None or empty
        assert result.args is None or result.args.strip() == ""


class TestParsedCommand:
    """Test ParsedCommand dataclass."""

    def test_has_args_true(self) -> None:
        """Test has_args property when args present."""
        cmd = ParsedCommand(name="test", args="value", raw="/test value")
        assert cmd.has_args is True

    def test_has_args_false(self) -> None:
        """Test has_args property when no args."""
        cmd = ParsedCommand(name="test", args=None, raw="/test")
        assert cmd.has_args is False

        cmd = ParsedCommand(name="test", args="", raw="/test")
        assert cmd.has_args is False

        cmd = ParsedCommand(name="test", args="   ", raw="/test")
        assert cmd.has_args is False
