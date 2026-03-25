"""Tests for Agent API endpoints."""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from anyclaw.api.routes.agents import router, AgentInfo
from anyclaw.api.deps import get_agent_manager


@pytest.fixture
def mock_agent_manager():
    """Create a mock AgentManager."""
    manager = MagicMock()

    # Setup mock agents
    agent1 = MagicMock()
    agent1.to_dict.return_value = {
        "id": "default",
        "name": "Default Agent",
        "emoji": "🤖",
        "avatar": "",
        "enabled": True,
        "workspace": "/tmp/agents/default",
        "sessionCount": 5,
    }

    agent2 = MagicMock()
    agent2.to_dict.return_value = {
        "id": "researcher",
        "name": "Research Assistant",
        "emoji": "🔬",
        "avatar": "avatars/researcher.png",
        "enabled": True,
        "workspace": "/tmp/agents/researcher",
        "sessionCount": 2,
    }

    manager.list_agents.return_value = [
        agent1.to_dict(), agent2.to_dict()
    ]
    manager.get_agent.side_effect = lambda agent_id: {
        "default": agent1,
        "researcher": agent2,
    }.get(agent_id)

    manager.create_agent.return_value = agent1
    manager.delete_agent.return_value = True
    manager.switch_agent.return_value = True
    manager.enable_agent.return_value = True
    manager.get_status.return_value = {
        "agentsCount": 2,
        "enabledAgentsCount": 2,
        "defaultAgentId": "default",
        "defaultAgent": agent1.to_dict(),
    }

    # Mock identity_manager
    identity_manager = MagicMock()
    identity_manager.update_identity.return_value = MagicMock()
    manager.identity_manager = identity_manager

    return manager


@pytest.fixture
def app(mock_agent_manager):
    """Create a FastAPI app with mocked dependencies."""
    app = FastAPI()
    app.include_router(router)

    # Override dependency using FastAPI's dependency_override
    app.dependency_overrides[get_agent_manager] = lambda: mock_agent_manager

    yield app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


class TestListAgents:
    """Tests for GET /agents endpoint."""

    def test_list_agents_success(self, client, mock_agent_manager):
        """Test listing agents returns all agents."""
        response = client.get("/agents")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "default"
        assert data[1]["id"] == "researcher"

    def test_list_agents_include_disabled(self, client, mock_agent_manager):
        """Test listing agents with include_disabled parameter."""
        response = client.get("/agents?include_disabled=true")

        assert response.status_code == 200
        mock_agent_manager.list_agents.assert_called()


class TestGetAgent:
    """Tests for GET /agents/{agent_id} endpoint."""

    def test_get_agent_success(self, client, mock_agent_manager):
        """Test getting an existing agent."""
        response = client.get("/agents/default")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "default"
        assert data["name"] == "Default Agent"

    def test_get_agent_not_found(self, client, mock_agent_manager):
        """Test getting a non-existent agent returns 404."""
        response = client.get("/agents/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestCreateAgent:
    """Tests for POST /agents endpoint."""

    def test_create_agent_success(self, client, mock_agent_manager):
        """Test creating an agent successfully."""
        response = client.post(
            "/agents",
            json={
                "name": "Test Agent",
                "creature": "AI",
                "vibe": "helpful",
                "emoji": "🤖",
            },
        )

        assert response.status_code == 201
        mock_agent_manager.create_agent.assert_called_once()

    def test_create_agent_missing_name(self, client, mock_agent_manager):
        """Test creating an agent without name fails validation."""
        response = client.post(
            "/agents",
            json={
                "creature": "AI",
                "vibe": "helpful",
            },
        )

        assert response.status_code == 422  # Validation error

    def test_create_agent_duplicate_name(self, client, mock_agent_manager):
        """Test creating an agent with duplicate name fails."""
        mock_agent_manager.create_agent.return_value = None

        response = client.post(
            "/agents",
            json={
                "name": "Duplicate",
                "creature": "AI",
            },
        )

        assert response.status_code == 400


class TestUpdateAgent:
    """Tests for PATCH /agents/{agent_id} endpoint."""

    def test_update_agent_success(self, client, mock_agent_manager):
        """Test updating an agent successfully."""
        response = client.patch(
            "/agents/default",
            json={"name": "Updated Name", "emoji": "🎉"},
        )

        assert response.status_code == 200
        mock_agent_manager.identity_manager.update_identity.assert_called()

    def test_update_agent_not_found(self, client, mock_agent_manager):
        """Test updating a non-existent agent returns 404."""
        response = client.patch(
            "/agents/nonexistent",
            json={"name": "New Name"},
        )

        assert response.status_code == 404


class TestDeleteAgent:
    """Tests for DELETE /agents/{agent_id} endpoint."""

    def test_delete_agent_success(self, client, mock_agent_manager):
        """Test deleting an agent successfully."""
        response = client.delete("/agents/default")

        assert response.status_code == 204
        mock_agent_manager.delete_agent.assert_called_once_with("default")

    def test_delete_agent_not_found(self, client, mock_agent_manager):
        """Test deleting a non-existent agent returns 404."""
        mock_agent_manager.get_agent.return_value = None

        response = client.delete("/agents/nonexistent")

        assert response.status_code == 404


class TestActivateAgent:
    """Tests for POST /agents/{agent_id}/activate endpoint."""

    def test_activate_agent_success(self, client, mock_agent_manager):
        """Test activating an agent successfully."""
        response = client.post("/agents/researcher/activate")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "activated" in data["message"]
        mock_agent_manager.switch_agent.assert_called_once_with("researcher")

    def test_activate_agent_not_found(self, client, mock_agent_manager):
        """Test activating a non-existent agent returns 404."""
        response = client.post("/agents/nonexistent/activate")

        assert response.status_code == 404


class TestDeactivateAgent:
    """Tests for POST /agents/{agent_id}/deactivate endpoint."""

    def test_deactivate_agent_success(self, client, mock_agent_manager):
        """Test deactivating an agent successfully."""
        response = client.post("/agents/researcher/deactivate")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "deactivated" in data["message"]
        mock_agent_manager.enable_agent.assert_called_once_with(
            "researcher", enabled=False
        )

    def test_deactivate_agent_not_found(self, client, mock_agent_manager):
        """Test deactivating a non-existent agent returns 404."""
        response = client.post("/agents/nonexistent/deactivate")

        assert response.status_code == 404


class TestGetAgentsStatus:
    """Tests for GET /agents/status/summary endpoint."""

    def test_get_status_success(self, client, mock_agent_manager):
        """Test getting agent status summary."""
        response = client.get("/agents/status/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["agentsCount"] == 2
        assert data["enabledAgentsCount"] == 2
        assert data["defaultAgentId"] == "default"


class TestAgentInfoModel:
    """Tests for AgentInfo Pydantic model."""

    def test_agent_info_from_dict(self):
        """Test creating AgentInfo from dictionary."""
        info = AgentInfo(
            id="test",
            name="Test Agent",
            emoji="🧪",
            enabled=True,
            sessionCount=10,
        )

        assert info.id == "test"
        assert info.name == "Test Agent"
        assert info.session_count == 10  # aliased field

    def test_agent_info_default_values(self):
        """Test AgentInfo default values."""
        info = AgentInfo(id="test", name="Test")

        assert info.emoji == "🤖"
        assert info.avatar == ""
        assert info.enabled is True
