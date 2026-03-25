"""Cron types."""

import logging
from dataclasses import dataclass, field
from typing import Literal, Optional


logger = logging.getLogger(__name__)


@dataclass
class CronSchedule:
    """Schedule definition for a cron job."""
    kind: Literal["at", "every", "cron"]
    # For "at": timestamp in ms
    at_ms: Optional[int] = None
    # For "every": interval in ms
    every_ms: Optional[int] = None
    # For "cron": cron expression (e.g. "0 9 * * *")
    expr: Optional[str] = None
    # Timezone for cron expressions
    tz: Optional[str] = None


@dataclass
class CronPayload:
    """What to do when a job runs."""
    kind: Literal["system_event", "agent_turn"] = "agent_turn"
    message: str = ""
    # Deliver response to channel
    deliver: bool = False
    channel: Optional[str] = None  # e.g. "whatsapp"
    to: Optional[str] = None  # e.g. phone number


@dataclass
class CronJobState:
    """Runtime state of a job."""
    next_run_at_ms: Optional[int] = None
    last_run_at_ms: Optional[int] = None
    last_status: Optional[Literal["ok", "error", "skipped"]] = None
    last_error: Optional[str] = None
    # Resilience fields
    consecutive_failures: int = 0
    running_since_ms: Optional[int] = None


@dataclass
class CronRunLog:
    """Execution log record for a cron job."""
    id: int
    job_id: str
    run_at_ms: int
    duration_ms: int
    status: Literal["success", "error"]
    result: Optional[str] = None
    error: Optional[str] = None


@dataclass
class CronPayload:
    """What to do when a job runs (alias for compatibility)."""
    kind: Literal["system_event", "agent_turn"] = "agent_turn"
    message: str = ""
    deliver: bool = False
    channel: Optional[str] = None
    to: Optional[str] = None


@dataclass
class CronJob:
    """A scheduled job."""
    id: str
    name: str
    enabled: bool = True
    schedule: CronSchedule = field(default_factory=lambda: CronSchedule(kind="every"))
    payload: CronPayload = field(default_factory=CronPayload)
    state: CronJobState = field(default_factory=CronJobState)
    created_at_ms: int = 0
    updated_at_ms: int = 0
    delete_after_run: bool = False


@dataclass
class CronStore:
    """Persistent store for cron jobs."""
    version: int = 1
    jobs: list[CronJob] = field(default_factory=list)
