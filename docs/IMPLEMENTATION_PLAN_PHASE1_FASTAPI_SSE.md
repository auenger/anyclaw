# 实施计划 Phase 1: FastAPI + SSE

> **目标**：实现 AnyClaw 的 HTTP API 层和 SSE 流式事件，为 Tauri 前端提供数据接口

## 📋 概述

**时间估算**：2-3 天
**优先级**：P0（必须）
**依赖**：AnyClaw 现有核心功能（ServeManager, MessageBus, AgentLoop）

## 🎯 核心目标

1. ✅ 创建 FastAPI 服务器
2. ✅ 暴露核心 API 端点
3. ✅ 实现 SSE 流式事件
4. ✅ 集成到 ServeManager
5. ✅ 提供 Swagger API 文档

---

## 📂 目录结构

```
anyclaw/
├── anyclaw/
│   ├── api/                    # 新增：API 层
│   │   ├── __init__.py
│   │   ├── server.py           # FastAPI 服务器
│   │   ├── sse.py              # SSE 流式事件
│   │   ├── deps.py             # 依赖注入
│   │   └── routes/             # API 路由
│   │       ├── __init__.py
│   │       ├── health.py       # 健康检查
│   │       ├── agents.py       # Agent 管理
│   │       ├── messages.py     # 消息发送
│   │       ├── skills.py       # Skills 管理
│   │       └── tasks.py        # 定时任务
│   ├── core/
│   │   └── serve.py            # 修改：集成 API 服务器
│   └── cli/
│       └── sidecar_cmd.py      # 新增：Sidecar 模式启动命令
```

---

## 🔧 技术栈

### 核心依赖

```toml
[tool.poetry.dependencies]
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
sse-starlette = "^2.1.0"
pydantic = "^2.12.0"
pydantic-settings = "^2.0.0"
```

### 开发依赖

```toml
[tool.poetry.group.dev.dependencies]
httpx = "^0.27.0"    # API 测试
pytest-asyncio = "^0.23.0"
```

---

## 📝 详细任务清单

### Task 1.1: 创建 API 模块骨架

**文件**：`anyclaw/anyclaw/api/__init__.py`

```python
"""AnyClaw API Server module.

Provides HTTP API and SSE streaming for Tauri desktop app.
"""

from anyclaw.api.server import create_app, run_server

__all__ = ["create_app", "run_server"]
```

**文件**：`anyclaw/anyclaw/api/deps.py`

```python
"""Dependency injection for API routes."""

from __future__ import annotations

from typing import Generator

from anyclaw.core.serve import ServeManager
from anyclaw.bus.queue import MessageBus

# Global instances (set by sidecar_cmd.py)
_serve_manager: ServeManager | None = None


def set_serve_manager(manager: ServeManager) -> None:
    """Set the global ServeManager instance."""
    global _serve_manager
    _serve_manager = manager


def get_serve_manager() -> ServeManager:
    """Get the global ServeManager instance.

    Raises:
        RuntimeError: If ServeManager is not initialized
    """
    if _serve_manager is None:
        raise RuntimeError("ServeManager not initialized. Call set_serve_manager() first.")
    return _serve_manager


def get_message_bus() -> MessageBus:
    """Get the global MessageBus instance."""
    return get_serve_manager().bus
```

---

### Task 1.2: 实现 FastAPI 服务器

**文件**：`anyclaw/anyclaw/api/server.py`

```python
"""FastAPI server for AnyClaw HTTP API and SSE streaming."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from anyclaw.api.routes.health import router as health_router
from anyclaw.api.routes.agents import router as agents_router
from anyclaw.api.routes.messages import router as messages_router
from anyclaw.api.routes.skills import router as skills_router
from anyclaw.api.routes.tasks import router as tasks_router
from anyclaw.api.sse import router as sse_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("AnyClaw API server starting...")

    # TODO: Initialize database, cache, etc.

    yield

    # Shutdown
    logger.info("AnyClaw API server shutting down...")


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
    app.include_router(messages_router, prefix="/api", tags=["Messages"])
    app.include_router(skills_router, prefix="/api", tags=["Skills"])
    app.include_router(tasks_router, prefix="/api", tags=["Tasks"])
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
```

---

### Task 1.3: 实现健康检查端点

**文件**：`anyclaw/anyclaw/api/routes/health.py`

