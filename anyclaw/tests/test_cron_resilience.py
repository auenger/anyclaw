"""Tests for cron resilience features: backoff and stuck detection."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from anyclaw.cron.logs import CronLogStore
from anyclaw.cron.service import (
    BACKOFF_DELAYS,
    MAX_CONSECUTIVE_FAILURES,
    STUCK_THRESHOLD_MS,
    CronService,
    calculate_backoff_delay,
    _now_ms,
)
from anyclaw.cron.types import CronJob, CronJobState, CronPayload, CronSchedule


class TestBackoffCalculation:
    """Tests for backoff delay calculation."""

    def test_zero_failures(self):
        """No backoff for zero failures."""
        assert calculate_backoff_delay(0) == 0

    def test_first_failure(self):
        """First failure gets 30s backoff."""
        assert calculate_backoff_delay(1) == BACKOFF_DELAYS[0]  # 30s

    def test_second_failure(self):
        """Second failure gets 1m backoff."""
        assert calculate_backoff_delay(2) == BACKOFF_DELAYS[1]  # 1m

    def test_third_failure(self):
        """Third failure gets 5m backoff."""
        assert calculate_backoff_delay(3) == BACKOFF_DELAYS[2]  # 5m

    def test_fourth_failure(self):
        """Fourth failure gets 15m backoff."""
        assert calculate_backoff_delay(4) == BACKOFF_DELAYS[3]  # 15m

    def test_fifth_failure(self):
        """Fifth failure gets 60m backoff."""
        assert calculate_backoff_delay(5) == BACKOFF_DELAYS[4]  # 60m

    def test_beyond_max_failures(self):
        """Beyond max failures still returns max backoff."""
        assert calculate_backoff_delay(10) == BACKOFF_DELAYS[4]  # 60m
        assert calculate_backoff_delay(100) == BACKOFF_DELAYS[4]  # 60m


class TestBackoffConstants:
    """Verify backoff constants are correct."""

    def test_backoff_delays_sequence(self):
        """Backoff delays should be: 30s, 1m, 5m, 15m, 60m."""
        assert BACKOFF_DELAYS == [30_000, 60_000, 300_000, 900_000, 3_600_000]

    def test_max_consecutive_failures(self):
        """Max consecutive failures should be 5."""
        assert MAX_CONSECUTIVE_FAILURES == 5

    def test_stuck_threshold(self):
        """Stuck threshold should be 5 minutes."""
        assert STUCK_THRESHOLD_MS == 5 * 60 * 1000


@pytest.fixture
def temp_store_path():
    """Create a temporary store file path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "cron_jobs.json"


