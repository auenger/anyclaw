"""Spawn tool for creating background subagents."""

import logging
import uuid
from typing import TYPE_CHECKING, Any, Optional

from anyclaw.tools.base import Tool


logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from anyclaw.agent.subagent import SubagentManager


class SpawnTool(Tool):
    """Tool to spawn a subagent for background task execution."""

    def __init__(self, manager: "SubagentManager"):
        self._manager = manager
        self._origin_channel = "cli"
        self._origin_chat_id = "direct"
        self._session_key = "cli:direct"

    def set_context(self, channel: str, chat_id: str) -> None:
        """Set origin context for subagent announcements."""
        self._origin_channel = channel
        self._origin_chat_id = chat_id
        self._session_key = f"{channel}:{chat_id}"

    @property
    def name(self) -> str:
        return "spawn"

    @property
    def description(self) -> str:
        return (
            "Spawn a subagent to handle a task in background. "
            "Use this for complex or time-consuming tasks that can run independently. "
            "The subagent will complete task and report back when done."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The task for subagent to complete",
                },
                "label": {
                    "type": "string",
                    "description": "Optional short label for task (for display)",
                },
            },
            "required": ["task"],
        }

    async def execute(self, task: str, label: Optional[str] = None, **kwargs: Any) -> str:
        """Spawn a subagent to execute given task."""
        return await self._manager.spawn(
            task=task,
            label=label,
            origin_channel=self._origin_channel,
            origin_chat_id=self._origin_chat_id,
            session_key=self._session_key,
        )
