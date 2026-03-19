"""Tests for Channel system."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from anyclaw.channels.base import BaseChannel
from anyclaw.channels.cli import CLIChannel, CLIConfig
from anyclaw.bus import MessageBus, OutboundMessage


class TestBaseChannel:
    """Test BaseChannel abstract class."""

    def test_is_allowed_with_star(self):
        """Test allow_from with wildcard."""
        bus = MagicMock()
        config = MagicMock()
        config.allow_from = ["*"]

        # Create concrete implementation for testing
        class TestChannel(BaseChannel):
            name = "test"
            display_name = "Test"

            async def start(self): pass
            async def stop(self): pass
            async def send(self, msg): pass

        channel = TestChannel(config, bus)
        assert channel.is_allowed("anyone") is True

    def test_is_allowed_with_list(self):
        """Test allow_from with specific IDs."""
        bus = MagicMock()
        config = MagicMock()
        config.allow_from = ["user1", "user2"]

        class TestChannel(BaseChannel):
            name = "test"
            display_name = "Test"
            async def start(self): pass
            async def stop(self): pass
            async def send(self, msg): pass

        channel = TestChannel(config, bus)
        assert channel.is_allowed("user1") is True
        assert channel.is_allowed("user2") is True
        assert channel.is_allowed("user3") is False

    def test_is_allowed_empty_list(self):
        """Test allow_from with empty list denies all."""
        bus = MagicMock()
        config = MagicMock()
        config.allow_from = []

        class TestChannel(BaseChannel):
            name = "test"
            display_name = "Test"
            async def start(self): pass
            async def stop(self): pass
            async def send(self, msg): pass

        channel = TestChannel(config, bus)
        assert channel.is_allowed("anyone") is False


class TestCLIChannel:
    """Test CLI channel."""

    def test_cli_config_defaults(self):
        """Test CLI config default values."""
        config = CLIConfig()
        assert config.enabled is True
        assert config.allow_from == ["*"]

    def test_cli_config_from_dict(self):
        """Test CLI config from dict."""
        config = CLIConfig({
            "enabled": False,
            "prompt": "> ",
            "agent_name": "TestBot"
        })
        assert config.enabled is False
        assert config.prompt == "> "
        assert config.agent_name == "TestBot"

    @pytest.mark.asyncio
    async def test_cli_send(self):
        """Test CLI send method."""
        bus = MessageBus()
        config = CLIConfig({"agent_name": "TestBot"})
        channel = CLIChannel(config, bus)

        msg = OutboundMessage(
            channel="cli",
            chat_id="default",
            content="Hello from bot"
        )

        # send() should print to console without error
        await channel.send(msg)

    def test_default_config(self):
        """Test default_config class method."""
        config = CLIChannel.default_config()
        assert "enabled" in config
        assert config["enabled"] is True


class TestMessageSplit:
    """Test message splitting for Discord."""

    def test_short_message(self):
        """Test that short messages are not split."""
        from anyclaw.channels.discord import _split_message

        result = _split_message("Hello", max_len=2000)
        assert result == ["Hello"]

    def test_empty_message(self):
        """Test empty message handling."""
        from anyclaw.channels.discord import _split_message

        result = _split_message("")
        assert result == []

    def test_long_message_split(self):
        """Test that long messages are split."""
        from anyclaw.channels.discord import _split_message

        # Create a message longer than limit
        content = "Line " * 500  # ~2500 chars
        chunks = _split_message(content, max_len=100)

        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 100
