"""Agent Command Handler - /agent for viewing and switching agents."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from anyclaw.commands.base import CommandHandler, CommandResult
from anyclaw.commands.context import CommandContext

if TYPE_CHECKING:
    from anyclaw.agents.manager import AgentManager


class AgentCommandHandler(CommandHandler):
    """Handle /agent command - view and switch agents.

    Usage:
        /agent              - Show current agent and available agents
        /agent <name>       - Switch to specified agent
    """

    @property
    def description(self) -> str:
        return "查看/切换 Agent"

    @property
    def aliases(self) -> list[str]:
        return ["agents"]

    async def execute(
        self,
        args: Optional[str],
        context: CommandContext,
    ) -> CommandResult:
        """Execute /agent command.

        Args:
            args: Optional agent name to switch to.
            context: Execution context.

        Returns:
            CommandResult with agent info or switch result.
        """
        # Get agent manager from context
        agent_manager: AgentManager | None = context.get("agent_manager")

        # Get current agent info
        current_agent = context.get("agent_id", "default")
        current_agent_name = context.get("agent_name", "Default")

        # No args - show current agent and available agents
        if not args or not args.strip():
            return self._show_agents(current_agent, current_agent_name, agent_manager)

        # Switch agent
        new_agent = args.strip()
        return await self._switch_agent(new_agent, current_agent, agent_manager, context)

    def _show_agents(
        self,
        current: str,
        current_name: str,
        agent_manager: AgentManager | None,
    ) -> CommandResult:
        """Show current agent and available agents.

        Args:
            current: Current agent ID.
            current_name: Current agent name.
            agent_manager: Agent manager instance.

        Returns:
            CommandResult with agent list.
        """
        lines = [
            "🤖 **Agent 信息**",
            "",
            f"**当前 Agent**: {current_name} ({current})",
            "",
            "**可用 Agents**:",
        ]

        # Get available agents from manager
        if agent_manager and hasattr(agent_manager, "list_agents"):
            agents = agent_manager.list_agents()
            for agent_id, agent_info in agents.items():
                name = agent_info.get("name", agent_id)
                marker = " ✅" if agent_id == current else ""
                lines.append(f"  {name} ({agent_id}){marker}")
        else:
            # Default agents when no manager
            default_agents = [
                ("default", "Default", current == "default"),
                ("coder", "Coder", current == "coder"),
                ("writer", "Writer", current == "writer"),
                ("analyst", "Analyst", current == "analyst"),
            ]
            for agent_id, name, is_current in default_agents:
                marker = " ✅" if is_current else ""
                lines.append(f"  {name} ({agent_id}){marker}")

        lines.append("\n💡 使用 `/agent <名称>` 切换 Agent")

        return CommandResult.success("\n".join(lines))

    async def _switch_agent(
        self,
        new_agent: str,
        current: str,
        agent_manager: AgentManager | None,
        context: CommandContext,
    ) -> CommandResult:
        """Switch to a new agent.

        Args:
            new_agent: Agent ID to switch to.
            current: Current agent ID.
            agent_manager: Agent manager instance.
            context: Execution context.

        Returns:
            CommandResult with switch result.
        """
        # Check if already using this agent
        if new_agent == current:
            return CommandResult.success(f"💡 已经在使用 Agent: {new_agent}")

        # Validate agent exists
        if agent_manager and hasattr(agent_manager, "agent_exists"):
            if not agent_manager.agent_exists(new_agent):
                return CommandResult.success(
                    f"❌ Agent 不存在: {new_agent}\n"
                    "使用 `/agent` 查看可用 Agent 列表"
                )

        try:
            # Switch agent
            if agent_manager and hasattr(agent_manager, "switch"):
                await agent_manager.switch(new_agent)
                new_name = new_agent.capitalize()
            else:
                # Just update context
                context.set("agent_id", new_agent)
                new_name = new_agent.capitalize()

            return CommandResult.success(
                f"✅ 已切换 Agent\n"
                f"   {current} → {new_agent}"
            )

        except Exception as e:
            return CommandResult.fail(f"切换 Agent 失败: {e}")
