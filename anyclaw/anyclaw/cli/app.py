"""CLI 应用"""
from pathlib import Path

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
from .config_cmd import create_config_app
from .skill_cmd import create_skill_app

app.add_typer(create_onboard_app(), name="onboard")
app.add_typer(create_workspace_app(), name="workspace")
app.add_typer(create_token_app(), name="token")
app.add_typer(create_persona_app(), name="persona")
app.add_typer(create_compress_app(), name="compress")
app.add_typer(create_memory_app(), name="memory")
app.add_typer(create_config_app(), name="config")
app.add_typer(create_skill_app(), name="skill")


@app.command()
def chat(
    agent_name: str = typer.Option(None, help="Agent name"),
    model: str = typer.Option(None, help="LLM model"),
    stream: bool = typer.Option(None, "--stream/--no-stream", help="Enable streaming output"),
    workspace: str = typer.Option(None, "--workspace", "-w", help="Workspace directory"),
):
    """Start interactive chat"""
    from anyclaw.workspace.manager import WorkspaceManager
    from anyclaw.workspace import sync_workspace_templates
    from pathlib import Path

    # 覆盖配置
    if agent_name:
        settings.agent_name = agent_name
    if model:
        settings.llm_model = model
    if stream is not None:
        settings.stream_enabled = stream

    # 确保 workspace 存在
    ws_manager = WorkspaceManager(workspace_path=workspace)
    if not ws_manager.exists():
        console.print("[dim]初始化工作区...[/dim]")
        ws_manager.ensure_exists(silent=True)

    console.print(f"[bold blue]Starting {settings.agent_name}...[/bold blue]")
    console.print(f"[dim]Workspace: {ws_manager.path}[/dim]")
    console.print(f"[dim]Streaming: {'enabled' if settings.stream_enabled else 'disabled'}[/dim]\n")

    # 初始化组件
    agent = AgentLoop(workspace=ws_manager.path)
    channel = CLIChannel()

    # 加载技能
    skill_loader = SkillLoader(skills_dir=settings.skills_dir)
    skills_info = skill_loader.load_all()  # 加载所有技能
    skills_dict = skill_loader.get_skill_definitions()  # 获取 SkillDefinition 格式

    # 设置技能（如果有）
    if skills_dict:
        agent.set_skills(skills_dict)

    console.print(f"[dim]Loaded {len(skills_info)} skills ({len(skills_dict)} with definitions)[/dim]\n")

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
    force: bool = typer.Option(False, "--force", "-f", help="强制重新创建工作区"),
):
    """初始化设置（创建工作区和默认文件）"""
    from anyclaw.workspace.manager import WorkspaceManager
    from anyclaw.workspace import sync_workspace_templates

    console.print("\n[bold blue]AnyClaw Setup[/bold blue]\n")

    # 创建工作区
    manager = WorkspaceManager(workspace_path=workspace)

    if manager.exists() and not force:
        console.print(f"[yellow]工作区已存在: {manager.path}[/yellow]")
        console.print("[dim]同步模板文件...[/dim]")
    else:
        try:
            added = manager.create(init_git=not no_git, force=force)
            console.print(f"[green]✓[/green] 工作区创建成功: {manager.path}")
            for name in added:
                console.print(f"  [dim]Created {name}[/dim]")
        except Exception as e:
            console.print(f"[red]创建失败: {e}[/red]")
            raise typer.Exit(1)

    # 同步模板（只创建缺失的）
    added = sync_workspace_templates(manager.path)
    if added:
        console.print("[green]✓[/green] 新增模板文件:")
        for name in added:
            console.print(f"  [dim]{name}[/dim]")

    # 显示状态
    if manager.is_git_repo():
        console.print("[green]✓[/green] Git 仓库已初始化")

    # 显示工作区结构
    console.print(f"\n[bold]工作区结构:[/bold]")
    console.print(f"  {manager.path}")
    console.print(f"  ├── SOUL.md       # Agent 人设")
    console.print(f"  ├── USER.md       # 用户档案")
    console.print(f"  ├── AGENTS.md     # Agent 指令")
    console.print(f"  ├── TOOLS.md      # 工具说明")
    console.print(f"  ├── HEARTBEAT.md  # 心跳任务")
    console.print(f"  ├── memory/       # 记忆存储")
    console.print(f"  │   ├── MEMORY.md")
    console.print(f"  │   └── HISTORY.md")
    console.print(f"  └── skills/       # 自定义技能")

    console.print("\n[bold green]设置完成！[/bold green]")
    console.print(f"\n下一步:")
    console.print(f"  1. 编辑 [cyan]{manager.path}/USER.md[/cyan] 填写你的信息")
    console.print(f"  2. 运行 [cyan]anyclaw chat[/cyan] 开始对话")


@app.command()
def init(
    workspace: str = typer.Option(None, "--workspace", "-w", help="自定义工作区路径"),
):
    """在工作目录初始化 .anyclaw（用于项目级配置）"""
    from anyclaw.workspace import sync_workspace_templates

    # 在当前目录创建 .anyclaw
    cwd = Path.cwd()
    anyclaw_dir = cwd / ".anyclaw"
    anyclaw_dir.mkdir(exist_ok=True)

    console.print(f"[bold]在当前目录初始化 .anyclaw[/bold]")
    console.print(f"路径: {anyclaw_dir}\n")

    # 同步模板
    added = sync_workspace_templates(anyclaw_dir)

    if added:
        console.print("[green]✓[/green] 创建文件:")
        for name in added:
            console.print(f"  [dim]{name}[/dim]")
    else:
        console.print("[dim]所有文件已存在，无需更新[/dim]")

    console.print("\n[green]完成！[/green] 编辑 .anyclaw 下的文件来自定义行为。")


if __name__ == "__main__":
    app()
