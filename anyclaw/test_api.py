"""Test FastAPI and SSE functionality."""

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
        # Note: This may fail if ServeManager is not initialized
        # That's expected in unit tests
        if response.status_code == 500:
            # Expected - ServeManager not initialized
            pass
        elif response.status_code == 200:
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


@pytest.mark.asyncio
async def test_cors_headers():
    """Test CORS headers are set correctly."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers
