"""Chat history management endpoints."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from anyclaw.api.deps import get_serve_manager

router = APIRouter()

logger = logging.getLogger(__name__)


class ChatItem(BaseModel):
    """Chat item for list display."""

    chat_id: str  # 完整 session key，如 "api:conv_1711084800"
    conversation_id: str  # 短 ID，如 "conv_1711084800"
    name: str
    agent_id: str
    channel: str
    last_message_time: str
    last_message: Optional[str] = None
    avatar: Optional[str] = None
    message_count: int = 0
    created_at: Optional[str] = None


class ChatMessage(BaseModel):
    """Chat message with full tool calling support."""

    id: str
    role: str  # "user" | "assistant" | "tool"
    content: str
    timestamp: str
    tool_calls: Optional[List[Dict[str, Any]]] = None  # assistant 发起的工具调用
    tool_call_id: Optional[str] = None  # tool 消息关联 ID
    name: Optional[str] = None  # 工具名称 (role="tool" 时)


class ChatDetail(BaseModel):
    """Chat detail with messages."""

    chat_id: str
    messages: list[ChatMessage]


class ChatUpdateRequest(BaseModel):
    """Request body for updating chat."""

    name: Optional[str] = None
    avatar: Optional[str] = None


def _generate_chat_name(session_info: dict) -> str:
    """Generate a friendly display name from session info."""
    from datetime import datetime

    # First check if there's a custom display_name in metadata
    metadata = session_info.get("metadata", {})
    if metadata.get("display_name"):
        return metadata["display_name"]

    # Try to use updated_at or created_at for naming
    updated_at = session_info.get("updated_at")
    if updated_at:
        try:
            dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            # Format: "Chat 3月22日 14:30"
            return f"Chat {dt.month}月{dt.day}日 {dt.hour:02d}:{dt.minute:02d}"
        except (ValueError, TypeError):
            pass

    # Fallback: use timestamp from conversation_id if available
    key = session_info.get("key", "")
    parts = key.split(":", 1)
    conversation_id = parts[1] if len(parts) == 2 else key

    # Try to extract timestamp from conv_XXXXXX format
    if conversation_id.startswith("conv_"):
        try:
            timestamp_str = conversation_id[5:]  # Remove "conv_" prefix
            timestamp = int(timestamp_str)
            dt = datetime.fromtimestamp(timestamp / 1000)  # Assume milliseconds
            return f"Chat {dt.month}月{dt.day}日 {dt.hour:02d}:{dt.minute:02d}"
        except (ValueError, TypeError):
            pass

    # Final fallback
    if conversation_id == "default":
        return "默认对话"
    return f"Chat {conversation_id[:8]}"


def _extract_last_message(session_info: dict) -> Optional[str]:
    """Extract last message preview from session info."""
    # Check if last_message is already provided
    if session_info.get("last_message"):
        msg = session_info["last_message"]
        # Truncate to 50 chars
        return msg[:50] + "..." if len(msg) > 50 else msg
    return None


def _extract_avatar(session_info: dict) -> Optional[str]:
    """Extract avatar from session metadata."""
    metadata = session_info.get("metadata", {})
    return metadata.get("avatar")


def _session_to_chat_item(session_info: dict) -> ChatItem:
    """Convert session info to ChatItem format."""
    key = session_info.get("key", "")
    # Parse key format: "channel:chat_id" or just "chat_id"
    parts = key.split(":", 1)
    if len(parts) == 2:
        channel, conversation_id = parts
    else:
        channel = "cli"
        conversation_id = key

    # Generate a friendly display name
    name = _generate_chat_name(session_info)

    # Extract last message preview
    last_message = _extract_last_message(session_info)

    # Extract avatar from metadata
    avatar = _extract_avatar(session_info)

    return ChatItem(
        chat_id=key,  # 完整 key，如 "api:conv_1711084800"
        conversation_id=conversation_id,  # 短 ID，如 "conv_1711084800"
        name=name,
        agent_id="default",
        channel=channel,
        last_message_time=session_info.get("updated_at", ""),
        last_message=last_message,
        avatar=avatar,
        message_count=session_info.get("message_count", 0),
        created_at=session_info.get("created_at"),
    )


@router.get("/chats", response_model=list[ChatItem])
async def list_chats() -> list[ChatItem]:
    """List all chat sessions.

    Returns:
        List of ChatItem
    """
    manager = get_serve_manager()

    # Get sessions from SessionManager (via agent)
    if manager.agent and manager.agent.session_manager:
        sessions = manager.agent.session_manager.list_sessions()
        chats = [_session_to_chat_item(s) for s in sessions]
    else:
        chats = []

    return chats


@router.get("/chats/{chat_id}", response_model=ChatDetail)
async def get_chat(chat_id: str) -> ChatDetail:
    """Get chat messages by ID.

    Args:
        chat_id: Chat ID (完整 session key，如 "api:conv_1711084800")

    Returns:
        ChatDetail with messages

    Raises:
        HTTPException: If chat not found
    """
    manager = get_serve_manager()

    # Check if session_manager is available
    if not manager.agent or not manager.agent.session_manager:
        raise HTTPException(status_code=404, detail="Session manager not available")

    # chat_id 已经是完整的 session key，直接查找
    session = manager.agent.session_manager.get(chat_id)

    if not session:
        # 尝试补充前缀（兼容旧版 API）
        for prefix in ["api:", "cli:", "channel:"]:
            session = manager.agent.session_manager.get(f"{prefix}{chat_id}")
            if session and session.messages:
                break
            session = None

    if not session:
        raise HTTPException(status_code=404, detail=f"Chat {chat_id} not found")

    # Convert messages to response format (include all roles: user, assistant, tool)
    messages = [
        ChatMessage(
            id=str(i),
            role=msg.role,
            content=msg.content or "",
            timestamp=msg.timestamp or "",
            tool_calls=msg.tool_calls if msg.tool_calls else None,
            tool_call_id=msg.tool_call_id if msg.tool_call_id else None,
            name=msg.name if msg.name else None,
        )
        for i, msg in enumerate(session.messages)
        if msg.role in ("user", "assistant", "tool")
    ]

    return ChatDetail(chat_id=chat_id, messages=messages)


@router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str) -> dict[str, bool]:
    """Delete a chat session.

    Args:
        chat_id: Chat ID (完整 session key，如 "api:conv_1711084800")

    Returns:
        Success status
    """
    manager = get_serve_manager()

    # Check if session_manager is available
    if not manager.agent or not manager.agent.session_manager:
        return {"success": False}

    # chat_id 已经是完整的 session key，直接删除
    try:
        manager.agent.session_manager.delete_session(chat_id)
        return {"success": True}
    except Exception:
        # 尝试补充前缀（兼容旧版 API）
        for prefix in ["api:", "cli:", "channel:"]:
            try:
                manager.agent.session_manager.delete_session(f"{prefix}{chat_id}")
                return {"success": True}
            except Exception:
                continue
        return {"success": False}


@router.patch("/chats/{chat_id}")
async def update_chat(chat_id: str, data: ChatUpdateRequest) -> dict[str, bool]:
    """Update chat metadata (name, avatar).

    Args:
        chat_id: Chat ID (完整 session key)
        data: Update data (name and/or avatar)

    Returns:
        Success status
    """
    manager = get_serve_manager()

    # Check if session_manager is available
    if not manager.agent or not manager.agent.session_manager:
        logger.warning(f"Session manager not available for update: {chat_id}")
        return {"success": False}

    # Build metadata update
    metadata = {}
    if data.name is not None:
        metadata["display_name"] = data.name
    if data.avatar is not None:
        metadata["avatar"] = data.avatar

    if not metadata:
        return {"success": True}  # Nothing to update

    # Update metadata
    success = manager.agent.session_manager.update_metadata(chat_id, metadata)

    if success:
        logger.info(f"Updated chat {chat_id}: {metadata}")
    else:
        logger.warning(f"Failed to update chat {chat_id}")

    return {"success": success}
