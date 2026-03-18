"""Token CLI 命令"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from anyclaw.agent.token_counter import TokenCounter, get_token_counter
from anyclaw.agent.token_limiter import TokenLimiter, get_token_limiter
from anyclaw.config.settings import settings

app = typer.Typer(help="Token 管理命令")
console = Console()


@app.command("count")
def count_tokens(
    text: str = typer.Argument(..., help="要计算的文本"),
    model: str = typer.Option(None, "--model", "-m", help="模型名称"),
):
    """计算文本的 token 数量"""
    counter = TokenCounter(model or settings.llm_model)

    token_count = counter.count(text)

    console.print(f"\n[bold]Token 计数结果[/bold]")
    console.print(f"  文本长度: {len(text)} 字符")
    console.print(f"  Token 数: {token_count}")
    console.print(f"  编码器: {counter.encoding_name}")
    console.print(f"  tiktoken: {'可用' if counter.tiktoken_available else '不可用 (使用估算)'}")


@app.command("stats")
def show_stats(
    text: str = typer.Option(None, "--text", "-t", help="示例文本"),
    model: str = typer.Option(None, "--model", "-m", help="模型名称"),
):
    """显示 token 统计信息"""
    model = model or settings.llm_model
    counter = TokenCounter(model)

    console.print(f"\n[bold]Token 统计[/bold]")
    console.print(f"  模型: {model}")
    console.print(f"  编码器: {counter.encoding_name}")
    console.print(f"  上下文窗口: {counter.get_context_window():,}")
    console.print(f"  tiktoken: {'✓ 可用' if counter.tiktoken_available else '✗ 不可用'}")

    if text:
        token_count = counter.count(text)
        console.print(f"\n[bold]示例文本[/bold]")
        console.print(f"  字符数: {len(text)}")
        console.print(f"  Token 数: {token_count}")


@app.command("limit")
def manage_limits(
    soft: int = typer.Option(None, "--soft", "-s", help="软限制"),
    hard: int = typer.Option(None, "--hard", "-h", help="硬限制"),
    show: bool = typer.Option(False, "--show", help="显示当前限制"),
):
    """管理 token 限制"""
    limiter = get_token_limiter()

    if show or (soft is None and hard is None):
        # 显示当前限制
        table = Table(title="Token 限制设置")
        table.add_column("设置", style="cyan")
        table.add_column("值", justify="right")

        table.add_row("软限制", f"{limiter.soft_limit:,}")
        table.add_row("硬限制", f"{limiter.hard_limit:,}")
        table.add_row("警告阈值", f"{limiter.warning_threshold * 100:.0f}%")
        table.add_row("警告启用", "是" if limiter.warning_enabled else "否")

        console.print(table)
        return

    # 更新限制
    if soft is not None:
        limiter.soft_limit = soft
        console.print(f"[green]✓[/green] 软限制已设置为: {soft:,}")

    if hard is not None:
        limiter.hard_limit = hard
        console.print(f"[green]✓[/green] 硬限制已设置为: {hard:,}")


@app.command("warn")
def manage_warning(
    action: str = typer.Argument("status", help="操作: status/on/off"),
    threshold: float = typer.Option(None, "--threshold", "-t", help="警告阈值 (0.5-1.0)"),
):
    """管理 token 警告"""
    limiter = get_token_limiter()

    if action == "status":
        console.print(f"\n[bold]警告状态[/bold]")
        console.print(f"  启用: {'是' if limiter.warning_enabled else '否'}")
        console.print(f"  阈值: {limiter.warning_threshold * 100:.0f}%")

    elif action == "on":
        limiter.warning_enabled = True
        console.print("[green]✓[/green] Token 警告已启用")

        if threshold is not None:
            if 0.5 <= threshold <= 1.0:
                limiter.warning_threshold = threshold
                console.print(f"[green]✓[/green] 警告阈值已设置为: {threshold * 100:.0f}%")
            else:
                console.print("[red]阈值必须在 0.5 到 1.0 之间[/red]")

    elif action == "off":
        limiter.warning_enabled = False
        console.print("[yellow]Token 警告已禁用[/yellow]")

    else:
        console.print(f"[red]未知操作: {action}[/red]")
        console.print("可用操作: status, on, off")


@app.command("test")
def test_counter(
    model: str = typer.Option(None, "--model", "-m", help="模型名称"),
):
    """测试 token 计数器"""
    model = model or settings.llm_model
    counter = TokenCounter(model)

    console.print(f"\n[bold]Token 计数器测试[/bold]")
    console.print(f"模型: {model}")
    console.print(f"编码器: {counter.encoding_name}")

    # 测试文本
    test_texts = [
        "Hello, world!",
        "这是一个中文测试文本。",
        "The quick brown fox jumps over the lazy dog.",
        "人工智能正在改变世界，让我们一起探索未来。",
    ]

    table = Table(title="测试结果")
    table.add_column("文本", max_width=40)
    table.add_column("字符", justify="right")
    table.add_column("Token", justify="right")

    for text in test_texts:
        tokens = counter.count(text)
        table.add_row(text[:40] + "..." if len(text) > 40 else text, str(len(text)), str(tokens))

    console.print(table)


def create_token_app() -> typer.Typer:
    """创建 token 子应用"""
    return app
