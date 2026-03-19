"""Skills management endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from anyclaw.api.deps import get_serve_manager

router = APIRouter()


@router.get("/skills")
async def list_skills():
    """List all available skills.

    Returns:
        List of skills with metadata
    """
    # TODO: Get skills from SkillLoader
    return {
        "skills": [
            {
                "name": "example-skill",
                "description": "Example skill for demonstration",
                "version": "0.1.0",
                "enabled": True,
            }
        ]
    }


@router.get("/skills/{skill_name}")
async def get_skill(skill_name: str):
    """Get skill details.

    Args:
        skill_name: Skill name

    Returns:
        Skill details
    """
    # TODO: Get skill from SkillLoader
    return {
        "name": skill_name,
        "description": f"Details for {skill_name}",
        "version": "0.1.0",
    }


@router.post("/skills/{skill_name}/enable")
async def enable_skill(skill_name: str):
    """Enable a skill.

    Args:
        skill_name: Skill name

    Returns:
        Success message
    """
    # TODO: Enable skill in SkillLoader
    return {"status": "ok", "message": f"Skill {skill_name} enabled"}


@router.post("/skills/{skill_name}/disable")
async def disable_skill(skill_name: str):
    """Disable a skill.

    Args:
        skill_name: Skill name

    Returns:
        Success message
    """
    # TODO: Disable skill in SkillLoader
    return {"status": "ok", "message": f"Skill {skill_name} disabled"}
