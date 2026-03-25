"""API routes module."""

from anyclaw.api.routes.health import router as health_router
from anyclaw.api.routes.agents import router as agents_router
from anyclaw.api.routes.messages import router as messages_router
from anyclaw.api.routes.skills import router as skills_router
from anyclaw.api.routes.tasks import router as tasks_router
from anyclaw.api.routes.memory import router as memory_router
from anyclaw.api.routes.logs import router as logs_router

__all__ = [
    "health_router",
    "agents_router",
    "messages_router",
    "skills_router",
    "tasks_router",
    "memory_router",
    "logs_router",
]
