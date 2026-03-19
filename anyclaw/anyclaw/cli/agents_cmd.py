"""Agent CLI commands for AnyClaw."""

import asyncio
import logging
import click
from pathlib import Path

from anyclaw.agents.manager import AgentManager
from anyclaw.agents.identity import IdentityManager
from anyclaw.config.settings import settings


logger = logging.getLogger(__name__)


def get_agent_manager() -> AgentManager:
    """Get agent manager instance."""
    root_workspace = Path.home() / ".anyclaw" / "workspace"
    identity_manager = IdentityManager(root_workspace)
    return AgentManager(root_workspace, identity_manager)


@click.group()
def agents():
    """Multi-agent management commands."""
    pass


@agents.command("list")
@click.option("--include-disabled", is_flag=True, help="Include disabled agents")
def list_agents(include_disabled: bool = False):
    """List all agents."""
    manager = get_agent_manager()
    
    agents = manager.list_agents(include_disabled=include_disabled)
    
    if not agents:
        click.echo("No agents found.")
        return
    
    # Display header
    click.echo("=" * 60)
    click.echo(f"{'Agent ID':<20} {'Name':<20} {'Workspace':<30} {'Enabled':<10}")
    click.echo("=" * 60)
    
    for agent in agents:
        agent_id = agent["id"]
        name = agent["name"]
        workspace = agent["workspace"]
        enabled = "✓" if agent["enabled"] else "✗"
        sessions = agent.get("sessionCount", 0)
        
        click.echo(f"{agent_id:<20} {name:<20} {workspace:<30} {enabled:<10} [{sessions} sessions]")
    
    click.echo("=" * 60)
    click.echo(f"Total: {len(agents)} agents")


@agents.command("create")
@click.option("--name", prompt="Agent name", help="Agent name")
@click.option("--creature", type=click.Choice(["AI", "robot", "ghost", "cat", "dog", "alien"]), default="AI", help="Creature type")
@click.option("--vibe", type=click.Choice(["sharp", "warm", "chaotic", "calm"]), default="warm", help="Personality vibe")
@click.option("--emoji", default="🤖", help="Emoji signature")
@click.option("--avatar", help="Avatar path (workspace-relative or URL)")
@click.option("--workspace", help="Workspace path (relative or absolute)")
@click.option("--enabled/--disabled", default=True, help="Whether agent is enabled")
def create_agent(name: str, creature: str, vibe: str, emoji: str, avatar: str, workspace: str, enabled: bool):
    """Create a new agent."""
    manager = get_agent_manager()
    
    agent = manager.create_agent(
        name=name,
        creature=creature,
        vibe=vibe,
        emoji=emoji,
        avatar=avatar,
        workspace=workspace,
        enabled=enabled,
    )
    
    if not agent:
        click.echo(f"Failed to create agent: {name}")
        return
    
    click.echo(f"✓ Agent created: {agent.agent_id}")
    click.echo(f"  Name: {agent.identity.name}")
    click.echo(f"  Workspace: {agent.workspace.get_path()}")
    click.echo(f"  Enabled: {agent.enabled}")
    click.echo()
    click.echo("Next steps:")
    click.echo("  1. Add skills to agent workspace")
    click.echo("  2. Configure agent-specific tools")
    click.echo("  3. Set as default agent: anyclaw agents switch")


@agents.command("delete")
@click.argument("agent_id", type=str)
@click.option("--confirm", is_flag=True, help="Confirm deletion without prompt")
def delete_agent(agent_id: str, confirm: bool = False):
    """Delete an agent."""
    manager = get_agent_manager()
    
    # Get agent info
    agent = manager.get_agent(agent_id)
    if not agent:
        click.echo(f"Agent {agent_id} not found.")
        return
    
    click.echo(f"Agent to delete: {agent.identity.name} ({agent_id})")
    click.echo(f"  Workspace: {agent.workspace.get_path()}")
    
    if not confirm:
        if not click.confirm("Are you sure you want to delete this agent? This will delete all associated files and data."):
            click.echo("Aborted.")
            return
    
    if manager.delete_agent(agent_id):
        click.echo(f"✓ Agent deleted: {agent_id}")
    else:
        click.echo(f"✗ Failed to delete agent: {agent_id}")


