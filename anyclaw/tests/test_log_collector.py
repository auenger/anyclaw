"""Tests for SystemLogCollector with file persistence."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from anyclaw.utils.log_collector import (
    LogEntry,
    SystemLogCollector,
)


class TestLogEntry:
    """Tests for LogEntry dataclass."""

    def test_to_dict(self):
        """Test converting LogEntry to dictionary."""
        entry = LogEntry(
            time="12:00:00",
            level="INFO",
            category="agent",
            message="Test message",
            timestamp="2026-03-26T12:00:00",
        )
        result = entry.to_dict()

        assert result["time"] == "12:00:00"
        assert result["level"] == "INFO"
        assert result["category"] == "agent"
        assert result["message"] == "Test message"
        assert result["timestamp"] == "2026-03-26T12:00:00"
        assert "agent" not in result
        assert "details" not in result

    def test_to_dict_with_optional_fields(self):
        """Test LogEntry with optional fields."""
        entry = LogEntry(
            time="12:00:00",
            level="ERROR",
            category="tool",
            message="Error message",
            agent="test-agent",
            details={"key": "value"},
            timestamp="2026-03-26T12:00:00",
        )
        result = entry.to_dict()

        assert result["agent"] == "test-agent"
        assert result["details"] == {"key": "value"}

    def test_to_jsonl(self):
        """Test converting LogEntry to JSONL format."""
        entry = LogEntry(
            time="12:00:00",
            level="INFO",
            category="system",
            message="Test message",
            timestamp="2026-03-26T12:00:00",
        )
        jsonl = entry.to_jsonl()

        # Should be valid JSON
        parsed = json.loads(jsonl)
        assert parsed["time"] == "12:00:00"

        # Should not contain newlines
        assert "\n" not in jsonl


class TestSystemLogCollectorFilePersistence:
    """Tests for file persistence functionality."""

    def test_get_log_file_path(self):
        """Test log file path generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)

            # Create a non-singleton instance for testing
            collector = object.__new__(SystemLogCollector)
            collector._log_dir = log_dir

            path = collector._get_log_file_path("2026-03-26")
            assert path == log_dir / "system-2026-03-26.jsonl"

    def test_read_logs_from_file(self):
        """Test reading logs from a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)

            # Create a log file
            log_file = log_dir / "system-2026-03-25.jsonl"
            with open(log_file, "w") as f:
                f.write('{"time":"12:00:00","level":"INFO","category":"agent","message":"Historical log","timestamp":"2026-03-25T12:00:00"}\n')

            # Create a non-singleton instance for testing
            collector = object.__new__(SystemLogCollector)
            collector._log_dir = log_dir

            logs = collector._read_logs_from_file("2026-03-25")

            assert len(logs) == 1
            assert logs[0]["message"] == "Historical log"

    def test_read_logs_from_nonexistent_file(self):
        """Test reading from a non-existent file returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)

            collector = object.__new__(SystemLogCollector)
            collector._log_dir = log_dir

            logs = collector._read_logs_from_file("2020-01-01")
            assert logs == []

    def test_get_available_dates(self):
        """Test getting list of available dates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)

            # Create some log files
            (log_dir / "system-2026-03-24.jsonl").touch()
            (log_dir / "system-2026-03-25.jsonl").touch()

            collector = object.__new__(SystemLogCollector)
            collector._log_dir = log_dir

            dates = collector.get_available_dates()

            # Should include created dates
            assert "2026-03-24" in dates
            assert "2026-03-25" in dates

    def test_get_logs_from_file_for_historical_date(self):
        """Test that get_logs reads from file for historical dates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)

            # Create a historical log file
            log_file = log_dir / "system-2026-03-25.jsonl"
            with open(log_file, "w") as f:
                f.write('{"time":"12:00:00","level":"INFO","category":"agent","message":"Historical log","timestamp":"2026-03-25T12:00:00"}\n')

            collector = object.__new__(SystemLogCollector)
            collector._log_dir = log_dir
            collector._lock = MagicMock()
            collector._entries = []

            logs = collector.get_logs(date="2026-03-25")

            assert len(logs) == 1
            assert logs[0]["message"] == "Historical log"

    def test_get_logs_with_filters(self):
        """Test get_logs with level and category filters."""
        collector = object.__new__(SystemLogCollector)
        collector._lock = MagicMock()

        # Create entries with different levels and categories
        collector._entries = [
            LogEntry(time="12:00:00", level="INFO", category="agent", message="INFO agent", timestamp="2026-03-26T12:00:00"),
            LogEntry(time="12:01:00", level="ERROR", category="tool", message="ERROR tool", timestamp="2026-03-26T12:01:00"),
            LogEntry(time="12:02:00", level="INFO", category="tool", message="INFO tool", timestamp="2026-03-26T12:02:00"),
        ]

        # Filter by level
        logs = collector.get_logs(level="ERROR")
        assert len(logs) == 1
        assert logs[0]["level"] == "ERROR"

        # Filter by category
        logs = collector.get_logs(category="agent")
        assert len(logs) == 1
        assert logs[0]["category"] == "agent"

        # Filter by both
        logs = collector.get_logs(level="INFO", category="tool")
        assert len(logs) == 1

    def test_get_logs_with_search(self):
        """Test get_logs with search filter."""
        collector = object.__new__(SystemLogCollector)
        collector._lock = MagicMock()

        collector._entries = [
            LogEntry(time="12:00:00", level="INFO", category="agent", message="Unique search term here", timestamp="2026-03-26T12:00:00"),
            LogEntry(time="12:01:00", level="INFO", category="agent", message="Another message", timestamp="2026-03-26T12:01:00"),
        ]

        logs = collector.get_logs(search="Unique search term")
        assert len(logs) == 1

        logs = collector.get_logs(search="not found")
        assert len(logs) == 0

    def test_get_logs_limit(self):
        """Test get_logs respects limit."""
        collector = object.__new__(SystemLogCollector)
        collector._lock = MagicMock()

        collector._entries = [
            LogEntry(time=f"12:0{i}:00", level="INFO", category="agent", message=f"Message {i}", timestamp=f"2026-03-26T12:0{i}:00")
            for i in range(10)
        ]

        logs = collector.get_logs(limit=5)
        assert len(logs) == 5
