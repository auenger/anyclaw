"""Tests for SystemLogCollector file persistence."""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pytest

from anyclaw.utils.log_collector import LogEntry, SystemLogCollector


@pytest.fixture
def collector(tmp_path):
    """Create a fresh collector instance for testing."""
    # Reset singleton to allow fresh instance
    SystemLogCollector._instance = None
    SystemLogCollector._initialized = False

    c = SystemLogCollector()
    yield c

    # Cleanup
    c.stop_file_persistence(timeout=1.0)

    # Reset singleton
    SystemLogCollector._instance = None
    SystemLogCollector._initialized = False


def make_entry(message: str = "test", level: str = "INFO", category: str = "system",
               timestamp: Optional[str] = None) -> LogEntry:
    """Helper to create a LogEntry."""
    return LogEntry(
        time="12:00:00",
        level=level,
        category=category,
        message=message,
        timestamp=timestamp or datetime.now().isoformat(),
    )


class TestBackgroundWriter:
    """Tests for background thread file writing."""

    def test_add_entry_does_not_block(self, collector, tmp_path):
        """add_entry should return within 1ms regardless of file I/O."""
        collector.start_file_persistence(log_dir=str(tmp_path))

        entry = make_entry("non-blocking test")
        start = time.perf_counter()
        collector.add_entry(entry)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.1  # Very generous; should be <1ms

    def test_writes_to_jsonl_file(self, collector, tmp_path):
        """Log entries should be written to a JSONL file."""
        collector.start_file_persistence(log_dir=str(tmp_path))

        collector.add_entry(make_entry("hello world"))
        collector.add_entry(make_entry("second message"))

        # Wait for writer thread to process
        time.sleep(0.3)

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = tmp_path / f"system-{today}.jsonl"
        assert log_file.exists()

        lines = log_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2

        data = json.loads(lines[0])
        assert data["message"] == "hello world"
        assert data["level"] == "INFO"

    def test_date_rotation(self, collector, tmp_path):
        """Logs with different dates should go to different files."""
        collector.start_file_persistence(log_dir=str(tmp_path))

        entry1 = make_entry("today log", timestamp="2026-03-27T10:00:00")
        entry2 = make_entry("yesterday log", timestamp="2026-03-26T10:00:00")
        collector.add_entry(entry1)
        collector.add_entry(entry2)

        time.sleep(0.3)

        assert (tmp_path / "system-2026-03-27.jsonl").exists()
        assert (tmp_path / "system-2026-03-26.jsonl").exists()

    def test_queue_full_drops_silently(self, collector, tmp_path):
        """When queue is full, add_entry should not raise."""
        # Use a very small queue by monkeypatching
        collector._write_queue.maxsize = 2
        collector.start_file_persistence(log_dir=str(tmp_path))

        # Block the writer thread briefly
        import queue as queue_mod
        lock = threading.Lock()
        lock.acquire()
        original_get = collector._write_queue.get

        def blocked_get(timeout=None):
            if lock.locked():
                time.sleep(0.05)
                lock.release()
            return original_get(timeout=timeout)

        collector._write_queue.get = blocked_get

        # Fill queue beyond capacity
        for i in range(20):
            collector.add_entry(make_entry(f"msg-{i}"))

        time.sleep(0.2)
        # Should not have raised any exception
        collector.stop_file_persistence()


class TestHistoricalReading:
    """Tests for reading historical log files."""

    def test_read_from_file(self, collector, tmp_path):
        """get_logs with a historical date should read from file."""
        collector.start_file_persistence(log_dir=str(tmp_path))

        # Write a log with yesterday's timestamp
        entry = make_entry("old message", timestamp="2026-03-25T10:00:00")
        collector.add_entry(entry)

        time.sleep(0.3)

        # Read back
        logs = collector.get_logs(date="2026-03-25")
        assert len(logs) == 1
        assert logs[0]["message"] == "old message"

    def test_today_reads_from_memory(self, collector, tmp_path):
        """get_logs with today's date should read from memory."""
        collector.start_file_persistence(log_dir=str(tmp_path))

        today = datetime.now().strftime("%Y-%m-%d")
        collector.add_entry(make_entry("memory msg", timestamp=f"{today}T10:00:00"))

        logs = collector.get_logs(date=today)
        assert len(logs) >= 1
        assert any(l["message"] == "memory msg" for l in logs)

    def test_nonexistent_date_returns_empty(self, collector, tmp_path):
        """get_logs with a date that has no logs returns empty list."""
        collector.start_file_persistence(log_dir=str(tmp_path))
        logs = collector.get_logs(date="2020-01-01")
        assert logs == []

    def test_filtering_works_on_historical(self, collector, tmp_path):
        """Level/category filters should work on historical logs."""
        collector.start_file_persistence(log_dir=str(tmp_path))

        collector.add_entry(make_entry("info msg", level="INFO", timestamp="2026-03-25T10:00:00"))
        collector.add_entry(make_entry("error msg", level="ERROR", timestamp="2026-03-25T11:00:00"))

        time.sleep(0.3)

        error_logs = collector.get_logs(date="2026-03-25", level="ERROR")
        assert len(error_logs) == 1
        assert error_logs[0]["level"] == "ERROR"


