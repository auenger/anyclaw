"""Daemon management for AnyClaw serve mode.

Supports:
- Background daemon process
- PID file management
- Status checking
- Graceful shutdown
"""

from __future__ import annotations

import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import psutil

# Default paths
DEFAULT_PID_FILE = Path.home() / ".anyclaw" / "serve.pid"
DEFAULT_LOG_FILE = Path.home() / ".anyclaw" / "logs" / "serve.log"
DEFAULT_STATUS_FILE = Path.home() / ".anyclaw" / "serve.status"


class DaemonManager:
    """Manages daemon process lifecycle.

    Responsibilities:
    - Start daemon process
    - Write/read PID file
    - Check process status
    - Stop daemon gracefully
    """

    def __init__(
        self,
        pid_file: Optional[Path] = None,
        log_file: Optional[Path] = None,
        status_file: Optional[Path] = None,
    ):
        """Initialize daemon manager.

        Args:
            pid_file: Path to PID file
            log_file: Path to log file
            status_file: Path to status file
        """
        self.pid_file = pid_file or DEFAULT_PID_FILE
        self.log_file = log_file or DEFAULT_LOG_FILE
        self.status_file = status_file or DEFAULT_STATUS_FILE

        # Ensure parent directories exist
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def write_pid(self, pid: Optional[int] = None) -> None:
        """Write PID to file.

        Args:
            pid: Process ID (default: current process)
        """
        pid = pid or os.getpid()
        self.pid_file.write_text(str(pid))

    def read_pid(self) -> Optional[int]:
        """Read PID from file.

        Returns:
            PID or None if file doesn't exist
        """
        if not self.pid_file.exists():
            return None

        try:
            content = self.pid_file.read_text().strip()
            return int(content) if content else None
        except (ValueError, IOError):
            return None

    def remove_pid(self) -> None:
        """Remove PID file."""
        if self.pid_file.exists():
            self.pid_file.unlink()

    def is_running(self) -> bool:
        """Check if daemon/serve process is running.

        Returns:
            True if daemon/serve is running
        """
        # First check PID file
        pid = self.read_pid()
        if pid is not None:
            try:
                process = psutil.Process(pid)
                # Check if it's actually an anyclaw process
                cmdline = " ".join(process.cmdline()).lower()
                return "anyclaw" in cmdline and process.is_running()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # PID file exists but process is gone, clean up
                self.remove_pid()

        # Fallback: search for anyclaw serve processes
        # This handles foreground mode (no PID file)
        current_pid = os.getpid()
        try:
            for proc in psutil.process_iter(['pid', 'cmdline', 'name']):
                try:
                    # Skip current process (the one checking status)
                    if proc.info['pid'] == current_pid:
                        continue

                    cmdline_list = proc.info['cmdline'] or []
                    cmdline = " ".join(cmdline_list).lower()

                    # Must be a Python process (anyclaw runs with Python)
                    proc_name = (proc.info['name'] or "").lower()
                    if "python" not in proc_name:
                        continue

                    # Check if it's actually an anyclaw serve process
                    # More strict matching: must have "anyclaw" as a command/module name
                    # and "serve" as a subcommand (not just in parameters like --server_port)
                    is_anyclaw = False
                    is_serve = False

                    for arg in cmdline_list:
                        arg_lower = arg.lower()
                        # Check for anyclaw command (e.g., "anyclaw", "anyclaw/__main__.py", "-m anyclaw")
                        if arg_lower == "anyclaw" or arg_lower.endswith("/anyclaw") or \
                           arg_lower.endswith("\\anyclaw") or "anyclaw/__main__.py" in arg_lower:
                            is_anyclaw = True
                        # Check for serve subcommand (exact match, not in parameters)
                        if arg_lower == "serve":
                            is_serve = True

                    if is_anyclaw and is_serve:
                        # Exclude subcommands that don't actually run the serve
                        if any(x in cmdline for x in ["--logs", "--status", "--stop"]):
                            continue
                        # Update PID file for future checks
                        self.write_pid(proc.info['pid'])
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass

        return False

    def get_status(self) -> dict:
        """Get daemon status.

        Returns:
            Status dictionary with PID, uptime, memory, etc.
        """
        pid = self.read_pid()

        if pid is None or not self.is_running():
            return {
                "running": False,
                "pid": None,
                "uptime": None,
                "memory_mb": None,
                "channels": [],
                "messages_processed": 0,
            }

        try:
            process = psutil.Process(pid)
            create_time = datetime.fromtimestamp(process.create_time())
            uptime = datetime.now() - create_time

            # Read status file for additional info
            status_info = self._read_status_file()

            return {
                "running": True,
                "pid": pid,
                "uptime": str(uptime).split(".")[0],  # Remove microseconds
                "memory_mb": round(process.memory_info().rss / 1024 / 1024, 1),
                "channels": status_info.get("channels", []),
                "messages_processed": status_info.get("messages_processed", 0),
                "started_at": create_time.isoformat(),
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {
                "running": False,
                "pid": pid,
                "uptime": None,
                "memory_mb": None,
                "channels": [],
                "messages_processed": 0,
            }

    def write_status(self, status: dict) -> None:
        """Write status to file.

        Args:
            status: Status dictionary
        """
        import json

        status["updated_at"] = datetime.now().isoformat()
        self.status_file.write_text(json.dumps(status, indent=2))

    def _read_status_file(self) -> dict:
        """Read status file.

        Returns:
            Status dictionary
        """
        if not self.status_file.exists():
            return {}

        try:
            import json

            content = self.status_file.read_text()
            return json.loads(content)
        except (json.JSONDecodeError, IOError):
            return {}

    def stop(self, timeout: int = 30) -> bool:
        """Stop daemon process gracefully.

        Args:
            timeout: Seconds to wait for graceful shutdown

        Returns:
            True if stopped successfully
        """
        pid = self.read_pid()
        if pid is None:
            return True

        if not self.is_running():
            self.remove_pid()
            return True

        try:
            process = psutil.Process(pid)

            # Send SIGTERM for graceful shutdown
            process.terminate()

            # Wait for process to exit
            try:
                process.wait(timeout=timeout)
            except psutil.TimeoutExpired:
                # Force kill if still running
                process.kill()
                process.wait(timeout=5)

            self.remove_pid()
            return True

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            self.remove_pid()
            return True

    def daemonize(self) -> bool:
        """Daemonize the current process (Unix only).

        Uses double-fork technique for proper daemonization.

        Returns:
            True if this is the daemon process, False if parent
        """
        # Check if already running
        if self.is_running():
            raise RuntimeError(f"Daemon already running (PID: {self.read_pid()})")

        # First fork
        try:
            pid = os.fork()
            if pid > 0:
                # Parent process exits
                return False
        except OSError as e:
            raise RuntimeError(f"First fork failed: {e}")

        # Decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Second fork
        try:
            pid = os.fork()
            if pid > 0:
                # First child exits
                sys.exit(0)
        except OSError as e:
            raise RuntimeError(f"Second fork failed: {e}")

        # This is the daemon process
        # Redirect standard file descriptors
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()

        # Redirect to log file
        log_dir = self.log_file.parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # Open log file for stdout/stderr
        log_fd = os.open(self.log_file, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o644)
        os.dup2(log_fd, sys.stdout.fileno() if hasattr(sys.stdout, "fileno") else 1)
        os.dup2(log_fd, sys.stderr.fileno() if hasattr(sys.stderr, "fileno") else 2)

        # Write PID
        self.write_pid()

        return True


def setup_signal_handlers(shutdown_callback) -> None:
    """Setup signal handlers for graceful shutdown.

    Args:
        shutdown_callback: Async callback to call on shutdown
    """
    import asyncio
    import logging

    logger = logging.getLogger(__name__)
    loop = asyncio.get_event_loop()

    def handle_signal(sig):
        logger.info(f"Received signal {sig.name}, initiating shutdown...")
        asyncio.create_task(shutdown_callback())

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))
