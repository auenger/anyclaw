"""MCP CLI 命令"""

import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from anyclaw.config.settings import settings

app = typer.Typer(help="MCP Server 管理")
console = Console()


@app.command("list")
def list_servers():
    """列出配置的 MCP Servers"""
    mcp_servers = settings.mcp_servers

    if not mcp_servers:
        console.print("[yellow]没有配置 MCP Server[/yellow]")
        console.print("\n[dim]在配置文件中添加 mcp_servers 配置，例如:[/dim]")
        console.print("""[dim]
{
  "mcp_servers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "~"]
    }
  }
}
[/dim]""")
        return

    table = Table(title="MCP Servers")
    table.add_column("名称", style="cyan")
    table.add_column("类型", style="green")
    table.add_column("地址/命令", style="dim")
    table.add_column("超时", justify="right")
    table.add_column("启用工具")

    for name, cfg in mcp_servers.items():
        transport_type = cfg.get_effective_type() or "unknown"

        if transport_type == "stdio":
            location = f"{cfg.command} {' '.join(cfg.args)}".strip()
        else:
            location = cfg.url

        enabled_tools = cfg.enabled_tools
        if "*" in enabled_tools:
            tools_str = "* (全部)"
        elif not enabled_tools:
            tools_str = "无"
        else:
            tools_str = ", ".join(enabled_tools[:3])
            if len(enabled_tools) > 3:
                tools_str += f" (+{len(enabled_tools) - 3})"

        table.add_row(
            name,
            transport_type,
            location[:50] + "..." if len(location) > 50 else location,
            f"{cfg.tool_timeout}s",
            tools_str
        )

    console.print(table)


@app.command("test")
def test_server(
    name: str = typer.Argument(..., help="MCP Server 名称"),
    timeout: int = typer.Option(10, "--timeout", "-t", help="连接超时（秒）")
):
    """测试 MCP Server 连接"""
    mcp_servers = settings.mcp_servers

    if name not in mcp_servers:
        console.print(f"[red]错误: MCP Server '{name}' 未配置[/red]")
        console.print(f"\n可用的 servers: {', '.join(mcp_servers.keys()) or '无'}")
        raise typer.Exit(1)

    cfg = mcp_servers[name]
    console.print(f"\n[bold]测试 MCP Server: {name}[/bold]")
    console.print(f"类型: {cfg.get_effective_type()}")
    console.print(f"超时: {timeout}s\n")

    async def do_test():
        from contextlib import AsyncExitStack
        from anyclaw.tools.mcp import connect_mcp_servers
        from anyclaw.tools.registry import ToolRegistry

        registry = ToolRegistry()
        stack = AsyncExitStack()

        try:
            # 设置超时
            async with asyncio.timeout(timeout):
                async with stack:
                    await connect_mcp_servers({name: cfg}, registry, stack)

            # 显示结果
            tools = registry.tool_names
            if tools:
                console.print(f"[green]✓ 连接成功[/green]")
                console.print(f"\n注册的工具 ({len(tools)}):")
                for tool in tools[:20]:  # 最多显示 20 个
                    console.print(f"  • {tool}")
                if len(tools) > 20:
                    console.print(f"  [dim]... 还有 {len(tools) - 20} 个工具[/dim]")
            else:
                console.print("[yellow]✓ 连接成功，但没有注册任何工具[/yellow]")

        except asyncio.TimeoutError:
            console.print(f"[red]✗ 连接超时（{timeout}s）[/red]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]✗ 连接失败: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(do_test())


def create_mcp_app() -> typer.Typer:
    """创建 MCP CLI 应用"""
    return app
