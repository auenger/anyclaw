"""Async message queue for decoupled channel-agent communication."""

from __future__ import annotations

import asyncio
import logging
from typing import AsyncIterator, Optional, AsyncGenerator

from anyclaw.bus.events import InboundMessage, OutboundMessage

logger = logging.getLogger(__name__)


class MessageBus:
    """
    Async message bus that decouples chat channels from the agent core.

    Channels push messages to the inbound queue, and the agent processes
    them and pushes responses to the outbound queue.
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize the message bus.

        Args:
            max_size: Maximum queue size (0 = unlimited)
        """
        self._inbound: asyncio.Queue[InboundMessage] = asyncio.Queue(maxsize=max_size)
        self._outbound: asyncio.Queue[OutboundMessage] = asyncio.Queue(maxsize=max_size)

    async def publish_inbound(self, msg: InboundMessage) -> None:
        """Publish a message from a channel to the agent."""
        await self._inbound.put(msg)
        logger.debug(f"[Bus] 📥 入站消息: channel={msg.channel}, chat_id={msg.chat_id}, "
                     f"queue_size={self._inbound.qsize()}")

    async def consume_inbound(self) -> InboundMessage:
        """Consume the next inbound message (blocks until available)."""
        return await self._inbound.get()

    async def publish_outbound(self, msg: OutboundMessage) -> None:
        """Publish a response from the agent to channels."""
        await self._outbound.put(msg)
        logger.debug(f"[Bus] 📤 出站消息: channel={msg.channel}, chat_id={msg.chat_id}, "
                     f"queue_size={self._outbound.qsize()}")

    async def consume_outbound(self) -> OutboundMessage:
        """Consume the next outbound message (blocks until available)."""
        return await self._outbound.get()

    async def subscribe(self) -> AsyncGenerator[dict, None]:
        """
        Subscribe to all events on the bus (for SSE streaming).

        Yields:
            Event dictionaries with 'type' and 'payload' keys
        """
        while True:
            try:
                msg = await self._outbound.get()
                # Convert OutboundMessage to event dict
                yield {
                    "type": "message:outbound",
                    "payload": {
                        "channel": msg.channel,
                        "chat_id": msg.chat_id,
                        "content": msg.content,
                    }
                }
            except asyncio.CancelledError:
                break

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
