"""CLI 应用"""
import typer
from rich.console import Console
from anyclaw.config.settings import settings
from anyclaw.agent.loop import AgentLoop
from anyclaw.channels.cli import CLIChannel
from anyclaw.skills.loader import SkillLoader

app = typer.Typer()
console = Console()


@app.command()
def chat(
    agent_name: str = typer.Option(None, help="Agent name"),
    model: str = typer.Option(None, help="LLM model"),
):
    """Start interactive chat"""

    # 覆盖配置
    if agent_name:
        settings.agent_name = agent_name
    if model:
        settings.llm_model = model

    console.print(f"[bold blue]Starting {settings.agent_name}...[/bold blue]\n")

    # 初始化组件
    agent = AgentLoop()
    channel = CLIChannel()

    # 加载技能
    skill_loader = SkillLoader(settings.skills_dir)
    skills_info = skill_loader.load_all()
    agent.set_skills(skills_info)

    console.print(f"[dim]Loaded {len(skills_info)} skills[/dim]\n")

    # 定义处理函数
    async def process(user_input: str) -> str:
        return await agent.process(user_input)

    # 运行 CLI
    import asyncio
    asyncio.run(channel.run(process))


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current config"),
):
    """Manage configuration"""

    if show:
        console.print("\n[bold]Current Configuration:[/bold]\n")
        console.print(f"Agent Name: {settings.agent_name}")
        console.print(f"LLM Provider: {settings.llm_provider}")
        console.print(f"LLM Model: {settings.llm_model}")
        console.print(f"Temperature: {settings.llm_temperature}")
        console.print(f"Max Tokens: {settings.llm_max_tokens}")
        console.print(f"Timeout: {settings.llm_timeout}")
        console.print(f"Skills Dir: {settings.skills_dir}")
        console.print(f"Workspace Dir: {settings.workspace_dir}")


@app.command()
def version():
    """Show version"""
    console.print("AnyClaw v0.1.0-MVP")


if __name__ == "__main__":
    app()