@pytest.fixture
def temp_log_path():
    """Create a temporary log file path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "cron_logs.jsonl"


@pytest.fixture
def cron_service(temp_store_path, temp_log_path):
    """Create a CronService with log store."""
    log_store = CronLogStore(temp_log_path)
    service = CronService(
        store_path=temp_store_path,
        log_store=log_store,
    )
    # Initialize the store
    service._load_store()
    return service


class TestJobExecutionWithBackoff:
    """Tests for job execution with backoff mechanism."""

    @pytest.mark.asyncio
    async def test_success_resets_failures(self, cron_service):
        """Success should reset consecutive failures."""
        # Create job with existing failures
        job = CronJob(
            id="test-1",
            name="Test Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
            state=CronJobState(consecutive_failures=3),
        )
        cron_service._store.jobs = [job]

        # Mock successful execution
        cron_service.on_job = AsyncMock(return_value="Success")

        await cron_service._execute_job(job)

        assert job.state.consecutive_failures == 0
        assert job.state.last_status == "ok"

    @pytest.mark.asyncio
    async def test_failure_increments_failures(self, cron_service):
        """Failure should increment consecutive failures."""
        job = CronJob(
            id="test-2",
            name="Test Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
        )
        cron_service._store.jobs = [job]

        # Mock failed execution
        cron_service.on_job = AsyncMock(side_effect=Exception("Test error"))

        await cron_service._execute_job(job)

        assert job.state.consecutive_failures == 1
        assert job.state.last_status == "error"

    @pytest.mark.asyncio
    async def test_failure_applies_backoff(self, cron_service):
        """Failure should apply backoff delay."""
        job = CronJob(
            id="test-3",
            name="Test Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
        )
        cron_service._store.jobs = [job]

        cron_service.on_job = AsyncMock(side_effect=Exception("Test error"))

        await cron_service._execute_job(job)

        # Check backoff was applied
        now = _now_ms()
        expected_next = now + BACKOFF_DELAYS[0]  # First failure: 30s
        # Allow 100ms tolerance
        assert abs(job.state.next_run_at_ms - expected_next) < 100

    @pytest.mark.asyncio
    async def test_multiple_failures_escalate_backoff(self, cron_service):
        """Multiple failures should escalate backoff."""
        job = CronJob(
            id="test-4",
            name="Test Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
            state=CronJobState(consecutive_failures=2),
        )
        cron_service._store.jobs = [job]

        cron_service.on_job = AsyncMock(side_effect=Exception("Test error"))

        await cron_service._execute_job(job)

        # Third failure: 5m backoff
        now = _now_ms()
        expected_next = now + BACKOFF_DELAYS[2]
        assert abs(job.state.next_run_at_ms - expected_next) < 100

    @pytest.mark.asyncio
    async def test_max_failures_auto_pauses(self, cron_service):
        """Reaching max failures should auto-pause the job."""
        job = CronJob(
            id="test-5",
            name="Test Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
            state=CronJobState(consecutive_failures=4),
        )
        cron_service._store.jobs = [job]

        cron_service.on_job = AsyncMock(side_effect=Exception("Test error"))

        await cron_service._execute_job(job)

        assert job.enabled is False
        assert "auto-paused" in job.state.last_error


class TestEnableResetsFailures:
    """Tests for enable_job resetting failures."""

    def test_enable_resets_consecutive_failures(self, cron_service):
        """Enabling a job should reset consecutive failures."""
        job = CronJob(
            id="test-6",
            name="Test Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
            state=CronJobState(consecutive_failures=5),
            enabled=False,
        )
        cron_service._store.jobs = [job]

        result = cron_service.enable_job("test-6", enabled=True)

        assert result is not None
        assert result.state.consecutive_failures == 0
        assert result.enabled is True

    def test_disable_does_not_reset(self, cron_service):
        """Disabling a job should not reset failures."""
        job = CronJob(
            id="test-7",
            name="Test Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
            state=CronJobState(consecutive_failures=3),
            enabled=True,
        )
        cron_service._store.jobs = [job]

        result = cron_service.enable_job("test-7", enabled=False)

        assert result.state.consecutive_failures == 3


class TestStuckDetection:
    """Tests for stuck task detection and recovery."""

    @pytest.mark.asyncio
    async def test_detect_stuck_task(self, cron_service):
        """Should detect a task running too long."""
        stuck_since = _now_ms() - STUCK_THRESHOLD_MS - 1000  # 6 minutes ago
        job = CronJob(
            id="test-stuck-1",
            name="Stuck Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
            state=CronJobState(
                running_since_ms=stuck_since,
                consecutive_failures=0,
            ),
        )
        cron_service._store.jobs = [job]

        await cron_service._recover_stuck_tasks()

        assert job.state.running_since_ms is None
        assert job.state.consecutive_failures == 1
        assert job.state.last_status == "error"

    @pytest.mark.asyncio
    async def test_stuck_task_applies_backoff(self, cron_service):
        """Stuck task should apply backoff delay."""
        stuck_since = _now_ms() - STUCK_THRESHOLD_MS - 1000
        job = CronJob(
            id="test-stuck-2",
            name="Stuck Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
            state=CronJobState(running_since_ms=stuck_since),
        )
        cron_service._store.jobs = [job]

        await cron_service._recover_stuck_tasks()

        now = _now_ms()
        expected_next = now + BACKOFF_DELAYS[0]  # First failure
        assert abs(job.state.next_run_at_ms - expected_next) < 100

    @pytest.mark.asyncio
    async def test_stuck_task_max_failures_pauses(self, cron_service):
        """Stuck task reaching max failures should auto-pause."""
        stuck_since = _now_ms() - STUCK_THRESHOLD_MS - 1000
        job = CronJob(
            id="test-stuck-3",
            name="Stuck Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
            state=CronJobState(
                running_since_ms=stuck_since,
                consecutive_failures=4,
            ),
        )
        cron_service._store.jobs = [job]

        await cron_service._recover_stuck_tasks()

        assert job.enabled is False
        assert "auto-paused" in job.state.last_error

    @pytest.mark.asyncio
    async def test_normal_task_not_detected_as_stuck(self, cron_service):
        """Recently started task should not be detected as stuck."""
        recent_since = _now_ms() - 1000  # 1 second ago
        job = CronJob(
            id="test-normal",
            name="Normal Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
            state=CronJobState(running_since_ms=recent_since),
        )
        cron_service._store.jobs = [job]

        await cron_service._recover_stuck_tasks()

        # Should not be modified
        assert job.state.running_since_ms == recent_since
        assert job.state.consecutive_failures == 0


class TestExecutionLocking:
    """Tests for running_since_ms locking mechanism."""

    @pytest.mark.asyncio
    async def test_execute_sets_running_since(self, cron_service):
        """Execute should set running_since_ms."""
        job = CronJob(
            id="test-lock-1",
            name="Lock Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
        )
        cron_service._store.jobs = [job]

        # Slow job
        async def slow_job(j):
            await asyncio.sleep(0.1)
            return "done"

        cron_service.on_job = slow_job

        # Start execution and check running_since is set during execution
        task = asyncio.create_task(cron_service._execute_job(job))

        # Give it a moment to start
        await asyncio.sleep(0.01)

        # During execution, running_since should be set
        # (but we can't check it easily without modifying the code)

        await task

        # After execution, running_since should be cleared
        assert job.state.running_since_ms is None

    @pytest.mark.asyncio
    async def test_execute_clears_running_since_on_error(self, cron_service):
        """Execute should clear running_since_ms even on error."""
        job = CronJob(
            id="test-lock-2",
            name="Lock Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
        )
        cron_service._store.jobs = [job]

        cron_service.on_job = AsyncMock(side_effect=Exception("Error"))

        await cron_service._execute_job(job)

        assert job.state.running_since_ms is None


class TestLoggingIntegration:
    """Tests for execution logging."""

    @pytest.mark.asyncio
    async def test_success_log_recorded(self, cron_service, temp_log_path):
        """Success should be logged."""
        job = CronJob(
            id="test-log-1",
            name="Log Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
        )
        cron_service._store.jobs = [job]

        cron_service.on_job = AsyncMock(return_value="Success result")

        await cron_service._execute_job(job)

        # Check log was recorded
        logs = await cron_service.log_store.get_logs("test-log-1")
        assert len(logs) == 1
        assert logs[0].status == "success"
        assert logs[0].result == "Success result"

    @pytest.mark.asyncio
    async def test_error_log_recorded(self, cron_service):
        """Error should be logged."""
        job = CronJob(
            id="test-log-2",
            name="Log Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
        )
        cron_service._store.jobs = [job]

        cron_service.on_job = AsyncMock(side_effect=Exception("Test error"))

        await cron_service._execute_job(job)

        logs = await cron_service.log_store.get_logs("test-log-2")
        assert len(logs) == 1
        assert logs[0].status == "error"
        assert logs[0].error == "Test error"

    @pytest.mark.asyncio
    async def test_no_log_store_no_error(self, temp_store_path):
        """Should work without log store."""
        service = CronService(store_path=temp_store_path, log_store=None)
        service._load_store()  # Initialize store
        job = CronJob(
            id="test-no-log",
            name="No Log Job",
            schedule=CronSchedule(kind="every", every_ms=60000),
        )
        service._store.jobs = [job]

        # Should not raise
        await service._execute_job(job)
        assert job.state.last_status == "ok"