```python
"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from anyclaw.api.deps import get_serve_manager

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    uptime_seconds: int
    version: str = "0.1.0"
    channels: list[str] = []
    messages_processed: int = 0


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check API server and AnyClaw service health.

    Returns:
        HealthResponse with service status
    """
    manager = get_serve_manager()

    return HealthResponse(
        status="ok" if manager.is_running else "stopped",
        uptime_seconds=manager.uptime_seconds,
        channels=manager.enabled_channels,
        messages_processed=manager._messages_processed,
    )
```

---

### Task 1.4: 实现 Agent 管理端点

**文件**：`anyclaw/anyclaw/api/routes/agents.py`

```python
"""Agent management endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from anyclaw.api.deps import get_serve_manager

router = APIRouter()


class AgentInfo(BaseModel):
    """Agent information."""

    id: str
    name: str
    model: str
    description: str | None = None
    is_active: bool = True


@router.get("/agents", response_model=list[AgentInfo])
async def list_agents() -> list[AgentInfo]:
    """List all available agents.

    Returns:
        List of AgentInfo
    """
    manager = get_serve_manager()

    # TODO: Get agents from AgentManager
    # For now, return mock data
    return [
        AgentInfo(
            id="default",
            name="Default Agent",
            model=manager.config.agent.model,
            description="Default AnyClaw agent",
        )
    ]


@router.get("/agents/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str) -> AgentInfo:
    """Get agent details by ID.

    Args:
        agent_id: Agent ID

    Returns:
        AgentInfo

    Raises:
        HTTPException: If agent not found
    """
    # TODO: Get agent from AgentManager
    if agent_id == "default":
        return AgentInfo(
            id="default",
            name="Default Agent",
            model="claude-sonnet-4",
            description="Default AnyClaw agent",
        )

    raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")


@router.post("/agents/{agent_id}/activate")
async def activate_agent(agent_id: str) -> dict[str, str]:
    """Activate an agent.

    Args:
        agent_id: Agent ID

    Returns:
        Success message
    """
    # TODO: Activate agent in AgentManager
    return {"status": "ok", "message": f"Agent {agent_id} activated"}


@router.post("/agents/{agent_id}/deactivate")
async def deactivate_agent(agent_id: str) -> dict[str, str]:
    """Deactivate an agent.

    Args:
        agent_id: Agent ID

    Returns:
        Success message
    """
    # TODO: Deactivate agent in AgentManager
    return {"status": "ok", "message": f"Agent {agent_id} deactivated"}
```

---

### Task 1.5: 实现消息发送端点

**文件**：`anyclaw/anyclaw/api/routes/messages.py`

```python
"""Message sending endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from anyclaw.api.deps import get_message_bus, get_serve_manager
from anyclaw.bus.events import InboundMessage

router = APIRouter()


class SendMessageRequest(BaseModel):
    """Request to send a message to an agent."""

    agent_id: str = Field(..., description="Agent ID to send message to")
    content: str = Field(..., description="Message content")
    conversation_id: str | None = Field(None, description="Conversation ID")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SendMessageResponse(BaseModel):
    """Response to send message request."""

    status: str
    message_id: str
    agent_id: str


@router.post("/messages", response_model=SendMessageResponse)
async def send_message(request: SendMessageRequest) -> SendMessageResponse:
    """Send a message to an agent.

    The message is published to the MessageBus and routed to the appropriate
    agent through the ServeManager.

    Args:
        request: Send message request

    Returns:
        SendMessageResponse with message ID

    Raises:
        HTTPException: If message cannot be sent
    """
    bus = get_message_bus()
    manager = get_serve_manager()

    # Generate message ID
    message_id = f"msg_{id(request)}"

    # Create inbound message
    inbound_msg = InboundMessage(
        message_id=message_id,
        agent_id=request.agent_id,
        content=request.content,
        conversation_id=request.conversation_id or f"conv_{request.agent_id}",
        source="api",
        metadata=request.metadata,
    )

    # Publish to bus
    await bus.publish(inbound_msg)

    # Update counter
    manager._messages_processed += 1

    return SendMessageResponse(
        status="ok",
        message_id=message_id,
        agent_id=request.agent_id,
    )
```

---

### Task 1.6: 实现 Skills 管理端点

**文件**：`anyclaw/anyclaw/api/routes/skills.py`

