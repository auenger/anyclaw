"""Tests for MessageBus."""

import asyncio
import pytest

from anyclaw.bus import MessageBus, InboundMessage, OutboundMessage


class TestMessageBus:
    """Test MessageBus functionality."""

    @pytest.mark.asyncio
    async def test_publish_consume_inbound(self):
        """Test publishing and consuming inbound messages."""
        bus = MessageBus()

        msg = InboundMessage(
            channel="cli",
            sender_id="user1",
            chat_id="chat1",
            content="Hello"
        )

        await bus.publish_inbound(msg)
        assert bus.inbound_size == 1

        received = await bus.consume_inbound()
        assert received.content == "Hello"
        assert received.channel == "cli"

    @pytest.mark.asyncio
    async def test_publish_consume_outbound(self):
        """Test publishing and consuming outbound messages."""
        bus = MessageBus()

        msg = OutboundMessage(
            channel="cli",
            chat_id="chat1",
            content="Response"
        )

        await bus.publish_outbound(msg)
        assert bus.outbound_size == 1

        received = await bus.consume_outbound()
        assert received.content == "Response"

    @pytest.mark.asyncio
    async def test_consume_inbound_iter(self):
        """Test async iterator for inbound messages."""
        bus = MessageBus()
        received_msgs = []

        async def publisher():
            for i in range(3):
                await bus.publish_inbound(
                    InboundMessage(
                        channel="cli",
                        sender_id="user",
                        chat_id="chat",
                        content=f"msg{i}"
                    )
                )

        async def consumer():
            count = 0
            async for msg in bus.consume_inbound_iter(timeout=0.1):
                received_msgs.append(msg)
                count += 1
                if count >= 3:
                    break

        await asyncio.gather(publisher(), consumer())
        assert len(received_msgs) == 3

    def test_clear_queues(self):
        """Test clearing both queues."""
        bus = MessageBus()

        # Add some messages synchronously
        bus._inbound.put_nowait(InboundMessage(
            channel="cli", sender_id="u", chat_id="c", content="1"
        ))
        bus._outbound.put_nowait(OutboundMessage(
            channel="cli", chat_id="c", content="2"
        ))

        assert bus.inbound_size == 1
        assert bus.outbound_size == 1

        bus.clear()
        assert bus.inbound_size == 0
        assert bus.outbound_size == 0


class TestInboundMessage:
    """Test InboundMessage dataclass."""

    def test_session_key_default(self):
        """Test default session key generation."""
        msg = InboundMessage(
            channel="cli",
            sender_id="user",
            chat_id="chat123",
            content="test"
        )
        assert msg.session_key == "cli:chat123"

    def test_session_key_override(self):
        """Test session key override."""
        msg = InboundMessage(
            channel="cli",
            sender_id="user",
            chat_id="chat123",
            content="test",
            session_key_override="custom:session"
        )
        assert msg.session_key == "custom:session"
