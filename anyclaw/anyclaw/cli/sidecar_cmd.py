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
import uvicorn
from rich.console import Console

from anyclaw.api.server import create_app
from anyclaw.api.deps import set_serve_manager, set_agent_manager, set_cron_service, set_cron_log_store
from anyclaw.config.loader import get_config
from anyclaw.core.serve import ServeManager
from anyclaw.agents.manager import AgentManager
from anyclaw.agents.identity import IdentityManager
from anyclaw.cron.service import CronService
from anyclaw.cron.logs import CronLogStore
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

    # Create agent manager
    workspace_path = ws_path or Path.home() / ".anyclaw" / "workspace"
    identity_manager = IdentityManager(workspace_path)
    agent_manager = AgentManager(workspace_path, identity_manager)

    # Create cron service
    data_path = workspace_path / "data"
    data_path.mkdir(parents=True, exist_ok=True)
    cron_service = CronService(
        store_path=data_path / "cron_jobs.json",
        log_store=CronLogStore(data_path / "cron_logs.jsonl"),
    )

    # Inject into API deps
    set_agent_manager(agent_manager)
    set_cron_service(cron_service)
    set_cron_log_store(cron_service.log_store)

    # Graceful shutdown
    shutdown_event = asyncio.Event()

    def signal_handler(sig, frame):
        logger.info("Received shutdown signal...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run both API server and channel service in parallel
    async def run_all():
        try:
            # Initialize serve manager
            manager.initialize()
            logger.info(f"ServeManager initialized with channels: {', '.join(manager.enabled_channels)}")

            # Load all agents
            await agent_manager.load_all_agents()
            logger.info(f"AgentManager loaded {len(agent_manager._agents)} agents")

            # Start cron service
            await cron_service.start()
            logger.info("CronService started")

            # Start channel service in background (don't await - it blocks)
            manager_task = asyncio.create_task(manager.start())
            logger.info("Channel service starting in background...")

            # Give channels a moment to start
            await asyncio.sleep(0.5)

            console.print(f"\n[green]✓ AnyClaw sidecar running[/green]")
            console.print(f"[dim]  API: http://127.0.0.1:{port}[/dim]")
            console.print(f"[dim]  SSE: http://127.0.0.1:{port}/api/stream[/dim]")
            console.print(f"[dim]  Docs: http://127.0.0.1:{port}/docs[/dim]")
            console.print(f"[dim]  Channels: {', '.join(manager.enabled_channels)}[/dim]")
            console.print(f"[dim]  Press Ctrl+C to stop[/dim]\n")

            # Create FastAPI app
            fastapi_app = create_app()

            # Run API server with async uvicorn (this blocks until shutdown)
            config = uvicorn.Config(
                fastapi_app,
                host="127.0.0.1",
                port=port,
                log_level=log_level,
                access_log=True,
            )
            server = uvicorn.Server(config)
            await server.serve()

        except Exception as e:
            logger.error(f"Error running sidecar: {e}")
            raise
        finally:
            # Cleanup
            cron_service.stop()
            await manager.stop()
            logger.info("Sidecar stopped")

    asyncio.run(run_all())


if __name__ == "__main__":
    app()
