"""Tests for command handlers."""

import pytest

from anyclaw.commands.base import CommandResult
from anyclaw.commands.context import CommandContext
from anyclaw.commands.handlers.session import (
    NewCommandHandler,
    ResetCommandHandler,
    ClearCommandHandler,
)
from anyclaw.commands.handlers.task import StopCommandHandler
from anyclaw.commands.handlers.info import (
    HelpCommandHandler,
    StatusCommandHandler,
    VersionCommandHandler,
)


class TestNewCommandHandler:
    """Test NewCommandHandler."""

    @pytest.fixture
    def handler(self) -> NewCommandHandler:
        return NewCommandHandler()

    @pytest.fixture
    def context(self) -> CommandContext:
        return CommandContext(
            user_id="test_user",
            chat_id="test_chat",
            channel_type="cli",
        )

    @pytest.mark.asyncio
    async def test_new_without_args(
        self, handler: NewCommandHandler, context: CommandContext
    ) -> None:
        """Test /new without arguments."""
        result = await handler.execute(None, context)

        assert result.handled is True
        assert "新会话" in result.reply

    @pytest.mark.asyncio
    async def test_new_with_args(
        self, handler: NewCommandHandler, context: CommandContext
    ) -> None:
        """Test /new with first message."""
        # Without session_manager, returns simple success message
        result = await handler.execute("hello world", context)

        assert result.handled is True
        assert "新会话" in result.reply


class TestResetCommandHandler:
    """Test ResetCommandHandler."""

    @pytest.fixture
    def handler(self) -> ResetCommandHandler:
        return ResetCommandHandler()

    @pytest.fixture
    def context(self) -> CommandContext:
        return CommandContext(
            user_id="test_user",
            chat_id="test_chat",
            channel_type="cli",
            session_key="test_session",
        )

    @pytest.mark.asyncio
    async def test_reset(self, handler: ResetCommandHandler, context: CommandContext) -> None:
        """Test /reset command."""
        result = await handler.execute(None, context)

        assert result.handled is True
        assert "重置" in result.reply or "清空" in result.reply


class TestClearCommandHandler:
    """Test ClearCommandHandler."""

    @pytest.fixture
    def handler(self) -> ClearCommandHandler:
        return ClearCommandHandler()

    @pytest.fixture
    def cli_context(self) -> CommandContext:
        return CommandContext(
            user_id="test_user",
            chat_id="test_chat",
            channel_type="cli",
        )

    @pytest.fixture
    def discord_context(self) -> CommandContext:
        return CommandContext(
            user_id="test_user",
            chat_id="test_chat",
            channel_type="discord",
        )

    @pytest.mark.asyncio
    async def test_clear_cli(
        self, handler: ClearCommandHandler, cli_context: CommandContext
    ) -> None:
        """Test /clear in CLI."""
        result = await handler.execute(None, cli_context)

        assert result.handled is True
        # CLI clear returns empty reply (screen is cleared)

    @pytest.mark.asyncio
    async def test_clear_discord(
        self, handler: ClearCommandHandler, discord_context: CommandContext
    ) -> None:
        """Test /clear in Discord (should show hint)."""
        result = await handler.execute(None, discord_context)

        assert result.handled is True
        assert "CLI" in result.reply or "仅" in result.reply


class TestHelpCommandHandler:
    """Test HelpCommandHandler."""

    @pytest.fixture
    def handler(self) -> HelpCommandHandler:
        return HelpCommandHandler()

    @pytest.fixture
    def context(self) -> CommandContext:
        return CommandContext(
            user_id="test_user",
            chat_id="test_chat",
            channel_type="cli",
        )

    @pytest.mark.asyncio
    async def test_help(self, handler: HelpCommandHandler, context: CommandContext) -> None:
        """Test /help command."""
        result = await handler.execute(None, context)

        assert result.handled is True
        assert "/new" in result.reply
        assert "/help" in result.reply
        assert "/stop" in result.reply


class TestStatusCommandHandler:
    """Test StatusCommandHandler."""

    @pytest.fixture
    def handler(self) -> StatusCommandHandler:
        return StatusCommandHandler()

    @pytest.fixture
    def context(self) -> CommandContext:
        return CommandContext(
            user_id="test_user",
            chat_id="test_chat",
            channel_type="cli",
            session_key="test_session",
            session_id="test_session_id",
        )

    @pytest.mark.asyncio
    async def test_status(self, handler: StatusCommandHandler, context: CommandContext) -> None:
        """Test /status command."""
        result = await handler.execute(None, context)

        assert result.handled is True
        assert "cli" in result.reply.lower()
        assert "test_user" in result.reply


class TestVersionCommandHandler:
    """Test VersionCommandHandler."""

    @pytest.fixture
    def handler(self) -> VersionCommandHandler:
        return VersionCommandHandler()

    @pytest.fixture
    def context(self) -> CommandContext:
        return CommandContext(
            user_id="test_user",
            chat_id="test_chat",
            channel_type="cli",
        )

    @pytest.mark.asyncio
    async def test_version(
        self, handler: VersionCommandHandler, context: CommandContext
    ) -> None:
        """Test /version command."""
        result = await handler.execute(None, context)

        assert result.handled is True
        assert "版本" in result.reply or "Version" in result.reply.lower()