@agents.command("switch")
@click.argument("agent_id", type=str, required=False)
def switch_agent(agent_id: str = None):
    """Switch to a different agent (set as default)."""
    manager = get_agent_manager()
    
    if agent_id:
        if manager.set_default_agent(agent_id):
            agent = manager.get_agent(agent_id)
            if agent:
                click.echo(f"✓ Switched to agent: {agent.identity.name} ({agent_id})")
            else:
                click.echo(f"✗ Failed to switch to agent: {agent_id}")
        else:
            click.echo(f"✗ Agent {agent_id} not found")
    else:
        # List available agents and prompt
        default = manager.get_default_agent()
        if default:
            click.echo(f"Current default: {default.identity.name} ({default.agent_id})")
        
        agents = manager.list_agents(include_disabled=False)
        if agents:
            click.echo("Available agents:")
            for agent in agents:
                is_default = " (default)" if agent["id"] == default.agent_id else ""
                click.echo(f"  - {agent['name']} ({agent['id']}){is_default}")
        else:
            click.echo("No available agents.")


@agents.command("identity")
@click.argument("agent_id", type=str)
@click.option("--name", help="Update name")
@click.option("--avatar", help="Update avatar path")
@click.option("--emoji", help="Update emoji")
@click.option("--workspace", help="Update workspace path")
def edit_identity(agent_id: str, name: str, avatar: str, emoji: str, workspace: str):
    """Edit agent identity."""
    manager = get_agent_manager()
    
    agent = manager.get_agent(agent_id)
    if not agent:
        click.echo(f"Agent {agent_id} not found.")
        return
    
    # Note: Full identity editing would require recreating IDENTITY.md
    # For now, we can show the current identity
    identity = agent.identity
    
    click.echo(f"Agent: {identity.name} ({agent_id})")
    click.echo(f"  Creature: AI (default)")
    click.echo(f"  Vibe: {identity.workspace.get_path()}")
    click.echo(f"  Avatar: {identity.avatar or 'none'}")
    click.echo(f"  Emoji: {identity.emoji or 'none'}")
    
    click.echo()
    click.echo("To edit identity, manually edit IDENTITY.md in:")
    click.echo(f"  {agent.workspace.get_path()}/IDENTITY.md")


@agents.command("tools")
@click.argument("agent_id", type=str)
def list_tools(agent_id: str):
    """List agent's tool catalog."""
    manager = get_agent_manager()
    
    catalog = manager.get_tools_catalog(agent_id)
    
    if not catalog:
        click.echo(f"Agent {agent_id} not found or no tools.")
        return
    
    click.echo(f"Agent: {agent_id}")
    click.echo(f"  Tool catalog file: {catalog.get('file', 'N/A')}")
    click.echo()
    click.echo("Tools:")
    
    if catalog.get("tools"):
        for tool in catalog["tools"]:
            click.echo(f"  - {tool.get('name', 'unknown')}")
            if tool.get("description"):
                click.echo(f"    {tool['description']}")
    else:
        click.echo("  (No tools)")
    
    if catalog.get("plugins"):
        click.echo()
        click.echo("Plugins:")
        for plugin in catalog["plugins"]:
            click.echo(f"  - {plugin.get('name', 'unknown')}")


@agents.command("status")
def agent_status():
    """Show agent manager status."""
    manager = get_agent_manager()
    status = manager.get_status()
    
    click.echo("=" * 60)
    click.echo("Agent Manager Status")
    click.echo("=" * 60)
    click.echo(f"  Total agents: {status.get('agentsCount', 0)}")
    click.echo(f"  Enabled agents: {status.get('enabledAgentsCount', 0)}")
    click.echo(f"  Default agent: {status.get('defaultAgent', {}).get('name', 'None')}")
    click.echo("=" * 60)


if __name__ == "__main__":
    agents()
