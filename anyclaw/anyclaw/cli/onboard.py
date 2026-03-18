"""CLI Onboard 命令"""
import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from ..providers.zai_detect import list_available_endpoints
from ..providers.zai import ZAI_ENDPOINTS

console = Console()

# Auth choices 配置
AUTH_CHOICES = {
    "zai-coding-global": {
        "provider": "zai",
        "endpoint": "coding-global",
        "env_key": "ZAI_API_KEY",
        "model": "zai/glm-5",
        "description": "Z.AI GLM Coding Plan (Global)",
    },
    "zai-coding-cn": {
        "provider": "zai",
        "endpoint": "coding-cn",
        "env_key": "ZAI_API_KEY",
        "model": "zai/glm-5",
        "description": "Z.AI GLM Coding Plan (China)",
    },
    "zai-global": {
        "provider": "zai",
        "endpoint": "global",
        "env_key": "ZAI_API_KEY",
        "model": "zai/glm-5",
        "description": "Z.AI Global API",
    },
    "zai-cn": {
        "provider": "zai",
        "endpoint": "cn",
        "env_key": "ZAI_API_KEY",
        "model": "zai/glm-5",
        "description": "Z.AI China API",
    },
    "openai": {
        "provider": "openai",
        "endpoint": "default",
        "env_key": "OPENAI_API_KEY",
        "model": "gpt-4o-mini",
        "description": "OpenAI API",
    },
    "anthropic": {
        "provider": "anthropic",
        "endpoint": "default",
        "env_key": "ANTHROPIC_API_KEY",
        "model": "claude-3-5-sonnet-20241022",
        "description": "Anthropic API",
    },
}


def create_onboard_app() -> typer.Typer:
    """创建 onboard 子应用"""
    app = typer.Typer(help="Onboard configuration")

    @app.command("start")
    def onboard_start(
        auth_choice: str = typer.Option(
            None,
            "--auth-choice",
            "-a",
            help="Authentication choice (use --list-auth-choices to see options)",
        ),
        list_choices: bool = typer.Option(
            False,
            "--list-auth-choices",
            "-l",
            help="List available auth choices",
        ),
        api_key: Optional[str] = typer.Option(
            None,
            "--api-key",
            "-k",
            help="API key (will prompt if not provided)",
        ),
        model: Optional[str] = typer.Option(
            None,
            "--model",
            "-m",
            help="Default model",
        ),
        save: bool = typer.Option(
            True,
            "--save/--no-save",
            help="Save configuration to .env file",
        ),
    ):
        """Start onboard configuration"""

        if list_choices:
            show_auth_choices()
            return

        if not auth_choice:
            # 交互式选择
            auth_choice = prompt_auth_choice()

        if auth_choice not in AUTH_CHOICES:
            console.print(f"[red]Unknown auth choice: {auth_choice}[/red]")
            console.print("Use --list-auth-choices to see available options")
            raise typer.Exit(1)

        choice_config = AUTH_CHOICES[auth_choice]

        # 获取 API Key
        if not api_key:
            api_key = Prompt.ask(
                f"Enter your {choice_config['env_key']}",
                password=True,
            )

        if not api_key:
            console.print("[red]API key is required[/red]")
            raise typer.Exit(1)

        # 确定模型
        final_model = model or choice_config["model"]

        # 保存配置
        if save:
            save_config(choice_config, api_key, final_model)
        else:
            # 设置环境变量（当前会话）
            os.environ[choice_config["env_key"]] = api_key
            if choice_config["provider"] == "zai":
                os.environ["ZAI_ENDPOINT"] = choice_config["endpoint"]
            os.environ["LLM_MODEL"] = final_model

        console.print("\n[green]✓ Configuration complete![/green]")
        console.print(f"  Provider: {choice_config['provider']}")
        console.print(f"  Model: {final_model}")
        if choice_config["provider"] == "zai":
            console.print(f"  Endpoint: {choice_config['endpoint']}")

    @app.command("detect-zai")
    def detect_zai(
        api_key: Optional[str] = typer.Option(
            None,
            "--api-key",
            "-k",
            help="ZAI API key (uses env var if not provided)",
        ),
        save: bool = typer.Option(
            False,
            "--save",
            "-s",
            help="Save detected endpoint to .env",
        ),
    ):
        """Detect best ZAI endpoint"""
        from ..providers.zai_detect import detect_zai_endpoint

        if not api_key:
            from anyclaw.config.settings import settings
            api_key = settings.zai_api_key

        if not api_key:
            console.print("[red]No ZAI API key provided[/red]")
            console.print("Set ZAI_API_KEY or use --api-key option")
            raise typer.Exit(1)

        console.print("[yellow]Detecting best ZAI endpoint...[/yellow]")

        result = detect_zai_endpoint(api_key)

        if result.get("success"):
            console.print(f"\n[green]✓ Detected endpoint: {result['endpoint']}[/green]")
            console.print(f"  Base URL: {result['base_url']}")
            console.print(f"  Default Model: {result['default_model']}")
            console.print(f"  Description: {result.get('description', 'N/A')}")

            if save:
                update_env_file({
                    "ZAI_ENDPOINT": result["endpoint"],
                })
                console.print("\n[green]Saved to .env file[/green]")
        else:
            console.print(f"\n[yellow]Detection failed: {result.get('error')}[/yellow]")
            console.print("Using default endpoint: coding-global")

    return app


def show_auth_choices() -> None:
    """显示所有 auth choices"""
    table = Table(title="Available Auth Choices")
    table.add_column("Choice", style="cyan")
    table.add_column("Provider", style="green")
    table.add_column("Description")
    table.add_column("Default Model")

    for choice_id, config in AUTH_CHOICES.items():
        table.add_row(
            choice_id,
            config["provider"],
            config["description"],
            config["model"],
        )

    console.print(table)


def prompt_auth_choice() -> str:
    """交互式选择 auth choice"""
    console.print("\n[bold]Select your authentication method:[/bold]\n")

    choices = list(AUTH_CHOICES.keys())
    for i, choice in enumerate(choices, 1):
        config = AUTH_CHOICES[choice]
        console.print(f"  {i}. [cyan]{choice}[/cyan] - {config['description']}")

    console.print()

    selection = Prompt.ask(
        "Enter choice number or name",
        choices=choices + [str(i) for i in range(1, len(choices) + 1)],
    )

    # 支持数字选择
    if selection.isdigit():
        idx = int(selection) - 1
        if 0 <= idx < len(choices):
            return choices[idx]

    return selection


def save_config(
    choice_config: dict,
    api_key: str,
    model: str,
) -> None:
    """保存配置到 .env 文件"""
    env_vars = {
        choice_config["env_key"]: api_key,
        "LLM_MODEL": model,
    }

    if choice_config["provider"] == "zai":
        env_vars["ZAI_ENDPOINT"] = choice_config["endpoint"]

    update_env_file(env_vars)


def update_env_file(env_vars: dict) -> None:
    """更新 .env 文件"""
    env_path = Path(".env")

    # 读取现有内容
    existing = {}
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    existing[key.strip()] = value.strip()

    # 更新值
    existing.update(env_vars)

    # 写回文件
    with open(env_path, "w") as f:
        for key, value in existing.items():
            # 如果值包含空格或特殊字符，加引号
            if " " in value or any(c in value for c in ['"', "'", "#"]):
                value = f'"{value}"'
            f.write(f"{key}={value}\n")
