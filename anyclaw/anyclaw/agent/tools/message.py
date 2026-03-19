"""Message tool for sending messages to users."""

import logging
from typing import Any, Awaitable, Callable, Optional

from anyclaw.tools.base import Tool
from anyclaw.bus.events import OutboundMessage


logger = logging.getLogger(__name__)


class MessageTool(Tool):
    """Tool to send messages to users on chat channels."""

    def __init__(
        self,
        send_callback: Optional[Callable[[OutboundMessage], Awaitable[None]]] = None,
        default_channel: str = "",
        default_chat_id: str = "",
        default_message_id: Optional[str] = None,
    ):
        self._send_callback = send_callback
        self._default_channel = default_channel
        self._default_chat_id = default_chat_id
        self._default_message_id = default_message_id
        self._sent_in_turn: bool = False

    def set_context(self, channel: str, chat_id: str, message_id: Optional[str] = None) -> None:
        """Set current message context."""
        self._default_channel = channel
        self._default_chat_id = chat_id
        self._default_message_id = message_id

    def set_send_callback(self, callback: Callable[[OutboundMessage], Awaitable[None]]) -> None:
        """Set callback for sending messages."""
        self._send_callback = callback

    def start_turn(self) -> None:
        """Reset per-turn send tracking."""
        self._sent_in_turn = False

    @property
    def name(self) -> str:
        return "message"

    @property
    def description(self) -> str:
        return "Send a message to user. Use this when you want to communicate something."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The message content to send"
                },
                "channel": {
                    "type": "string",
                    "description": "Optional: target channel (telegram, discord, feishu, etc.)"
                },
                "chat_id": {
                    "type": "string",
                    "description": "Optional: target chat/user ID"
                },
                "message_id": {
                    "type": "string",
                    "description": "Optional: message ID to reply to"
                },
                "media": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional: list of file paths to attach (images, audio, documents)"
                }
            },
            "required": ["content"]
        }

    async def execute(
        self,
        content: str,
        channel: Optional[str] = None,
        chat_id: Optional[str] = None,
        message_id: Optional[str] = None,
        media: Optional[list[str]] = None,
        **kwargs: Any
    ) -> str:
        """Execute message sending."""
        channel = channel or self._default_channel
        chat_id = chat_id or self._default_chat_id
        message_id = message_id or self._default_message_id

        if not channel or not chat_id:
            return "Error: No target channel/chat specified. Use message tool to send to current chat."

        if not self._send_callback:
            return "Error: Message sending not configured. Please check channel settings."

        msg = OutboundMessage(
            channel=channel,
            chat_id=chat_id,
            content=content,
            media=media or [],
            metadata={
                "message_id": message_id,
                "reply_to": message_id,
            },
        )

        try:
            await self._send_callback(msg)
            if channel == self._default_channel and chat_id == self._default_chat_id:
                self._sent_in_turn = True
            media_info = f" with {len(media)} attachments" if media else ""
            return f"Message sent to {channel}:{chat_id}{media_info}"
        except Exception as e:
            logger.error("Failed to send message: {}", e)
            return f"Error sending message: {str(e)}"
