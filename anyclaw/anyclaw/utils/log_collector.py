"""System Log Collector

Collects Python logging module output for the API.
Supports both in-memory storage and file persistence.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Iterator
from typing_extensions import Literal


LogLevel = Literal["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"]
LogCategory = Literal["agent", "tool", "task", "system"]

# Default log directory
DEFAULT_LOG_DIR = Path.home() / ".anyclaw" / "logs"
# Keep logs for N days
DEFAULT_RETENTION_DAYS = 7


@dataclass
class LogEntry:
    """A single log entry."""
    time: str
    level: str
    category: str
    message: str
    agent: Optional[str] = None
    details: Optional[dict] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            "time": self.time,
            "level": self.level,
            "category": self.category,
            "message": self.message,
            "timestamp": self.timestamp,
        }
        if self.agent:
            result["agent"] = self.agent
        if self.details:
            result["details"] = self.details
        return result

    def to_jsonl(self) -> str:
        """Convert to JSONL format (single line JSON)."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class LogCollectorHandler(logging.Handler):
    """Custom logging handler that collects logs in memory and persists to file."""

    def __init__(self, collector: "SystemLogCollector", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collector = collector

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to the collector."""
        try:
            # Format time
            log_time = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

            # Map log level
            level = record.levelname
            if level == "WARNING":
                level = "WARN"
            elif level == "CRITICAL":
                level = "ERROR"

            # Determine category from logger name
            category = self._get_category(record.name)

            # Extract agent name if available
            agent = None
            if hasattr(record, "agent_id"):
                agent = record.agent_id

            # Build details from extra fields
            details = None
            extra_fields = {
                k: v for k, v in record.__dict__.items()
                if k not in (
                    "name", "msg", "args", "created", "filename", "funcName",
                    "levelname", "levelno", "lineno", "module", "msecs",
                    "pathname", "process", "processName", "relativeCreated",
                    "stack_info", "exc_info", "exc_text", "thread", "threadName",
                    "message", "agent_id"
                )
                and not k.startswith("_")
            }
            if extra_fields:
                details = extra_fields

            entry = LogEntry(
                time=log_time,
                level=level,
                category=category,
                message=record.getMessage(),
                agent=agent,
                details=details,
                timestamp=datetime.fromtimestamp(record.created).isoformat(),
            )

            self.collector.add_entry(entry)

        except Exception:
            # Don't let logging errors propagate
            pass

    def _get_category(self, logger_name: str) -> str:
        """Determine log category from logger name."""
        name_lower = logger_name.lower()

        if "agent" in name_lower:
            return "agent"
        elif "tool" in name_lower:
            return "tool"
        elif "task" in name_lower or "cron" in name_lower or "subagent" in name_lower:
            return "task"
        else:
            return "system"


class SystemLogCollector:
    """
    Collects system logs in memory and persists to file.

    Thread-safe singleton that captures Python logging output.
    Logs are stored both in memory (for fast access) and on disk (for persistence).
    """

    _instance: Optional["SystemLogCollector"] = None
    _lock = threading.Lock()

    def __new__(cls, max_entries: int = 1000, log_dir: Optional[Path] = None):
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, max_entries: int = 1000, log_dir: Optional[Path] = None):
        """Initialize the collector."""
        if self._initialized:
            return

        self.max_entries = max_entries
        self._entries: deque[LogEntry] = deque(maxlen=max_entries)
        self._handler: Optional[LogCollectorHandler] = None
        self._subscribers: List[object] = []

        # File persistence
        self._log_dir = log_dir or DEFAULT_LOG_DIR
        self._current_date: Optional[str] = None
        self._file_handle: Optional[object] = None
        self._file_lock = threading.Lock()

        # Retention
        self._retention_days = DEFAULT_RETENTION_DAYS

        self._initialized = True

    @property
    def log_dir(self) -> Path:
        """Get log directory path."""
        return self._log_dir

    def add_handler(self, level: int = logging.DEBUG) -> None:
        """Add the custom handler to Python logging."""
        if self._handler is not None:
            return

        self._handler = LogCollectorHandler(self)
        self._handler.setLevel(level)

        # Add to root logger to capture all logs
        root_logger = logging.getLogger()
        root_logger.addHandler(self._handler)

    def remove_handler(self) -> None:
        """Remove the custom handler from Python logging."""
        if self._handler is None:
            return

        root_logger = logging.getLogger()
        root_logger.removeHandler(self._handler)
        self._handler = None

        # Close file handle
        self._close_file_handle()

    def add_entry(self, entry: LogEntry) -> None:
        """Add a log entry to memory and persist to file."""
        with self._lock:
            self._entries.append(entry)

        # Persist to file
        self._persist_entry(entry)

        # Notify subscribers
        for subscriber in self._subscribers:
            try:
                if hasattr(subscriber, "on_log_entry"):
                    subscriber.on_log_entry(entry)
            except Exception:
                pass

    def _get_log_file_path(self, date_str: str) -> Path:
        """Get log file path for a specific date."""
        return self._log_dir / f"system-{date_str}.jsonl"

    def _get_current_date(self) -> str:
        """Get current date string (YYYY-MM-DD)."""
        return datetime.now().strftime("%Y-%m-%d")

    def _ensure_log_dir(self) -> None:
        """Ensure log directory exists."""
        if not self._log_dir.exists():
            self._log_dir.mkdir(parents=True, exist_ok=True)
            # Set restrictive permissions
            os.chmod(self._log_dir, 0o700)

    def _get_file_handle(self, date_str: str):
        """Get or create file handle for the given date."""
        with self._file_lock:
            if self._current_date != date_str or self._file_handle is None:
                # Close previous handle
                self._close_file_handle()

                # Ensure directory exists
                self._ensure_log_dir()

                # Open new file
                file_path = self._get_log_file_path(date_str)
                self._file_handle = open(file_path, "a", encoding="utf-8")
                self._current_date = date_str

                # Set restrictive permissions on file
                os.chmod(file_path, 0o600)

            return self._file_handle

    def _close_file_handle(self) -> None:
        """Close the current file handle."""
        with self._file_lock:
            if self._file_handle is not None:
                try:
                    self._file_handle.close()
                except Exception:
                    pass
                self._file_handle = None
                self._current_date = None

    def _persist_entry(self, entry: LogEntry) -> None:
        """Persist a log entry to file."""
        try:
            # Extract date from timestamp
            date_str = entry.timestamp[:10]  # YYYY-MM-DD

            # Get file handle (will rotate if date changed)
            fh = self._get_file_handle(date_str)

            # Write entry as JSONL
            fh.write(entry.to_jsonl() + "\n")
            fh.flush()

        except Exception:
            # Don't let file write errors affect logging
            pass

    def _read_logs_from_file(self, date_str: str) -> List[dict]:
        """Read logs from a specific date file."""
        file_path = self._get_log_file_path(date_str)

        if not file_path.exists():
            return []

        logs = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            logs.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception:
            pass

        return logs

    def _cleanup_old_logs(self) -> None:
        """Clean up logs older than retention period."""
        if not self._log_dir.exists():
            return

        cutoff_date = datetime.now()
        from datetime import timedelta
        cutoff_date = cutoff_date - timedelta(days=self._retention_days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")

        try:
            for log_file in self._log_dir.glob("system-*.jsonl"):
                # Extract date from filename
                date_part = log_file.stem.replace("system-", "")
                if date_part < cutoff_str:
                    log_file.unlink()
        except Exception:
            pass

    def get_logs(
        self,
        level: Optional[str] = None,
        category: Optional[str] = None,
        date: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
    ) -> List[dict]:
        """
        Get filtered log entries.

        Args:
            level: Filter by log level (DEBUG, INFO, WARN, ERROR)
            category: Filter by category (agent, tool, task, system)
            date: Filter by date (YYYY-MM-DD)
            search: Search in message
            limit: Maximum entries to return

        Returns:
            List of log entry dictionaries
        """
        today = self._get_current_date()

        # Determine source: memory or file
        if date and date != today:
            # Historical date - read from file
            raw_logs = self._read_logs_from_file(date)
        else:
            # Today or no date - read from memory
            with self._lock:
                raw_logs = [e.to_dict() for e in self._entries]

        # Apply filters
        filtered = []
        for log in raw_logs:
            # Filter by level
            if level and level != "all" and log.get("level") != level:
                continue

            # Filter by category
            if category and category != "all" and log.get("category") != category:
                continue

            # Filter by date (for memory logs)
            if date and log.get("timestamp", "").startswith(date) is False:
                continue

            # Search in message
            if search:
                search_lower = search.lower()
                if search_lower not in log.get("message", "").lower():
                    continue

            filtered.append(log)

        # Apply limit (most recent last)
        if len(filtered) > limit:
            filtered = filtered[-limit:]

        return filtered

    def get_available_dates(self) -> List[str]:
        """Get list of dates that have log files."""
        dates = []

        if not self._log_dir.exists():
            return dates

        try:
            for log_file in self._log_dir.glob("system-*.jsonl"):
                date_part = log_file.stem.replace("system-", "")
                if len(date_part) == 10 and date_part.count("-") == 2:
                    dates.append(date_part)
        except Exception:
            pass

        # Add today if not in list (in-memory logs)
        today = self._get_current_date()
        if today not in dates:
            dates.append(today)

        return sorted(dates, reverse=True)

    def get_stats(self) -> dict:
        """Get log statistics."""
        with self._lock:
            entries = list(self._entries)

        stats = {
            "total": len(entries),
            "by_level": {},
            "by_category": {},
        }

        for entry in entries:
            # Count by level
            level = entry.level
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1

            # Count by category
            category = entry.category
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

        return stats

    def clear(self) -> None:
        """Clear all log entries from memory (does not delete files)."""
        with self._lock:
            self._entries.clear()

    def stream_logs(self) -> Iterator[dict]:
        """
        Stream log entries as they arrive.

        This is a generator that yields log entries.
        """
        import queue

        entry_queue: queue.Queue[Optional[LogEntry]] = queue.Queue()

        class Subscriber:
            def on_log_entry(self, entry: LogEntry):
                entry_queue.put(entry)

        subscriber = Subscriber()
        self._subscribers.append(subscriber)

        try:
            while True:
                entry = entry_queue.get()
                if entry is None:
                    break
                yield entry.to_dict()
        finally:
            self._subscribers.remove(subscriber)

    def stop_stream(self) -> None:
        """Stop all active streams."""
        for subscriber in self._subscribers:
            try:
                if hasattr(subscriber, "on_log_entry"):
                    subscriber.on_log_entry(None)  # Signal to stop
            except Exception:
                pass


# Global instance
collector = SystemLogCollector()


def get_log_collector() -> SystemLogCollector:
    """Get the global log collector instance."""
    return collector
