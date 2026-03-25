"""Tests for Logs API endpoints."""

import pytest
from fastapi.testclient import TestClient

from anyclaw.api.server import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestLogsAPI:
    """Tests for Logs API endpoints."""

    def test_get_log_stats(self, client):
        """Test GET /api/logs/stats endpoint."""
        response = client.get("/api/logs/stats")
        assert response.status_code == 200

        data = response.json()
        assert "sessions_total" in data
        assert "sessions_today" in data
        assert "system_logs_total" in data
        assert "by_level" in data
        assert "by_category" in data

    def test_list_session_logs(self, client):
        """Test GET /api/logs/sessions endpoint."""
        response = client.get("/api/logs/sessions")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_list_session_logs_with_date(self, client):
        """Test GET /api/logs/sessions with date filter."""
        response = client.get("/api/logs/sessions?date=2024-01-01")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_list_session_logs_with_limit(self, client):
        """Test GET /api/logs/sessions with limit."""
        response = client.get("/api/logs/sessions?limit=10")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_get_session_not_found(self, client):
        """Test GET /api/logs/sessions/:id with non-existent ID."""
        response = client.get("/api/logs/sessions/non-existent-id")
        assert response.status_code == 404

    def test_search_session_logs(self, client):
        """Test GET /api/logs/sessions/search endpoint."""
        response = client.get("/api/logs/sessions/search?q=test")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_get_system_logs(self, client):
        """Test GET /api/logs/system endpoint."""
        response = client.get("/api/logs/system")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_get_system_logs_with_level(self, client):
        """Test GET /api/logs/system with level filter."""
        response = client.get("/api/logs/system?level=ERROR")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        # All entries should be ERROR level
        for entry in data:
            assert entry["level"] == "ERROR"

    def test_get_system_logs_with_category(self, client):
        """Test GET /api/logs/system with category filter."""
        response = client.get("/api/logs/system?category=tool")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        # All entries should be tool category
        for entry in data:
            assert entry["category"] == "tool"

    def test_get_system_logs_with_search(self, client):
        """Test GET /api/logs/system with search."""
        response = client.get("/api/logs/system?search=error")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_get_system_logs_with_limit(self, client):
        """Test GET /api/logs/system with limit."""
        response = client.get("/api/logs/system?limit=50")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 50


class TestLogCollector:
    """Tests for SystemLogCollector."""

    def test_collector_singleton(self):
        """Test that collector is a singleton."""
        from anyclaw.utils.log_collector import get_log_collector

        collector1 = get_log_collector()
        collector2 = get_log_collector()

        assert collector1 is collector2

    def test_collector_get_logs(self):
        """Test collector get_logs method."""
        from anyclaw.utils.log_collector import get_log_collector

        collector = get_log_collector()
        logs = collector.get_logs()

        assert isinstance(logs, list)

    def test_collector_get_stats(self):
        """Test collector get_stats method."""
        from anyclaw.utils.log_collector import get_log_collector

        collector = get_log_collector()
        stats = collector.get_stats()

        assert "total" in stats
        assert "by_level" in stats
        assert "by_category" in stats
