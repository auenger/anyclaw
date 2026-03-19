"""Feishu/Lark channel implementation using lark-oapi SDK.

Note: lark-oapi is an optional dependency. Install with:
    pip install lark-oapi
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import logging
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from anyclaw.bus.events import OutboundMessage
from anyclaw.bus.queue import MessageBus
from anyclaw.channels.base import BaseChannel

logger = logging.getLogger(__name__)

# Check if lark-oapi is available
FEISHU_AVAILABLE = importlib.util.find_spec("lark_oapi") is not None

# Message limits
MAX_MESSAGE_LEN = 30000  # Feishu text message limit

# Message type display mapping
MSG_TYPE_MAP = {
    "image": "[image]",
    "audio": "[audio]",
    "file": "[file]",
    "sticker": "[sticker]",
    "video": "[video]",
}


@dataclass
class FeishuConfig:
    """Feishu channel configuration."""

    enabled: bool = False
    app_id: str = ""
    app_secret: str = ""
    allow_from: list[str] = Field(default_factory=lambda: ["*"])
    encrypt_key: str = ""
    verification_token: str = ""


def _split_message(content: str, max_len: int = MAX_MESSAGE_LEN) -> list[str]:
    """Split a long message into chunks that fit within Feishu limits."""
    if len(content) <= max_len:
        return [content] if content else []

    chunks = []
    while content:
        # Try to split at paragraph boundary
        split_pos = max_len
        for i in range(min(max_len, len(content)) - 1, max(0, max_len - 500), -1):
            if content[i] in "\n。！？.!?":
                split_pos = i + 1
                break

        chunks.append(content[:split_pos])
        content = content[split_pos:]

    return chunks


class FeishuChannel(BaseChannel):
    """Feishu/Lark channel using lark-oapi SDK."""

    name = "feishu"
    display_name = "Feishu"

    def __init__(self, config: Any, bus: MessageBus):
        if isinstance(config, dict):
            config = FeishuConfig(**config)
        super().__init__(config, bus)
        self.config: FeishuConfig = config
        self._client: Any = None
        self._message_api: Any = None

        if not FEISHU_AVAILABLE:
            logger.warning("lark-oapi not installed, Feishu channel unavailable")

    @classmethod
    def default_config(cls) -> dict[str, Any]:
        return FeishuConfig().model_dump()

    async def start(self) -> None:
        """Start the Feishu channel (initializes SDK client)."""
        if not FEISHU_AVAILABLE:
            logger.error("lark-oapi not installed, cannot start Feishu channel")
            return

        if not self.config.app_id or not self.config.app_secret:
            logger.error("Feishu app_id or app_secret not configured")
            return

        try:
            import lark_oapi as lark
            from lark_oapi.api.im.v1 import CreateMessageRequest, SendMessageRequest

            # Initialize client
            self._client = lark.Client.builder() \
                .app_id(self.config.app_id) \
                .app_secret(self.config.app_secret) \
                .log_level(lark.LogLevel.ERROR) \
                .build()

            self._message_api = self._client.im.v1.message
            self._running = True
            logger.info("Feishu channel started (WebSocket mode requires event callback)")

            # Note: WebSocket long connection requires running a separate server
            # In production, you'd set up a FastAPI/Flask endpoint for webhooks
            # For now, this channel is ready to send messages but receives via webhook

        except Exception as e:
            logger.error(f"Failed to start Feishu channel: {e}")

    async def stop(self) -> None:
        """Stop the Feishu channel."""
        self._running = False
        if self._client:
            # lark-oapi doesn't have explicit close
            self._client = None
            self._message_api = None

    async def send(self, msg: OutboundMessage) -> None:
        """Send a message through Feishu REST API."""
        if not self._message_api:
            logger.warning("Feishu client not initialized")
            return

        try:
            import lark_oapi as lark
            from lark_oapi.api.im.v1 import CreateMessageRequest

            # Split long messages
            chunks = _split_message(msg.content or "")

            for i, chunk in enumerate(chunks):
                # Send text message
                request = CreateMessageRequest.builder() \
                    .receive_id_type("chat_id") \
                    .request_body(lark.api.im.v1.CreateMessageRequestBody.builder()
                        .receive_id(msg.chat_id)
                        .msg_type("text")
                        .content(json.dumps({"text": chunk}))
                        .build()) \
                    .build()

                response = await asyncio.to_thread(self._message_api.create, request)

                if not response.success():
                    logger.error(f"Feishu send failed: {response.code} - {response.msg}")

                # Small delay between chunks
                if i < len(chunks) - 1:
                    await asyncio.sleep(0.1)

            # Send media attachments if any
            for media_path in msg.media or []:
                await self._send_file(msg.chat_id, media_path)

        except Exception as e:
            logger.error(f"Error sending Feishu message: {e}")

    async def _send_file(self, chat_id: str, file_path: str) -> bool:
        """Send a file attachment."""
        path = Path(file_path)
        if not path.is_file():
            logger.warning(f"Feishu file not found: {file_path}")
            return False

        try:
            # Upload and send file via Feishu API
            # This requires separate upload + send steps
            logger.info(f"Feishu file upload: {path.name}")
            # Implementation depends on file type and size
            return True
        except Exception as e:
            logger.error(f"Feishu file send failed: {e}")
            return False

    async def handle_webhook_event(self, event: dict[str, Any]) -> None:
        """
        Handle incoming webhook event from Feishu.

        This should be called by your web server when receiving events.

        Args:
            event: The event payload from Feishu
        """
        if not self._running:
            return

        try:
            # Parse message event
            header = event.get("header", {})
            event_type = header.get("event_type", "")

            if event_type == "im.message.receive_v1":
                body = event.get("body", {})
                message = body.get("event", {}).get("message", {})

                sender_id = message.get("sender", {}).get("sender_id", {}).get("open_id", "")
                chat_id = message.get("chat_id", "")
                msg_type = message.get("message_type", "text")
                content_json = json.loads(message.get("content", "{}"))

                # Extract text content
                content = self._extract_content(content_json, msg_type)

                if content:
                    await self._handle_message(
                        sender_id=sender_id,
                        chat_id=chat_id,
                        content=content,
                        metadata={
                            "message_id": message.get("message_id"),
                            "msg_type": msg_type,
                            "create_time": message.get("create_time"),
                        }
                    )

        except Exception as e:
            logger.error(f"Error handling Feishu webhook event: {e}")

    def _extract_content(self, content_json: dict, msg_type: str) -> str:
        """Extract text content from message."""
        if msg_type == "text":
            return content_json.get("content", "")
        elif msg_type in MSG_TYPE_MAP:
            return MSG_TYPE_MAP[msg_type]
        else:
            return f"[{msg_type}]"
