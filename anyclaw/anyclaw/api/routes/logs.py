"""Logs API endpoints.

Provides endpoints for viewing:
- Session archive logs (from SessionArchiveManager)
- System runtime logs (from SystemLogCollector)
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from anyclaw.session.archive import SessionArchiveManager, ArchiveConfig
from anyclaw.utils.log_collector import get_log_collector, LogEntry

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== Models ====================

class SessionLogInfo(BaseModel):
    """Session log information."""
    session_id: str
    project_id: str
    channel: str
    cwd: Optional[str] = None
    git_branch: Optional[str] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    message_count: int = 0
    tool_call_count: int = 0
    duration_seconds: Optional[float] = None
    path: str


class SessionLogDetail(BaseModel):
    """Session log detail with records."""
    session_id: str
    project_id: str
    channel: str
    cwd: Optional[str] = None
    git_branch: Optional[str] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    message_count: int = 0
    tool_call_count: int = 0
    duration_seconds: Optional[float] = None
    records: List[dict] = []


class SystemLogEntry(BaseModel):
    """System log entry."""
    time: str
    level: str
    category: str
    agent: Optional[str] = None
    message: str
    details: Optional[dict] = None
    timestamp: str


class LogStats(BaseModel):
    """Log statistics."""
    sessions_total: int
    sessions_today: int
    system_logs_total: int
    by_level: dict = {}
    by_category: dict = {}


class SearchResult(BaseModel):
    """Search result."""
    session_id: str
    path: str
    type: str
    timestamp: Optional[str] = None
    content: dict


# ==================== Helper Functions ====================

def get_archive_manager() -> SessionArchiveManager:
    """Get SessionArchiveManager instance."""
    return SessionArchiveManager(ArchiveConfig())


# ==================== Endpoints ====================

@router.get("/logs/stats", response_model=LogStats)
async def get_log_stats() -> LogStats:
    """Get log statistics.

    Returns:
        LogStats with session and system log counts
    """
    archive = get_archive_manager()
    collector = get_log_collector()

    # Get all sessions
    all_sessions = archive.list_sessions(limit=1000)
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_sessions = [s for s in all_sessions if s.get("started_at", "").startswith(today_str)]

    # Get system log stats
    system_stats = collector.get_stats()

    return LogStats(
        sessions_total=len(all_sessions),
        sessions_today=len(today_sessions),
        system_logs_total=system_stats["total"],
        by_level=system_stats["by_level"],
        by_category=system_stats["by_category"],
    )


@router.get("/logs/sessions", response_model=List[SessionLogInfo])
async def list_session_logs(
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    project: Optional[str] = Query(None, description="Filter by project ID"),
    channel: Optional[str] = Query(None, description="Filter by channel"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results"),
) -> List[SessionLogInfo]:
    """List session logs.

    Args:
        date: Filter by date (YYYY-MM-DD)
        project: Filter by project ID
        channel: Filter by channel
        limit: Maximum number of results

    Returns:
        List of SessionLogInfo
    """
    archive = get_archive_manager()
    sessions = archive.list_sessions(date=date, project=project, channel=channel, limit=limit)

    return [
        SessionLogInfo(
            session_id=s.get("session_id", ""),
            project_id=s.get("project_id", ""),
            channel=s.get("channel", "cli"),
            cwd=s.get("cwd"),
            git_branch=s.get("git_branch"),
            started_at=s.get("started_at"),
            path=s.get("path", ""),
        )
        for s in sessions
    ]


@router.get("/logs/sessions/search", response_model=List[SearchResult])
async def search_session_logs(
    q: str = Query(..., description="Search query"),
    tool: Optional[str] = Query(None, description="Filter by tool name"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
) -> List[SearchResult]:
    """Search session logs.

    Args:
        q: Search query
        tool: Filter by tool name
        limit: Maximum number of results

    Returns:
        List of SearchResult
    """
    archive = get_archive_manager()
    results = archive.search_sessions(query=q, tool=tool, limit=limit)

    return [
        SearchResult(
            session_id=r.get("session_id", ""),
            path=r.get("path", ""),
            type=r.get("type", ""),
            timestamp=r.get("timestamp"),
            content=r.get("content", {}),
        )
        for r in results
    ]


@router.get("/logs/sessions/{session_id}", response_model=SessionLogDetail)
async def get_session_log(session_id: str) -> SessionLogDetail:
    """Get session log detail.

    Args:
        session_id: Session ID

    Returns:
        SessionLogDetail with all records

    Raises:
        HTTPException: If session not found
    """
    archive = get_archive_manager()
    session = archive.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    return SessionLogDetail(
        session_id=session.get("session_id", ""),
        project_id=session.get("project_id", ""),
        channel=session.get("channel", "cli"),
        cwd=session.get("cwd"),
        git_branch=session.get("git_branch"),
        started_at=session.get("started_at"),
        ended_at=session.get("ended_at"),
        message_count=session.get("message_count", 0),
        tool_call_count=session.get("tool_call_count", 0),
        duration_seconds=session.get("duration_seconds"),
        records=session.get("records", []),
        path=session.get("path", ""),
    )


@router.get("/logs/system", response_model=List[SystemLogEntry])
async def get_system_logs(
    level: Optional[str] = Query(None, description="Filter by level (DEBUG, INFO, WARN, ERROR)"),
    category: Optional[str] = Query(None, description="Filter by category (agent, tool, task, system)"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search in message"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results"),
) -> List[SystemLogEntry]:
    """Get system logs.

    Args:
        level: Filter by log level
        category: Filter by category
        date: Filter by date (YYYY-MM-DD)
        search: Search in message
        limit: Maximum number of results

    Returns:
        List of SystemLogEntry
    """
    collector = get_log_collector()
    logs = collector.get_logs(level=level, category=category, date=date, search=search, limit=limit)

    return [SystemLogEntry(**log) for log in logs]


@router.get("/logs/stream")
async def stream_logs(
    category: Optional[str] = Query(None, description="Filter by category"),
):
    """Stream system logs in real-time via SSE.

    Args:
        category: Filter by category (optional)

    Returns:
        SSE stream of log entries
    """
    from sse_starlette.sse import EventSourceResponse

    collector = get_log_collector()

    async def event_generator():
        """Generate SSE events from log stream."""
        import queue
        import threading

        entry_queue: queue.Queue[Optional[dict]] = queue.Queue()
        stop_event = threading.Event()

        class Subscriber:
            def on_log_entry(self, entry: LogEntry):
                if stop_event.is_set():
                    return
                data = entry.to_dict()
                # Apply category filter
                if category and category != "all":
                    if data.get("category") != category:
                        return
                entry_queue.put(data)

        subscriber = Subscriber()
        collector._subscribers.append(subscriber)

        try:
            while True:
                try:
                    # Non-blocking get with timeout
                    entry = entry_queue.get(timeout=1.0)
                    if entry is None:
                        break

                    # Format as SSE event
                    import json
                    yield {
                        "event": "log",
                        "data": json.dumps(entry),
                    }

                except queue.Empty:
                    # Send keepalive
                    yield {"event": "keepalive", "data": ""}
                    continue

        except asyncio.CancelledError:
            stop_event.set()
        finally:
            if subscriber in collector._subscribers:
                collector._subscribers.remove(subscriber)

    return EventSourceResponse(event_generator())
