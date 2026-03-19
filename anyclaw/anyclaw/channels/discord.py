"""Discord channel implementation using Discord Gateway websocket.

Dependencies:
    pip install websockets httpx
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

# Check dependencies
WEBSOCKETS_AVAILABLE = importlib.util.find_spec("websockets") is not None
HTTPX_AVAILABLE = importlib.util.find_spec("httpx") is not None

DISCORD_API_BASE = "https://discord.com/api/v10"
MAX_ATTACHMENT_BYTES = 20 * 1024 * 1024  # 20MB
MAX_MESSAGE_LEN = 2000  # Discord message character limit


@dataclass
class DiscordConfig:
    """Discord channel configuration."""

    enabled: bool = False
    token: str = ""
    allow_from: list[str] = Field(default_factory=lambda: ["*"])
    gateway_url: str = "wss://gateway.discord.gg/?v=10&encoding=json"
    intents: int = 37377  # GUILD_MESSAGES + DIRECT_MESSAGES + MESSAGE_CONTENT
    group_policy: Literal["mention", "open"] = "mention"


def _split_message(content: str, max_len: int = MAX_MESSAGE_LEN) -> list[str]:
    """Split content into chunks that fit Discord's message limit."""
    if not content:
        return []
    if len(content) <= max_len:
        return [content]

    chunks = []
    remaining = content
    while remaining:
        if len(remaining) <= max_len:
            chunks.append(remaining)
            break
        # Find a good break point
        break_point = remaining.rfind("\n", 0, max_len)
        if break_point == -1:
            break_point = remaining.rfind(" ", 0, max_len)
        if break_point == -1:
            break_point = max_len
        chunks.append(remaining[:break_point].rstrip())
        remaining = remaining[break_point:].lstrip()

    return chunks


