"""Chat history management endpoints."""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from anyclaw.api.deps import get_serve_manager

router = APIRouter()

logger = logging.getLogger(__name__)


class ChatItem(BaseModel):
    """Chat item for list display."""

    chat_id: str
    name: str
    agent_id: str
    channel: str
    last_message_time: str
    last_message: Optional[str] = None
    avatar: Optional[str] = None


class ChatMessage(BaseModel):
    """Chat message."""

    id: str
    role: str
    content: str
    timestamp: str


class ChatDetail(BaseModel):
    """Chat detail with messages."""

    chat_id: str
    messages: list[ChatMessage]


class ChatUpdateRequest(BaseModel):
    """Request body for updating chat."""

    name: Optional[str] = None
    avatar: Optional[str] = None


def _session_to_chat_item(session_info: dict) -> ChatItem:
    """Convert session info to ChatItem format."""
    key = session_info.get("key", "")
    # Parse key format: "channel:chat_id" or just "chat_id"
    parts = key.split(":", 1)
    if len(parts) == 2:
        channel, chat_id = parts
    else:
        channel = "cli"
        chat_id = key

    # Generate a display name from the chat_id or use default
    name = f"Chat {chat_id[:8]}" if len(chat_id) > 8 else f"Chat {chat_id}"

    return ChatItem(
        chat_id=chat_id,
        name=name,
        agent_id="default",
        channel=channel,
        last_message_time=session_info.get("updated_at", ""),
        last_message=None,  # TODO: Extract last message from session
        avatar=None,
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
        chat_id: Chat ID

    Returns:
        ChatDetail with messages

    Raises:
        HTTPException: If chat not found
    """
    manager = get_serve_manager()

    # Check if session_manager is available
    if not manager.agent or not manager.agent.session_manager:
        raise HTTPException(status_code=404, detail="Session manager not available")

    # Try to find session with various key formats
    # Session keys may be "cli:chat_id", "channel:chat_id", or just "chat_id"
    session = None
    for key_format in [f"cli:{chat_id}", chat_id, f"channel:{chat_id}"]:
        try:
            session = manager.agent.session_manager.get_or_create(key_format)
            if session.messages:
                break
        except Exception:
            continue

    if not session:
        raise HTTPException(status_code=404, detail=f"Chat {chat_id} not found")

    # Convert messages to response format
    messages = [
        ChatMessage(
            id=str(i),
            role=msg.role,
            content=msg.content or "",
            timestamp=msg.timestamp or "",
        )
        for i, msg in enumerate(session.messages)
        if msg.role in ("user", "assistant")
    ]

    return ChatDetail(chat_id=chat_id, messages=messages)


@router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str) -> dict[str, bool]:
    """Delete a chat session.

    Args:
        chat_id: Chat ID

    Returns:
        Success status
    """
    manager = get_serve_manager()

    # Check if session_manager is available
    if not manager.agent or not manager.agent.session_manager:
        return {"success": False}

    # Try to delete with various key formats
    deleted = False
    for key_format in [f"cli:{chat_id}", chat_id, f"channel:{chat_id}"]:
        try:
            manager.agent.session_manager.delete_session(key_format)
            deleted = True
            break
        except Exception:
            continue

    return {"success": deleted}


@router.patch("/chats/{chat_id}")
async def update_chat(chat_id: str, data: ChatUpdateRequest) -> dict[str, bool]:
    """Update chat metadata (name, avatar).

    Args:
        chat_id: Chat ID
        data: Update data

    Returns:
        Success status

    Note:
        Currently a placeholder. Full implementation would require
        extending Session model to support metadata.
    """
    # TODO: Implement chat metadata storage
    # For now, just return success
    logger.info(f"Update chat {chat_id}: name={data.name}, avatar={data.avatar}")
    return {"success": True}
