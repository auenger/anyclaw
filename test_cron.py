"""Test Cron functionality."""

import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from anyclaw.cron.service import CronService
from anyclaw.cron.tool import CronTool
from anyclaw.cron.types import CronSchedule


class MockBus:
    """Mock message bus for testing."""

    async def publish_inbound(self, msg):
        """Mock publish message."""
        print(f"[Mock Bus] Published cron message: {msg.content[:100]}...")


async def mock_cron_callback(job):
    """Mock cron job callback."""
    print(f"[Mock Callback] Executing job: {job.name}")
    return f"Completed: {job.payload.message}"


async def test_cron_add_every_job():
    """Test adding an 'every' job."""
    print("=== Test 1: Add 'every' Job ===")
    service = CronService(
        store_path=Path("/tmp/test_cron_jobs.json"),
        on_job=mock_cron_callback,
    )
    await service.start()

    job = service.add_job(
        name="Test every job",
        schedule=CronSchedule(kind="every", every_ms=5000),  # 5 seconds
        message="Every 5 seconds reminder",
    )

    assert job.id
    assert job.enabled
    assert job.schedule.kind == "every"
    print(f"✅ Job created: {job.name} (id: {job.id})\n")

    service.stop()


async def test_cron_add_at_job():
    """Test adding an 'at' job."""
    print("=== Test 2: Add 'at' Job ===")
    service = CronService(
        store_path=Path("/tmp/test_cron_jobs.json"),
        on_job=mock_cron_callback,
    )
    await service.start()

    # Schedule for 2 seconds from now
    at_time = datetime.now() + timedelta(seconds=2)
    job = service.add_job(
        name="Test at job",
        schedule=CronSchedule(kind="at", at_ms=int(at_time.timestamp() * 1000)),
        message="One-time reminder",
    )

    assert job.id
    assert job.schedule.kind == "at"
    print(f"✅ Job created: {job.name}\n")

    service.stop()


async def test_cron_list_jobs():
    """Test listing jobs."""
    print("=== Test 3: List Jobs ===")
    service = CronService(
        store_path=Path("/tmp/test_cron_jobs.json"),
        on_job=mock_cron_callback,
    )
    await service.start()

    # Add a job
    service.add_job(
        name="Test job 1",
        schedule=CronSchedule(kind="every", every_ms=5000),
        message="Test message 1",
    )

    service.add_job(
        name="Test job 2",
        schedule=CronSchedule(kind="every", every_ms=10000),
        message="Test message 2",
    )

    jobs = service.list_jobs()
    print(f"Total jobs: {len(jobs)}")
    for j in jobs:
        print(f"  - {j.name} (id: {j.id}, {j.schedule.kind})")

    assert len(jobs) >= 2  # At least 2 jobs
    print("✅ Test 3 passed\n")

    service.stop()


async def test_cron_remove_job():
    """Test removing a job."""
    print("=== Test 4: Remove Job ===")
    service = CronService(
        store_path=Path("/tmp/test_cron_jobs.json"),
        on_job=mock_cron_callback,
    )
    await service.start()

    # Add a job
    job = service.add_job(
        name="Test remove job",
        schedule=CronSchedule(kind="every", every_ms=5000),
        message="Test message",
    )

    # Remove it
    removed = service.remove_job(job.id)
    print(f"Removed: {removed}")

    assert removed

    jobs = service.list_jobs()
    assert len(jobs) < 4  # At least one job should be removed
    print("✅ Test 4 passed\n")

    service.stop()


async def test_cron_enable_disable():
    """Test enabling/disabling a job."""
    print("=== Test 5: Enable/Disable Job ===")
    service = CronService(
        store_path=Path("/tmp/test_cron_jobs.json"),
        on_job=mock_cron_callback,
    )
    await service.start()

    job = service.add_job(
        name="Test enable job",
        schedule=CronSchedule(kind="every", every_ms=5000),
        message="Test message",
    )

    # Disable job
    service.enable_job(job.id, enabled=False)
    print(f"Disabled job: {job.name}")

    jobs = service.list_jobs(include_disabled=False)
    assert len(jobs) == 0

    # Enable job
    service.enable_job(job.id, enabled=True)
    print(f"Enabled job: {job.name}")

    jobs = service.list_jobs(include_disabled=False)
    assert len(jobs) == 1
    print("✅ Test 5 passed\n")

    service.stop()


async def test_cron_tool():
    """Test CronTool."""
    print("=== Test 6: CronTool ===")
    service = CronService(
        store_path=Path("/tmp/test_cron_jobs.json"),
        on_job=mock_cron_callback,
    )
    await service.start()

    tool = CronTool(service)
    tool.set_context("discord", "12345")

    # Add job
    result = await tool.execute(
        action="add",
        message="Test reminder",
        every_seconds=60,
    )
    print(f"Result: {result}")
    assert "Created job" in result

    # List jobs
    result = await tool.execute(action="list")
    print(f"Result: {result}")
    assert "Scheduled jobs" in result

    # Remove job
    import re
    match = re.search(r"\(id: ([a-f0-9]+)\)", result)
    if match:
        job_id = match.group(1)
        result = await tool.execute(action="remove", job_id=job_id)
        print(f"Result: {result}")
        assert "Removed" in result

    print("✅ Test 6 passed\n")

    service.stop()


async def test_cron_status():
    """Test getting service status."""
    print("=== Test 7: Service Status ===")
    service = CronService(
        store_path=Path("/tmp/test_cron_jobs.json"),
        on_job=mock_cron_callback,
    )
    await service.start()

    status = service.status()
    print(f"Status: {status}")

    assert "enabled" in status
    assert "jobs" in status
    print("✅ Test 7 passed\n")

    service.stop()


async def main():
    """Run all tests."""
    print("🧪 Cron Tests\n" + "=" * 50)

    await test_cron_add_every_job()
    await test_cron_add_at_job()
    await test_cron_list_jobs()
    await test_cron_remove_job()
    await test_cron_enable_disable()
    await test_cron_tool()
    await test_cron_status()

    print("=" * 50)
    print("🎉 All Cron tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