```python
"""Skills management endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from anyclaw.api.deps import get_serve_manager

router = APIRouter()


@router.get("/skills")
async def list_skills():
    """List all available skills.

    Returns:
        List of skills with metadata
    """
    manager = get_serve_manager()

    # TODO: Get skills from SkillLoader
    return {
        "skills": [
            {
                "name": "example-skill",
                "description": "Example skill for demonstration",
                "version": "0.1.0",
                "enabled": True,
            }
        ]
    }


@router.get("/skills/{skill_name}")
async def get_skill(skill_name: str):
    """Get skill details.

    Args:
        skill_name: Skill name

    Returns:
        Skill details
    """
    # TODO: Get skill from SkillLoader
    return {
        "name": skill_name,
        "description": f"Details for {skill_name}",
        "version": "0.1.0",
    }


@router.post("/skills/{skill_name}/enable")
async def enable_skill(skill_name: str):
    """Enable a skill.

    Args:
        skill_name: Skill name

    Returns:
        Success message
    """
    # TODO: Enable skill in SkillLoader
    return {"status": "ok", "message": f"Skill {skill_name} enabled"}


@router.post("/skills/{skill_name}/disable")
async def disable_skill(skill_name: str):
    """Disable a skill.

    Args:
        skill_name: Skill name

    Returns:
        Success message
    """
    # TODO: Disable skill in SkillLoader
    return {"status": "ok", "message": f"Skill {skill_name} disabled"}
```

---

### Task 1.7: 实现定时任务端点

**文件**：`anyclaw/anyclaw/api/routes/tasks.py`

```python
"""Scheduled tasks management endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from anyclaw.api.deps import get_serve_manager

router = APIRouter()


@router.get("/tasks")
async def list_tasks():
    """List all scheduled tasks.

    Returns:
        List of tasks with schedule and status
    """
    manager = get_serve_manager()

    # TODO: Get tasks from CronService
    return {
        "tasks": [
            {
                "id": "task_1",
                "name": "Example Task",
                "schedule": "0 * * * *",  # Every hour
                "enabled": True,
                "next_run": "2026-03-20T05:00:00Z",
            }
        ]
    }


@router.post("/tasks")
async def create_task():
    """Create a new scheduled task.

    Returns:
        Created task details
    """
    # TODO: Create task in CronService
    return {"status": "ok", "message": "Task created"}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a scheduled task.

    Args:
        task_id: Task ID

    Returns:
        Success message
    """
    # TODO: Delete task in CronService
    return {"status": "ok", "message": f"Task {task_id} deleted"}
```

---

### Task 1.8: 实现 SSE 流式事件

**文件**：`anyclaw/anyclaw/api/sse.py`

```python
"""Server-Sent Events (SSE) streaming endpoint."""

from __future__ import annotations

import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from anyclaw.api.deps import get_message_bus

logger = logging.getLogger(__name__)

router = APIRouter()


async def event_publisher(request: Request) -> AsyncGenerator[dict[str, str], None]:
    """Publish events from MessageBus to SSE clients.

    Yields:
        SSE event dictionaries
    """
    bus = get_message_bus()

    # Subscribe to all events
    async for event in bus.subscribe():
        # Check if client disconnected
        if await request.is_disconnected():
            logger.info("SSE client disconnected")
            break

        # Convert event to SSE format
        yield {
            "event": event["type"],
            "data": json.dumps(event["payload"]),
        }


@router.get("/stream")
async def stream_events(request: Request) -> StreamingResponse:
    """Stream events from MessageBus via SSE.

    Clients can subscribe to real-time updates including:
    - message:inbound - New inbound messages
    - message:outbound - Agent responses
    - tool:start - Tool calls starting
    - tool:complete - Tool calls completed
    - agent:thinking - Agent thinking updates

    Returns:
        StreamingResponse with SSE events
    """
    logger.info("SSE client connected")

    return EventSourceResponse(event_publisher(request))
```

---

### Task 1.9: 创建 Sidecar 启动命令

**文件**：`anyclaw/anyclaw/cli/sidecar_cmd.py`

```python
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
```

---

### Task 1.10: 集成到 CLI 主程序

**文件**：`anyclaw/anyclaw/cli/app.py`（修改）

