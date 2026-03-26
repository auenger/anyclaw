"""Agent Manager for multi-agent system.

Implements OpenClaw-style agent management with:
- Multiple independent agents
- Independent workspaces per agent
- Independent tool catalog per agent
- Dynamic agent switching
"""

import asyncio
import json
import logging
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Any

from anyclaw.agents.identity import IdentityManager, AgentIdentity
from anyclaw.config.settings import settings


logger = logging.getLogger(__name__)


class AgentWorkspace:
    """Agent workspace management."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.files_dir = workspace_path / "files"
        self.skills_dir = workspace_path / "skills"
        self.config_dir = workspace_path / "config"

    def create(self) -> None:
        """Create workspace directories."""
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        """Check if workspace exists."""
        return self.workspace_path.exists()

    def get_path(self) -> Path:
        """Get workspace path."""
        return self.workspace_path

    def get_files_dir(self) -> Path:
        """Get files directory."""
        return self.files_dir

    def get_skills_dir(self) -> Path:
        """Get skills directory."""
        return self.skills_dir
    
    def get_config_dir(self) -> Path:
        """Get config directory."""
        return self.config_dir


class AgentToolCatalog:
    """Agent tool catalog management."""

    def __init__(self, catalog_file: Path):
        self.catalog_file = catalog_file
        self.catalog_file.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        """Load tool catalog."""
        if not self.catalog_file.exists():
            return {}

        try:
            with open(self.catalog_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load tool catalog: {e}")
            return {}

    def save(self, catalog: Dict[str, Any]) -> bool:
        """Save tool catalog."""
        try:
            with open(self.catalog_file, "w", encoding="utf-8") as f:
                json.dump(catalog, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save tool catalog: {e}")
            return False


class Agent:
    """Multi-agent instance."""

    def __init__(
        self,
        agent_id: str,
        identity: AgentIdentity,
        workspace: AgentWorkspace,
        tool_catalog: AgentToolCatalog,
        enabled: bool = True,
    ):
        self.agent_id = agent_id
        self.identity = identity
        self.workspace = workspace
        self.tool_catalog = tool_catalog
        self.enabled = enabled
        self._session_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        # Use id as fallback when name is empty
        display_name = self.identity.name or self.agent_id
        return {
            "id": self.agent_id,
            "name": display_name,
            "avatar": self.identity.avatar,
            "emoji": self.identity.emoji,
            "workspace": str(self.workspace.get_path()),
            "enabled": self.enabled,
            "sessionCount": self._session_count,
        }


class AgentManager:
    """Manages multiple agents with isolated workspaces."""

    def __init__(self, root_workspace: Path, identity_manager: IdentityManager):
        self.root_workspace = root_workspace
        self.agents_dir = root_workspace / "agents"
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.identity_manager = identity_manager
        self._agents: Dict[str, Agent] = {}
        self._default_agent_id: Optional[str] = None

    def create_agent(
        self,
        name: str,
        creature: str = "AI",
        vibe: str = "helpful",
        emoji: str = "🤖",
        avatar: str = "",
        workspace: str = "",
        enabled: bool = True,
    ) -> Optional[Agent]:
        """
        Create a new agent.

        Args:
            name: Agent name
            creature: Creature type (AI, robot, ghost, cat, dog...)
            vibe: Personality vibe (sharp, warm, chaotic, calm)
            emoji: Emoji signature
            avatar: Avatar path (workspace-relative, URL, or data URI)
            workspace: Workspace path (for isolated workspace)
            enabled: Whether agent is enabled

        Returns:
            Created Agent if successful, None otherwise
        """
        # Generate agent ID
        agent_id = name.lower().replace(" ", "_")

        # Check if agent already exists
        if self._agents.get(agent_id):
            logger.error(f"Agent {agent_id} already exists")
            return None

        # Create identity
        identity = self.identity_manager.create_identity(
            agent_id=agent_id,
            name=name,
            creature=creature,
            vibe=vibe,
            emoji=emoji,
            avatar=avatar,
            workspace=workspace,
        )

        if not identity:
            logger.error(f"Failed to create identity for {agent_id}")
            return None

        # Create workspace
        agent_workspace = AgentWorkspace(self.agents_dir / agent_id)

        if workspace:
            workspace_path = Path(workspace)
            if not workspace_path.is_absolute():
                workspace_path = self.agents_dir / agent_id / workspace

            agent_workspace = AgentWorkspace(workspace_path)
        else:
            agent_workspace.create()

        # Create tool catalog
        tool_catalog = AgentToolCatalog(agent_workspace.get_config_dir() / "tools.json")

        # Create agent
        agent = Agent(
            agent_id=agent_id,
            identity=identity,
            workspace=agent_workspace,
            tool_catalog=tool_catalog,
            enabled=enabled,
        )

        # Store agent
        self._agents[agent_id] = agent

        # Set as default if first agent
        if self._default_agent_id is None:
            self._default_agent_id = agent_id

        logger.info(f"Created agent: {agent_id} - {name}")
        return agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        return self._agents.get(agent_id)

    def get_default_agent(self) -> Optional[Agent]:
        """Get default agent."""
        if self._default_agent_id:
            return self._agents.get(self._default_agent_id)
        return None

    def set_default_agent(self, agent_id: str) -> bool:
        """Set default agent."""
        if agent_id not in self._agents:
            logger.error(f"Agent {agent_id} not found")
            return False

        self._default_agent_id = agent_id
        logger.info(f"Set default agent: {agent_id}")
        return True

    def list_agents(self, include_disabled: bool = False) -> List[Dict[str, Any]]:
        """List all agents."""
        agents = []

        for agent in self._agents.values():
            if include_disabled or agent.enabled:
                agents.append(agent.to_dict())

        return sorted(agents, key=lambda x: x.get("name", ""))

    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        if agent_id not in self._agents:
            logger.error(f"Agent {agent_id} not found")
            return False

        # Delete agent
        del self._agents[agent_id]

        # Delete identity
        if self.identity_manager:
            self.identity_manager.delete_agent(agent_id)

        # Delete workspace
        agent_workspace = self.agents_dir / agent_id
        if agent_workspace.exists():
            shutil.rmtree(agent_workspace)

        # Reset default if deleted agent was default
        if self._default_agent_id == agent_id:
            remaining = list(self._agents.keys())
            self._default_agent_id = remaining[0] if remaining else None

        logger.info(f"Deleted agent: {agent_id}")
        return True

    def enable_agent(self, agent_id: str, enabled: bool = True) -> bool:
        """Enable or disable an agent."""
        agent = self._agents.get(agent_id)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            return False

        agent.enabled = enabled

        logger.info(f"Agent {agent_id} {'enabled' if enabled else 'disabled'}")
        return True

    def switch_agent(self, agent_id: str) -> bool:
        """Switch to an agent (set as default)."""
        return self.set_default_agent(agent_id)

    def get_tools_catalog(self, agent_id: str) -> Dict[str, Any]:
        """Get tool catalog for an agent."""
        agent = self._agents.get(agent_id)
        if not agent:
            return {}

        return agent.tool_catalog.load()

    def update_tools_catalog(self, agent_id: str, catalog: Dict[str, Any]) -> bool:
        """Update tool catalog for an agent."""
        agent = self._agents.get(agent_id)
        if not agent:
            return False

        return agent.tool_catalog.save(catalog)

    def increment_session_count(self, agent_id: str) -> None:
        """Increment session count for an agent."""
        agent = self._agents.get(agent_id)
        if agent:
            agent._session_count += 1

    def get_status(self) -> Dict[str, Any]:
        """Get agent manager status."""
        return {
            "agentsCount": len(self._agents),
            "enabledAgentsCount": sum(1 for a in self._agents.values() if a.enabled),
            "defaultAgentId": self._default_agent_id,
            "defaultAgent": self.get_default_agent().to_dict() if self.get_default_agent() else None,
        }

    async def load_all_agents(self) -> List[Agent]:
        """Load all agents from disk.

        This includes:
        1. The root workspace as "default" agent
        2. All agents in the agents/ subdirectory
        """
        # First, register the root workspace as "default" agent
        root_identity = self.identity_manager.get_root_identity()
        root_workspace = AgentWorkspace(self.root_workspace)
        root_catalog = AgentToolCatalog(root_workspace.get_config_dir() / "tools.json")

        default_agent = Agent(
            agent_id="default",
            identity=root_identity,
            workspace=root_workspace,
            tool_catalog=root_catalog,
            enabled=True,
        )
        self._agents["default"] = default_agent
        self._default_agent_id = "default"
        logger.info("Registered root workspace as 'default' agent")

        # Then load additional agents from agents/ subdirectory
        identities = self.identity_manager.list_agents()

        for agent_id, identity in identities.items():
            # Skip if already exists (shouldn't happen, but safety check)
            if agent_id in self._agents:
                continue

            # Create workspace
            agent_workspace = AgentWorkspace(self.agents_dir / agent_id)

            if not agent_workspace.exists():
                continue

            # Create tool catalog
            tool_catalog = AgentToolCatalog(agent_workspace.get_config_dir() / "tools.json")

            # Create agent
            agent = Agent(
                agent_id=agent_id,
                identity=identity,
                workspace=agent_workspace,
                tool_catalog=tool_catalog,
                enabled=True,
            )

            self._agents[agent_id] = agent

        logger.info(f"Loaded {len(self._agents)} agents (1 default + {len(self._agents) - 1} additional)")

        return list(self._agents.values())
