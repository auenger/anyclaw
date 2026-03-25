"""System Log Collector

Collects Python logging module output for the API.
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Iterator
from typing_extensions import Literal


LogLevel = Literal["DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"]
LogCategory = Literal["agent", "tool", "task", "system"]


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

    def add_entry(self, entry: LogEntry) -> None:
        """Add a log entry."""
        with self._lock:
            self._entries.append(entry)

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

        Args:
            level: Filter by log level (DEBUG, INFO, WARN, ERROR)
            category: Filter by category (agent, tool, task, system)
            date: Filter by date (YYYY-MM-DD)
            search: Search in message
            limit: Maximum entries to return

        Returns:
            List of log entry dictionaries
        """
        with self._lock:
            entries = list(self._entries)

        # Filter by level
        if level and level != "all":
            entries = [e for e in entries if e.level == level]

        # Filter by category
        if category and category != "all":
            entries = [e for e in entries if e.category == category]

        # Filter by date
        if date:
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
