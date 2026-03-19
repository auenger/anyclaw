"""Serve command for AnyClaw.

Usage:
    anyclaw serve                    # Start in foreground
    anyclaw serve --debug            # Debug mode
    anyclaw serve --daemon           # Background mode
    anyclaw serve --status           # Check status
    anyclaw serve --stop             # Stop daemon
    anyclaw serve --logs             # View logs
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from anyclaw.config.loader import get_config
from anyclaw.core.daemon import DaemonManager, setup_signal_handlers
from anyclaw.core.serve import ServeManager
from anyclaw.utils.logging_config import setup_logging, get_log_file_path

app = typer.Typer(help="Multi-channel serve mode")
console = Console()


@app.command()
def serve(
    debug: bool = typer.Option(
        False, "--debug", "-d", help="Enable debug logging (detailed timestamps)"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Minimal output (warnings and errors only)"
    ),
    daemon: bool = typer.Option(
        False, "--daemon", "-D", help="Run as background daemon"
    ),
    status: bool = typer.Option(
        False, "--status", help="Check daemon status"
    ),
    stop: bool = typer.Option(
        False, "--stop", help="Stop running daemon"
    ),
    logs: bool = typer.Option(
        False, "--logs", help="View daemon logs (follow mode)"
    ),
    workspace: Optional[str] = typer.Option(
        None, "--workspace", "-w", help="Workspace directory"
    ),
):
    """Start AnyClaw in multi-channel serve mode.

    This command starts all enabled channels (CLI, Discord, Feishu, etc.)
    and routes messages to the agent.

    Examples:
        anyclaw serve                  # Start in foreground
        anyclaw serve --debug          # Debug mode with detailed logs
        anyclaw serve --daemon         # Run in background
        anyclaw serve --status         # Check if daemon is running
        anyclaw serve --stop           # Stop background daemon
        anyclaw serve --logs           # Follow daemon logs
    """
    # Determine log level
    if debug:
        log_level = "debug"
    elif verbose:
        log_level = "verbose"
    elif quiet:
        log_level = "quiet"
    else:
        log_level = "info"

    # Handle status/stop/logs commands
    if status:
        _show_status()
        return

    if stop:
        _stop_daemon()
        return

    if logs:
        _follow_logs()
        return

    # Setup logging
    setup_logging(level=log_level, log_file=get_log_file_path())

    # Check if daemon is already running
    daemon_mgr = DaemonManager()
    if daemon_mgr.is_running():
        pid = daemon_mgr.read_pid()
        console.print(f"[yellow]AnyClaw daemon is already running (PID: {pid})[/yellow]")
        console.print("Use 'anyclaw serve --status' to check status")
        console.print("Use 'anyclaw serve --stop' to stop it")
        raise typer.Exit(1)

    if daemon:
        # Daemon mode
        _start_daemon(log_level, workspace)
    else:
        # Foreground mode
        _run_foreground(log_level, workspace)


def _show_status() -> None:
    """Show daemon status."""
    daemon_mgr = DaemonManager()
    status = daemon_mgr.get_status()

    if not status["running"]:
        console.print("[yellow]AnyClaw daemon is not running[/yellow]")
        raise typer.Exit(0)

    # Display status table
    table = Table(title="AnyClaw Daemon Status", show_header=False)
    table.add_column("Key", style="cyan")
    table.add_column("Value")

    table.add_row("PID", str(status["pid"]))
    table.add_row("Uptime", str(status["uptime"]))
    table.add_row("Memory", f"{status['memory_mb']} MB")
    table.add_row("Channels", ", ".join(status["channels"]) or "None")
    table.add_row("Messages", str(status["messages_processed"]))

    console.print(table)
    console.print(f"\n[dim]Use 'anyclaw serve --logs' to view logs[/dim]")


def _stop_daemon() -> None:
    """Stop running daemon."""
    daemon_mgr = DaemonManager()

    if not daemon_mgr.is_running():
        console.print("[yellow]AnyClaw daemon is not running[/yellow]")
        return

    pid = daemon_mgr.read_pid()
    console.print(f"[dim]Stopping AnyClaw daemon (PID: {pid})...[/dim]")

    if daemon_mgr.stop(timeout=30):
        console.print("[green]✓ Stopped[/green]")
    else:
        console.print("[red]Failed to stop daemon[/red]")
        raise typer.Exit(1)


def _follow_logs() -> None:
    """Follow daemon logs."""
    log_file = get_log_file_path()

    if not log_file.exists():
        console.print("[yellow]No log file found[/yellow]")
        console.print(f"[dim]Expected: {log_file}[/dim]")
        raise typer.Exit(1)

    console.print(f"[dim]Following {log_file} (Ctrl+C to exit)...[/dim]\n")

    # Use tail -f equivalent
    import subprocess
    try:
        subprocess.run(["tail", "-f", str(log_file)])
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped following logs[/dim]")


def _start_daemon(log_level: str, workspace: Optional[str]) -> None:
    """Start daemon in background."""
    daemon_mgr = DaemonManager()

    console.print("[dim]Starting AnyClaw daemon...[/dim]")

    # Check platform
    if sys.platform == "win32":
        console.print("[red]Daemon mode is not supported on Windows[/red]")
        console.print("[dim]Use 'anyclaw serve' without --daemon for foreground mode[/dim]")
        raise typer.Exit(1)

    try:
        # Fork to background
        if daemon_mgr.daemonize():
            # This is the daemon process
            # Setup logging
            setup_logging(level=log_level, log_file=get_log_file_path())

            # Run serve manager
            asyncio.run(_run_serve_manager(workspace))

    except RuntimeError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def _run_foreground(log_level: str, workspace: Optional[str]) -> None:
    """Run in foreground."""
    console.print("\n[bold blue]Starting AnyClaw Serve Mode[/bold blue]\n")

    # Write PID file for foreground mode too (for status/stop commands)
    daemon_mgr = DaemonManager()
    daemon_mgr.write_pid()

    try:
        asyncio.run(_run_serve_manager(workspace))
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")
    finally:
        # Clean up PID file on exit
        daemon_mgr.remove_pid()


async def _run_serve_manager(workspace: Optional[str]) -> None:
    """Run the serve manager."""
    import logging

    logger = logging.getLogger(__name__)

    # Get config
    config = get_config()
    ws_path = Path(workspace) if workspace else None

    # Create serve manager
    manager = ServeManager(
        config=config,
        workspace=ws_path,
    )

    # Setup signal handlers for graceful shutdown
    async def shutdown():
        logger.info("Shutting down...")
        await manager.stop()

    setup_signal_handlers(shutdown)

    try:
        # Initialize
        manager.initialize()

        # Show startup info
        console.print(f"[green]Enabled channels:[/green] {', '.join(manager.enabled_channels)}")
        console.print(f"[dim]Workspace: {manager.workspace}[/dim]")
        console.print(f"[dim]Press Ctrl+C to stop[/dim]\n")

        # Start serving
        await manager.start()

    except RuntimeError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        await manager.stop()


if __name__ == "__main__":
    app()
