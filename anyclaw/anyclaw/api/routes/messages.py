"""Message sending endpoints."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from anyclaw.api.deps import get_message_bus, get_serve_manager
from anyclaw.bus.events import InboundMessage

router = APIRouter()
logger = logging.getLogger(__name__)


class SendMessageRequest(BaseModel):
    """Request to send a message to an agent."""

    agent_id: str = Field(..., description="Agent ID to send message to")
    content: str = Field(..., description="Message content")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SendMessageResponse(BaseModel):
    """Response to send message request."""

    status: str
    message_id: str
    agent_id: str


@router.post("/messages", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest) -> SendMessageResponse:
    """Send a message to an agent.

    The message is published to the MessageBus and routed to the appropriate
    agent through the ServeManager.

    Args:
        request: Send message request

    Returns:
        SendMessageResponse with message ID

    Raises:
        HTTPException: If message cannot be sent
    """
    import time
    _start_time = time.time()

    bus = get_message_bus()
    manager = get_serve_manager()

    # Generate message ID
    import uuid
    message_id = f"msg_{uuid.uuid4().hex[:8]}"

    # 详细日志：消息接收
    logger.info(f"[API] ▶️ 收到消息请求: agent_id={request.agent_id}, "
                f"content={request.content[:50]}{'...' if len(request.content) > 50 else ''}, "
                f"conversation_id={request.conversation_id}")

    # Determine session key handling
    # If conversation_id contains ":", it's already a complete session key (e.g., "api:conv_XXX")
    # Use session_key_override to prevent double-prefixing in serve.py
    conv_id = request.conversation_id
    if conv_id and ":" in conv_id:
        # Already a complete session key, use as override and set chat_id to the short ID
        parts = conv_id.split(":", 1)
        chat_id = parts[1] if len(parts) == 2 else conv_id
        session_key_override = conv_id
    else:
        # Short ID or None, will be prefixed with "api:" in serve.py
        chat_id = conv_id or f"conv_{request.agent_id}"
        session_key_override = None

    # Create inbound message
    inbound_msg = InboundMessage(
        channel="api",
        sender_id="api_user",
        chat_id=chat_id,
        content=request.content,
        metadata=request.metadata or {},
        session_key_override=session_key_override,
    )

    # Publish to bus
    await bus.publish_inbound(inbound_msg)
    logger.info(f"[API] ✅ 消息已发布到总线: message_id={message_id}, "
                f"bus_inbound_size={bus.inbound_size}")

    # Update counter
    manager._messages_processed += 1

    logger.info(f"[API] ⏱️ 处理耗时: {(time.time() - _start_time)*1000:.1f}ms")

    return SendMessageResponse(
        status="ok",
        message_id=message_id,
        agent_id=request.agent_id,
    )
