"""Session CLI commands

会话管理命令：
- anyclaw session list: 列出会话
- anyclaw session show: 查看会话详情
- anyclaw session search: 搜索会话内容
- anyclaw session export: 导出会话
- anyclaw session clean: 清理旧会话
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

app = typer.Typer(name="session", help="会话管理")
console = Console()


def _get_archive_manager():
    """获取 SessionArchiveManager 实例"""
    from anyclaw.session.archive import SessionArchiveManager, ArchiveConfig
    return SessionArchiveManager(ArchiveConfig())


@app.command("list")
def list_sessions(
    date: Optional[str] = typer.Option(None, "--date", "-d", help="指定日期 (YYYY-MM-DD)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="指定项目 ID"),
    channel: Optional[str] = typer.Option(None, "--channel", "-c", help="指定渠道 (cli/feishu/discord)"),
    limit: int = typer.Option(20, "--limit", "-l", help="限制数量"),
):
    """列出会话"""
    manager = _get_archive_manager()
    sessions = manager.list_sessions(
        date=date,
        project=project,
        channel=channel,
        limit=limit,
    )

    if not sessions:
        console.print("[yellow]没有找到会话记录[/yellow]")
        return

    table = Table(title=f"会话列表 (共 {len(sessions)} 条)")
    table.add_column("Session ID", style="cyan", width=12)
    table.add_column("Channel", style="dim", width=8)
    table.add_column("Project", style="green", width=30)
    table.add_column("Started", style="yellow", width=20)
    table.add_column("Branch", style="dim", width=12)

    for session in sessions:
        session_id = session.get("session_id", "unknown")[:8]
        channel = session.get("channel", "cli")
        project = session.get("project_id", "unknown")
        if len(project) > 28:
            project = project[:25] + "..."
        started = session.get("started_at", "unknown")
        if started and len(started) > 19:
            started = started[:19]
        branch = session.get("git_branch", "-") or "-"
        if len(branch) > 10:
            branch = branch[:10]

        table.add_row(session_id, channel, project, started, branch)

    console.print(table)


@app.command("show")
def show_session(
    session_id: str = typer.Argument(..., help="会话 ID"),
    format: str = typer.Option("tree", "--format", "-f", help="输出格式 (tree/json/markdown)"),
    limit: int = typer.Option(50, "--limit", "-l", help="限制记录数量"),
):
    """显示会话详情"""
    manager = _get_archive_manager()
    session = manager.get_session(session_id)

    if not session:
        console.print(f"[red]未找到会话: {session_id}[/red]")
        raise typer.Exit(1)

    if format == "json":
        import json
        output = json.dumps(session, ensure_ascii=False, indent=2)
        console.print(Syntax(output, "json", theme="monokai"))
    elif format == "markdown":
        output = manager._format_as_markdown(session)
        console.print(Panel(output, title=f"Session: {session_id[:8]}"))
    else:
        # tree 格式（默认）
        _print_session_tree(session, limit)


def _print_session_tree(session: dict, limit: int = 50) -> None:
    """以树形结构打印会话"""
    console.print(f"\n[bold cyan]Session: {session.get('session_id', 'unknown')}[/bold cyan]")
    console.print(f"[dim]Channel:[/dim] {session.get('channel', 'cli')}")
    console.print(f"[dim]Project:[/dim] {session.get('project_id', 'unknown')}")
    console.print(f"[dim]CWD:[/dim] {session.get('cwd', 'unknown')}")
    console.print(f"[dim]Started:[/dim] {session.get('started_at', 'unknown')}")

    if session.get("git_branch"):
        console.print(f"[dim]Branch:[/dim] {session['git_branch']}")

    if session.get("duration_seconds"):
        duration = session["duration_seconds"]
        console.print(f"[dim]Duration:[/dim] {duration:.1f}s")

    console.print()
    console.print("[bold]Records:[/bold]")

    records = session.get("records", [])[:limit]
    for record in records:
        record_type = record.get("type", "unknown")
        timestamp = record.get("timestamp", "")[11:19] if record.get("timestamp") else ""

        if record_type == "user_message":
            content = record.get("content", "")[:60]
            console.print(f"  [{timestamp}] [green]User:[/green] {content}...")

        elif record_type == "assistant_message":
            content = record.get("content", "")[:60]
            model = record.get("model", "")
            console.print(f"  [{timestamp}] [blue]Assistant[/blue] ({model}): {content}...")

        elif record_type == "tool_call":
            tool_name = record.get("tool_name", "unknown")
            console.print(f"  [{timestamp}] [yellow]Tool:[/yellow] {tool_name}()")

        elif record_type == "tool_result":
            success = "✓" if record.get("success") else "✗"
            duration_ms = record.get("duration_ms", 0)
            console.print(f"  [{timestamp}] [dim]Result:[/dim] [{success}] {duration_ms}ms")

        elif record_type == "skill_call":
            skill_name = record.get("skill_name", "unknown")
            console.print(f"  [{timestamp}] [magenta]Skill:[/magenta] {skill_name}")

        elif record_type == "error":
            error_type = record.get("error_type", "unknown")
            message = record.get("message", "")[:50]
            console.print(f"  [{timestamp}] [red]Error:[/red] {error_type}: {message}")


@app.command("search")
def search_sessions(
    query: str = typer.Argument(..., help="搜索关键词"),
    tool: Optional[str] = typer.Option(None, "--tool", "-t", help="按工具名称过滤"),
    limit: int = typer.Option(20, "--limit", "-l", help="限制数量"),
):
    """搜索会话内容"""
    manager = _get_archive_manager()
    results = manager.search_sessions(
        query=query,
        tool=tool,
        limit=limit,
    )

    if not results:
        console.print(f"[yellow]未找到匹配 '{query}' 的内容[/yellow]")
        return

    console.print(f"\n[bold]搜索结果: '{query}' (共 {len(results)} 条)[/bold]\n")

    for result in results:
        session_id = result.get("session_id", "unknown")[:8]
        record_type = result.get("type", "unknown")
        timestamp = result.get("timestamp", "")[:19] if result.get("timestamp") else ""

        content = result.get("content", {})
        content_str = ""

        if record_type == "user_message":
            content_str = content.get("content", "")[:80]
        elif record_type == "assistant_message":
            content_str = content.get("content", "")[:80]
        elif record_type == "tool_call":
            content_str = f"{content.get('tool_name', '')}({content.get('tool_input', {})})"
        elif record_type == "tool_result":
            content_str = content.get("output", "")[:80]

        console.print(f"  [cyan]{session_id}[/cyan] [{timestamp}] [dim]{record_type}[/dim]")
        console.print(f"    {content_str}...")
        console.print()


@app.command("export")
def export_session(
    session_id: str = typer.Argument(..., help="会话 ID"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径"),
    format: str = typer.Option("markdown", "--format", "-f", help="导出格式 (json/markdown)"),
):
    """导出会话"""
    manager = _get_archive_manager()

    output_path = Path(output) if output else None
    content = manager.export_session(session_id, format=format, output_path=output_path)

    if content is None and output_path is None:
        console.print(f"[red]未找到会话: {session_id}[/red]")
        raise typer.Exit(1)

    if output_path:
        console.print(f"[green]✓[/green] 会话已导出到: {output_path}")
    else:
        console.print(content)


@app.command("clean")
def clean_sessions(
    days: int = typer.Option(30, "--days", "-d", help="保留天数"),
    dry_run: bool = typer.Option(False, "--dry-run", help="仅显示将删除的内容"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="跳过确认"),
):
    """清理旧会话"""
    manager = _get_archive_manager()

    if dry_run:
        console.print(f"[yellow]模拟模式: 查找 {days} 天前的会话...[/yellow]\n")
    else:
        console.print(f"[yellow]查找 {days} 天前的会话...[/yellow]\n")

    deleted = manager.clean_old_sessions(days=days, dry_run=True)

    if not deleted:
        console.print("[green]没有需要清理的会话[/green]")
        return

    console.print(f"找到 {len(deleted)} 个会话文件:")
    for path in deleted[:10]:
        console.print(f"  [dim]{path}[/dim]")
    if len(deleted) > 10:
        console.print(f"  [dim]... 还有 {len(deleted) - 10} 个[/dim]")

    if dry_run:
        console.print(f"\n[yellow]模拟完成，未删除任何文件[/yellow]")
        console.print(f"[dim]运行不带 --dry-run 的命令来实际删除[/dim]")
        return

    if not confirm:
        if not typer.confirm(f"\n确定要删除这 {len(deleted)} 个会话吗?"):
            console.print("[yellow]已取消[/yellow]")
            return

    # 实际删除
    deleted_actual = manager.clean_old_sessions(days=days, dry_run=False)
    console.print(f"[green]✓[/green] 已删除 {len(deleted_actual)} 个会话")


@app.command("path")
def show_session_path():
    """显示会话存储路径"""
    from anyclaw.session.archive import DEFAULT_ARCHIVE_BASE
    console.print(f"[cyan]会话存储路径:[/cyan] {DEFAULT_ARCHIVE_BASE}")


def create_session_app() -> typer.Typer:
    """创建 session 命令应用"""
    return app
