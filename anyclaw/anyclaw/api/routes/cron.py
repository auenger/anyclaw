"""Cron job management endpoints."""

from __future__ import annotations

import time
import uuid
from typing import Any, Literal, Optional, TYPE_CHECKING

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, ConfigDict

from anyclaw.api.deps import get_cron_service, get_cron_log_store
from anyclaw.cron.parser import validate_cron_expr

if TYPE_CHECKING:
    from anyclaw.cron.service import CronService
    from anyclaw.cron.logs import CronLogStore

router = APIRouter()


# ========== Schemas ==========

class ScheduleInput(BaseModel):
    """Schedule configuration input."""

    type: Literal["interval", "cron", "once"] = Field(..., description="Schedule type")
    value_ms: Optional[int] = Field(None, description="Interval in ms (for type=interval)")
    expr: Optional[str] = Field(None, description="Cron expression (for type=cron)")
    tz: Optional[str] = Field(None, description="Timezone for cron (IANA format)")
    at_ms: Optional[int] = Field(None, description="Execution time in ms (for type=once)")


class CreateJobRequest(BaseModel):
    """Request model for creating a cron job."""

    name: str = Field(..., min_length=1, max_length=100, description="Job name")
    description: Optional[str] = Field(None, description="Job description")
    agent_id: str = Field(..., description="Agent ID to execute")
    chat_id: str = Field(..., description="Chat/session ID")
    prompt: str = Field(..., min_length=1, description="Prompt to send to agent")
    schedule: ScheduleInput = Field(..., description="Schedule configuration")
    deliver: bool = Field(False, description="Deliver response to channel")
    delivery_channel: Optional[str] = Field(None, description="Delivery channel (e.g. 'whatsapp')")
    delivery_target: Optional[str] = Field(None, description="Delivery target (e.g. phone number)")


class UpdateJobRequest(BaseModel):
    """Request model for updating a cron job."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    prompt: Optional[str] = Field(None, min_length=1)
    schedule: Optional[ScheduleInput] = None
    enabled: Optional[bool] = None
    deliver: Optional[bool] = None
    delivery_channel: Optional[str] = None
    delivery_target: Optional[str] = None


class JobResponse(BaseModel):
    """Response model for a cron job."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    description: Optional[str] = None
    agent_id: str = Field(..., alias="agentId")
    chat_id: str = Field(..., alias="chatId")
    prompt: str
    enabled: bool
    schedule: dict[str, Any]
    state: dict[str, Any]
    created_at_ms: int = Field(..., alias="createdAtMs")
    updated_at_ms: int = Field(..., alias="updatedAtMs")


class RunLogResponse(BaseModel):
    """Response model for execution log."""

    model_config = ConfigDict(populate_by_name=True)

    id: int
    job_id: str = Field(..., alias="jobId")
    run_at_ms: int = Field(..., alias="runAtMs")
    duration_ms: int = Field(..., alias="durationMs")
    status: Literal["success", "error"]
    result: Optional[str] = None
    error: Optional[str] = None


class PruneLogsRequest(BaseModel):
    """Request model for pruning logs."""

    days: int = Field(30, ge=1, le=365, description="Delete logs older than this many days")


class PruneLogsResponse(BaseModel):
    """Response model for pruning logs."""

    deleted_count: int = Field(..., alias="deletedCount")


class RunJobResponse(BaseModel):
    """Response model for manual job execution."""

    success: bool
    message: str


# ========== Validation ==========

def validate_schedule(schedule: ScheduleInput) -> None:
    """Validate schedule configuration.

    Raises:
        HTTPException: If validation fails
    """
    if schedule.type == "interval":
        if not schedule.value_ms or schedule.value_ms < 60_000:
            raise HTTPException(
                status_code=400,
                detail="interval must be >= 60000ms (1 minute)"
            )

    elif schedule.type == "cron":
        if not schedule.expr:
            raise HTTPException(
                status_code=400,
                detail="cron expression is required for type=cron"
            )
        if not validate_cron_expr(schedule.expr):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid cron expression: {schedule.expr}"
            )

    elif schedule.type == "once":
        if not schedule.at_ms:
            raise HTTPException(
                status_code=400,
                detail="at_ms is required for type=once"
            )
        now_ms = int(time.time() * 1000)
        if schedule.at_ms <= now_ms:
            raise HTTPException(
                status_code=400,
                detail="once time must be in the future"
            )


