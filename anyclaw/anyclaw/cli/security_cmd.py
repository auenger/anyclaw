"""Security 命令模块"""

from typing import Optional, Tuple

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from anyclaw.tools.guards import CoreGuard, CommandGuard
from anyclaw.config.settings import settings


def create_security_app() -> typer.Typer:
    """创建 security 子命令应用"""
    app = typer.Typer(
        name="security",
        help="安全策略管理命令"
    )
    console = Console()

    @app.command("show")
    def show_rules():
        """显示当前安全规则"""
        console.print()

        # 获取核心保护规则
        core_patterns = CoreGuard.get_patterns()

        # 创建核心规则表格
        core_table = Table(
            title="[bold red]核心保护规则 [CoreGuard][/bold red]",
            show_header=True,
            header_style="bold cyan"
        )
        core_table.add_column("模式", style="dim")
        core_table.add_column("说明", style="yellow")

        for pattern, description in core_patterns:
            core_table.add_row(pattern, description)

        console.print(core_table)
        console.print("[dim]核心保护规则不可通过配置绕过[/dim]\n")

        # 获取用户配置
        user_deny = settings.exec_deny_patterns
        user_allow = settings.exec_allow_patterns

        # 创建用户规则表格
        user_table = Table(
            title="[bold blue]用户自定义规则 [UserGuard][/bold blue]",
            show_header=True,
            header_style="bold cyan"
        )
        user_table.add_column("类型", style="cyan")
        user_table.add_column("模式", style="dim")
        user_table.add_column("状态", style="green")

        if user_deny:
            for pattern in user_deny:
                user_table.add_row("deny", pattern, "✓ 启用")
        else:
            user_table.add_row("deny", "(空)", "未配置")

        if user_allow:
            for pattern in user_allow:
                user_table.add_row("allow", pattern, "✓ 启用")
            user_table.add_row("", "", "[yellow]白名单模式已启用[/yellow]")
        else:
            user_table.add_row("allow", "(空)", "未配置")

        console.print(user_table)

        # 显示配置路径
        console.print(f"\n[dim]配置文件: ~/.anyclaw/config.json[/dim]")
        console.print("[dim]配置项: exec_deny_patterns / exec_allow_patterns[/dim]")

    @app.command("test")
    def test_command(
        command: str = typer.Argument(..., help="要测试的命令"),
    ):
        """测试命令是否会被安全策略阻止"""
        console.print()

        # 创建命令保护器
        guard = CommandGuard(
            user_deny_patterns=settings.exec_deny_patterns,
            user_allow_patterns=settings.exec_allow_patterns,
        )

        # 检查命令
        blocked, reason = guard.check(command)

        if blocked:
            console.print(Panel(
                f"[red]✗ 被阻止[/red]\n\n命令: [dim]{command}[/dim]\n原因: [yellow]{reason}[/yellow]",
                title="安全检查结果",
                border_style="red"
            ))
        else:
            console.print(Panel(
                f"[green]✓ 允许执行[/green]\n\n命令: [dim]{command}[/dim]",
                title="安全检查结果",
                border_style="green"
            ))

    @app.command("list")
    def list_patterns():
        """列出所有安全模式（简洁版）"""
        console.print()

        # 核心保护
        console.print("[bold red]核心保护 [CoreGuard]:[/bold red]")
        for pattern, description in CoreGuard.get_patterns():
            console.print(f"  [dim]{pattern}[/dim] - {description}")

        # 用户配置
        console.print("\n[bold blue]用户规则 [UserGuard]:[/bold blue]")

        if settings.exec_deny_patterns:
            console.print("  deny_patterns:")
            for p in settings.exec_deny_patterns:
                console.print(f"    [dim]- {p}[/dim]")
        else:
            console.print("  deny_patterns: [dim](未配置)[/dim]")

        if settings.exec_allow_patterns:
            console.print("  allow_patterns:")
            for p in settings.exec_allow_patterns:
                console.print(f"    [dim]- {p}[/dim]")
            console.print("  [yellow]⚠ 白名单模式已启用[/yellow]")
        else:
            console.print("  allow_patterns: [dim](未配置)[/dim]")

    return app
