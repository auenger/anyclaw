"""Dependency injection for API routes."""

from __future__ import annotations

from typing import Generator, Optional

from anyclaw.core.serve import ServeManager
from anyclaw.bus.queue import MessageBus

# Global instances (set by sidecar_cmd.py)
_serve_manager: Optional[ServeManager] = None


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


def get_message_bus() -> MessageBus:
    """Get the global MessageBus instance."""
    return get_serve_manager().bus
