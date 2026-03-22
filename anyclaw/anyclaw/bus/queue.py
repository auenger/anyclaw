"""Async message queue for decoupled channel-agent communication."""

from __future__ import annotations

import asyncio
import logging
from typing import AsyncIterator, Optional, AsyncGenerator, List

from anyclaw.bus.events import InboundMessage, OutboundMessage

logger = logging.getLogger(__name__)


class MessageBus:
    """
    Async message bus that decouples chat channels from the agent core.

    Channels push messages to the inbound queue, and the agent processes
    them and pushes responses to the outbound queue.

    Outbound messages are broadcast to all subscribers (channels + SSE).
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize the message bus.

        Args:
            max_size: Maximum queue size (0 = unlimited)
        """
        self._inbound: asyncio.Queue[InboundMessage] = asyncio.Queue(maxsize=max_size)
        self._outbound: asyncio.Queue[OutboundMessage] = asyncio.Queue(maxsize=max_size)
        # Broadcast subscribers for outbound messages
        self._outbound_subscribers: List[asyncio.Queue] = []

    async def publish_inbound(self, msg: InboundMessage) -> None:
        """Publish a message from a channel to the agent."""
        await self._inbound.put(msg)
        logger.debug(f"[Bus] 📥 入站消息: channel={msg.channel}, chat_id={msg.chat_id}, "
                     f"queue_size={self._inbound.qsize()}")

    async def consume_inbound(self) -> InboundMessage:
        """Consume the next inbound message (blocks until available)."""
        return await self._inbound.get()

    async def publish_outbound(self, msg: OutboundMessage) -> None:
        """Publish a response from the agent to channels.

        Messages are broadcast to all subscribers.
        """
        await self._outbound.put(msg)
        # Also broadcast to all subscribers (SSE, etc.)
        for queue in self._outbound_subscribers:
            try:
                queue.put_nowait(msg)
            except asyncio.QueueFull:
                logger.warning(f"[Bus] Subscriber queue full, dropping message")
        logger.debug(f"[Bus] 📤 出站消息: channel={msg.channel}, chat_id={msg.chat_id}, "
                     f"queue_size={self._outbound.qsize()}, subscribers={len(self._outbound_subscribers)}")

    async def consume_outbound(self) -> OutboundMessage:
        """Consume the next outbound message (blocks until available).

        This is used by channels to receive messages they need to send.
        """
        return await self._outbound.get()

    def subscribe_outbound(self) -> asyncio.Queue[OutboundMessage]:
        """Subscribe to outbound messages without consuming the main queue.

        Returns a new queue that will receive all outbound messages.
        Callers should call unsubscribe_outbound() when done.

        Returns:
            A queue that will receive all outbound messages
        """
        queue: asyncio.Queue[OutboundMessage] = asyncio.Queue(maxsize=100)
        self._outbound_subscribers.append(queue)
        logger.debug(f"[Bus] New outbound subscriber, total={len(self._outbound_subscribers)}")
        return queue

    def unsubscribe_outbound(self, queue: asyncio.Queue) -> None:
        """Unsubscribe from outbound messages.

        Args:
            queue: The queue returned by subscribe_outbound()
        """
        if queue in self._outbound_subscribers:
            self._outbound_subscribers.remove(queue)
            logger.debug(f"[Bus] Unsubscribed, remaining={len(self._outbound_subscribers)}")

    async def subscribe(
        self, channel_filter: Optional[str] = None
    ) -> AsyncGenerator[dict, None]:
        """
        Subscribe to events on the bus (for SSE streaming).

        Uses broadcast mode - does not consume from the main queue.

        Args:
            channel_filter: Optional channel name to filter (e.g., "api" for desktop app)

        Yields:
            Event dictionaries with 'type' and 'payload' keys
        """
        queue = self.subscribe_outbound()
        try:
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=30.0)
                    # Filter by channel if specified
                    if channel_filter and msg.channel != channel_filter:
                        continue
                    # Convert OutboundMessage to event dict
                    yield {
                        "type": "message:outbound",
                        "payload": {
                            "channel": msg.channel,
                            "chat_id": msg.chat_id,
                            "content": msg.content,
                        }
                    }
                except asyncio.TimeoutError:
                    # Send keepalive comment to prevent connection timeout
                    yield {"comment": "keepalive"}
                except asyncio.CancelledError:
                    break
        finally:
            self.unsubscribe_outbound(queue)

    async def consume_inbound_iter(
        self, timeout: Optional[float] = None
    ) -> AsyncIterator[InboundMessage]:
        """
        Async iterator for inbound messages.

        Args:
            timeout: Optional timeout in seconds for each message
        """
        while True:
            try:
                if timeout:
                    msg = await asyncio.wait_for(self._inbound.get(), timeout=timeout)
                else:
                    msg = await self._inbound.get()
                yield msg
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    @property
    def inbound_size(self) -> int:
        """Number of pending inbound messages."""
        return self._inbound.qsize()

    @property
    def outbound_size(self) -> int:
        """Number of pending outbound messages."""
        return self._outbound.qsize()

    def clear(self) -> None:
        """Clear both queues."""
        while not self._inbound.empty():
            try:
                self._inbound.get_nowait()
            except asyncio.QueueEmpty:
                break
        while not self._outbound.empty():
            try:
                self._outbound.get_nowait()
            except asyncio.QueueEmpty:
                break
        # Clear subscriber queues
        for queue in self._outbound_subscribers:
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
