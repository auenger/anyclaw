"""Server-Sent Events (SSE) streaming endpoint."""

from __future__ import annotations

import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from anyclaw.api.deps import get_message_bus

logger = logging.getLogger(__name__)

router = APIRouter()


async def event_publisher(request: Request) -> AsyncGenerator[dict[str, str], None]:
    """Publish events from MessageBus to SSE clients.

    Yields:
        SSE event dictionaries
    """
    bus = get_message_bus()

    # Subscribe to all events
    async for event in bus.subscribe():
        # Check if client disconnected
        if await request.is_disconnected():
            logger.info("SSE client disconnected")
            break

        # Convert event to SSE format
        yield {
            "event": event["type"],
            "data": json.dumps(event["payload"]),
        }


@router.get("/stream")
async def stream_events(request: Request) -> StreamingResponse:
    """Stream events from MessageBus via SSE.

    Clients can subscribe to real-time updates including:
    - message:inbound - New inbound messages
    - message:outbound - Agent responses
    - tool:start - Tool calls starting
    - tool:complete - Tool calls completed
    - agent:thinking - Agent thinking updates

    Returns:
        StreamingResponse with SSE events
    """
    logger.info("SSE client connected")

    return EventSourceResponse(event_publisher(request))
