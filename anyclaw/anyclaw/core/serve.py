"""Serve manager for multi-channel parallel service.

Coordinates:
- Channel lifecycle (start/stop)
- Message routing between channels and agent
- Status tracking
"""

from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Callable, Optional

from anyclaw.agent.loop import AgentLoop
from anyclaw.bus.events import InboundMessage, OutboundMessage
from anyclaw.bus.queue import MessageBus
from anyclaw.channels.manager import ChannelManager
from anyclaw.config.loader import Config, get_config
from anyclaw.skills.loader import SkillLoader
from anyclaw.workspace.manager import WorkspaceManager

logger = logging.getLogger(__name__)


class ServeManager:
    """Manages multi-channel parallel service.

    Responsibilities:
    - Initialize channels from config
    - Start/stop all channels
    - Route messages between channels and agent
    - Track service status
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        workspace: Optional[Path] = None,
        status_file: Optional[Path] = None,
    ):
        """Initialize serve manager.

        Args:
            config: Configuration (default: load from file)
            workspace: Workspace path
            status_file: Path to status file
        """
        self.config = config or get_config()
        self.workspace = workspace or Path(self.config.agent.workspace).expanduser()
        self.status_file = status_file or Path.home() / ".anyclaw" / "serve.status"

        # Components
        self.bus = MessageBus()
        self.channel_manager: Optional[ChannelManager] = None
        self.agent: Optional[AgentLoop] = None

        # State
        self._running = False
        self._started_at: Optional[float] = None
        self._messages_processed = 0
        self._tasks: list[asyncio.Task] = []

    @property
    def enabled_channels(self) -> list[str]:
        """Get list of enabled channel names."""
        if self.channel_manager:
            return self.channel_manager.enabled_channels
        return []

    @property
    def uptime_seconds(self) -> int:
        """Get uptime in seconds."""
        if self._started_at is None:
            return 0
        return int(time.time() - self._started_at)

    def initialize(self) -> None:
        """Initialize all components.

        Raises:
            RuntimeError: If no channels are enabled
        """
        logger.info("Initializing AnyClaw serve mode...")

        # Ensure workspace exists
        ws_manager = WorkspaceManager(workspace_path=str(self.workspace))
        if not ws_manager.exists():
            logger.info(f"Creating workspace: {self.workspace}")
            ws_manager.ensure_exists(silent=True)

        # Initialize channel manager
        self.channel_manager = ChannelManager(self.config, self.bus)

        if not self.channel_manager.channels:
            logger.warning("No channels enabled in configuration")
            raise RuntimeError(
                "No channels enabled. "
                "Edit ~/.anyclaw/config.toml to enable channels:\n"
                "[channels.cli]\nenabled = true\n\n"
                "[channels.discord]\nenabled = true\ntoken = 'your-token'"
            )

        # Initialize agent
        logger.info("Initializing agent...")
        self.agent = AgentLoop(workspace=self.workspace)

        # Load skills
        skill_loader = SkillLoader()
        skills_dict = skill_loader.get_skill_definitions()
        if skills_dict:
            self.agent.set_skills(skills_dict)
            logger.info(f"Loaded {len(skills_dict)} skills")

        logger.info(f"Enabled channels: {', '.join(self.enabled_channels)}")

    async def start(self) -> None:
        """Start all channels and message processing.

        This runs indefinitely until stopped.
        """
        if self._running:
            logger.warning("Serve manager already running")
            return

        self._running = True
        self._started_at = time.time()

        logger.info("Starting AnyClaw serve mode...")

        # Start message processor
        processor_task = asyncio.create_task(self._process_messages())
        self._tasks.append(processor_task)

        # Start status updater
        status_task = asyncio.create_task(self._update_status_periodically())
        self._tasks.append(status_task)

        # Start all channels
        try:
            await self.channel_manager.start_all()
        except Exception as e:
            logger.error(f"Error starting channels: {e}")
            await self.stop()
            raise

    async def stop(self) -> None:
        """Stop all channels and cleanup."""
        if not self._running:
            return

        logger.info("Stopping AnyClaw serve mode...")
        self._running = False

        # Cancel background tasks
        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        self._tasks.clear()

        # Stop channels
        if self.channel_manager:
            await self.channel_manager.stop_all()

        # Cleanup status file
        if self.status_file.exists():
            self.status_file.unlink()

        logger.info("AnyClaw stopped")

    async def _process_messages(self) -> None:
        """Process inbound messages from channels."""
        logger.info("Message processor started")

        while self._running:
            try:
                # Wait for inbound message
                msg = await asyncio.wait_for(
                    self.bus.consume_inbound(),
                    timeout=1.0
                )

                # Process with agent
                logger.debug(f"Processing message from {msg.channel}: {msg.content[:50]}...")

                try:
                    # Get response from agent
                    response = await self.agent.process(msg.content)

                    # Send response back
                    outbound = OutboundMessage(
                        channel=msg.channel,
                        chat_id=msg.chat_id,
                        content=response,
                        reply_to=msg.message_id,
                    )
                    await self.bus.publish_outbound(outbound)

                    self._messages_processed += 1

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    # Send error response
                    error_msg = OutboundMessage(
                        channel=msg.channel,
                        chat_id=msg.chat_id,
                        content=f"Error: {str(e)}",
                        reply_to=msg.message_id,
                    )
                    await self.bus.publish_outbound(error_msg)

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Unexpected error in message processor: {e}")

        logger.info("Message processor stopped")

    async def _update_status_periodically(self) -> None:
        """Update status file periodically."""
        while self._running:
            try:
                self._write_status()
                await asyncio.sleep(10)  # Update every 10 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error updating status: {e}")

    def _write_status(self) -> None:
        """Write current status to file."""
        import json

        status = {
            "pid": _get_pid(),
            "started_at": self._started_at,
            "uptime_seconds": self.uptime_seconds,
            "channels": self.enabled_channels,
            "messages_processed": self._messages_processed,
            "running": self._running,
        }

        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        self.status_file.write_text(json.dumps(status, indent=2))

    def get_status(self) -> dict[str, Any]:
        """Get current status.

        Returns:
            Status dictionary
        """
        return {
            "running": self._running,
            "uptime_seconds": self.uptime_seconds,
            "channels": self.enabled_channels,
            "messages_processed": self._messages_processed,
            "started_at": self._started_at,
        }


def _get_pid() -> int:
    """Get current process ID."""
    import os
    return os.getpid()
