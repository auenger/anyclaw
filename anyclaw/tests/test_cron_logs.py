"""Tests for cron execution log storage."""

import asyncio
import json
import tempfile
from pathlib import Path

import pytest

from anyclaw.cron.logs import CronLogStore
from anyclaw.cron.types import CronRunLog


@pytest.fixture
def temp_log_path():
    """Create a temporary log file path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "cron_logs.jsonl"


@pytest.fixture
def log_store(temp_log_path):
    """Create a CronLogStore instance."""
    return CronLogStore(temp_log_path)


@pytest.mark.asyncio
async def test_log_store_init(log_store, temp_log_path):
    """Test log store initializes correctly."""
    assert log_store.log_path == temp_log_path
    assert temp_log_path.exists()


@pytest.mark.asyncio
async def test_append_log(log_store):
    """Test appending a log record."""
    log = CronRunLog(
        id=1,
        job_id="job-123",
        run_at_ms=1000000,
        duration_ms=500,
        status="success",
        result="Done",
    )
    await log_store.append(log)

    # Verify the log was written
    logs = await log_store.get_logs("job-123")
    assert len(logs) == 1
    assert logs[0].job_id == "job-123"
    assert logs[0].status == "success"
    assert logs[0].result == "Done"


@pytest.mark.asyncio
async def test_append_error_log(log_store):
    """Test appending an error log record."""
    log = CronRunLog(
        id=1,
        job_id="job-456",
        run_at_ms=1000000,
        duration_ms=300,
        status="error",
        error="Something went wrong",
    )
    await log_store.append(log)

    logs = await log_store.get_logs("job-456")
    assert len(logs) == 1
    assert logs[0].status == "error"
    assert logs[0].error == "Something went wrong"


@pytest.mark.asyncio
async def test_get_logs_limit(log_store):
    """Test get_logs respects limit parameter."""
    for i in range(10):
        log = CronRunLog(
            id=i + 1,
            job_id="job-limit",
            run_at_ms=1000000 + i * 1000,
            duration_ms=100,
            status="success",
        )
        await log_store.append(log)

    logs = await log_store.get_logs("job-limit", limit=5)
    assert len(logs) == 5
    # Should return most recent first
    assert logs[0].run_at_ms == 1009000  # Most recent


@pytest.mark.asyncio
async def test_get_logs_by_job_id(log_store):
    """Test get_logs filters by job_id."""
    await log_store.append(CronRunLog(id=1, job_id="job-a", run_at_ms=1000, duration_ms=100, status="success"))
    await log_store.append(CronRunLog(id=2, job_id="job-b", run_at_ms=2000, duration_ms=100, status="success"))
    await log_store.append(CronRunLog(id=3, job_id="job-a", run_at_ms=3000, duration_ms=100, status="error"))

    logs_a = await log_store.get_logs("job-a")
    assert len(logs_a) == 2

    logs_b = await log_store.get_logs("job-b")
    assert len(logs_b) == 1


@pytest.mark.asyncio
async def test_get_logs_empty(log_store):
    """Test get_logs returns empty list for unknown job."""
    logs = await log_store.get_logs("nonexistent")
    assert logs == []


@pytest.mark.asyncio
async def test_prune_old_logs(log_store):
    """Test pruning old logs."""
    import time

    now_ms = int(time.time() * 1000)
    old_ms = now_ms - 31 * 24 * 60 * 60 * 1000  # 31 days ago

    # Add old log
    await log_store.append(CronRunLog(
        id=1,
        job_id="old-job",
        run_at_ms=old_ms,
        duration_ms=100,
        status="success",
    ))

    # Add recent log
    await log_store.append(CronRunLog(
        id=2,
        job_id="new-job",
        run_at_ms=now_ms,
        duration_ms=100,
        status="success",
    ))

    removed = await log_store.prune_old_logs(days=30)
    assert removed == 1

    # Verify old log is gone
    old_logs = await log_store.get_logs("old-job")
    assert len(old_logs) == 0

    # Verify new log remains
    new_logs = await log_store.get_logs("new-job")
    assert len(new_logs) == 1


@pytest.mark.asyncio
async def test_concurrent_append(log_store):
    """Test concurrent append operations are safe."""
    async def append_log(i):
        log = CronRunLog(
            id=i,
            job_id=f"concurrent-job",
            run_at_ms=1000000 + i,
            duration_ms=100,
            status="success",
        )
        await log_store.append(log)

    # Run 10 concurrent appends
    await asyncio.gather(*[append_log(i) for i in range(10)])

    logs = await log_store.get_logs("concurrent-job")
    assert len(logs) == 10


@pytest.mark.asyncio
async def test_result_truncation(log_store):
    """Test long results are truncated to 500 chars."""
    long_result = "x" * 1000
    log = CronRunLog(
        id=1,
        job_id="truncate-job",
        run_at_ms=1000000,
        duration_ms=100,
        status="success",
        result=long_result,
    )
    await log_store.append(log)

    logs = await log_store.get_logs("truncate-job")
    assert len(logs[0].result) == 500


@pytest.mark.asyncio
async def test_jsonl_format(log_store, temp_log_path):
    """Test log file is valid JSONL format."""
    await log_store.append(CronRunLog(
        id=1,
        job_id="format-job",
        run_at_ms=1000000,
        duration_ms=100,
        status="success",
        result="test",
    ))

    # Read and parse the file
    with open(temp_log_path, "r") as f:
        line = f.readline()
        data = json.loads(line)

        assert data["id"] == 1
        assert data["jobId"] == "format-job"
        assert data["runAtMs"] == 1000000
        assert data["durationMs"] == 100
        assert data["status"] == "success"
        assert data["result"] == "test"
