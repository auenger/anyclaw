"""Tests for Feishu Channel outbound loop."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from anyclaw.bus import MessageBus, OutboundMessage


class TestFeishuOutboundLoop:
    """Test Feishu channel outbound message handling."""

    @pytest.fixture
    def bus(self):
        """Create a MessageBus instance."""
        return MessageBus()

    @pytest.fixture
    def feishu_config(self):
        """Create Feishu config."""
        from anyclaw.channels.feishu import FeishuConfig
        return FeishuConfig(
            enabled=True,
            app_id="test_app_id",
            app_secret="test_secret",
        )

    @pytest.mark.asyncio
    async def test_outbound_loop_filters_by_channel(self, bus, feishu_config):
        """Test that outbound loop only processes feishu messages."""
        from anyclaw.channels.feishu import FeishuChannel

        channel = FeishuChannel(feishu_config, bus)
        channel._running = True
        channel._message_api = MagicMock()  # Pretend client is ready

        # Track calls to send
        send_calls = []
        original_send = channel.send

        async def track_send(msg):
            send_calls.append(msg)

        channel.send = track_send

        # Run the outbound loop in a task
        loop_task = asyncio.create_task(channel._outbound_loop())

        # Publish a discord message (should be ignored)
        discord_msg = OutboundMessage(
            channel="discord",
            chat_id="discord_chat",
            content="Hello Discord"
        )
        await bus.publish_outbound(discord_msg)

        # Publish a feishu message
        feishu_msg = OutboundMessage(
            channel="feishu",
            chat_id="feishu_chat",
            content="Hello Feishu"
        )
        await bus.publish_outbound(feishu_msg)

        # Wait for processing
        await asyncio.sleep(0.3)

        # Stop the loop
        channel._running = False
        loop_task.cancel()
        try:
            await loop_task
        except asyncio.CancelledError:
            pass

        # Only feishu message should be sent
        assert len(send_calls) == 1
        assert send_calls[0].channel == "feishu"
        assert send_calls[0].content == "Hello Feishu"

    @pytest.mark.asyncio
    async def test_outbound_loop_handles_errors(self, bus, feishu_config):
        """Test that outbound loop continues after errors."""
        from anyclaw.channels.feishu import FeishuChannel

        channel = FeishuChannel(feishu_config, bus)
        channel._running = True
        channel._message_api = MagicMock()

        call_count = 0

        async def failing_send(msg):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Send failed")

        channel.send = failing_send

        loop_task = asyncio.create_task(channel._outbound_loop())

        # Publish two feishu messages
        msg1 = OutboundMessage(channel="feishu", chat_id="chat1", content="Msg 1")
        msg2 = OutboundMessage(channel="feishu", chat_id="chat2", content="Msg 2")

        await bus.publish_outbound(msg1)
        await asyncio.sleep(0.2)
        await bus.publish_outbound(msg2)
        await asyncio.sleep(0.2)

        channel._running = False
        loop_task.cancel()
        try:
            await loop_task
        except asyncio.CancelledError:
            pass

        # Both messages should have been attempted (loop didn't crash)
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_outbound_loop_handles_timeout(self, bus, feishu_config):
        """Test that outbound loop handles timeout gracefully."""
        from anyclaw.channels.feishu import FeishuChannel

        channel = FeishuChannel(feishu_config, bus)
        channel._running = True
        channel._message_api = MagicMock()

        loop_task = asyncio.create_task(channel._outbound_loop())

        # Wait without publishing any messages
        await asyncio.sleep(1.5)

        # Loop should still be running
        assert channel._running is True
        assert not loop_task.done()

        channel._running = False
        loop_task.cancel()
        try:
            await loop_task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_outbound_loop_stops_on_cancel(self, bus, feishu_config):
        """Test that outbound loop stops when cancelled."""
        from anyclaw.channels.feishu import FeishuChannel

        channel = FeishuChannel(feishu_config, bus)
        channel._running = True
        channel._message_api = MagicMock()

        loop_task = asyncio.create_task(channel._outbound_loop())

        await asyncio.sleep(0.3)

        # Cancel the task
        loop_task.cancel()

        # Wait for task to complete (it catches CancelledError and breaks)
        await asyncio.sleep(0.1)

        # Task should be done (stopped gracefully)
        assert loop_task.done()

    @pytest.mark.asyncio
    async def test_start_creates_outbound_task(self, bus, feishu_config):
        """Test that start() creates outbound task when client initializes."""
        from anyclaw.channels.feishu import FeishuChannel

        channel = FeishuChannel(feishu_config, bus)

        # Mock the lark-oapi import chain
        mock_client = MagicMock()
        mock_message_api = MagicMock()
        mock_client.im.v1.message = mock_message_api

        # Create a proper mock for lark_oapi
        mock_lark = MagicMock()
        mock_lark.Client.builder.return_value.app_id.return_value \
            .app_secret.return_value.log_level.return_value.build.return_value = mock_client
        mock_lark.LogLevel.ERROR = "ERROR"
        mock_lark.api = MagicMock()

        # Need to mock the entire import chain
        with patch.dict("sys.modules", {
            "lark_oapi": mock_lark,
            "lark_oapi.api": mock_lark.api,
            "lark_oapi.api.im": mock_lark.api.im,
            "lark_oapi.api.im.v1": mock_lark.api.im.v1,
        }):
            with patch("anyclaw.channels.feishu.FEISHU_AVAILABLE", True):
                await channel.start()

                assert channel._outbound_task is not None
                assert not channel._outbound_task.done()

                await channel.stop()

    @pytest.mark.asyncio
    async def test_stop_cancels_outbound_task(self, bus, feishu_config):
        """Test that stop() cancels outbound task."""
        from anyclaw.channels.feishu import FeishuChannel

        channel = FeishuChannel(feishu_config, bus)
        channel._running = True
        channel._message_api = MagicMock()

        # Manually create outbound task (simulating start)
        channel._outbound_task = asyncio.create_task(channel._outbound_loop())

        await channel.stop()

        assert channel._outbound_task is None


class TestFeishuMessageSplit:
    """Test Feishu message splitting."""

    def test_short_message_not_split(self):
        """Test that short messages are not split."""
        from anyclaw.channels.feishu import _split_message

        result = _split_message("Hello", max_len=30000)
        assert result == ["Hello"]

    def test_empty_message(self):
        """Test empty message handling."""
        from anyclaw.channels.feishu import _split_message

        result = _split_message("")
        assert result == []

    def test_long_message_split_at_sentence(self):
        """Test that long messages are split at sentence boundaries."""
        from anyclaw.channels.feishu import _split_message

        # Create a long message with Chinese sentence endings
        content = "这是第一句话。" + "很长的内容" * 5000 + "这是第二句话。"

        chunks = _split_message(content, max_len=10000)

        assert len(chunks) > 1
        # Each chunk should be within limit
        for chunk in chunks:
            assert len(chunk) <= 10000

    def test_split_without_good_boundary(self):
        """Test split when no good boundary exists."""
        from anyclaw.channels.feishu import _split_message

        # Create content without any good break points
        content = "x" * 35000

        chunks = _split_message(content, max_len=30000)

        assert len(chunks) == 2
        assert chunks[0] == "x" * 30000
        assert chunks[1] == "x" * 5000

    def test_split_at_period(self):
        """Test split at period."""
        from anyclaw.channels.feishu import _split_message

        content = "A" * 9990 + ". " + "B" * 100

        chunks = _split_message(content, max_len=10000)

        # Should split at the period
        assert len(chunks) == 2
        assert chunks[0] == "A" * 9990 + "."
        # Space is preserved at start of second chunk
        assert chunks[1] == " " + "B" * 100