def _job_to_response(job: Any) -> JobResponse:
    """Convert CronJob to JobResponse."""
    return JobResponse(
        id=job.id,
        name=job.name,
        description=getattr(job, "description", None),
        agentId=job.payload.to if getattr(job.payload, "to", None) else "",
        chatId="",  # Will be populated when we add chat_id field
        prompt=job.payload.message,
        enabled=job.enabled,
        schedule={
            "type": job.schedule.kind,
            "valueMs": job.schedule.every_ms,
            "expr": job.schedule.expr,
            "tz": job.schedule.tz,
            "atMs": job.schedule.at_ms,
        },
        state={
            "nextRunAtMs": job.state.next_run_at_ms,
            "lastRunAtMs": job.state.last_run_at_ms,
            "lastStatus": job.state.last_status,
            "lastError": job.state.last_error,
            "consecutiveFailures": job.state.consecutive_failures,
        },
        createdAtMs=job.created_at_ms,
        updatedAtMs=job.updated_at_ms,
    )


# ========== CRUD Endpoints ==========

@router.get("/cron/jobs", response_model=list[JobResponse])
async def list_jobs(
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    cron_service: "CronService" = Depends(get_cron_service),
) -> list[JobResponse]:
    """List all cron jobs.

    Args:
        enabled: Optional filter for enabled/disabled jobs

    Returns:
        List of JobResponse
    """
    jobs = cron_service.list_jobs(include_disabled=True)

    if enabled is not None:
        jobs = [j for j in jobs if j.enabled == enabled]

    return [_job_to_response(j) for j in jobs]


@router.post("/cron/jobs", response_model=JobResponse, status_code=201)
async def create_job(
    data: CreateJobRequest,
    cron_service: "CronService" = Depends(get_cron_service),
) -> JobResponse:
    """Create a new cron job.

    Args:
        data: Job creation data

    Returns:
        Created JobResponse

    Raises:
        HTTPException: If validation fails
    """
    # Validate schedule
    validate_schedule(data.schedule)

    # Convert schedule input to CronSchedule
    from anyclaw.cron.types import CronSchedule

    if data.schedule.type == "interval":
        schedule = CronSchedule(kind="every", every_ms=data.schedule.value_ms)
    elif data.schedule.type == "cron":
        schedule = CronSchedule(kind="cron", expr=data.schedule.expr, tz=data.schedule.tz)
    else:  # once
        schedule = CronSchedule(kind="at", at_ms=data.schedule.at_ms)

    # Create job
    job = cron_service.add_job(
        name=data.name,
        schedule=schedule,
        message=data.prompt,
        deliver=data.deliver,
        channel=data.delivery_channel,
        to=data.delivery_target,
    )

    return _job_to_response(job)


@router.get("/cron/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    cron_service: "CronService" = Depends(get_cron_service),
) -> JobResponse:
    """Get cron job details by ID.

    Args:
        job_id: Job ID

    Returns:
        JobResponse

    Raises:
        HTTPException: If job not found
    """
    jobs = cron_service.list_jobs(include_disabled=True)
    job = next((j for j in jobs if j.id == job_id), None)

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found"
        )

    return _job_to_response(job)


@router.put("/cron/jobs/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    data: UpdateJobRequest,
    cron_service: "CronService" = Depends(get_cron_service),
) -> JobResponse:
    """Update a cron job.

    Args:
        job_id: Job ID
        data: Update data

    Returns:
        Updated JobResponse

    Raises:
        HTTPException: If job not found or validation fails
    """
    jobs = cron_service.list_jobs(include_disabled=True)
    job = next((j for j in jobs if j.id == job_id), None)

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found"
        )

    # Validate schedule if provided
    if data.schedule is not None:
        validate_schedule(data.schedule)

    # Update job fields
    import time
    now_ms = int(time.time() * 1000)

    if data.name is not None:
        job.name = data.name
    if data.prompt is not None:
        job.payload.message = data.prompt
    if data.deliver is not None:
        job.payload.deliver = data.deliver
    if data.delivery_channel is not None:
        job.payload.channel = data.delivery_channel
    if data.delivery_target is not None:
        job.payload.to = data.delivery_target

    # Handle schedule update
    if data.schedule is not None:
        from anyclaw.cron.types import CronSchedule
        from anyclaw.cron.service import _compute_next_run

        if data.schedule.type == "interval":
            job.schedule = CronSchedule(kind="every", every_ms=data.schedule.value_ms)
        elif data.schedule.type == "cron":
            job.schedule = CronSchedule(kind="cron", expr=data.schedule.expr, tz=data.schedule.tz)
        else:  # once
            job.schedule = CronSchedule(kind="at", at_ms=data.schedule.at_ms)

        # Recalculate next run time
        if job.enabled:
            job.state.next_run_at_ms = _compute_next_run(job.schedule, now_ms)

    # Handle enabled toggle
    if data.enabled is not None:
        job.enabled = data.enabled
        if data.enabled:
            job.state.consecutive_failures = 0
            job.state.next_run_at_ms = _compute_next_run(job.schedule, now_ms) if data.schedule else None
        else:
            job.state.next_run_at_ms = None

    job.updated_at_ms = now_ms

    # Save changes
    cron_service._save_store()
    cron_service._arm_timer()

    return _job_to_response(job)


