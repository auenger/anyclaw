"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from anyclaw.api.deps import get_serve_manager

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    uptime_seconds: int
    version: str = "0.1.0"
    channels: list[str] = []
    messages_processed: int = 0


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check the API server and AnyClaw service health.

    Returns:
        HealthResponse with service status
    """
    manager = get_serve_manager()

    return HealthResponse(
        status="ok" if manager.is_running else "stopped",
        uptime_seconds=manager.uptime_seconds,
        channels=manager.enabled_channels,
        messages_processed=manager._messages_processed,
    )
