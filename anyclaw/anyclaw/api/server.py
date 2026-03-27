"""FastAPI server for AnyClaw HTTP API and SSE streaming."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from anyclaw.api.routes.health import router as health_router
from anyclaw.api.routes.agents import router as agents_router
from anyclaw.api.routes.chats import router as chats_router
from anyclaw.api.routes.messages import router as messages_router
from anyclaw.api.routes.skills import router as skills_router
from anyclaw.api.routes.tasks import router as tasks_router
from anyclaw.api.routes.memory import router as memory_router
from anyclaw.api.routes.logs import router as logs_router
from anyclaw.api.routes.providers import router as providers_router
from anyclaw.api.routes.cron import router as cron_router
from anyclaw.api.sse import router as sse_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("AnyClaw API server starting...")

    # Initialize log collector
    from anyclaw.utils.log_collector import get_log_collector
    collector = get_log_collector()
    collector.add_handler()
    collector.start_file_persistence()
    logger.info("Log collector initialized")

    yield

    # Shutdown
    logger.info("AnyClaw API server shutting down...")
    collector.stop_file_persistence()
    collector.remove_handler()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AnyClaw API",
        description="HTTP API and SSE streaming for AnyClaw desktop app",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware - allow Tauri WebView and Vite Dev Server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",           # Vite Dev Server
            "http://localhost:62601",          # AnyClaw API (self)
            "tauri://localhost",               # macOS Tauri WebView
            "http://tauri.localhost",          # Windows Tauri WebView
            "https://tauri.localhost",         # Linux Tauri WebView
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # Mount routers
    app.include_router(health_router, prefix="/api", tags=["Health"])
    app.include_router(agents_router, prefix="/api", tags=["Agents"])
    app.include_router(chats_router, prefix="/api", tags=["Chats"])
    app.include_router(messages_router, prefix="/api", tags=["Messages"])
    app.include_router(skills_router, prefix="/api", tags=["Skills"])
    app.include_router(tasks_router, prefix="/api", tags=["Tasks"])
    app.include_router(memory_router, prefix="/api", tags=["Memory"])
    app.include_router(logs_router, prefix="/api", tags=["Logs"])
    app.include_router(providers_router, prefix="/api", tags=["Providers"])
    app.include_router(cron_router, prefix="/api", tags=["Cron"])
    app.include_router(sse_router, prefix="/api", tags=["SSE"])

    return app


def run_server(
    host: str = "127.0.0.1",
    port: int = 62601,
    log_level: str = "info",
) -> None:
    """Run the API server with uvicorn.

    Args:
        host: Host to bind to
        port: Port to listen on
        log_level: Log level (debug, info, warning, error)
    """
    app = create_app()

    # Configure uvicorn
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level,
        access_log=True,
    )


# Create app instance for import
_app = create_app()
