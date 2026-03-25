"""Cron execution log storage using JSONL format."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

from .types import CronRunLog

logger = logging.getLogger(__name__)


class CronLogStore:
    """Persistent storage for cron execution logs using JSONL format."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._lock = asyncio.Lock()
        self._counter = 0
        self._ensure_log_file()

    def _ensure_log_file(self) -> None:
        """Ensure log file exists and load counter."""
        if not self.log_path.exists():
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            self.log_path.write_text("", encoding="utf-8")
            return

        # Load counter from existing logs
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        if data.get("id", 0) > self._counter:
                            self._counter = data["id"]
        except Exception as e:
            logger.warning(f"Failed to load log counter: {e}")

    async def append(self, log: CronRunLog) -> None:
        """Append a log record to the log file."""
        async with self._lock:
            data = {
                "id": log.id,
                "jobId": log.job_id,
                "runAtMs": log.run_at_ms,
                "durationMs": log.duration_ms,
                "status": log.status,
            }
            if log.result:
                data["result"] = log.result[:500]  # Truncate long results
            if log.error:
                data["error"] = log.error

            line = json.dumps(data, ensure_ascii=False)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

    async def get_logs(
        self, job_id: str, limit: int = 50, offset: int = 0
    ) -> list[CronRunLog]:
        """Get execution logs for a job, ordered by time descending."""
        logs: list[CronRunLog] = []

        async with self._lock:
            if not self.log_path.exists():
                return logs

            try:
                all_logs: list[CronRunLog] = []
                with open(self.log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        data = json.loads(line)
                        if data.get("jobId") == job_id:
                            all_logs.append(CronRunLog(
                                id=data["id"],
                                job_id=data["jobId"],
                                run_at_ms=data["runAtMs"],
                                duration_ms=data["durationMs"],
                                status=data["status"],
                                result=data.get("result"),
                                error=data.get("error"),
                            ))

                # Sort by run_at_ms descending and apply pagination
                all_logs.sort(key=lambda x: x.run_at_ms, reverse=True)
                end = offset + limit if limit > 0 else len(all_logs)
                logs = all_logs[offset:end]
            except Exception as e:
                logger.warning(f"Failed to read logs: {e}")

        return logs

    async def prune_old_logs(self, days: int = 30) -> int:
        """Remove logs older than specified days. Returns count of removed logs."""
        import time

        cutoff_ms = int(time.time() * 1000) - (days * 24 * 60 * 60 * 1000)
        removed = 0

        async with self._lock:
            if not self.log_path.exists():
                return 0

            try:
                kept_lines: list[str] = []
                with open(self.log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        data = json.loads(line)
                        if data.get("runAtMs", 0) >= cutoff_ms:
                            kept_lines.append(line)
                        else:
                            removed += 1

                # Rewrite file with kept logs
                with open(self.log_path, "w", encoding="utf-8") as f:
                    for line in kept_lines:
                        f.write(line + "\n")

                logger.info(f"Pruned {removed} old log entries")
            except Exception as e:
                logger.warning(f"Failed to prune logs: {e}")

        return removed