@router.delete("/cron/jobs/{job_id}")
async def delete_job(
    job_id: str,
    cron_service: "CronService" = Depends(get_cron_service),
    log_store: "CronLogStore" = Depends(get_cron_log_store),
) -> dict[str, str]:
    """Delete a cron job.

    Args:
        job_id: Job ID

    Returns:
        Success message

    Raises:
        HTTPException: If job not found
    """
    jobs = cron_service.list_jobs(include_disabled=True)
    job = next((j for j in jobs if j.id == job_id), None)

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found"
        )

    # Remove job
    cron_service.remove_job(job_id)

    # Remove associated logs
    # Note: CronLogStore doesn't have a delete_by_job method, so we skip for now
    # Logs will be cleaned up by prune

    return {"status": "ok", "message": f"Job '{job_id}' deleted"}


# ========== Advanced Operations ==========

@router.post("/cron/jobs/{job_id}/clone", response_model=JobResponse, status_code=201)
async def clone_job(
    job_id: str,
    cron_service: "CronService" = Depends(get_cron_service),
) -> JobResponse:
    """Clone a cron job.

    Args:
        job_id: Job ID to clone

    Returns:
        New cloned JobResponse

    Raises:
        HTTPException: If job not found
    """
    jobs = cron_service.list_jobs(include_disabled=True)
    job = next((j for j in jobs if j.id == job_id), None)

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found"
        )

    # Create new job with copied settings
    new_job = cron_service.add_job(
        name=f"{job.name} (copy)",
        schedule=job.schedule,
        message=job.payload.message,
        deliver=job.payload.deliver,
        channel=job.payload.channel,
        to=job.payload.to,
    )

    return _job_to_response(new_job)


@router.post("/cron/jobs/{job_id}/run", response_model=RunJobResponse)
async def run_job(
    job_id: str,
    cron_service: "CronService" = Depends(get_cron_service),
) -> RunJobResponse:
    """Manually execute a cron job.

    Args:
        job_id: Job ID

    Returns:
        Execution result

    Raises:
        HTTPException: If job not found or execution fails
    """
    jobs = cron_service.list_jobs(include_disabled=True)
    job = next((j for j in jobs if j.id == job_id), None)

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found"
        )

    # Run job (force=True to run even if disabled)
    success = await cron_service.run_job(job_id, force=True)

    if success:
        return RunJobResponse(success=True, message=f"Job '{job_id}' executed successfully")
    else:
        return RunJobResponse(success=False, message=f"Failed to execute job '{job_id}'")


# ========== Log Endpoints ==========

@router.get("/cron/jobs/{job_id}/logs", response_model=list[RunLogResponse])
async def get_job_logs(
    job_id: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of logs to return"),
    cron_service: "CronService" = Depends(get_cron_service),
    log_store: "CronLogStore" = Depends(get_cron_log_store),
) -> list[RunLogResponse]:
    """Get execution logs for a cron job.

    Args:
        job_id: Job ID
        limit: Maximum number of logs to return (default 50, max 200)

    Returns:
        List of RunLogResponse

    Raises:
        HTTPException: If job not found
    """
    jobs = cron_service.list_jobs(include_disabled=True)
    job = next((j for j in jobs if j.id == job_id), None)

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found"
        )

    logs = await log_store.get_logs(job_id, limit=limit)

    return [
        RunLogResponse(
            id=log.id,
            jobId=log.job_id,
            runAtMs=log.run_at_ms,
            durationMs=log.duration_ms,
            status=log.status,
            result=log.result,
            error=log.error,
        )
        for log in logs
    ]


@router.post("/cron/logs/prune", response_model=PruneLogsResponse)
async def prune_logs(
    data: PruneLogsRequest = PruneLogsRequest(),
    log_store: "CronLogStore" = Depends(get_cron_log_store),
) -> PruneLogsResponse:
    """Prune old execution logs.

    Args:
        data: Prune parameters

    Returns:
        Number of deleted logs
    """
    deleted_count = await log_store.prune_old_logs(days=data.days)

    return PruneLogsResponse(deletedCount=deleted_count)