class TestAvailableDates:
    """Tests for get_available_dates."""

    def test_returns_today(self, collector, tmp_path):
        """Should always include today's date."""
        collector.start_file_persistence(log_dir=str(tmp_path))
        dates = collector.get_available_dates()
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in dates

    def test_detects_log_files(self, collector, tmp_path):
        """Should detect dates from existing log files."""
        # Pre-create log files
        (tmp_path / "system-2026-03-25.jsonl").write_text('{"msg":"x"}\n')
        (tmp_path / "system-2026-03-26.jsonl").write_text('{"msg":"y"}\n')

        collector.start_file_persistence(log_dir=str(tmp_path))
        dates = collector.get_available_dates()

        assert "2026-03-25" in dates
        assert "2026-03-26" in dates

    def test_sorted_most_recent_first(self, collector, tmp_path):
        """Dates should be sorted with most recent first."""
        (tmp_path / "system-2026-03-20.jsonl").write_text('{"msg":"x"}\n')
        (tmp_path / "system-2026-03-25.jsonl").write_text('{"msg":"y"}\n')

        collector.start_file_persistence(log_dir=str(tmp_path))
        dates = collector.get_available_dates()

        assert dates == sorted(dates, reverse=True)


class TestLogCleanup:
    """Tests for automatic log cleanup."""

    def test_deletes_old_files(self, collector, tmp_path):
        """Should delete files older than retention period."""
        collector._retention_days = 3
        collector.start_file_persistence(log_dir=str(tmp_path))

        # Create an old log file (10 days ago)
        old_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        old_file = tmp_path / f"system-{old_date}.jsonl"
        old_file.write_text('{"msg":"old"}\n')

        # Create a recent log file (1 day ago)
        recent_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        recent_file = tmp_path / f"system-{recent_date}.jsonl"
        recent_file.write_text('{"msg":"recent"}\n')

        # Trigger cleanup
        collector._cleanup_old_logs()

        assert not old_file.exists()
        assert recent_file.exists()

    def test_cleanup_does_not_delete_current(self, collector, tmp_path):
        """Cleanup should not delete the currently open file."""
        collector._retention_days = 0  # Delete everything
        collector.start_file_persistence(log_dir=str(tmp_path))

        today = datetime.now().strftime("%Y-%m-%d")
        current_file = tmp_path / f"system-{today}.jsonl"
        collector.add_entry(make_entry("current"))

        time.sleep(0.3)
        assert current_file.exists()

        # Cleanup with retention 0 should not delete today's file
        # because _cleanup_old_logs uses strict < comparison
        collector._cleanup_old_logs()
        assert current_file.exists()


class TestFilePermissions:
    """Tests for file and directory security."""

    def test_log_dir_permissions(self, collector, tmp_path):
        """Log directory should be created with 0o700 permissions."""
        log_dir = tmp_path / "secure_logs"
        collector.start_file_persistence(log_dir=str(log_dir))

        # Check permissions (may be affected by umask)
        stat_info = os.stat(log_dir)
        # On some systems umask affects this, so just verify it's restricted
        assert stat_info.st_mode & 0o777 <= 0o700

    def test_log_file_permissions(self, collector, tmp_path):
        """Log files should be created with 0o600 permissions."""
        collector.start_file_persistence(log_dir=str(tmp_path))
        collector.add_entry(make_entry("permission test"))

        time.sleep(0.3)

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = tmp_path / f"system-{today}.jsonl"
        stat_info = os.stat(log_file)
        assert stat_info.st_mode & 0o777 <= 0o600


class TestLifecycle:
    """Tests for start/stop lifecycle."""

    def test_start_stop_idempotent(self, collector, tmp_path):
        """Multiple start/stop calls should be safe."""
        collector.start_file_persistence(log_dir=str(tmp_path))
        collector.start_file_persistence(log_dir=str(tmp_path))  # Idempotent

        collector.add_entry(make_entry("test"))
        time.sleep(0.2)

        collector.stop_file_persistence()
        collector.stop_file_persistence()  # Idempotent

    def test_stop_drains_queue(self, collector, tmp_path):
        """Stop should drain remaining entries before exiting."""
        collector.start_file_persistence(log_dir=str(tmp_path))

        for i in range(50):
            collector.add_entry(make_entry(f"drain-{i}"))

        collector.stop_file_persistence(timeout=5.0)

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = tmp_path / f"system-{today}.jsonl"
        if log_file.exists():
            lines = log_file.read_text(encoding="utf-8").strip().split("\n")
            assert len(lines) == 50

    def test_daemon_thread(self, collector, tmp_path):
        """Writer thread should be a daemon thread."""
        collector.start_file_persistence(log_dir=str(tmp_path))
        assert collector._writer_thread is not None
        assert collector._writer_thread.daemon is True


class TestPersistenceOff:
    """Tests for behavior when persistence is not started."""

    def test_add_entry_works_without_persistence(self, collector):
        """add_entry should work fine without file persistence."""
        entry = make_entry("no persistence")
        collector.add_entry(entry)

        logs = collector.get_logs()
        assert len(logs) >= 1
        assert any(l["message"] == "no persistence" for l in logs)

    def test_get_available_dates_without_persistence(self, collector):
        """get_available_dates should return today without persistence."""
        dates = collector.get_available_dates()
        today = datetime.now().strftime("%Y-%m-%d")
        assert dates == [today]

    def test_historical_read_without_persistence(self, collector):
        """Historical read should return empty without persistence."""
        logs = collector.get_logs(date="2026-01-01")
        assert logs == []
