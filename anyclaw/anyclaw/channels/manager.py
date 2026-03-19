"""Channel manager for coordinating chat channels."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from anyclaw.bus.queue import MessageBus
from anyclaw.channels.base import BaseChannel
from anyclaw.channels.registry import discover_all

logger = logging.getLogger(__name__)


class ChannelManager:
    """
    Manages chat channels and coordinates message routing.

    Responsibilities:
    - Initialize enabled channels (CLI, Feishu, Discord, etc.)
    - Start/stop channels
    - Route outbound messages
    """

    def __init__(self, config: Any, bus: MessageBus):
        """
        Initialize the channel manager.

        Args:
            config: Application configuration with channels section.
            bus: The message bus for communication.
        """
        self.config = config
        self.bus = bus
        self.channels: dict[str, BaseChannel] = {}
        self._dispatch_task: asyncio.Task | None = None

        self._init_channels()

    def _init_channels(self) -> None:
        """Initialize channels discovered via registry."""
        channels_config = getattr(self.config, "channels", None)
        if channels_config is None:
            logger.warning("No channels configuration found")
            return

        for name, cls in discover_all().items():
            # Get channel config (dict or object)
            section = getattr(channels_config, name, None)
            if section is None:
                section = channels_config.get(name) if isinstance(channels_config, dict) else None
            if section is None:
                continue

            # Check if enabled
            enabled = (
                section.get("enabled", False)
                if isinstance(section, dict)
                else getattr(section, "enabled", False)
            )
            if not enabled:
                continue

            try:
                channel = cls(section, self.bus)
                self.channels[name] = channel
                logger.info(f"{cls.display_name} channel enabled")
            except Exception as e:
                logger.warning(f"{name} channel not available: {e}")

        self._validate_allow_from()

    def _validate_allow_from(self) -> None:
        """Validate allow_from is not empty for security."""
        for name, ch in self.channels.items():
            allow_from = getattr(ch.config, "allow_from", None)
            if isinstance(allow_from, dict):
                allow_from = allow_from.get("list", [])
            if allow_from == []:
                logger.warning(
                    f'Channel "{name}" has empty allow_from (denies all). '
                    f'Set ["*"] to allow everyone, or add specific user IDs.'
                )

    async def _start_channel(self, name: str, channel: BaseChannel) -> None:
        """Start a channel and log any exceptions."""
        try:
            await channel.start()
        except Exception as e:
            logger.error(f"Failed to start channel {name}: {e}")

    async def start_all(self) -> None:
        """Start all channels and the outbound dispatcher."""
        if not self.channels:
            logger.warning("No channels enabled")
            return

        # Start outbound dispatcher
        self._dispatch_task = asyncio.create_task(self._dispatch_outbound())

        # Start channels
        tasks = []
        for name, channel in self.channels.items():
            logger.info(f"Starting {name} channel...")
            tasks.append(asyncio.create_task(self._start_channel(name, channel)))

        # Wait for all to complete (they should run forever)
        await asyncio.gather(*tasks, return_exceptions=True)

    async def stop_all(self) -> None:
        """Stop all channels and the dispatcher."""
        logger.info("Stopping all channels...")

        # Stop dispatcher
        if self._dispatch_task:
            self._dispatch_task.cancel()
            try:
                await self._dispatch_task
            except asyncio.CancelledError:
                pass

        # Stop all channels
        for name, channel in self.channels.items():
            try:
                await channel.stop()
                logger.info(f"Stopped {name} channel")
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")

    async def _dispatch_outbound(self) -> None:
        """Dispatch outbound messages to the appropriate channel."""
        logger.info("Outbound dispatcher started")

        while True:
            try:
                msg = await asyncio.wait_for(self.bus.consume_outbound(), timeout=1.0)

                channel = self.channels.get(msg.channel)
                if channel:
                    try:
                        await channel.send(msg)
                    except Exception as e:
                        logger.error(f"Error sending to {msg.channel}: {e}")
                else:
                    logger.warning(f"Unknown channel: {msg.channel}")

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    def get_channel(self, name: str) -> BaseChannel | None:
        """Get a channel by name."""
        return self.channels.get(name)

    def get_status(self) -> dict[str, Any]:
        """Get status of all channels."""
        return {
            name: {"enabled": True, "running": channel.is_running}
            for name, channel in self.channels.items()
        }

    @property
    def enabled_channels(self) -> list[str]:
        """Get list of enabled channel names."""
        return list(self.channels.keys())
