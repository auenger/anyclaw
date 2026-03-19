"""Tests for logging configuration."""

import logging
import pytest
from pathlib import Path

from anyclaw.utils.logging_config import (
    setup_logging,
    get_log_level,
    get_log_file_path,
    LOG_LEVELS,
)


class TestGetLogLevel:
    """Tests for get_log_level function."""

    def test_debug_level(self):
        assert get_log_level("debug") == logging.DEBUG
        assert get_log_level("DEBUG") == logging.DEBUG

    def test_verbose_level(self):
        assert get_log_level("verbose") == logging.INFO

    def test_quiet_level(self):
        assert get_log_level("quiet") == logging.WARNING

    def test_info_level(self):
        assert get_log_level("info") == logging.INFO

    def test_unknown_level_defaults_to_info(self):
        assert get_log_level("unknown") == logging.INFO


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_basic_setup(self, tmp_path):
        """Test basic logging setup."""
        logger = setup_logging(level="info", rich_output=False)

        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_debug_level(self, tmp_path):
        """Test debug logging level."""
        logger = setup_logging(level="debug", rich_output=False)

        assert logger.level == logging.DEBUG

    def test_quiet_level(self, tmp_path):
        """Test quiet logging level."""
        logger = setup_logging(level="quiet", rich_output=False)

        assert logger.level == logging.WARNING

    def test_file_handler(self, tmp_path):
        """Test file handler creation."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(level="info", log_file=log_file, rich_output=False)

        # Check that file handler was added
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0

        # Clean up
        for handler in file_handlers:
            handler.close()

    def test_log_dir_created(self, tmp_path):
        """Test that log directory is created."""
        log_dir = tmp_path / "logs"
        log_file = log_dir / "test.log"

        logger = setup_logging(level="info", log_file=log_file, rich_output=False)

        assert log_dir.exists()

        # Clean up
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()


class TestGetLogFilePath:
    """Tests for get_log_file_path function."""

    def test_default_path(self):
        """Test default log file path."""
        path = get_log_file_path()

        assert path.name == "serve.log"
        assert ".anyclaw" in str(path)
