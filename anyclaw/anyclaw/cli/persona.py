"""Persona CLI 命令"""

import os
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from anyclaw.workspace.persona import PersonaLoader, get_persona_loader
from anyclaw.workspace.manager import WorkspaceManager
from anyclaw.workspace.templates import (
    SOUL_TEMPLATE,
    USER_TEMPLATE,
    IDENTITY_TEMPLATE,
    TOOLS_TEMPLATE,
)

app = typer.Typer(help="人设管理命令")
console = Console()


@app.command("show")
def show_persona(
    file: str = typer.Argument(
        None,
        help="要显示的文件 (soul/user/identity/tools)，不指定则显示所有",
    ),
    private: bool = typer.Option(True, "--private/--public", help="是否为私密会话"),
):
    """显示当前人设"""
    loader = get_persona_loader()

    if file:
        # 显示单个文件
        file_map = {
            "soul": loader.SOUL_FILE,
            "user": loader.USER_FILE,
            "identity": loader.IDENTITY_FILE,
            "tools": loader.TOOLS_FILE,
        }

        if file.lower() not in file_map:
            console.print(f"[red]未知文件: {file}[/red]")
            console.print(f"可用文件: {', '.join(file_map.keys())}")
            raise typer.Exit(1)

        content = loader._load_file(file_map[file.lower()])
        if content:
            console.print(Panel(content, title=file_map[file.lower()], border_style="blue"))
        else:
            console.print(f"[yellow]文件 {file_map[file.lower()]} 不存在[/yellow]")
    else:
        # 显示系统提示预览
        system_prompt = loader.build_system_prompt(is_private=private)

        if system_prompt:
            console.print(Panel(system_prompt, title="系统提示预览", border_style="green"))
        else:
            console.print("[yellow]没有人设文件存在[/yellow]")


@app.command("edit")
def edit_persona(
    file: str = typer.Argument(..., help="要编辑的文件 (soul/user/identity/tools)"),
):
    """编辑人设文件（打开编辑器）"""
    loader = get_persona_loader()

    file_map = {
        "soul": loader.SOUL_FILE,
        "user": loader.USER_FILE,
        "identity": loader.IDENTITY_FILE,
        "tools": loader.TOOLS_FILE,
    }

    if file.lower() not in file_map:
        console.print(f"[red]未知文件: {file}[/red]")
        console.print(f"可用文件: {', '.join(file_map.keys())}")
        raise typer.Exit(1)

    # 确保文件存在
    loader.create_default_files()

    filepath = loader.workspace.path / file_map[file.lower()]

    # 使用系统编辑器
    editor = os.environ.get("EDITOR", "nano")

    try:
        subprocess.run([editor, str(filepath)], check=True)
        console.print(f"[green]✓[/green] 已编辑 {file_map[file.lower()]}")
        loader.clear_cache()
    except subprocess.CalledProcessError:
        console.print(f"[red]编辑器启动失败[/red]")
        raise typer.Exit(1)
    except FileNotFoundError:
        console.print(f"[red]编辑器 {editor} 未找到[/red]")
        console.print(f"[dim]文件路径: {filepath}[/dim]")
        raise typer.Exit(1)


@app.command("reset")
def reset_persona(
    file: str = typer.Argument(
        None,
        help="要重置的文件 (soul/user/identity/tools)，不指定则重置所有",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="强制重置，不询问确认"),
):
    """重置人设文件为默认模板"""
    loader = get_persona_loader()

    file_map = {
        "soul": (loader.SOUL_FILE, SOUL_TEMPLATE),
        "user": (loader.USER_FILE, USER_TEMPLATE),
        "identity": (loader.IDENTITY_FILE, IDENTITY_TEMPLATE),
        "tools": (loader.TOOLS_FILE, TOOLS_TEMPLATE),
    }

    if file:
        if file.lower() not in file_map:
            console.print(f"[red]未知文件: {file}[/red]")
            console.print(f"可用文件: {', '.join(file_map.keys())}")
            raise typer.Exit(1)

        files_to_reset = {file.lower(): file_map[file.lower()]}
    else:
        files_to_reset = file_map

    for name, (filename, template) in files_to_reset.items():
        filepath = loader.workspace.path / filename

        if filepath.exists() and not force:
            console.print(f"[yellow]跳过 {filename}（已存在，使用 --force 强制重置）[/yellow]")
            continue

        filepath.write_text(template, encoding="utf-8")
        console.print(f"[green]✓[/green] 已重置 {filename}")

    loader.clear_cache()


@app.command("build")
def build_persona(
    private: bool = typer.Option(True, "--private/--public", help="是否为私密会话"),
    output: str = typer.Option(None, "--output", "-o", help="输出到文件"),
):
    """构建系统提示预览"""
    loader = get_persona_loader()
    system_prompt = loader.build_system_prompt(is_private=private)

    if not system_prompt:
        console.print("[yellow]没有人设文件存在[/yellow]")
        console.print("\n[dim]运行 'anyclaw persona reset' 创建默认模板[/dim]")
        return

    if output:
        Path(output).write_text(system_prompt, encoding="utf-8")
        console.print(f"[green]✓[/green] 系统提示已保存到 {output}")
    else:
        console.print(Panel(system_prompt, title="系统提示", border_style="green"))


@app.command("status")
def show_status():
    """显示人设状态"""
    loader = get_persona_loader()
    status = loader.get_status()

    console.print(f"\n[bold]人设状态[/bold]")
    console.print(f"工作区: {status['workspace_path']}")
    console.print(f"最大字符数: {status['max_chars']}")

    table = Table(title="文件状态")
    table.add_column("文件", style="cyan")
    table.add_column("状态")
    table.add_column("大小", justify="right")

    for filename, info in status["files"].items():
        if info["exists"]:
            size = f"{info['size']} bytes"
            status_str = "[green]✓ 存在[/green]"
        else:
            size = "-"
            status_str = "[yellow]✗ 不存在[/yellow]"

        table.add_row(filename, status_str, size)

    console.print(table)


def create_persona_app() -> typer.Typer:
    """创建 persona 子应用"""
    return app
