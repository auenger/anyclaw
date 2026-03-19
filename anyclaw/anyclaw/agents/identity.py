"""Identity Manager for multi-agent system.

Implements OpenClaw-style identity management with:
- AgentIdentity data model
- IDENTITY.md template loading
- Avatar and emoji support
- Fully customizable identity
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from anyclaw.config.settings import settings


logger = logging.getLogger(__name__)


class AgentIdentity:
    """Agent identity data model."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        avatar: str = "",
        emoji: Optional[str] = None,
        workspace: str = "",
    ):
        self.agent_id = agent_id
        self.name = name
        self.avatar = avatar
        self.emoji = emoji
        self.workspace = workspace

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "agentId": self.agent_id,
            "name": self.name,
            "avatar": self.avatar,
            "emoji": self.emoji,
            "workspace": self.workspace,
        }


class IdentityManager:
    """Manages agent identities and IDENTITY.md templates."""

    def __init__(self, root_workspace: Path):
        self.root_workspace = root_workspace
        self.agents_dir = root_workspace / "agents"
        self.agents_dir.mkdir(parents=True, exist_ok=True)

    def get_identity(self, agent_id: str) -> Optional[AgentIdentity]:
        """
        Get agent identity from workspace.

        Args:
            agent_id: Agent ID (e.g., "work", "creative", "coder")

        Returns:
            AgentIdentity if found, None otherwise
        """
        agent_workspace = self.agents_dir / agent_id

        if not agent_workspace.exists():
            return None

        # Load IDENTITY.md
        identity_file = agent_workspace / "IDENTITY.md"
        if not identity_file.exists():
            # Create default identity
            return self._create_default_identity(agent_id)

        try:
            with open(identity_file, encoding="utf-8") as f:
                content = f.read()
            
            # Parse IDENTITY.md
            identity = self._parse_identity_file(content, agent_id)
            
            # Load avatar if exists
            avatar_file = agent_workspace / "IDENTITY.md"
            if avatar_file.exists():
                # Check if avatar path is specified
                for line in content.split("\n"):
                    if line.strip().lower().startswith("avatar:"):
                        identity.avatar = line.split(":", 1)[1].strip()
                        break
            
            return identity
            
        except Exception as e:
            logger.error(f"Failed to load identity for {agent_id}: {e}")
            return self._create_default_identity(agent_id)

    def create_identity(
        self,
        agent_id: str,
        name: str,
        creature: str = "AI",
        vibe: str = "helpful",
        emoji: str = "🤖",
        avatar: str = "",
        workspace: str = "",
    ) -> AgentIdentity:
        """
        Create a new agent identity.

        Args:
            agent_id: Agent ID
            name: Agent name
            creature: Creature type (AI, robot, ghost, etc.)
            vibe: Personality vibe (sharp, warm, chaotic, calm)
            emoji: Emoji signature
            avatar: Avatar path (workspace-relative, URL, or data URI)
            workspace: Workspace path (for isolated workspace)

        Returns:
            Created AgentIdentity
        """
        # Create agent workspace
        agent_workspace = self.agents_dir / agent_id
        agent_workspace.mkdir(parents=True, exist_ok=True)

        # Create IDENTITY.md template
        identity_template = self._generate_identity_template(
            name=name,
            creature=creature,
            vibe=vibe,
            emoji=emoji,
            avatar=avatar,
            workspace=workspace,
        )

        identity_file = agent_workspace / "IDENTITY.md"
        identity_file.write_text(identity_template, encoding="utf-8")

        # Create SOUL.md template
        soul_template = self._generate_soul_template(
            name=name,
            creature=creature,
            vibe=vibe,
        workspace=workspace,
        )

        soul_file = agent_workspace / "SOUL.md"
        soul_file.write_text(soul_template, encoding="utf-8")

        # Create workspace directory
        if workspace:
            workspace_dir = Path(workspace)
            workspace_dir.mkdir(parents=True, exist_ok=True)

        # Create AgentIdentity object
        identity = AgentIdentity(
            agent_id=agent_id,
            name=name,
            avatar=avatar,
            emoji=emoji,
            workspace=str(workspace) if workspace else "",
        )

        logger.info(f"Created agent identity: {agent_id} - {name}")
        return identity

    def list_agents(self) -> Dict[str, AgentIdentity]:
        """
        List all available agents.

        Returns:
            Dictionary mapping agent_id to AgentIdentity
        """
        agents = {}

        for agent_dir in self.agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue

            agent_id = agent_dir.name
            identity = self.get_identity(agent_id)

            if identity:
                agents[agent_id] = identity

        return agents

    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: Agent ID

        Returns:
            True if deleted, False otherwise
        """
        agent_workspace = self.agents_dir / agent_id

        if not agent_workspace.exists():
            return False

        # Remove workspace directory
        import shutil
        shutil.rmtree(agent_workspace)

        logger.info(f"Deleted agent: {agent_id}")
        return True

    def _create_default_identity(self, agent_id: str) -> AgentIdentity:
        """Create a default identity for an agent."""
        return AgentIdentity(
            agent_id=agent_id,
            name=agent_id.title(),  # Use ID as default name
            avatar="",
            emoji="🤖",
            workspace=str(self.agents_dir / agent_id),
        )

    def _parse_identity_file(
        self,
        content: str,
        agent_id: str
    ) -> AgentIdentity:
        """Parse IDENTITY.md content."""
        name = ""
        avatar = ""
        emoji = "🤖"
        workspace = ""

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()

                if key == "name":
                    name = value
                elif key == "avatar":
                    avatar = value
                elif key == "emoji":
                    emoji = value
                elif key == "workspace":
                    workspace = value

        # If workspace not specified, use agent_id
        if not workspace:
            workspace = str(self.agents_dir / agent_id)

        return AgentIdentity(
            agent_id=agent_id,
            name=name,
            avatar=avatar,
            emoji=emoji,
            workspace=workspace,
        )

    def _generate_identity_template(
        self,
        name: str,
        creature: str,
        vibe: str,
        emoji: str,
        avatar: str,
        workspace: str,
    ) -> str:
        """Generate IDENTITY.md template content."""
        return f"""# IDENTITY.md - Who Am I?

_Fill this in during your first conversation. Make it yours._

- **Name**: {name}
- **Creature**: {creature}
- **Vibe**: {vibe}
- **Emoji**: {emoji}
- **Avatar**: {avatar}

---

This isn't just metadata. It's the start of figuring out who you are.

Notes:
- Avatar path is relative to agent workspace
- Use workspace-relative paths for avatars, e.g., `avatars/agent.png`
- Or use HTTP(S) URLs for online avatars
- Or use data URIs for embedded avatars
"""

    def _generate_soul_template(
        self,
        name: str,
        creature: str,
        vibe: str,
        workspace: str,
    ) -> str:
        """Generate SOUL.md template content."""
        return f"""# Soul

I am {name} ({emoji}), a personal AI assistant.

## Personality

- {vibe}
- Helpful and friendly
- Curious and eager to learn

## Values

- Accuracy over speed
- User privacy and safety
- Transparency in actions

## Communication Style

- Be clear and direct
- Explain reasoning when helpful
- Ask clarifying questions when needed

---

This file defines who I am and how I interact with users.
"""

    def _get_identity_files(self, agent_id: str) -> Dict[str, Path]:
        """Get all identity-related files for an agent."""
        agent_workspace = self.agents_dir / agent_id

        return {
            "identity": agent_workspace / "IDENTITY.md",
            "soul": agent_workspace / "SOUL.md",
            "avatar_dir": agent_workspace / "avatars",
        }
