"""Multi-Agent system for AnyClaw.

This module implements OpenClaw-style multi-agent support with:
- Multiple independent agents
- Independent workspaces per agent
- Independent identity per agent
- Independent tool catalog per agent
"""

from anyclaw.agents.identity import IdentityManager
from anyclaw.agents.manager import AgentManager


__all__ = [
    "IdentityManager",
    "AgentManager",
]
