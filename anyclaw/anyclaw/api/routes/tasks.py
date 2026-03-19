"""Scheduled tasks management endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from anyclaw.api.deps import get_serve_manager

router = APIRouter()


@router.get("/tasks")
async def list_tasks():
    """List all scheduled tasks.

    Returns:
        List of tasks with schedule and status
    """
    # TODO: Get tasks from CronService
    return {
        "tasks": [
            {
                "id": "task_1",
                "name": "Example Task",
                "schedule": "0 * * * *",  # Every hour
                "enabled": True,
                "next_run": "2026-03-20T05:00:00Z",
            }
        ]
    }


@router.post("/tasks")
async def create_task():
    """Create a new scheduled task.

    Returns:
        Created task details
    """
    # TODO: Create task in CronService
    return {"status": "ok", "message": "Task created"}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a scheduled task.

    Args:
        task_id: Task ID

    Returns:
        Success message
    """
    # TODO: Delete task in CronService
    return {"status": "ok", "message": f"Task {task_id} deleted"}