```python
"""AnyClaw CLI main application."""

# ... existing imports ...

from anyclaw.cli.sidecar_cmd import app as sidecar_app

# ... existing code ...

# Register sidecar subcommand
typer_app.add_typer(sidecar_app, name="sidecar", help="Run as Tauri sidecar")

# ... existing code ...
```

---

### Task 1.11: 更新依赖

**文件**：`anyclaw/pyproject.toml`（修改）

```toml
[tool.poetry.dependencies]
# ... existing dependencies ...
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
sse-starlette = "^2.1.0"

[tool.poetry.dependencies]
# ... existing dev dependencies ...
httpx = "^0.27.0"
```

---

### Task 1.12: 编写测试

**文件**：`anyclaw/test_api.py`

```python
"""Test FastAPI and SSE functionality."""

import asyncio
import pytest
from httpx import AsyncClient
from anyclaw.api.server import create_app

app = create_app()


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "uptime_seconds" in data


@pytest.mark.asyncio
async def test_list_agents():
    """Test list agents endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_send_message():
    """Test send message endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/messages",
            json={
                "agent_id": "default",
                "content": "Hello, AnyClaw!",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "message_id" in data


@pytest.mark.asyncio
async def test_sse_stream():
    """Test SSE streaming endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/stream", timeout=5.0)
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
```

---

## 🧪 测试计划

### 单元测试

```bash
# 运行所有测试
poetry run pytest tests/api/

# 运行特定测试
poetry run pytest tests/api/test_server.py::test_health_check

# 覆盖率报告
poetry run pytest --cov=anyclaw/api tests/api/
```

### 集成测试

```bash
# 启动 sidecar
poetry run anyclaw sidecar --port 62601

# 测试健康检查
curl http://127.0.0.1:62601/api/health

# 测试消息发送
curl -X POST http://127.0.0.1:62601/api/messages \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "default", "content": "Hello!"}'

# 测试 SSE 流
curl -N http://127.0.0.1:62601/api/stream
```

### API 文档

访问 http://127.0.0.1:62601/docs 查看 Swagger 文档

---

## ✅ 验收标准

### 功能验收

- [ ] FastAPI 服务器可以正常启动
- [ ] 所有 API 端点返回正确的响应
- [ ] SSE 流式事件可以正常接收
- [ ] Swagger 文档自动生成且可用
- [ ] Sidecar 模式可以与 CLI 和 Daemon 模式共存

### 性能验收

- [ ] API 响应时间 < 100ms (P95)
- [ ] SSE 延迟 < 50ms
- [ ] 内存占用 < 200MB (空闲时)

### 文档验收

- [ ] 所有 API 端点都有文档注释
- [ ] Swagger 文档完整
- [ ] 测试覆盖率 > 80%

---

## 📅 时间线

| 任务 | 预计时间 | 状态 |
|------|---------|------|
| Task 1.1: 创建 API 模块骨架 | 0.5h | ⬜ 待开始 |
| Task 1.2: 实现 FastAPI 服务器 | 2h | ⬜ 待开始 |
| Task 1.3: 实现健康检查端点 | 1h | ⬜ 待开始 |
| Task 1.4: 实现 Agent 管理端点 | 2h | ⬜ 待开始 |
| Task 1.5: 实现消息发送端点 | 2h | ⬜ 待开始 |
| Task 1.6: 实现 Skills 管理端点 | 1.5h | ⬜ 待开始 |
| Task 1.7: 实现定时任务端点 | 1.5h | ⬜ 待开始 |
| Task 1.8: 实现 SSE 流式事件 | 2h | ⬜ 待开始 |
| Task 1.9: 创建 Sidecar 启动命令 | 1.5h | ⬜ 待开始 |
| Task 1.10: 集成到 CLI 主程序 | 0.5h | ⬜ 待开始 |
| Task 1.11: 更新依赖 | 0.5h | ⬜ 待开始 |
| Task 1.12: 编写测试 | 3h | ⬜ 待开始 |

**总计**: ~18 小时 (2.5 工作日)

---

## 🚀 下一步

完成 Phase 1 后，继续：

**Phase 2**: Tauri Shell 集成
**Phase 3**: 前端 UI 开发（参考 YouClaw 设计）

---

**记录时间**: 2026-03-20 04:15 (Asia/Shanghai)
**状态**: ✅ 计划完成，准备实施
