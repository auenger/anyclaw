"""Base channel interface for chat platforms."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from anyclaw.bus.events import InboundMessage, OutboundMessage
from anyclaw.bus.queue import MessageBus


class AuthorizationRequiredError(Exception):
    """需要授权异常 - 携带授权上下文

    当 PathGuard 检测到路径访问越界时抛出此异常，
    Channel 层应捕获此异常并请求用户授权。
    """

    def __init__(self, path: Path, suggested_dir: Path, message: Optional[str] = None):
        """初始化授权异常

        Args:
            path: 请求访问的路径
            suggested_dir: 建议授权的目录
            message: 自定义错误消息
        """
        self.path = path
        self.suggested_dir = suggested_dir
        self.message = message or f"需要授权访问: {suggested_dir}"
        super().__init__(self.message)


class BaseChannel(ABC):
    """
    Abstract base class for chat channel implementations.

    Each channel (CLI, Feishu, Discord, etc.) should implement this interface
    to integrate with the AnyClaw message bus.
    """

    name: str = "base"
    display_name: str = "Base"

    def __init__(self, config: Any, bus: MessageBus):
        """
        Initialize the channel.

        Args:
            config: Channel-specific configuration.
            bus: The message bus for communication.
        """
        self.config = config
        self.bus = bus
        self._running = False

    @abstractmethod
    async def start(self) -> None:
        """
        Start the channel and begin listening for messages.

        This should be a long-running async task that:
        1. Connects to the chat platform
        2. Listens for incoming messages
        3. Forwards messages to the bus via _handle_message()
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the channel and clean up resources."""
        pass

    @abstractmethod
    async def send(self, msg: OutboundMessage) -> None:
        """
        Send a message through this channel.

        Args:
            msg: The message to send.
        """
        pass

    async def request_authorization(
        self,
        error: AuthorizationRequiredError,
        chat_id: Optional[str] = None,
        timeout: float = 60.0,
    ) -> Optional[str]:
        """请求用户授权访问目录

        当 Agent 尝试访问受限目录时调用此方法。
        子类应重写此方法以提供适合该渠道的授权交互方式。

        Args:
            error: 授权异常，包含路径信息
            chat_id: 聊天 ID（用于发送授权请求）
            timeout: 授权超时时间（秒）

        Returns:
            授权决策:
            - "session": 临时授权（仅当前会话）
            - "persist": 永久授权
            - "deny": 拒绝
            - None: 超时或取消
        """
        # 默认实现：回复式授权（回退方案）
        # 子类应重写此方法以提供更好的用户体验
        return None

    def is_allowed(self, sender_id: str) -> bool:
        """
        Check if sender_id is permitted to use this channel.

        Empty list → deny all; "*" → allow all.

        Args:
            sender_id: The sender's identifier

        Returns:
            True if sender is allowed
        """
        allow_list = getattr(self.config, "allow_from", [])
        if isinstance(allow_list, dict):
            allow_list = allow_list.get("list", [])
        if not allow_list:
            return False
        if "*" in allow_list:
            return True
        return str(sender_id) in [str(x) for x in allow_list]

    async def _handle_message(
        self,
        sender_id: str,
        chat_id: str,
        content: str,
        media: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        session_key: Optional[str] = None,
    ) -> None:
        """
        Handle an incoming message from the chat platform.

        This method checks permissions and forwards to the bus.

        Args:
            sender_id: The sender's identifier.
            chat_id: The chat/channel identifier.
            content: Message text content.
            media: Optional list of media file paths.
            metadata: Optional channel-specific metadata.
            session_key: Optional session key override.
        """
        if not self.is_allowed(sender_id):
            # Silently ignore unauthorized messages
            return

        msg = InboundMessage(
            channel=self.name,
            sender_id=str(sender_id),
            chat_id=str(chat_id),
            content=content,
            media=media or [],
            metadata=metadata or {},
            session_key_override=session_key,
        )

        await self.bus.publish_inbound(msg)

    @classmethod
    def default_config(cls) -> Dict[str, Any]:
        """Return default config for this channel."""
        return {"enabled": False}

    @property
    def is_running(self) -> bool:
        """Check if the channel is running."""
        return self._running
