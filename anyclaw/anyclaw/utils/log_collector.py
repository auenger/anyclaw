"""System Log Collector

Collects Python logging module output for the API.
Supports in-memory storage with optional file persistence via background thread.
"""

from __future__ import annotations

import json
import logging
import os
import queue
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Iterator
from typing_extensions import Literal


LogLevel = Literal["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"]
LogCategory = Literal["agent", "tool", "task", "system"]

# Default log retention in days
DEFAULT_RETENTION_DAYS = 7
# Max queue size for file writer
_MAX_WRITE_QUEUE = 10000


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


class LogCollectorHandler(logging.Handler):
    """Custom logging handler that collects logs in memory."""

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
    Collects system logs in memory for API access.

    Thread-safe singleton that captures Python logging output.
    Supports optional file persistence via a background daemon thread.
    """

    _instance: Optional["SystemLogCollector"] = None
    _lock = threading.Lock()

    def __new__(cls, max_entries: int = 1000):
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, max_entries: int = 1000):
        """Initialize the collector."""
        if self._initialized:
            return

        self.max_entries = max_entries
        self._entries: deque[LogEntry] = deque(maxlen=max_entries)
        self._handler: Optional[LogCollectorHandler] = None
        self._subscribers: List[object] = []

        # File persistence state
        self._write_queue: queue.Queue[Optional[LogEntry]] = queue.Queue(maxsize=_MAX_WRITE_QUEUE)
        self._writer_thread: Optional[threading.Thread] = None
        self._writer_shutdown = threading.Event()
        self._current_date: str = ""
        self._current_file = None  # type: Optional[object]  # file handle
        self._log_dir: Optional[str] = None
        self._retention_days = DEFAULT_RETENTION_DAYS
        self._persistence_started = False

        self._initialized = True

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

    # ==================== File Persistence ====================

    def start_file_persistence(
        self,
        log_dir: Optional[str] = None,
        retention_days: int = DEFAULT_RETENTION_DAYS,
    ) -> None:
        """Start background file persistence thread.

        Args:
            log_dir: Directory for log files. Defaults to ~/.anyclaw/logs/
            retention_days: Number of days to keep log files (default 7)
        """
        if self._persistence_started:
            return

        self._log_dir = log_dir or os.path.join(
            os.path.expanduser("~"), ".anyclaw", "logs"
        )
        self._retention_days = retention_days

        # Ensure log directory exists with correct permissions
        os.makedirs(self._log_dir, mode=0o700, exist_ok=True)

        self._writer_shutdown.clear()
        self._writer_thread = threading.Thread(
            target=self._writer_loop,
            name="log-writer",
            daemon=True,
        )
        self._writer_thread.start()
        self._persistence_started = True

    def stop_file_persistence(self, timeout: float = 3.0) -> None:
        """Stop background file persistence thread.

        Args:
            timeout: Max seconds to wait for queue to drain
        """
        if not self._persistence_started:
            return

        # Signal shutdown and wait for queue to drain
        self._write_queue.put(None)  # Sentinel
        if self._writer_thread and self._writer_thread.is_alive():
            self._writer_thread.join(timeout=timeout)

        # Close current file
        if self._current_file is not None:
            try:
                self._current_file.close()
            except Exception:
                pass
            self._current_file = None
            self._current_date = ""

        self._persistence_started = False
        self._writer_thread = None

    def _writer_loop(self) -> None:
        """Background thread: consume queue and write to JSONL files."""
        while True:
            entry = self._write_queue.get()
            if entry is None:
                # Sentinel: drain remaining and exit
                # Process any remaining items
                while True:
                    try:
                        remaining = self._write_queue.get_nowait()
                        if remaining is None:
                            break
                        self._write_entry_to_file(remaining)
                    except queue.Empty:
                        break
                break

            self._write_entry_to_file(entry)

    def _write_entry_to_file(self, entry: LogEntry) -> None:
        """Write a single log entry to the appropriate date file."""
        try:
            # Determine date from entry timestamp
            date_str = entry.timestamp[:10]  # "YYYY-MM-DD"
            today_str = datetime.now().strftime("%Y-%m-%d")

            # Handle date rotation
            if date_str != self._current_date:
                # Close old file
                if self._current_file is not None:
                    try:
                        self._current_file.close()
                    except Exception:
                        pass
                    self._current_file = None
                    self._current_date = ""

                # Trigger cleanup on date change
                if self._current_date and date_str != self._current_date:
                    self._cleanup_old_logs()

                # Open new file
                self._current_date = date_str
                filename = f"system-{date_str}.jsonl"
                filepath = os.path.join(self._log_dir, filename)
                self._current_file = open(filepath, "a", encoding="utf-8")
                # Set file permissions (only on new file creation)
                try:
                    os.chmod(filepath, 0o600)
                except OSError:
                    pass

            if self._current_file is not None:
                line = json.dumps(entry.to_dict(), ensure_ascii=False)
                self._current_file.write(line + "\n")
                self._current_file.flush()

        except Exception:
            # Don't let writer errors propagate
            pass

    def _cleanup_old_logs(self) -> None:
        """Delete log files older than retention period."""
        if not self._log_dir:
            return

        try:
            cutoff = datetime.now() - timedelta(days=self._retention_days)
            cutoff_str = cutoff.strftime("%Y-%m-%d")

            for filename in os.listdir(self._log_dir):
                if not filename.startswith("system-") or not filename.endswith(".jsonl"):
                    continue

                # Extract date from filename: system-YYYY-MM-DD.jsonl
                date_part = filename[7:17]  # "YYYY-MM-DD"
                if date_part < cutoff_str:
                    filepath = os.path.join(self._log_dir, filename)
                    try:
                        os.remove(filepath)
                    except OSError:
                        pass

        except OSError:
            pass

    # ==================== Historical Log Reading ====================

    def _read_logs_from_file(self, date_str: str) -> List[LogEntry]:
        """Read log entries from a JSONL file for a specific date.

        Args:
            date_str: Date in YYYY-MM-DD format

        Returns:
            List of LogEntry objects
        """
        if not self._log_dir:
            return []

        filepath = os.path.join(self._log_dir, f"system-{date_str}.jsonl")
        if not os.path.exists(filepath):
            return []

        entries = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        entries.append(LogEntry(
                            time=data.get("time", ""),
                            level=data.get("level", "INFO"),
                            category=data.get("category", "system"),
                            message=data.get("message", ""),
                            agent=data.get("agent"),
                            details=data.get("details"),
                            timestamp=data.get("timestamp", ""),
                        ))
                    except (json.JSONDecodeError, TypeError):
                        continue
        except OSError:
            pass

        return entries

    def get_available_dates(self) -> List[str]:
        """Get list of dates with available log files.

        Returns:
            Sorted list of date strings (YYYY-MM-DD), most recent first.
            Always includes today's date.
        """
        dates = set()

        # Always include today
        dates.add(datetime.now().strftime("%Y-%m-%d"))

        # Scan log directory
        if self._log_dir and os.path.isdir(self._log_dir):
            try:
                for filename in os.listdir(self._log_dir):
                    if filename.startswith("system-") and filename.endswith(".jsonl"):
                        date_part = filename[7:17]
                        dates.add(date_part)
            except OSError:
                pass

        return sorted(dates, reverse=True)

    # ==================== Core API ====================

    def add_entry(self, entry: LogEntry) -> None:
        """Add a log entry.

        Only writes to memory deque and queues for file persistence.
        NO file I/O in this method.
        """
        with self._lock:
            self._entries.append(entry)

        # Queue for file persistence (non-blocking, drop if full)
        if self._persistence_started:
            try:
                self._write_queue.put_nowait(entry)
            except queue.Full:
                pass  # Drop entry silently

        # Notify subscribers
        for subscriber in self._subscribers:
            try:
                if hasattr(subscriber, "on_log_entry"):
                    subscriber.on_log_entry(entry)
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

        For today's date: reads from memory.
        For historical dates: reads from JSONL file.

        Args:
            level: Filter by log level (DEBUG, INFO, WARN, ERROR)
            category: Filter by category (agent, tool, task, system)
            date: Filter by date (YYYY-MM-DD)
            search: Search in message
            limit: Maximum entries to return

        Returns:
            List of log entry dictionaries
        """
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Route to file reader for historical dates
        if date and date != today_str:
            entries = self._read_logs_from_file(date)
        else:
            with self._lock:
                entries = list(self._entries)

        # Filter by level
        if level and level != "all":
            entries = [e for e in entries if e.level == level]

        # Filter by category
        if category and category != "all":
            entries = [e for e in entries if e.category == category]

        # Filter by date (for memory entries when no date or today)
        if date and date == today_str:
            entries = [e for e in entries if e.timestamp.startswith(date)]

        # Search in message
        if search:
            search_lower = search.lower()
            entries = [e for e in entries if search_lower in e.message.lower()]

        # Apply limit (most recent first)
        entries = entries[-limit:] if len(entries) > limit else entries

        return [e.to_dict() for e in entries]

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
        """Clear all log entries."""
        with self._lock:
            self._entries.clear()

    def stream_logs(self) -> Iterator[dict]:
        """
        Stream log entries as they arrive.

        This is a generator that yields log entries.
        """
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
