"""配置管理 CLI 命令"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from anyclaw.config.loader import (
    get_config,
    save_config,
    get_config_path,
    reload_config,
    Config,
    ProviderConfig,
)
from anyclaw.config.settings import settings

app = typer.Typer(help="配置管理")
console = Console()


@app.command("show")
def show_config():
    """显示当前配置"""
    config = get_config()

    console.print("\n[bold]AnyClaw 配置[/bold]\n")

    # Agent 配置
    table = Table(title="Agent")
    table.add_column("设置", style="cyan")
    table.add_column("值")
    table.add_row("名称", config.agent.name)
    table.add_row("工作区", config.agent.workspace)
    console.print(table)

    # LLM 配置
    table = Table(title="LLM")
    table.add_column("设置", style="cyan")
    table.add_column("值")
    table.add_row("Provider", config.llm.provider)
    table.add_row("Model", config.llm.model)
    table.add_row("Max Tokens", str(config.llm.max_tokens))
    table.add_row("Temperature", str(config.llm.temperature))
    console.print(table)

    # Provider 配置
    table = Table(title="Providers API Keys")
    table.add_column("Provider", style="cyan")
    table.add_column("API Key", style="dim")
    table.add_column("Base URL", style="dim")

    for name in ["openai", "anthropic", "zai", "deepseek", "openrouter"]:
        provider: ProviderConfig = getattr(config.providers, name)
        key = provider.api_key[:8] + "..." if provider.api_key else "(未设置)"
        base = provider.api_base or "(默认)"
        table.add_row(name, key, base)

    console.print(table)

    # 配置文件路径
    console.print(f"\n[dim]配置文件: {get_config_path()}[/dim]")


@app.command("set")
def set_config(
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="设置 provider 的 API key"),
    key: Optional[str] = typer.Argument(None, help="配置键 (如 openai.api_key)"),
    value: Optional[str] = typer.Argument(None, help="配置值"),
):
    """设置配置项

    示例:
        anyclaw config set openai.api_key sk-xxx
        anyclaw config set llm.model gpt-4o
        anyclaw config set -p openai sk-xxx
    """
    config = get_config()

    # 简化模式：-p provider key
    if provider and value is None and key:
        value = key
        key = f"{provider}.api_key"

    if not key or not value:
        console.print("[red]用法: anyclaw config set <key> <value>[/red]")
        console.print("[dim]示例: anyclaw config set openai.api_key sk-xxx[/dim]")
        raise typer.Exit(1)

    # 解析 key
    parts = key.split(".")
    if len(parts) != 2:
        console.print(f"[red]无效的配置键: {key}[/red]")
        console.print("[dim]格式应为: <section>.<field> (如 openai.api_key)[/dim]")
        raise typer.Exit(1)

    section, field = parts

    # 设置值
    if section == "llm":
        if hasattr(config.llm, field):
            # 类型转换
            current_val = getattr(config.llm, field)
            if isinstance(current_val, int):
                value = int(value)
            elif isinstance(current_val, float):
                value = float(value)
            setattr(config.llm, field, value)
        else:
            console.print(f"[red]未知的 LLM 配置项: {field}[/red]")
            raise typer.Exit(1)
    elif section == "agent":
        if hasattr(config.agent, field):
            setattr(config.agent, field, value)
        else:
            console.print(f"[red]未知的 Agent 配置项: {field}[/red]")
            raise typer.Exit(1)
    elif hasattr(config.providers, section):
        provider_config = getattr(config.providers, section)
        if hasattr(provider_config, field):
            setattr(provider_config, field, value)
        else:
            console.print(f"[red]未知的 Provider 配置项: {field}[/red]")
            raise typer.Exit(1)
    else:
        console.print(f"[red]未知的配置段: {section}[/red]")
        raise typer.Exit(1)

    # 保存配置
    save_config(config)
    console.print(f"[green]✓[/green] 已设置 {key} = {value[:8]}..." if len(value) > 8 else f"[green]✓[/green] 已设置 {key} = {value}")


@app.command("init")
def init_config():
    """初始化配置文件"""
    config_path = get_config_path()

    if config_path.exists():
        console.print(f"[yellow]配置文件已存在: {config_path}[/yellow]")
        console.print("使用 [cyan]anyclaw config show[/cyan] 查看配置")
        return

    # 创建默认配置
    config = Config()
    save_config(config)

    console.print(f"[green]✓[/green] 已创建配置文件: {config_path}")
    console.print("\n[bold]下一步:[/bold]")
    console.print("  1. 编辑配置文件或使用命令设置 API key:")
    console.print("     [cyan]anyclaw config set openai.api_key sk-xxx[/cyan]")
    console.print("  2. 运行 [cyan]anyclaw chat[/cyan] 开始对话")


@app.command("path")
def show_path():
    """显示配置文件路径"""
    console.print(str(get_config_path()))


@app.command("edit")
def edit_config():
    """用编辑器打开配置文件"""
    import os
    import subprocess

    config_path = get_config_path()

    # 确保文件存在
    if not config_path.exists():
        config = Config()
        save_config(config)

    # 获取编辑器
    editor = os.environ.get("EDITOR", "nano")

    # 打开编辑器
    subprocess.run([editor, str(config_path)])


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """配置管理"""
    if ctx.invoked_subcommand is None:
        # 默认显示配置
        show_config()


def create_config_app() -> typer.Typer:
    """创建配置管理应用"""
    return app


@app.command("providers")
def list_providers():
    """列出可用的 providers"""
    from anyclaw.config.settings import settings

    console.print("\n[bold]Available Providers:[/bold]\n")

    table = Table()
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Default Model")

    # OpenAI
    table.add_row(
        "openai",
        "✓ Configured" if settings.get_api_key("openai") else "✗ Not configured",
        "gpt-4o-mini"
    )

    # Anthropic
    table.add_row(
        "anthropic",
        "✓ Configured" if settings.get_api_key("anthropic") else "✗ Not configured",
        "claude-3-5-sonnet"
    )

    # ZAI
    table.add_row(
        "zai",
        "✓ Configured" if settings.get_api_key("zai") else "✗ Not configured",
        "zai/glm-5"
    )

    console.print(table)
    console.print("\n[dim]使用 'anyclaw config set openai.api_key sk-xxx' 设置 API key[/dim]")
