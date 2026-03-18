"""Memory CLI 命令"""
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
from typing import Optional

from anyclaw.memory.manager import MemoryManager, get_memory_manager
from anyclaw.memory.automation import MemoryAutomation
from anyclaw.config.settings import settings

app = typer.Typer(help="管理智能体记忆")
console = Console()


def get_manager() -> MemoryManager:
    """获取记忆管理器"""
    workspace = Path(settings.workspace).expanduser()
    return MemoryManager(
        workspace_path=workspace,
        max_chars=settings.memory_max_chars,
        daily_load_days=settings.memory_daily_load_days,
    )


@app.command()
def show():
    """显示长期记忆"""
    manager = get_manager()

    if not manager.long_term_exists():
        console.print("[yellow]长期记忆文件不存在[/yellow]")
        console.print("\n[dim]运行 'anyclaw memory edit' 创建记忆文件[/dim]")
        return

    content = manager.load_long_term()
    if content:
        console.print(Panel(content, title="MEMORY.md", border_style="blue"))
    else:
        console.print("[yellow]长期记忆为空[/yellow]")


@app.command()
def edit():
    """编辑长期记忆"""
    import subprocess
    import os

    manager = get_manager()

    # 确保文件存在
    if not manager.long_term_exists():
        manager.create_long_term()
        console.print("[green]已创建默认记忆文件[/green]")

    filepath = manager.workspace_path / manager.LONG_TERM_FILE

    # 获取编辑器
    editor = os.environ.get("EDITOR", "nano")

    try:
        subprocess.run([editor, str(filepath)], check=True)
        console.print(f"[green]已编辑: {filepath}[/green]")
    except subprocess.CalledProcessError:
        console.print(f"[red]编辑器启动失败[/red]")
    except FileNotFoundError:
        console.print(f"[red]找不到编辑器: {editor}[/red]")
        console.print("[dim]设置 EDITOR 环境变量指定编辑器[/dim]")


@app.command()
def today():
    """显示今日日志"""
    manager = get_manager()

    content = manager.get_today_content()
    if content:
        console.print(Panel(content, title="今日日志", border_style="green"))
    else:
        console.print("[yellow]今日还没有日志[/yellow]")
        console.print("\n[dim]运行 'anyclaw memory log <内容>' 添加日志[/dim]")


@app.command()
def log(
    entry: str = typer.Argument(..., help="日志内容"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="静默模式"),
):
    """追加到今日日志"""
    manager = get_manager()

    manager.append_to_today(entry)

    if not quiet:
        console.print("[green]✓[/green] 已追加到今日日志")


@app.command()
def search(
    keyword: str = typer.Argument(..., help="搜索关键词"),
    show_matches: bool = typer.Option(True, "--matches", "-m", help="显示匹配内容"),
):
    """搜索记忆"""
    manager = get_manager()

    results = manager.search(keyword)

    if not results:
        console.print(f"[yellow]未找到包含「{keyword}」的记忆[/yellow]")
        return

    console.print(f"\n[bold]搜索结果: 「{keyword}」[/bold]\n")

    for result in results:
        console.print(f"[cyan]{result.source}[/cyan]")

        if show_matches and result.matches:
            for match in result.matches[:5]:  # 最多显示 5 个匹配
                console.print(f"  • {match}")

        console.print()


@app.command()
def export(
    format: str = typer.Option("markdown", "--format", "-f", help="导出格式 (markdown/json)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="输出文件路径"),
):
    """导出记忆"""
    manager = get_manager()

    try:
        content = manager.export(format=format)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    if output:
        output.write_text(content, encoding="utf-8")
        console.print(f"[green]✓[/green] 已导出到: {output}")
    else:
        console.print(content)


@app.command()
def clean(
    days: int = typer.Option(30, "--days", "-d", help="保留最近多少天的日志"),
    dry_run: bool = typer.Option(False, "--dry-run", help="仅显示将删除的文件"),
):
    """清理旧日志"""
    manager = get_manager()

    if dry_run:
        # 仅统计
        if not manager.memory_dir.exists():
            console.print("[yellow]日志目录不存在[/yellow]")
            return

        from datetime import date, timedelta

        cutoff = date.today() - timedelta(days=days)
        count = 0

        for log_file in sorted(manager.memory_dir.glob("*.md")):
            try:
                file_date = date.fromisoformat(log_file.stem)
                if file_date < cutoff:
                    count += 1
                    console.print(f"  [dim]{log_file.name}[/dim]")
            except ValueError:
                pass

        if count == 0:
            console.print("[green]没有需要清理的日志[/green]")
        else:
            console.print(f"\n[yellow]将删除 {count} 个日志文件[/yellow]")
            console.print("[dim]运行不带 --dry-run 来实际删除[/dim]")
    else:
        deleted = manager.clean_old_logs(days_to_keep=days)

        if deleted == 0:
            console.print("[green]没有需要清理的日志[/green]")
        else:
            console.print(f"[green]✓[/green] 已清理 {deleted} 个旧日志")


@app.command()
def stats():
    """显示记忆统计"""
    manager = get_manager()

    stats = manager.get_stats()

    table = Table(title="记忆统计")
    table.add_column("项目", style="cyan")
    table.add_column("值", style="green")

    table.add_row("长期记忆", "✓ 存在" if stats["long_term_exists"] else "✗ 不存在")
    if stats["long_term_chars"]:
        table.add_row("长期记忆大小", f"{stats['long_term_chars']:,} 字符")

    table.add_row("每日日志数量", str(stats["daily_logs_count"]))

    if stats["oldest_log"]:
        table.add_row("最早日志", stats["oldest_log"])
    if stats["newest_log"]:
        table.add_row("最新日志", stats["newest_log"])

    console.print(table)


@app.command()
def analyze(
    message: str = typer.Argument(..., help="要分析的消息"),
):
    """分析消息中的记忆信息"""
    automation = MemoryAutomation()

    suggestion = automation.analyze_message(message)

    if suggestion:
        console.print("\n[bold]检测到潜在记忆信息:[/bold]\n")

        table = Table(show_header=False)
        table.add_column("Key", style="dim")
        table.add_column("Value")

        table.add_row("类型", suggestion.type)
        table.add_row("部分", suggestion.section)
        table.add_row("内容", suggestion.content)
        table.add_row("置信度", f"{suggestion.confidence:.0%}")

        console.print(table)

        console.print(f"\n[dim]建议: {automation.suggest_memory_update(suggestion)}[/dim]")
    else:
        console.print("[dim]未检测到需要记忆的信息[/dim]")


def create_memory_app() -> typer.Typer:
    """创建 memory 命令应用"""
    return app


if __name__ == "__main__":
    app()
