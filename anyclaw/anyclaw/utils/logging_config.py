"""Logging configuration for AnyClaw serve mode.

Supports multiple log levels:
- DEBUG: Detailed timestamps + module names
- INFO: Standard format
- WARNING: Minimal output
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

# Log level mapping
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "verbose": logging.INFO,
    "info": logging.INFO,
    "quiet": logging.WARNING,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}

# Default log directory
DEFAULT_LOG_DIR = Path.home() / ".anyclaw" / "logs"


def get_log_level(level_name: str) -> int:
    """Get logging level from name.

    Args:
        level_name: Level name (debug/verbose/quiet/info/warning/error)

    Returns:
        Logging level constant
    """
    return LOG_LEVELS.get(level_name.lower(), logging.INFO)


def setup_logging(
    level: str = "info",
    log_file: Optional[Path] = None,
    log_dir: Optional[Path] = None,
    rich_output: bool = True,
) -> logging.Logger:
    """Configure logging for AnyClaw.

    Args:
        level: Log level (debug/verbose/quiet/info)
        log_file: Optional log file path
        log_dir: Directory for log files (default: ~/.anyclaw/logs)
        rich_output: Use rich for console output

    Returns:
        Configured root logger
    """
    log_level = get_log_level(level)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    if rich_output:
        # Use RichHandler for beautiful output
        console = Console(stderr=True)
        show_time = level == "debug"
        show_path = level == "debug"

        console_handler = RichHandler(
            console=console,
            show_time=show_time,
            show_path=show_path,
            rich_tracebacks=True,
            markup=True,
            log_time_format="[%Y-%m-%d %H:%M:%S]",
        )
        console_handler.setLevel(log_level)

        # Custom format for different levels
        if level == "debug":
            console_handler.setFormatter(logging.Formatter("%(message)s"))
        elif level == "quiet":
            console_handler.setFormatter(logging.Formatter("[red]%(message)s[/red]"))
        else:
            console_handler.setFormatter(logging.Formatter("%(message)s"))
    else:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(log_level)

        if level == "debug":
            fmt = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"
            datefmt = "%Y-%m-%d %H:%M:%S"
        elif level == "quiet":
            fmt = "%(levelname)s: %(message)s"
            datefmt = None
        else:
            fmt = "%(asctime)s | %(levelname)-8s | %(message)s"
            datefmt = "%H:%M:%S"

        console_handler.setFormatter(logging.Formatter(fmt, datefmt))

    root_logger.addHandler(console_handler)

    # File handler (for daemon mode and persistence)
    if log_file or log_dir:
        log_dir = log_dir or DEFAULT_LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_file or log_dir / "serve.log"

        # Rotating file handler: 10MB * 5 files
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file

        # File format: detailed
        file_fmt = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"
        file_handler.setFormatter(logging.Formatter(file_fmt, "%Y-%m-%d %H:%M:%S"))

        root_logger.addHandler(file_handler)

    # Set specific logger levels
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)

    return root_logger


def get_log_file_path() -> Path:
    """Get the default log file path.

    Returns:
        Path to serve.log
    """
    return DEFAULT_LOG_DIR / "serve.log"
