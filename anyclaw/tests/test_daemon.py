"""Tests for daemon management."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from anyclaw.core.daemon import DaemonManager, DEFAULT_PID_FILE


class TestDaemonManager:
    """Tests for DaemonManager class."""

    def test_init_default_paths(self):
        """Test default path initialization."""
        manager = DaemonManager()

        assert manager.pid_file == DEFAULT_PID_FILE
        assert "serve.pid" in str(manager.pid_file)
        assert "serve.log" in str(manager.log_file)

    def test_init_custom_paths(self, tmp_path):
        """Test custom path initialization."""
        pid_file = tmp_path / "custom.pid"
        log_file = tmp_path / "custom.log"

        manager = DaemonManager(pid_file=pid_file, log_file=log_file)

        assert manager.pid_file == pid_file
        assert manager.log_file == log_file

    def test_write_and_read_pid(self, tmp_path):
        """Test PID file write and read."""
        manager = DaemonManager(pid_file=tmp_path / "test.pid")

        manager.write_pid(12345)
        pid = manager.read_pid()

        assert pid == 12345

    def test_write_pid_defaults_to_current(self, tmp_path):
        """Test that write_pid uses current process ID."""
        manager = DaemonManager(pid_file=tmp_path / "test.pid")

        manager.write_pid()
        pid = manager.read_pid()

        assert pid == os.getpid()

    def test_read_pid_nonexistent_file(self, tmp_path):
        """Test reading PID from nonexistent file."""
        manager = DaemonManager(pid_file=tmp_path / "nonexistent.pid")

        pid = manager.read_pid()

        assert pid is None

    def test_read_pid_invalid_content(self, tmp_path):
        """Test reading PID from file with invalid content."""
        pid_file = tmp_path / "invalid.pid"
        pid_file.write_text("not-a-number")

        manager = DaemonManager(pid_file=pid_file)

        pid = manager.read_pid()

        assert pid is None

    def test_remove_pid(self, tmp_path):
        """Test PID file removal."""
        pid_file = tmp_path / "test.pid"
        manager = DaemonManager(pid_file=pid_file)

        manager.write_pid(12345)
        assert pid_file.exists()

        manager.remove_pid()
        assert not pid_file.exists()

    def test_is_running_no_pid_file(self, tmp_path):
        """Test is_running with no PID file."""
        manager = DaemonManager(pid_file=tmp_path / "nonexistent.pid")

        assert not manager.is_running()

    @patch("psutil.Process")
    def test_is_running_with_process(self, mock_process_class, tmp_path):
        """Test is_running with running process."""
        pid_file = tmp_path / "test.pid"
        manager = DaemonManager(pid_file=pid_file)
        manager.write_pid(12345)

        # Mock psutil.Process
        mock_process = MagicMock()
        mock_process.is_running.return_value = True
        mock_process.cmdline.return_value = ["python", "-m", "anyclaw", "serve"]
        mock_process_class.return_value = mock_process

        assert manager.is_running()

    @patch("psutil.Process")
    def test_is_running_non_anyclaw_process(self, mock_process_class, tmp_path):
        """Test is_running with non-anyclaw process."""
        pid_file = tmp_path / "test.pid"
        manager = DaemonManager(pid_file=pid_file)
        manager.write_pid(12345)

        # Mock psutil.Process with non-anyclaw command
        mock_process = MagicMock()
        mock_process.is_running.return_value = True
        mock_process.cmdline.return_value = ["python", "other_program"]
        mock_process_class.return_value = mock_process

        assert not manager.is_running()

    def test_get_status_not_running(self, tmp_path):
        """Test get_status when not running."""
        manager = DaemonManager(pid_file=tmp_path / "nonexistent.pid")

        status = manager.get_status()

        assert not status["running"]
        assert status["pid"] is None

    def test_write_status(self, tmp_path):
        """Test status file writing."""
        status_file = tmp_path / "status.json"
        manager = DaemonManager(status_file=status_file)

        manager.write_status({"channels": ["cli", "discord"], "messages_processed": 10})

        assert status_file.exists()
        import json
        data = json.loads(status_file.read_text())
        assert data["channels"] == ["cli", "discord"]
        assert data["messages_processed"] == 10
        assert "updated_at" in data

    def test_stop_no_process(self, tmp_path):
        """Test stop when no process is running."""
        manager = DaemonManager(pid_file=tmp_path / "nonexistent.pid")

        result = manager.stop()

        assert result is True


class TestDaemonManagerStatus:
    """Tests for status tracking."""

    def test_status_file_path(self, tmp_path):
        """Test status file path configuration."""
        status_file = tmp_path / "custom.status"
        manager = DaemonManager(status_file=status_file)

        assert manager.status_file == status_file

    def test_read_status_file_empty(self, tmp_path):
        """Test reading empty/missing status file."""
        manager = DaemonManager(status_file=tmp_path / "nonexistent.status")

        status = manager._read_status_file()

        assert status == {}

    def test_read_status_file_valid(self, tmp_path):
        """Test reading valid status file."""
        import json
        status_file = tmp_path / "status.json"
        status_file.write_text(json.dumps({"channels": ["cli"]}))

        manager = DaemonManager(status_file=status_file)
        status = manager._read_status_file()

        assert status["channels"] == ["cli"]
