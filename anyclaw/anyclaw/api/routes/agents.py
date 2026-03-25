"""Agent management endpoints."""

from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, ConfigDict

from anyclaw.api.deps import get_agent_manager

if TYPE_CHECKING:
    from anyclaw.agents.manager import AgentManager

router = APIRouter()


class AgentInfo(BaseModel):
    """Agent information response model."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    emoji: str = "🤖"
    avatar: str = ""
    enabled: bool = True
    workspace: Optional[str] = None
    session_count: int = Field(default=0, alias="sessionCount")


class CreateAgentRequest(BaseModel):
    """Request model for creating an agent."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Agent name",
    )
    creature: str = Field(
        default="AI",
        description="Creature type (AI, robot, ghost, cat, dog...)",
    )
    vibe: str = Field(
        default="helpful",
        description="Personality vibe (sharp, warm, chaotic, calm)",
    )
    emoji: str = Field(default="🤖", description="Emoji signature")
    avatar: str = Field(default="", description="Avatar path or URL")
    workspace: str = Field(
        default="", description="Workspace path (optional)"
    )


class UpdateAgentRequest(BaseModel):
    """Request model for updating an agent."""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    emoji: Optional[str] = None
    avatar: Optional[str] = None
    enabled: Optional[bool] = None


def _agent_to_info(agent_dict: dict[str, Any]) -> AgentInfo:
    """Convert agent dict to AgentInfo model."""
    return AgentInfo(
        id=agent_dict["id"],
        name=agent_dict["name"],
        emoji=agent_dict.get("emoji", "🤖"),
        avatar=agent_dict.get("avatar", ""),
        enabled=agent_dict.get("enabled", True),
        workspace=agent_dict.get("workspace"),
        sessionCount=agent_dict.get("sessionCount", 0),
    )


@router.get("/agents", response_model=list[AgentInfo])
async def list_agents(
    include_disabled: bool = Query(False, description="Include disabled agents"),
    manager: "AgentManager" = Depends(get_agent_manager),
) -> list[AgentInfo]:
    """List all available agents.

    Args:
        include_disabled: Whether to include disabled agents

    Returns:
        List of AgentInfo
    """
    agents = manager.list_agents(include_disabled=include_disabled)
    return [_agent_to_info(a) for a in agents]


@router.post("/agents", response_model=AgentInfo, status_code=201)
async def create_agent(
    data: CreateAgentRequest,
    manager: "AgentManager" = Depends(get_agent_manager),
) -> AgentInfo:
    """Create a new agent.

    Args:
        data: Agent creation data

    Returns:
        Created AgentInfo

    Raises:
        HTTPException: If creation fails
    """
    agent = manager.create_agent(
        name=data.name,
        creature=data.creature,
        vibe=data.vibe,
        emoji=data.emoji,
        avatar=data.avatar,
        workspace=data.workspace,
    )

    if not agent:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create agent '{data.name}'. Name may already exist.",
        )

    return _agent_to_info(agent.to_dict())


@router.get("/agents/{agent_id}", response_model=AgentInfo)
async def get_agent(
    agent_id: str,
    manager: "AgentManager" = Depends(get_agent_manager),
) -> AgentInfo:
    """Get agent details by ID.

    Args:
        agent_id: Agent ID

    Returns:
        AgentInfo

    Raises:
        HTTPException: If agent not found
    """
    agent = manager.get_agent(agent_id)

    if not agent:
        raise HTTPException(
            status_code=404, detail=f"Agent '{agent_id}' not found"
        )

    return _agent_to_info(agent.to_dict())


@router.patch("/agents/{agent_id}", response_model=AgentInfo)
async def update_agent(
    agent_id: str,
    data: UpdateAgentRequest,
    manager: "AgentManager" = Depends(get_agent_manager),
) -> AgentInfo:
    """Update an agent.

    Args:
        agent_id: Agent ID
        data: Update data

    Returns:
        Updated AgentInfo

    Raises:
        HTTPException: If agent not found or update fails
    """
    agent = manager.get_agent(agent_id)

    if not agent:
        raise HTTPException(
            status_code=404, detail=f"Agent '{agent_id}' not found"
        )

    # Update identity via IdentityManager
    if data.name is not None or data.emoji is not None or data.avatar is not None:
        identity_manager = manager.identity_manager
        updates = {}
        if data.name is not None:
            updates["name"] = data.name
        if data.emoji is not None:
            updates["emoji"] = data.emoji
        if data.avatar is not None:
            updates["avatar"] = data.avatar

        identity_manager.update_identity(agent_id, **updates)

    # Update enabled status
    if data.enabled is not None:
        manager.enable_agent(agent_id, data.enabled)

    # Refresh agent data
    agent = manager.get_agent(agent_id)
    return _agent_to_info(agent.to_dict())


@router.delete("/agents/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str,
    manager: "AgentManager" = Depends(get_agent_manager),
):
    """Delete an agent.

    Args:
        agent_id: Agent ID

    Raises:
        HTTPException: If agent not found or deletion fails
    """
    if not manager.get_agent(agent_id):
        raise HTTPException(
            status_code=404, detail=f"Agent '{agent_id}' not found"
        )

    success = manager.delete_agent(agent_id)
    if not success:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete agent '{agent_id}'"
        )


@router.post("/agents/{agent_id}/activate")
async def activate_agent(
    agent_id: str,
    manager: "AgentManager" = Depends(get_agent_manager),
) -> dict[str, str]:
    """Activate an agent (set as default).

    Args:
        agent_id: Agent ID

    Returns:
        Success message

    Raises:
        HTTPException: If agent not found
    """
    if not manager.get_agent(agent_id):
        raise HTTPException(
            status_code=404, detail=f"Agent '{agent_id}' not found"
        )

    success = manager.switch_agent(agent_id)
    if not success:
        raise HTTPException(
            status_code=500, detail=f"Failed to activate agent '{agent_id}'"
        )

    return {"status": "ok", "message": f"Agent '{agent_id}' activated as default"}


@router.post("/agents/{agent_id}/deactivate")
async def deactivate_agent(
    agent_id: str,
    manager: "AgentManager" = Depends(get_agent_manager),
) -> dict[str, str]:
    """Deactivate an agent (disable it).

    Args:
        agent_id: Agent ID

    Returns:
        Success message

    Raises:
        HTTPException: If agent not found
    """
    if not manager.get_agent(agent_id):
        raise HTTPException(
            status_code=404, detail=f"Agent '{agent_id}' not found"
        )

    success = manager.enable_agent(agent_id, enabled=False)
    if not success:
        raise HTTPException(
            status_code=500, detail=f"Failed to deactivate agent '{agent_id}'"
        )

    return {"status": "ok", "message": f"Agent '{agent_id}' deactivated"}


@router.get("/agents/status/summary")
async def get_agents_status(
    manager: "AgentManager" = Depends(get_agent_manager),
) -> dict[str, Any]:
    """Get agent manager status summary.

    Returns:
        Status summary including counts and default agent
    """
    return manager.get_status()
