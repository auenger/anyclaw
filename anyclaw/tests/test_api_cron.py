"""Tests for Cron API endpoints."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from anyclaw.api.server import create_app
from anyclaw.api.deps import set_cron_service, set_cron_log_store
from anyclaw.cron.service import CronService
from anyclaw.cron.logs import CronLogStore


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def cron_service(temp_dir):
    """Create a CronService instance for testing."""
    store_path = temp_dir / "cron_jobs.json"
    log_store = CronLogStore(temp_dir / "cron_logs.jsonl")
    service = CronService(store_path=store_path, log_store=log_store)
    return service


@pytest.fixture
def cron_log_store(temp_dir):
    """Create a CronLogStore instance for testing."""
    return CronLogStore(temp_dir / "cron_logs.jsonl")


@pytest.fixture
def client(cron_service, cron_log_store):
    """Create a test client with cron services injected."""
    # Set global dependencies
    set_cron_service(cron_service)
    set_cron_log_store(cron_log_store)

    app = create_app()
    return TestClient(app)


class TestListJobs:
    """Tests for GET /api/cron/jobs."""

    def test_list_jobs_empty(self, client):
        """Test listing jobs when empty."""
        response = client.get("/api/cron/jobs")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_jobs_with_data(self, client, cron_service):
        """Test listing jobs with data."""
        from anyclaw.cron.types import CronSchedule

        cron_service.add_job(
            name="Test Job",
            schedule=CronSchedule(kind="every", every_ms=300000),
            message="Test prompt",
        )

        response = client.get("/api/cron/jobs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Job"

    def test_list_jobs_filter_enabled(self, client, cron_service):
        """Test filtering by enabled status."""
        from anyclaw.cron.types import CronSchedule

        cron_service.add_job(
            name="Enabled Job",
            schedule=CronSchedule(kind="every", every_ms=300000),
            message="Test",
        )

        job = cron_service.add_job(
            name="Disabled Job",
            schedule=CronSchedule(kind="every", every_ms=300000),
            message="Test",
        )
        cron_service.enable_job(job.id, enabled=False)

        # Filter enabled only
        response = client.get("/api/cron/jobs?enabled=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Enabled Job"

        # Filter disabled only
        response = client.get("/api/cron/jobs?enabled=false")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Disabled Job"


class TestCreateJob:
    """Tests for POST /api/cron/jobs."""

    def test_create_job_interval(self, client):
        """Test creating a job with interval schedule."""
        response = client.post(
            "/api/cron/jobs",
            json={
                "name": "Interval Job",
                "agent_id": "agent-1",
                "chat_id": "chat-1",
                "prompt": "Test prompt",
                "schedule": {
                    "type": "interval",
                    "value_ms": 300000,
                },
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Interval Job"
        assert data["enabled"] is True
        assert data["schedule"]["type"] == "every"
        assert data["schedule"]["valueMs"] == 300000

    def test_create_job_cron(self, client):
        """Test creating a job with cron schedule."""
        response = client.post(
            "/api/cron/jobs",
            json={
                "name": "Cron Job",
                "agent_id": "agent-1",
                "chat_id": "chat-1",
                "prompt": "Test prompt",
                "schedule": {
                    "type": "cron",
                    "expr": "0 9 * * *",
                    "tz": "Asia/Shanghai",
                },
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Cron Job"
        assert data["schedule"]["type"] == "cron"
        assert data["schedule"]["expr"] == "0 9 * * *"

    def test_create_job_validation_interval_too_small(self, client):
        """Test validation: interval must be >= 60000ms."""
        response = client.post(
            "/api/cron/jobs",
            json={
                "name": "Bad Interval",
                "agent_id": "agent-1",
                "chat_id": "chat-1",
                "prompt": "Test",
                "schedule": {
                    "type": "interval",
                    "value_ms": 30000,  # Too small
                },
            },
        )
        assert response.status_code == 400
        assert "interval must be >= 60000ms" in response.json()["detail"]

    def test_create_job_validation_invalid_cron(self, client):
        """Test validation: invalid cron expression."""
        response = client.post(
            "/api/cron/jobs",
            json={
                "name": "Bad Cron",
                "agent_id": "agent-1",
                "chat_id": "chat-1",
                "prompt": "Test",
                "schedule": {
                    "type": "cron",
                    "expr": "invalid cron",
                },
            },
        )
        assert response.status_code == 400
        assert "Invalid cron expression" in response.json()["detail"]

    def test_create_job_validation_missing_fields(self, client):
        """Test validation: missing required fields."""
        response = client.post(
            "/api/cron/jobs",
            json={
                "name": "Missing Fields",
            },
        )
        assert response.status_code == 422  # Pydantic validation error


class TestGetJob:
    """Tests for GET /api/cron/jobs/{job_id}."""

    def test_get_job_success(self, client, cron_service):
        """Test getting a job by ID."""
        from anyclaw.cron.types import CronSchedule

        job = cron_service.add_job(
            name="Test Job",
            schedule=CronSchedule(kind="every", every_ms=300000),
            message="Test prompt",
        )

        response = client.get(f"/api/cron/jobs/{job.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job.id
        assert data["name"] == "Test Job"

    def test_get_job_not_found(self, client):
        """Test getting a non-existent job."""
        response = client.get("/api/cron/jobs/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUpdateJob:
    """Tests for PUT /api/cron/jobs/{job_id}."""

    def test_update_job_name(self, client, cron_service):
        """Test updating job name."""
        from anyclaw.cron.types import CronSchedule

        job = cron_service.add_job(
            name="Original Name",
            schedule=CronSchedule(kind="every", every_ms=300000),
            message="Test",
        )

        response = client.put(
            f"/api/cron/jobs/{job.id}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_job_disable(self, client, cron_service):
        """Test disabling a job."""
        from anyclaw.cron.types import CronSchedule

        job = cron_service.add_job(
            name="Test Job",
            schedule=CronSchedule(kind="every", every_ms=300000),
            message="Test",
        )

        response = client.put(
            f"/api/cron/jobs/{job.id}",
            json={"enabled": False},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False
        assert data["state"]["nextRunAtMs"] is None

    def test_update_job_not_found(self, client):
        """Test updating a non-existent job."""
        response = client.put(
            "/api/cron/jobs/nonexistent",
            json={"name": "New Name"},
        )
        assert response.status_code == 404


class TestDeleteJob:
    """Tests for DELETE /api/cron/jobs/{job_id}."""

    def test_delete_job_success(self, client, cron_service):
        """Test deleting a job."""
        from anyclaw.cron.types import CronSchedule

        job = cron_service.add_job(
            name="To Delete",
            schedule=CronSchedule(kind="every", every_ms=300000),
            message="Test",
        )

        response = client.delete(f"/api/cron/jobs/{job.id}")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

        # Verify deleted
        response = client.get(f"/api/cron/jobs/{job.id}")
        assert response.status_code == 404

    def test_delete_job_not_found(self, client):
        """Test deleting a non-existent job."""
        response = client.delete("/api/cron/jobs/nonexistent")
        assert response.status_code == 404


class TestCloneJob:
    """Tests for POST /api/cron/jobs/{job_id}/clone."""

    def test_clone_job_success(self, client, cron_service):
        """Test cloning a job."""
        from anyclaw.cron.types import CronSchedule

        job = cron_service.add_job(
            name="Original Job",
            schedule=CronSchedule(kind="every", every_ms=300000),
            message="Test prompt",
        )

        response = client.post(f"/api/cron/jobs/{job.id}/clone")
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Original Job (copy)"
        assert data["id"] != job.id
        assert data["enabled"] is True

    def test_clone_job_not_found(self, client):
        """Test cloning a non-existent job."""
        response = client.post("/api/cron/jobs/nonexistent/clone")
        assert response.status_code == 404


class TestRunJob:
    """Tests for POST /api/cron/jobs/{job_id}/run."""

    def test_run_job_success(self, client, cron_service):
        """Test manually running a job."""
        from anyclaw.cron.types import CronSchedule

        job = cron_service.add_job(
            name="Manual Run",
            schedule=CronSchedule(kind="every", every_ms=300000),
            message="Test",
        )

        response = client.post(f"/api/cron/jobs/{job.id}/run")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_run_job_not_found(self, client):
        """Test running a non-existent job."""
        response = client.post("/api/cron/jobs/nonexistent/run")
        assert response.status_code == 404


class TestGetJobLogs:
    """Tests for GET /api/cron/jobs/{job_id}/logs."""

    def test_get_logs_empty(self, client, cron_service):
        """Test getting logs when empty."""
        from anyclaw.cron.types import CronSchedule

        job = cron_service.add_job(
            name="Test Job",
            schedule=CronSchedule(kind="every", every_ms=300000),
            message="Test",
        )

        response = client.get(f"/api/cron/jobs/{job.id}/logs")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_logs_not_found(self, client):
        """Test getting logs for non-existent job."""
        response = client.get("/api/cron/jobs/nonexistent/logs")
        assert response.status_code == 404


class TestPruneLogs:
    """Tests for POST /api/cron/logs/prune."""

    def test_prune_logs_default(self, client):
        """Test pruning logs with default days."""
        response = client.post("/api/cron/logs/prune")
        assert response.status_code == 200
        data = response.json()
        assert "deletedCount" in data

    def test_prune_logs_custom_days(self, client):
        """Test pruning logs with custom days."""
        response = client.post(
            "/api/cron/logs/prune",
            json={"days": 7},
        )
        assert response.status_code == 200
        data = response.json()
        assert "deletedCount" in data
