"""Agent management endpoints."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from anyclaw.api.deps import get_serve_manager

router = APIRouter()


class AgentInfo(BaseModel):
    """Agent information."""

    id: str
    name: str
    model: str
    description: Optional[str] = None
    is_active: bool = True


@router.get("/agents", response_model=list[AgentInfo])
async def list_agents() -> list[AgentInfo]:
    """List all available agents.

    Returns:
        List of AgentInfo
    """
    manager = get_serve_manager()

    # TODO: Get agents from AgentManager
    # For now, return mock data based on config
    return [
        AgentInfo(
            id="default",
            name="Default Agent",
            model=manager.config.agent.model,
            description="Default AnyClaw agent",
        )
    ]


@router.get("/agents/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str) -> AgentInfo:
    """Get agent details by ID.

    Args:
        agent_id: Agent ID

    Returns:
        AgentInfo

    Raises:
        HTTPException: If agent not found
    """
    manager = get_serve_manager()

    # TODO: Get agent from AgentManager
    if agent_id == "default":
        return AgentInfo(
            id="default",
            name="Default Agent",
            model=manager.config.agent.model,
            description="Default AnyClaw agent",
        )

    raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")


@router.post("/agents/{agent_id}/activate")
async def activate_agent(agent_id: str) -> dict[str, str]:
    """Activate an agent.

    Args:
        agent_id: Agent ID

    Returns:
        Success message
    """
    # TODO: Activate agent in AgentManager
    return {"status": "ok", "message": f"Agent {agent_id} activated"}


@router.post("/agents/{agent_id}/deactivate")
async def deactivate_agent(agent_id: str) -> dict[str, str]:
    """Deactivate an agent.

    Args:
        agent_id: Agent ID

    Returns:
        Success message
    """
    # TODO: Deactivate agent in AgentManager
    return {"status": "ok", "message": f"Agent {agent_id} deactivated"}
