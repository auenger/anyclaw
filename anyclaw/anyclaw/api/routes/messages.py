"""Message sending endpoints."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from anyclaw.api.deps import get_message_bus, get_serve_manager
from anyclaw.bus.events import InboundMessage

router = APIRouter()


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
    bus = get_message_bus()
    manager = get_serve_manager()

    # Generate message ID
    message_id = f"msg_{id(request)}"

    # Create inbound message
    inbound_msg = InboundMessage(
        message_id=message_id,
        agent_id=request.agent_id,
        content=request.content,
        conversation_id=request.conversation_id or f"conv_{request.agent_id}",
        source="api",
        metadata=request.metadata,
    )

    # Publish to bus
    await bus.publish(inbound_msg)

    # Update counter
    manager._messages_processed += 1

    return SendMessageResponse(
        status="ok",
        message_id=message_id,
        agent_id=request.agent_id,
    )
