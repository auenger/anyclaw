"""配置管理 CLI 命令"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from anyclaw.config.loader import (
    get_config,
    save_config,
    get_config_path,
    reload_config,
    init_config,
    get_template_path,
    Config,
    ProviderConfig,
)
from anyclaw.config.settings import settings

app = typer.Typer(help="配置管理")
console = Console()


def _mask_api_key(key: str, visible_chars: int = 4) -> str:
    """脱敏 API Key

    Args:
        key: 原始 API Key
        visible_chars: 可见的末尾字符数

    Returns:
        脱敏后的 API Key
    """
    if not key:
        return "(未设置)"
    if len(key) <= visible_chars:
        return "***"
    return f"***{key[-visible_chars:]}"


@app.command("show")
def show_config(
    reveal: bool = typer.Option(False, "--reveal", "-r", help="显示完整的 API Key（慎用）")
):
    """显示当前配置

    默认会脱敏显示敏感信息（API Key 等）。
    使用 --reveal 选项可显示完整信息（慎用）。
    """
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
        if reveal:
            key = provider.api_key or "(未设置)"
        else:
            key = _mask_api_key(provider.api_key)
        base = provider.api_base or "(默认)"
        table.add_row(name, key, base)

    console.print(table)

    # Channels 配置
    table = Table(title="IM Channels")
    table.add_column("Channel", style="cyan")
    table.add_column("Enabled", style="green")
    table.add_column("配置状态", style="dim")

    # CLI
    cli_status = "✓" if config.channels.cli.enabled else "✗"
    table.add_row("CLI", cli_status, "默认启用")

    # Feishu
    feishu = config.channels.feishu
    feishu_status = "✓" if feishu.enabled else "✗"
    feishu_configured = "已配置" if feishu.app_id and feishu.app_secret else "未配置"
    table.add_row("Feishu", feishu_status, feishu_configured)

    # Discord
    discord = config.channels.discord
    discord_status = "✓" if discord.enabled else "✗"
    if reveal:
        discord_configured = discord.token or "未配置"
    else:
        discord_configured = "已配置" if discord.token else "未配置"
    table.add_row("Discord", discord_status, discord_configured)

    console.print(table)

    # 配置文件路径
    config_path = get_config_path()
    console.print(f"\n[dim]配置文件: {config_path}[/dim]")

    if not reveal:
        console.print("[dim]提示: 使用 --reveal 选项显示完整 API Key（慎用）[/dim]")


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
        anyclaw config set feishu.enabled true
        anyclaw config set discord.token your_token
    """
    config = get_config()

    # 简化模式：-p provider key
    if provider and value is None and key:
        value = key
        key = f"{provider}.api_key"

    if not key or not value:
        console.print("[red]用法: anyclaw config set <key> <value>[/red]")
        console.print("[dim]示例: anyclaw config set openai.api_key sk-xxx[/dim]")
        console.print("[dim]示例: anyclaw config set feishu.enabled true[/dim]")
        raise typer.Exit(1)

    # 解析 key
    parts = key.split(".")
    if len(parts) != 2:
        console.print(f"[red]无效的配置键: {key}[/red]")
        console.print("[dim]格式应为: <section>.<field> (如 openai.api_key)[/dim]")
        raise typer.Exit(1)

    section, field = parts

    # 类型转换函数
    def convert_value(value: str, current_val):
        """根据当前值类型转换新值"""
        if isinstance(current_val, bool):
            return value.lower() in ("true", "1", "yes", "on")
        elif isinstance(current_val, int):
            return int(value)
        elif isinstance(current_val, float):
            return float(value)
        return value

    # 设置值
    if section == "llm":
        if hasattr(config.llm, field):
            current_val = getattr(config.llm, field)
            value = convert_value(value, current_val)
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
    elif section == "feishu":
        if hasattr(config.channels.feishu, field):
            current_val = getattr(config.channels.feishu, field)
            value = convert_value(value, current_val)
            setattr(config.channels.feishu, field, value)
        else:
            console.print(f"[red]未知的 Feishu 配置项: {field}[/red]")
            console.print("[dim]可用字段: enabled, app_id, app_secret, encrypt_key, verification_token[/dim]")
            raise typer.Exit(1)
    elif section == "discord":
        if hasattr(config.channels.discord, field):
            current_val = getattr(config.channels.discord, field)
            value = convert_value(value, current_val)
            setattr(config.channels.discord, field, value)
        else:
            console.print(f"[red]未知的 Discord 配置项: {field}[/red]")
            console.print("[dim]可用字段: enabled, token, group_policy[/dim]")
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
        console.print("[dim]可用配置段: llm, agent, feishu, discord, openai, anthropic, zai, deepseek, openrouter[/dim]")
        raise typer.Exit(1)

    # 保存配置
    save_config(config)
    value_str = str(value)
    console.print(f"[green]✓[/green] 已设置 {key} = {value_str[:8]}..." if len(value_str) > 8 else f"[green]✓[/green] 已设置 {key} = {value_str}")


@app.command("init")
def init_config_cmd(
    force: bool = typer.Option(False, "--force", "-f", help="强制覆盖现有配置"),
    format: str = typer.Option("toml", "--format", "-F", help="配置格式: toml 或 json"),
):
    """初始化配置文件

    创建带有详细注释的配置模板文件。
    """
    config_path = init_config(force=force, format=format)

    if force or not config_path.exists():
        console.print(f"[green]✓[/green] 已创建配置文件: {config_path}")
    else:
        console.print(f"[yellow]配置文件已存在: {config_path}[/yellow]")
        console.print("使用 [cyan]--force[/cyan] 选项覆盖")

    console.print("\n[bold]下一步:[/bold]")
    console.print("  1. 编辑配置文件:")
    console.print(f"     [cyan]anyclaw config edit[/cyan]")
    console.print("  2. 或使用命令设置 API key:")
    console.print("     [cyan]anyclaw config set openai.api_key sk-xxx[/cyan]")
    console.print("  3. 运行 [cyan]anyclaw chat[/cyan] 开始对话")


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
        init_config(force=False)

    # 获取编辑器
    editor = os.environ.get("EDITOR", "nano")

    # 打开编辑器
    subprocess.run([editor, str(config_path)])


@app.command("template")
def show_template():
    """显示配置模板"""
    template_path = get_template_path()

    if not template_path.exists():
        console.print("[red]配置模板文件不存在[/red]")
        raise typer.Exit(1)

    with open(template_path, encoding="utf-8") as f:
        content = f.read()

    syntax = Syntax(content, "toml", theme="monokai", line_numbers=True)
    console.print(syntax)


@app.command("migrate")
def migrate_config(
    format: str = typer.Option("toml", "--format", "-F", help="目标格式: toml 或 json"),
):
    """迁移配置文件格式

    将现有 JSON 配置转换为 TOML 格式（推荐）。
    """
    config = get_config()

    # 确定新配置路径
    config_dir = get_config_path().parent
    if format == "toml":
        new_path = config_dir / "config.toml"
    else:
        new_path = config_dir / "config.json"

    # 保存新格式
    save_config(config, new_path, format=format)

    console.print(f"[green]✓[/green] 配置已迁移到: {new_path}")

    # 如果是从 JSON 迁移到 TOML，询问是否删除旧文件
    old_json = config_dir / "config.json"
    if format == "toml" and old_json.exists():
        console.print(f"\n[dim]旧的 JSON 配置文件保留在: {old_json}[/dim]")
        console.print("[dim]确认无误后可手动删除[/dim]")


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
