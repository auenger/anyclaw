"""Context Compression CLI 命令"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from anyclaw.agent.compressor import get_compressor, CompressionResult
from anyclaw.agent.sliding_window import get_sliding_window
from anyclaw.agent.checkpoint import get_checkpoint_manager, CheckpointInfo
from anyclaw.config.settings import settings

app = typer.Typer(help="上下文压缩和管理命令")
console = Console()


# === Compress 命令 ===

@app.command("compress")
def compress_context(
    preview: bool = typer.Option(False, "--preview", "-p", help="仅预览，不执行"),
    strategy: str = typer.Option("truncate", "--strategy", "-s", help="压缩策略: summary/truncate/key_points"),
    threshold: int = typer.Option(None, "--threshold", "-t", help="压缩阈值"),
    keep_recent: int = typer.Option(None, "--keep-recent", "-k", help="保留最近消息数"),
):
    """压缩对话历史

    当对话历史过长时，压缩旧消息以节省 token。
    """
    compressor = get_compressor(
        compress_threshold=threshold or settings.compress_threshold,
        keep_recent=keep_recent or settings.compress_keep_recent,
    )

    # 获取当前对话历史（这里需要从 AgentLoop 获取，简化处理）
    console.print("[yellow]注意: 此命令需要与 AgentLoop 集成后才能使用[/yellow]")
    console.print("\n[bold]压缩器配置:[/bold]")
    console.print(f"  阈值: {compressor.compress_threshold} 条消息")
    console.print(f"  保留最近: {compressor.keep_recent} 条消息")
    console.print(f"  策略: {strategy}")


# === Window 命令 ===

window_app = typer.Typer(help="滑动窗口管理")


@window_app.command("set")
def set_window_size(
    size: int = typer.Argument(..., help="窗口大小"),
):
    """设置滑动窗口大小"""
    if size < 1:
        console.print("[red]窗口大小必须 >= 1[/red]")
        raise typer.Exit(1)

    window = get_sliding_window()
    window.set_window_size(size)

    console.print(f"[green]✓[/green] 窗口大小已设置为: {size}")


@window_app.command("show")
def show_window():
    """显示滑动窗口设置"""
    window = get_sliding_window()

    console.print("\n[bold]滑动窗口设置[/bold]")
    console.print(f"  窗口大小: {window.window_size}")
    console.print(f"  保护系统消息: {'是' if window.protect_system else '否'}")
    console.print(f"  保护标记消息: {'是' if window.protect_tagged else '否'}")


@window_app.command("apply")
def apply_window(
    preview: bool = typer.Option(False, "--preview", "-p", help="仅预览"),
    token_limit: int = typer.Option(None, "--token-limit", help="动态 token 限制"),
):
    """应用滑动窗口"""
    window = get_sliding_window()

    console.print("[yellow]注意: 此命令需要与 AgentLoop 集成后才能使用[/yellow]")

    stats = window.get_stats([])
    console.print(f"\n[bold]窗口统计[/bold]")
    console.print(f"  总消息数: {stats['total_messages']}")
    console.print(f"  窗口大小: {stats['window_size']}")


app.add_typer(window_app, name="window")


# === Checkpoint 命令 ===

checkpoint_app = typer.Typer(help="检查点管理")


@checkpoint_app.command("create")
def create_checkpoint(
    name: str = typer.Argument(..., help="检查点名称"),
):
    """创建检查点"""
    manager = get_checkpoint_manager()

    console.print("[yellow]注意: 此命令需要与 AgentLoop 集成后才能使用[/yellow]")
    console.print(f"\n检查点将保存到: {manager.checkpoint_dir / name}.json")


@checkpoint_app.command("list")
def list_checkpoints():
    """列出所有检查点"""
    manager = get_checkpoint_manager()
    checkpoints = manager.list()

    if not checkpoints:
        console.print("[yellow]没有检查点[/yellow]")
        console.print(f"\n检查点目录: {manager.checkpoint_dir}")
        return

    table = Table(title="检查点列表")
    table.add_column("名称", style="cyan")
    table.add_column("创建时间")
    table.add_column("消息数", justify="right")
    table.add_column("Token 数", justify="right")

    for cp in checkpoints:
        table.add_row(
            cp.name,
            cp.created_at,
            str(cp.message_count),
            str(cp.token_count),
        )

    console.print(table)


@checkpoint_app.command("restore")
def restore_checkpoint(
    name: str = typer.Argument(..., help="检查点名称"),
):
    """从检查点恢复"""
    manager = get_checkpoint_manager()

    if not manager.exists(name):
        console.print(f"[red]检查点不存在: {name}[/red]")
        raise typer.Exit(1)

    console.print("[yellow]注意: 此命令需要与 AgentLoop 集成后才能使用[/yellow]")

    messages, info = manager.load(name)
    console.print(f"\n[green]✓[/green] 检查点加载成功")
    console.print(f"  消息数: {info.message_count}")
    console.print(f"  Token 数: {info.token_count}")


@checkpoint_app.command("delete")
def delete_checkpoint(
    name: str = typer.Argument(..., help="检查点名称"),
    force: bool = typer.Option(False, "--force", "-f", help="强制删除，不确认"),
):
    """删除检查点"""
    manager = get_checkpoint_manager()

    if not manager.exists(name):
        console.print(f"[red]检查点不存在: {name}[/red]")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"确定要删除检查点 '{name}'?")
        if not confirm:
            console.print("[yellow]已取消[/yellow]")
            return

    if manager.delete(name):
        console.print(f"[green]✓[/green] 检查点已删除: {name}")
    else:
        console.print(f"[red]删除失败[/red]")


@checkpoint_app.command("export")
def export_checkpoint(
    name: str = typer.Argument(..., help="检查点名称"),
    output: str = typer.Option(None, "--output", "-o", help="输出文件路径"),
    format: str = typer.Option("markdown", "--format", "-f", help="导出格式: markdown/json"),
):
    """导出检查点"""
    manager = get_checkpoint_manager()

    if not manager.exists(name):
        console.print(f"[red]检查点不存在: {name}[/red]")
        raise typer.Exit(1)

    if format == "markdown":
        content = manager.export_to_markdown(name, output)
        if output:
            console.print(f"[green]✓[/green] 已导出到: {output}")
        else:
            console.print(Panel(content, title="导出内容", border_style="blue"))
    elif format == "json":
        messages, info = manager.load(name)
        import json
        data = {"info": info.to_dict(), "messages": messages}
        content = json.dumps(data, ensure_ascii=False, indent=2)

        if output:
            from pathlib import Path
            Path(output).write_text(content, encoding="utf-8")
            console.print(f"[green]✓[/green] 已导出到: {output}")
        else:
            console.print(content)
    else:
        console.print(f"[red]不支持的格式: {format}[/red]")


app.add_typer(checkpoint_app, name="checkpoint")


# === Stats 命令 ===

@app.command("stats")
def show_stats():
    """显示上下文统计信息"""
    compressor = get_compressor()
    window = get_sliding_window()
    checkpoint_manager = get_checkpoint_manager()

    console.print("\n[bold]上下文管理统计[/bold]\n")

    # 压缩器统计
    console.print("[bold cyan]压缩器[/bold cyan]")
    stats = compressor.get_compression_stats([])
    console.print(f"  压缩阈值: {stats['threshold']} 条消息")
    console.print(f"  保留最近: {stats['keep_recent']} 条消息")

    # 滑动窗口统计
    console.print("\n[bold cyan]滑动窗口[/bold cyan]")
    console.print(f"  窗口大小: {window.window_size}")
    console.print(f"  保护系统消息: {'是' if window.protect_system else '否'}")

    # 检查点统计
    console.print("\n[bold cyan]检查点[/bold cyan]")
    checkpoints = checkpoint_manager.list()
    console.print(f"  检查点数量: {len(checkpoints)}")
    console.print(f"  存储目录: {checkpoint_manager.checkpoint_dir}")


def create_compress_app() -> typer.Typer:
    """创建 compress 子应用"""
    return app
