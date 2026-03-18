"""Workspace CLI 命令"""

import os
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree

from anyclaw.workspace.manager import WorkspaceManager
from anyclaw.workspace.bootstrap import BootstrapLoader

app = typer.Typer(help="Workspace 工作区管理")
console = Console()


def get_workspace_manager(
    workspace_path: str = None,
    profile: str = None,
) -> WorkspaceManager:
    """获取工作区管理器"""
    return WorkspaceManager(
        workspace_path=workspace_path,
        profile=profile or os.environ.get("ANYCLAW_PROFILE"),
    )


@app.command("init")
def init_workspace(
    path: str = typer.Option(None, "--path", "-p", help="自定义工作区路径"),
    profile: str = typer.Option(None, "--profile", help="Profile 名称"),
    no_git: bool = typer.Option(False, "--no-git", help="跳过 git 初始化"),
    force: bool = typer.Option(False, "--force", "-f", help="强制重新创建"),
):
    """初始化工作区"""
    manager = get_workspace_manager(path, profile)

    if manager.exists() and not force:
        console.print(f"[yellow]工作区已存在: {manager.path}[/yellow]")
        console.print("使用 --force 强制重新创建")
        raise typer.Exit(1)

    try:
        manager.create(init_git=not no_git, force=force)
        console.print(f"[green]✓[/green] 工作区创建成功: {manager.path}")

        if manager.is_git_repo():
            console.print("[green]✓[/green] Git 仓库已初始化")

        console.print("\n[bold]创建的文件:[/bold]")
        for file_info in manager.get_files():
            console.print(f"  • {file_info['name']}")

    except Exception as e:
        console.print(f"[red]创建失败: {e}[/red]")
        raise typer.Exit(1)


@app.command("status")
def show_status(
    path: str = typer.Option(None, "--path", "-p", help="自定义工作区路径"),
    profile: str = typer.Option(None, "--profile", help="Profile 名称"),
):
    """显示工作区状态"""
    manager = get_workspace_manager(path, profile)
    status = manager.get_status()

    # 创建状态面板
    console.print()

    if not status["exists"]:
        console.print(Panel(
            f"[yellow]工作区不存在[/yellow]\n\n"
            f"运行 [cyan]anyclaw workspace init[/cyan] 创建工作区",
            title=f"Workspace: {status['path']}",
            border_style="yellow",
        ))
        return

    # 基本信息
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Key", style="dim")
    info_table.add_column("Value")

    info_table.add_row("路径", str(status["path"]))
    info_table.add_row("Profile", status["profile"])
    info_table.add_row("Git 仓库", "✓ 是" if status["is_git_repo"] else "✗ 否")

    console.print(Panel(info_table, title="Workspace 状态", border_style="blue"))

    # 文件列表
    if status["files"]:
        console.print("\n[bold]文件列表:[/bold]")

        file_table = Table()
        file_table.add_column("文件名", style="cyan")
        file_table.add_column("大小", justify="right")
        file_table.add_column("修改时间")

        for file_info in status["files"]:
            from datetime import datetime
            modified = datetime.fromtimestamp(file_info["modified"]).strftime("%Y-%m-%d %H:%M")
            size = _format_size(file_info["size"])
            file_table.add_row(file_info["name"], size, modified)

        console.print(file_table)
    else:
        console.print("\n[dim]工作区为空[/dim]")


def _format_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


@app.command("path")
def show_path(
    path: str = typer.Option(None, "--path", "-p", help="自定义工作区路径"),
    profile: str = typer.Option(None, "--profile", help="Profile 名称"),
):
    """显示工作区路径"""
    manager = get_workspace_manager(path, profile)
    console.print(str(manager.path))


@app.command("files")
def list_files(
    path: str = typer.Option(None, "--path", "-p", help="自定义工作区路径"),
    profile: str = typer.Option(None, "--profile", help="Profile 名称"),
    all: bool = typer.Option(False, "--all", "-a", help="显示隐藏文件"),
):
    """列出工作区文件"""
    manager = get_workspace_manager(path, profile)

    if not manager.exists():
        console.print("[red]工作区不存在[/red]")
        raise typer.Exit(1)

    files = manager.get_files()

    if not files:
        console.print("[dim]工作区为空[/dim]")
        return

    # 创建树形结构
    tree = Tree(f"[bold]{manager.path}[/bold]")

    for file_info in files:
        size = _format_size(file_info["size"])
        tree.add(f"[cyan]{file_info['name']}[/cyan] [dim]({size})[/dim]")

    console.print(tree)


@app.command("bootstrap")
def bootstrap_status(
    path: str = typer.Option(None, "--path", "-p", help="自定义工作区路径"),
    profile: str = typer.Option(None, "--profile", help="Profile 名称"),
    complete: bool = typer.Option(False, "--complete", "-c", help="标记引导完成"),
):
    """管理引导文件"""
    manager = get_workspace_manager(path, profile)
    loader = BootstrapLoader(manager)

    if complete:
        if loader.mark_completed():
            console.print("[green]✓[/green] 引导已标记为完成")
        else:
            console.print("[yellow]引导文件不存在或已完成[/yellow]")
        return

    if loader.is_completed():
        console.print("[green]✓[/green] 引导已完成")
    elif loader.has_bootstrap():
        console.print("[yellow]引导进行中[/yellow]")
        console.print(f"运行 [cyan]anyclaw chat[/cyan] 开始首次会话")
        console.print("或运行 [cyan]anyclaw workspace bootstrap --complete[/cyan] 跳过引导")
    else:
        console.print("[dim]无引导文件[/dim]")


def create_workspace_app() -> typer.Typer:
    """创建 workspace 子应用"""
    return app
