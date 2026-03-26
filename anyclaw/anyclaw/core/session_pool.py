"""Session-level AgentLoop pool for concurrent message processing."""

from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Optional

from anyclaw.agent.loop import AgentLoop

if TYPE_CHECKING:
    from anyclaw.session.manager import SessionManager

logger = logging.getLogger(__name__)


class SessionAgentPool:
    """
    Pool of session-level AgentLoop instances.

    Each session gets its own AgentLoop instance for complete isolation.
    The pool manages creation, reuse, and cleanup of AgentLoop instances.

    IMPORTANT: All AgentLoop instances share the same SessionManager to ensure
    session data consistency across the pool and the main ServeManager.
    """

    def __init__(
        self,
        workspace: Path,
        max_pool_size: int = 10,
        idle_timeout: float = 300.0,
        session_manager: Optional["SessionManager"] = None,  # 共享的 SessionManager
    ):
        """
        Initialize the session agent pool.

        Args:
            workspace: Workspace path for AgentLoop instances
            max_pool_size: Maximum number of AgentLoop instances in pool
            idle_timeout: Idle timeout in seconds for cleanup
            session_manager: Shared SessionManager instance for all AgentLoops
        """
        self.workspace = workspace
        self.max_pool_size = max_pool_size
        self.idle_timeout = idle_timeout
        self._shared_session_manager = session_manager  # 共享的 SessionManager

        # Pool storage: session_key -> (AgentLoop, last_access_time)
        self._pool: Dict[str, tuple[AgentLoop, float]] = {}
        self._lock = asyncio.Lock()

        logger.info(
            f"SessionAgentPool initialized: workspace={workspace}, "
            f"max_size={max_pool_size}, idle_timeout={idle_timeout}s, "
            f"shared_session_manager={session_manager is not None}"
        )

    def get_or_create(self, session_key: str, workspace: Optional[Path] = None) -> AgentLoop:
        """
        Get or create an AgentLoop for the given session.

        Args:
            session_key: Session identifier
            workspace: Optional workspace path (defaults to pool's default workspace)

        Returns:
            AgentLoop instance for the session
        """
        # Use provided workspace or default
        effective_workspace = workspace or self.workspace

        # Check if exists in pool
        if session_key in self._pool:
            agent, _ = self._pool[session_key]
            # Update last access time
            self._pool[session_key] = (agent, time.time())
            logger.debug(f"SessionAgentPool: Reused AgentLoop for {session_key}")
            return agent

        # Determine whether to use shared SessionManager
        # Only use shared SessionManager when using the default workspace
        # For agent-specific workspaces, let AgentLoop create its own SessionManager
        use_shared_session_manager = (
            self._shared_session_manager is not None
            and effective_workspace == self.workspace
        )

        if use_shared_session_manager:
            # Use shared SessionManager (for default workspace)
            logger.info(f"SessionAgentPool: Creating AgentLoop for {session_key} with workspace={effective_workspace} (shared SessionManager)")
            agent = AgentLoop(
                workspace=effective_workspace,
                enable_session_manager=True,
                enable_message_tool=True,
                enable_archive=True,
                session_manager=self._shared_session_manager,
            )
        else:
            # Let AgentLoop create its own SessionManager (for agent-specific workspace)
            logger.info(f"SessionAgentPool: Creating AgentLoop for {session_key} with workspace={effective_workspace} (dedicated SessionManager)")
            agent = AgentLoop(
                workspace=effective_workspace,
                enable_session_manager=True,
                enable_message_tool=True,
                enable_archive=True,
                session_manager=None,  # AgentLoop will create its own
            )

        # Set session key
        agent.set_session_key(session_key)

        # Store in pool
        self._pool[session_key] = (agent, time.time())

        return agent

    async def get_or_create_async(self, session_key: str, workspace: Optional[Path] = None) -> AgentLoop:
        """
        Async version of get_or_create with lock protection.

        Args:
            session_key: Session identifier
            workspace: Optional workspace path (defaults to pool's default workspace)

        Returns:
            AgentLoop instance for the session
        """
        async with self._lock:
            return self.get_or_create(session_key, workspace)

    def remove(self, session_key: str) -> bool:
        """
        Remove an AgentLoop from the pool.

        Args:
            session_key: Session identifier

        Returns:
            True if removed, False if not found
        """
        if session_key in self._pool:
            del self._pool[session_key]
            logger.info(f"SessionAgentPool: Removed AgentLoop for {session_key}")
            return True
        return False

    def clear(self) -> int:
        """
        Clear all AgentLoop instances from the pool.

        Returns:
            Number of instances removed
        """
        count = len(self._pool)
        self._pool.clear()
        logger.info(f"SessionAgentPool: Cleared {count} AgentLoop instances")
        return count

    def cleanup_idle(self) -> int:
        """
        Remove idle AgentLoop instances that exceeded idle_timeout.

        Returns:
            Number of instances removed
        """
        current_time = time.time()
        keys_to_remove = []

        for key, (_, last_access) in self._pool.items():
            if current_time - last_access > self.idle_timeout:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._pool[key]
            logger.info(f"SessionAgentPool: Cleaned up idle AgentLoop for {key}")

        return len(keys_to_remove)

    async def cleanup_idle_async(self) -> int:
        """
        Async version of cleanup_idle with lock protection.

        Returns:
            Number of instances removed
        """
        async with self._lock:
            return self.cleanup_idle()

    @property
    def size(self) -> int:
        """Current pool size."""
        return len(self._pool)

    @property
    def session_keys(self) -> list[str]:
        """List of session keys in pool."""
        return list(self._pool.keys())

    def get_stats(self) -> dict:
        """
        Get pool statistics.

        Returns:
            Dictionary with pool stats
        """
        current_time = time.time()
        active_count = 0
        idle_count = 0

        for _, (_, last_access) in self._pool.items():
            if current_time - last_access < 60:  # Active in last minute
                active_count += 1
            else:
                idle_count += 1

        return {
            "total": len(self._pool),
            "active": active_count,
            "idle": idle_count,
            "max_size": self.max_pool_size,
            "idle_timeout": self.idle_timeout,
        }