class DiscordChannel(BaseChannel):
    """Discord channel using Gateway websocket."""

    name = "discord"
    display_name = "Discord"

    def __init__(self, config: Any, bus: MessageBus):
        if isinstance(config, dict):
            config = DiscordConfig(**config)
        super().__init__(config, bus)
        self.config: DiscordConfig = config
        self._ws: Any = None
        self._seq: int | None = None
        self._heartbeat_task: asyncio.Task | None = None
        self._typing_tasks: dict[str, asyncio.Task] = {}
        self._http: Any = None
        self._bot_user_id: str | None = None

    @classmethod
    def default_config(cls) -> dict[str, Any]:
        return DiscordConfig().model_dump()

    async def start(self) -> None:
        """Start the Discord gateway connection."""
        if not WEBSOCKETS_AVAILABLE or not HTTPX_AVAILABLE:
            logger.error("websockets and httpx required for Discord channel")
            return

        if not self.config.token:
            logger.error("Discord bot token not configured")
            return

        import httpx
        import websockets

        self._running = True
        self._http = httpx.AsyncClient(timeout=30.0)

        while self._running:
            try:
                logger.info("Connecting to Discord gateway...")
                async with websockets.connect(self.config.gateway_url) as ws:
                    self._ws = ws
                    await self._gateway_loop()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Discord gateway error: {e}")
                if self._running:
                    logger.info("Reconnecting to Discord gateway in 5 seconds...")
                    await asyncio.sleep(5)

    async def stop(self) -> None:
        """Stop the Discord channel."""
        self._running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            self._heartbeat_task = None
        for task in self._typing_tasks.values():
            task.cancel()
        self._typing_tasks.clear()
        if self._ws:
            await self._ws.close()
            self._ws = None
        if self._http:
            await self._http.aclose()
            self._http = None

    async def send(self, msg: OutboundMessage) -> None:
        """Send a message through Discord REST API."""
        if not self._http:
            logger.warning("Discord HTTP client not initialized")
            return

        url = f"{DISCORD_API_BASE}/channels/{msg.chat_id}/messages"
        headers = {"Authorization": f"Bot {self.config.token}"}

        try:
            sent_media = False
            failed_media: list[str] = []

            # Send file attachments first
            for media_path in msg.media or []:
                if await self._send_file(url, headers, media_path, reply_to=msg.reply_to):
                    sent_media = True
                else:
                    failed_media.append(Path(media_path).name)

            # Send text content
            chunks = _split_message(msg.content or "")
            if not chunks and failed_media and not sent_media:
                chunks = _split_message(
                    "\n".join(f"[attachment: {name} - send failed]" for name in failed_media)
                )
            if not chunks:
                return

            for i, chunk in enumerate(chunks):
                payload: dict[str, Any] = {"content": chunk}

                # First chunk gets the reply reference
                if i == 0 and msg.reply_to and not sent_media:
                    payload["message_reference"] = {"message_id": msg.reply_to}
                    payload["allowed_mentions"] = {"replied_user": False}

                if not await self._send_payload(url, headers, payload):
                    break

        finally:
            await self._stop_typing(msg.chat_id)

    async def _send_payload(self, url: str, headers: dict, payload: dict) -> bool:
        """Send a Discord API payload with retry on rate-limit."""
        for attempt in range(3):
            try:
                response = await self._http.post(url, headers=headers, json=payload)
                if response.status_code == 429:
                    data = response.json()
                    retry_after = float(data.get("retry_after", 1.0))
                    logger.warning(f"Discord rate limited, retrying in {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue
                response.raise_for_status()
                return True
            except Exception as e:
                if attempt == 2:
                    logger.error(f"Error sending Discord message: {e}")
                else:
                    await asyncio.sleep(1)
        return False

    async def _send_file(
        self, url: str, headers: dict, file_path: str, reply_to: str | None = None
    ) -> bool:
        """Send a file attachment via Discord REST API."""
        path = Path(file_path)
        if not path.is_file():
            logger.warning(f"Discord file not found: {file_path}")
            return False

        if path.stat().st_size > MAX_ATTACHMENT_BYTES:
            logger.warning(f"Discord file too large (>20MB): {path.name}")
            return False

        payload_json: dict[str, Any] = {}
        if reply_to:
            payload_json["message_reference"] = {"message_id": reply_to}

        for attempt in range(3):
            try:
                with open(path, "rb") as f:
                    files = {"files[0]": (path.name, f)}
                    data = {}
                    if payload_json:
                        data["payload_json"] = json.dumps(payload_json)
                    response = await self._http.post(url, headers=headers, files=files, data=data)

                if response.status_code == 429:
                    resp_data = response.json()
                    retry_after = float(resp_data.get("retry_after", 1.0))
                    logger.warning(f"Discord rate limited, retrying in {retry_after}s")
                    await asyncio.sleep(retry_after)
                    continue
                response.raise_for_status()
                logger.info(f"Discord file sent: {path.name}")
                return True
            except Exception as e:
                if attempt == 2:
                    logger.error(f"Error sending Discord file {path.name}: {e}")
                else:
                    await asyncio.sleep(1)
        return False

    async def _gateway_loop(self) -> None:
        """Main gateway loop: identify, heartbeat, dispatch events."""
        if not self._ws:
            return

        async for raw in self._ws:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from Discord gateway")
                continue

            op = data.get("op")
            event_type = data.get("t")
            seq = data.get("s")
            payload = data.get("d")

            if seq is not None:
                self._seq = seq

            if op == 10:  # HELLO
                interval_ms = payload.get("heartbeat_interval", 45000)
                await self._start_heartbeat(interval_ms / 1000)
                await self._identify()
            elif op == 0 and event_type == "READY":
                logger.info("Discord gateway READY")
                user_data = payload.get("user") or {}
                self._bot_user_id = user_data.get("id")
                logger.info(f"Discord bot connected as user {self._bot_user_id}")
            elif op == 0 and event_type == "MESSAGE_CREATE":
                await self._handle_message_create(payload)
            elif op == 7:  # RECONNECT
                logger.info("Discord gateway requested reconnect")
                break
            elif op == 9:  # INVALID_SESSION
                logger.warning("Discord gateway invalid session")
                break

    async def _identify(self) -> None:
        """Send IDENTIFY payload."""
        if not self._ws:
            return

        identify = {
            "op": 2,
            "d": {
                "token": self.config.token,
                "intents": self.config.intents,
                "properties": {
                    "os": "anyclaw",
                    "browser": "anyclaw",
                    "device": "anyclaw",
                },
            },
        }
        await self._ws.send(json.dumps(identify))

    async def _start_heartbeat(self, interval_s: float) -> None:
        """Start or restart the heartbeat loop."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        async def heartbeat_loop() -> None:
            while self._running and self._ws:
                payload = {"op": 1, "d": self._seq}
                try:
                    await self._ws.send(json.dumps(payload))
                except Exception as e:
                    logger.warning(f"Discord heartbeat failed: {e}")
                    break
                await asyncio.sleep(interval_s)

        self._heartbeat_task = asyncio.create_task(heartbeat_loop())

    async def _handle_message_create(self, payload: dict[str, Any]) -> None:
        """Handle incoming Discord messages."""
        author = payload.get("author") or {}
        if author.get("bot"):
            return

        sender_id = str(author.get("id", ""))
        channel_id = str(payload.get("channel_id", ""))
        content = payload.get("content") or ""
        guild_id = payload.get("guild_id")

        if not sender_id or not channel_id:
            return

        if not self.is_allowed(sender_id):
            return

        # Check group channel policy
        if guild_id is not None:
            if not self._should_respond_in_group(payload, content):
                return

        content_parts = [content] if content else []
        media_paths: list[str] = []

        # Handle attachments
        for attachment in payload.get("attachments") or []:
            url = attachment.get("url")
            filename = attachment.get("filename") or "attachment"
            size = attachment.get("size") or 0

            if not url or not self._http:
                continue
            if size and size > MAX_ATTACHMENT_BYTES:
                content_parts.append(f"[attachment: {filename} - too large]")
                continue

            try:
                media_dir = Path.home() / ".anyclaw" / "media" / "discord"
                media_dir.mkdir(parents=True, exist_ok=True)
                file_path = media_dir / f"{attachment.get('id', 'file')}_{filename.replace('/', '_')}"
                resp = await self._http.get(url)
                resp.raise_for_status()
                file_path.write_bytes(resp.content)
                media_paths.append(str(file_path))
                content_parts.append(f"[attachment: {file_path}]")
            except Exception as e:
                logger.warning(f"Failed to download Discord attachment: {e}")
                content_parts.append(f"[attachment: {filename} - download failed]")

        reply_to = (payload.get("referenced_message") or {}).get("id")

        await self._start_typing(channel_id)

        await self._handle_message(
            sender_id=sender_id,
            chat_id=channel_id,
            content="\n".join(p for p in content_parts if p) or "[empty message]",
            media=media_paths,
            metadata={
                "message_id": str(payload.get("id", "")),
                "guild_id": guild_id,
                "reply_to": reply_to,
            },
        )

    def _should_respond_in_group(self, payload: dict[str, Any], content: str) -> bool:
        """Check if bot should respond in a group channel."""
        if self.config.group_policy == "open":
            return True

        if self.config.group_policy == "mention":
            if self._bot_user_id:
                mentions = payload.get("mentions") or []
                for mention in mentions:
                    if str(mention.get("id")) == self._bot_user_id:
                        return True
                if f"<@{self._bot_user_id}>" in content or f"<@!{self._bot_user_id}>" in content:
                    return True
            return False

        return True

    async def _start_typing(self, channel_id: str) -> None:
        """Start periodic typing indicator."""
        await self._stop_typing(channel_id)

        async def typing_loop() -> None:
            url = f"{DISCORD_API_BASE}/channels/{channel_id}/typing"
            headers = {"Authorization": f"Bot {self.config.token}"}
            while self._running:
                try:
                    await self._http.post(url, headers=headers)
                except asyncio.CancelledError:
                    return
                except Exception:
                    return
                await asyncio.sleep(8)

        self._typing_tasks[channel_id] = asyncio.create_task(typing_loop())

    async def _stop_typing(self, channel_id: str) -> None:
        """Stop typing indicator."""
        task = self._typing_tasks.pop(channel_id, None)
        if task:
            task.cancel()
