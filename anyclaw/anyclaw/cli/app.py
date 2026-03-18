"""CLI 应用"""
import typer
from rich.console import Console
from rich.table import Table
from anyclaw.config.settings import settings
from anyclaw.agent.loop import AgentLoop
from anyclaw.channels.cli import CLIChannel
from anyclaw.skills.loader import SkillLoader

app = typer.Typer()
console = Console()

# 导入并注册子命令
from .onboard import create_onboard_app
from .workspace import create_workspace_app
from .token import create_token_app
from .persona import create_persona_app
from .compress import create_compress_app
from .memory import create_memory_app

app.add_typer(create_onboard_app(), name="onboard")
app.add_typer(create_workspace_app(), name="workspace")
app.add_typer(create_token_app(), name="token")
app.add_typer(create_persona_app(), name="persona")
app.add_typer(create_compress_app(), name="compress")
app.add_typer(create_memory_app(), name="memory")


@app.command()
def chat(
    agent_name: str = typer.Option(None, help="Agent name"),
    model: str = typer.Option(None, help="LLM model"),
    stream: bool = typer.Option(None, "--stream/--no-stream", help="Enable streaming output"),
):
    """Start interactive chat"""

    # 覆盖配置
    if agent_name:
        settings.agent_name = agent_name
    if model:
        settings.llm_model = model
    if stream is not None:
        settings.stream_enabled = stream

    console.print(f"[bold blue]Starting {settings.agent_name}...[/bold blue]")
    console.print(f"[dim]Streaming: {'enabled' if settings.stream_enabled else 'disabled'}[/dim]\n")

    # 初始化组件
    agent = AgentLoop()
    channel = CLIChannel()

    # 加载技能
    skill_loader = SkillLoader(settings.skills_dir)
    skills_info = skill_loader.load_all()
    agent.set_skills(skills_info)

    console.print(f"[dim]Loaded {len(skills_info)} skills[/dim]\n")

    # 运行 CLI
    import asyncio

    if settings.stream_enabled:
        # 流式模式
        async def stream_process(user_input: str):
            async for chunk in agent.process_stream(user_input):
                yield chunk

        asyncio.run(channel.run_stream(stream_process))
    else:
        # 非流式模式
        async def process(user_input: str) -> str:
            return await agent.process(user_input)

        asyncio.run(channel.run(process))


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current config"),
    provider: str = typer.Option(None, "--provider", "-p", help="Filter by provider (zai, openai, anthropic)"),
):
    """Manage configuration"""

    if show:
        console.print("\n[bold]Current Configuration:[/bold]\n")

        # 基础配置
        console.print(f"Agent Name: {settings.agent_name}")
        console.print(f"LLM Provider: {settings.llm_provider}")
        console.print(f"LLM Model: {settings.llm_model}")
        console.print(f"Temperature: {settings.llm_temperature}")
        console.print(f"Max Tokens: {settings.llm_max_tokens}")
        console.print(f"Timeout: {settings.llm_timeout}")
        console.print(f"Skills Dir: {settings.skills_dir}")
        console.print(f"Workspace Dir: {settings.workspace_dir}")

        # Provider 特定配置
        if provider == "zai" or provider is None:
            show_zai_config()


def show_zai_config() -> None:
    """显示 ZAI 配置"""
    console.print("\n[bold cyan]ZAI Provider Configuration:[/bold cyan]\n")

    table = Table(show_header=False)
    table.add_column("Key", style="dim")
    table.add_column("Value")

    table.add_row("API Key", "✓ Set" if settings.zai_api_key else "✗ Not set")
    table.add_row("Endpoint", settings.zai_endpoint)
    table.add_row("Base URL", settings.zai_base_url or "(auto)")

    console.print(table)

    # 显示 endpoint 信息
    if settings.zai_endpoint != "auto":
        from anyclaw.providers.zai import ZAI_ENDPOINTS
        base_url = ZAI_ENDPOINTS.get(settings.zai_endpoint)
        if base_url:
            console.print(f"\n[dim]Resolved Base URL: {base_url}[/dim]")


@app.command()
def version():
    """Show version"""
    console.print("AnyClaw v0.1.0-MVP")


@app.command()
def providers():
    """List available providers"""
    console.print("\n[bold]Available Providers:[/bold]\n")

    table = Table()
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Default Model")

    # OpenAI
    table.add_row(
        "openai",
        "✓ Configured" if settings.openai_api_key else "✗ Not configured",
        "gpt-4o-mini"
    )

    # Anthropic
    table.add_row(
        "anthropic",
        "✓ Configured" if settings.anthropic_api_key else "✗ Not configured",
        "claude-3-5-sonnet"
    )

    # ZAI
    table.add_row(
        "zai",
        "✓ Configured" if settings.zai_api_key else "✗ Not configured",
        "zai/glm-5"
    )

    console.print(table)
    console.print("\n[dim]Use 'anyclaw onboard --list-auth-choices' to configure[/dim]")


@app.command()
def setup(
    workspace: str = typer.Option(None, "--workspace", "-w", help="自定义工作区路径"),
    no_git: bool = typer.Option(False, "--no-git", help="跳过 git 初始化"),
    skip_bootstrap: bool = typer.Option(False, "--skip-bootstrap", help="跳过引导文件创建"),
):
    """初始化设置（创建工作区和默认文件）"""
    from anyclaw.workspace.manager import WorkspaceManager
    from anyclaw.workspace.bootstrap import BootstrapLoader

    console.print("\n[bold blue]AnyClaw Setup[/bold blue]\n")

    # 创建工作区
    manager = WorkspaceManager(workspace_path=workspace)

    if manager.exists():
        console.print(f"[yellow]工作区已存在: {manager.path}[/yellow]")
    else:
        try:
            manager.create(init_git=not no_git)
            console.print(f"[green]✓[/green] 工作区创建成功: {manager.path}")
        except Exception as e:
            console.print(f"[red]创建失败: {e}[/red]")
            raise typer.Exit(1)

    # 显示状态
    if manager.is_git_repo():
        console.print("[green]✓[/green] Git 仓库已初始化")

    # 引导状态
    if not skip_bootstrap:
        loader = BootstrapLoader(manager)
        if loader.has_bootstrap():
            console.print("[green]✓[/green] 引导文件已创建")
            console.print("\n[dim]运行 'anyclaw chat' 开始首次会话[/dim]")
        else:
            console.print("[dim]引导文件已跳过[/dim]")

    console.print("\n[bold green]设置完成！[/bold green]")
    console.print(f"工作区路径: {manager.path}")


if __name__ == "__main__":
    app()
