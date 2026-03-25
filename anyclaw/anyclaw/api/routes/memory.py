"""Memory API endpoints.

Provides memory management for agents.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from anyclaw.config.loader import get_config

logger = logging.getLogger(__name__)

router = APIRouter()


# Response models
class MemoryInfo(BaseModel):
    """Memory info for list response."""
    id: str
    name: str
    is_global: bool
    agent_id: Optional[str] = None
    exists: bool
    char_count: int


class MemoryContent(BaseModel):
    """Memory content response."""
    id: str
    content: str
    exists: bool


class DailyLogInfo(BaseModel):
    """Daily log info."""
    date: str
    content: str
    char_count: int


class MemoryStats(BaseModel):
    """Memory statistics."""
    long_term_exists: bool
    long_term_chars: int
    daily_logs_count: int
    oldest_log: Optional[str] = None
    newest_log: Optional[str] = None


class SearchMatch(BaseModel):
    """Search match result."""
    source: str
    matches: list[str]


class SearchResponse(BaseModel):
    """Search response."""
    results: list[SearchMatch]


class UpdateMemoryRequest(BaseModel):
    """Update memory request."""
    content: str


class SearchRequest(BaseModel):
    """Search request."""
    keyword: str
    memory_id: Optional[str] = None


def get_memory_dir() -> Path:
    """Get memory directory path."""
    config = get_config()
    workspace = Path(config.agent.workspace).expanduser()
    return workspace / "memory"


def get_memory_path(memory_id: str) -> Path:
    """Get memory file path."""
    memory_dir = get_memory_dir()
    if memory_id == "MEMORY" or memory_id == "global":
        return memory_dir / "MEMORY.md"
    else:
        # Agent memory
        return memory_dir / "agents" / f"{memory_id}.md"


@router.get("/memory")
async def list_memories() -> list[MemoryInfo]:
    """List all memories."""
    memory_dir = get_memory_dir()
    memories = []

    # Global memory
    global_memory = memory_dir / "MEMORY.md"
    global_exists = global_memory.exists()
    global_chars = len(global_memory.read_text()) if global_exists else 0

    memories.append(
        MemoryInfo(
            id="MEMORY",
            name="Global Memory",
            is_global=True,
            exists=global_exists,
            char_count=global_chars,
        )
    )

    # Agent memories
    config = get_config()
    workspace = Path(config.agent.workspace).expanduser()
    agents_dir = workspace / "agents"

    if agents_dir.exists():
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                memory_file = agent_dir / "MEMORY.md"
                exists = memory_file.exists()
                chars = len(memory_file.read_text()) if exists else 0
                memories.append(
                    MemoryInfo(
                        id=agent_dir.name,
                        name=f"{agent_dir.name} Memory",
                        is_global=False,
                        agent_id=agent_dir.name,
                        exists=exists,
                        char_count=chars,
                    )
                )

    return memories


@router.get("/memory/{memory_id}")
async def get_memory_content(memory_id: str) -> MemoryContent:
    """Get memory content."""
    memory_path = get_memory_path(memory_id)

    if not memory_path.exists():
        return MemoryContent(id=memory_id, content="", exists=False)

    content = memory_path.read_text()
    return MemoryContent(id=memory_id, content=content, exists=True)


@router.put("/memory/{memory_id}")
async def update_memory(memory_id: str, request: UpdateMemoryRequest) -> dict:
    """Update memory content."""
    memory_path = get_memory_path(memory_id)

    # Ensure directory exists
    memory_path.parent.mkdir(parents=True, exist_ok=True)

    # Write content
    memory_path.write_text(request.content)

    return {
        "status": "success",
        "message": f"Memory {memory_id} updated",
        "char_count": len(request.content),
    }


@router.get("/memory/{memory_id}/daily-logs")
async def get_daily_logs(memory_id: str, days: int = 7) -> list[DailyLogInfo]:
    """Get daily logs."""
    memory_dir = get_memory_dir()
    logs = []

    # Get daily logs directory
    daily_dir = memory_dir / "daily"
    if not daily_dir.exists():
        return logs

    # Get logs from last N days
    today = datetime.now().date
    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        log_file = daily_dir / f"{date_str}.md"

        if log_file.exists():
            content = log_file.read_text()
            logs.append(
                DailyLogInfo(
                    date=date_str,
                    content=content,
                    char_count=len(content),
                )
            )

    return logs


@router.get("/memory/{memory_id}/stats")
async def get_memory_stats(memory_id: str) -> MemoryStats:
    """Get memory statistics."""
    memory_path = get_memory_path(memory_id)

    long_term_exists = memory_path.exists()
    long_term_chars = len(memory_path.read_text()) if long_term_exists else 0

    # Count daily logs
    memory_dir = get_memory_dir()
    daily_dir = memory_dir / "daily"
    daily_logs_count = 0
    oldest_log = None
    newest_log = None

    if daily_dir.exists():
        log_files = sorted(daily_dir.glob("*.md"))
        daily_logs_count = len(log_files)
        if log_files:
            oldest_log = log_files[0].stem
            newest_log = log_files[-1].stem

    return MemoryStats(
        long_term_exists=long_term_exists,
        long_term_chars=long_term_chars,
        daily_logs_count=daily_logs_count,
        oldest_log=oldest_log,
        newest_log=newest_log,
    )


@router.post("/memory/search")
async def search_memory(request: SearchRequest) -> SearchResponse:
    """Search memory content."""
    results = []
    memory_dir = get_memory_dir()

    if not memory_dir.exists():
        return SearchResponse(results=results)

    keyword = request.keyword.lower()
    target_id = request.memory_id

    # Search in memory files
    for md_file in memory_dir.glob("**/*.md"):
        if target_id and target_id not in str(md_file):
            continue

        try:
            content = md_file.read_text()
            lines = content.split("\n")
            matches = []

            for i, line in enumerate(lines):
                if keyword in line.lower():
                    # Get context around match
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    context = "\n".join(lines[start:end])
                    matches.append(context)

            if matches:
                results.append(
                    SearchMatch(
                        source=str(md_file.relative_to(memory_dir)),
                        matches=matches[:5],
                    )
                )
        except Exception as e:
            logger.warning(f"Error searching {md_file}: {e}")

    return SearchResponse(results=results)
