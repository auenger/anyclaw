"""Sidecar command for Tauri desktop app.

Runs AnyClaw as a background service with HTTP API and SSE streaming.
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from pathlib import Path

import typer
from rich.console import Console

from anyclaw.api.server import run_server
from anyclaw.api.deps import set_serve_manager
from anyclaw.config.loader import get_config
from anyclaw.core.serve import ServeManager
from anyclaw.utils.logging_config import setup_logging, get_log_file_path

app = typer.Typer(help="Run AnyClaw as Tauri sidecar")
console = Console()


@app.command()
def sidecar(
    port: int = typer.Option(62601, "--port", "-p", help="HTTP server port"),
    data_dir: str = typer.Option(None, "--data-dir", "-d", help="Data directory"),
    log_level: str = typer.Option("info", "--log-level", help="Log level (debug, info, warning, error)"),
):
    """Run AnyClaw as Tauri sidecar.

    This mode starts:
    1. ServeManager (multi-channel service)
    2. FastAPI HTTP server (port)
    3. SSE event streaming

    Examples:
        anyclaw sidecar                    # Default port 62601
        anyclaw sidecar --port 8080        # Custom port
        anyclaw sidecar --log-level debug  # Debug logging
    """
    # Setup logging to file
    setup_logging(level=log_level, log_file=get_log_file_path())

    logger = logging.getLogger(__name__)
    logger.info(f"Starting AnyClaw sidecar on port {port}...")

    # Get config
    config = get_config()
    ws_path = Path(data_dir) if data_dir else None

    # Create serve manager
    manager = ServeManager(config=config, workspace=ws_path)
    set_serve_manager(manager)

    # Graceful shutdown
    shutdown_event = asyncio.Event()

    def signal_handler(sig, frame):
        logger.info("Received shutdown signal...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run both API server and channel service
    async def run_all():
        try:
            # Initialize serve manager
            manager.initialize()
            logger.info(f"ServeManager initialized with channels: {', '.join(manager.enabled_channels)}")

            # Start channel service
            await manager.start()
            logger.info("Channel service started")

            # Start API server (blocks until shutdown)
            console.print(f"\n[green]✓ AnyClaw sidecar running[/green]")
            console.print(f"[dim]  API: http://127.0.0.1:{port}[/dim]")
            console.print(f"[dim]  SSE: http://127.0.0.1:{port}/api/stream[/dim]")
            console.print(f"[dim]  Docs: http://127.0.0.1:{port}/docs[/dim]")
            console.print(f"[dim]  Channels: {', '.join(manager.enabled_channels)}[/dim]")
            console.print(f"[dim]  Press Ctrl+C to stop[/dim]\n")

            # Run API server (this blocks)
            run_server(host="127.0.0.1", port=port, log_level=log_level)

        except Exception as e:
            logger.error(f"Error running sidecar: {e}")
            raise
        finally:
            # Cleanup
            await manager.stop()
            logger.info("Sidecar stopped")

    asyncio.run(run_all())


if __name__ == "__main__":
    app()
