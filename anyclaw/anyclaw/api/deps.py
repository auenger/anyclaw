"""Dependency injection for API routes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from anyclaw.core.serve import ServeManager
from anyclaw.bus.queue import MessageBus

if TYPE_CHECKING:
    from anyclaw.agents.manager import AgentManager

# Global instances (set by sidecar_cmd.py)
_serve_manager: Optional[ServeManager] = None
_agent_manager: Optional["AgentManager"] = None


def set_serve_manager(manager: ServeManager) -> None:
    """Set the global ServeManager instance."""
    global _serve_manager
    _serve_manager = manager


def get_serve_manager() -> ServeManager:
    """Get the global ServeManager instance.

    Raises:
        RuntimeError: If ServeManager is not initialized
    """
    if _serve_manager is None:
        raise RuntimeError("ServeManager not initialized. Call set_serve_manager() first.")
    return _serve_manager


def set_agent_manager(manager: "AgentManager") -> None:
    """Set the global AgentManager instance."""
    global _agent_manager
    _agent_manager = manager


def get_agent_manager() -> "AgentManager":
    """Get the global AgentManager instance.

    Raises:
        RuntimeError: If AgentManager is not initialized
    """
    if _agent_manager is None:
        raise RuntimeError("AgentManager not initialized. Call set_agent_manager() first.")
    return _agent_manager


def get_message_bus() -> MessageBus:
    """Get the global MessageBus instance."""
    return get_serve_manager().bus
