"""Tests for SessionArchiveManager."""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from anyclaw.session.archive import (
    ArchiveConfig,
    SessionArchiveManager,
)


class TestArchiveConfig:
    """Tests for ArchiveConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = ArchiveConfig()

        assert config.enable_archive is True
        assert config.retention_days == 30

    def test_custom_config(self):
        """Test custom configuration."""
        config = ArchiveConfig(
            base_dir=Path("/tmp/sessions"),
            enable_archive=False,
            retention_days=60,
        )

        assert config.base_dir == Path("/tmp/sessions")
        assert config.enable_archive is False
        assert config.retention_days == 60


class TestSessionArchiveManager:
    """Tests for SessionArchiveManager."""

    @pytest.fixture
    def temp_base_dir(self, tmp_path):
        """Create a temporary base directory."""
        return tmp_path / "sessions"

    @pytest.fixture
    def manager(self, temp_base_dir):
        """Create a manager with temp directory."""
        config = ArchiveConfig(base_dir=temp_base_dir)
        return SessionArchiveManager(config)

    def test_init(self, manager, temp_base_dir):
        """Test manager initialization."""
        assert manager.base_dir == temp_base_dir
        assert manager.current_session_id is None

    def test_start_session(self, manager):
        """Test starting a session."""
        session_id = manager.start_session(
            cwd=Path("/tmp/test"),
            channel="cli",
            version="0.1.0",
        )

        assert session_id is not None
        assert manager.current_session_id == session_id
        assert manager.current_project_id is not None

    def test_start_session_disabled(self, temp_base_dir):
        """Test starting session when archive is disabled."""
        config = ArchiveConfig(base_dir=temp_base_dir, enable_archive=False)
        manager = SessionArchiveManager(config)

        session_id = manager.start_session(cwd=Path("/tmp/test"))

        assert session_id == ""

    def test_end_session(self, manager):
        """Test ending a session."""
        manager.start_session(cwd=Path("/tmp/test"))
        manager.end_session()

        # Session should still exist in memory
        assert manager.current_session_id is not None

    def test_record_user_message(self, manager):
        """Test recording user message."""
        manager.start_session(cwd=Path("/tmp/test"))
        uuid = manager.record_user_message("Hello, world!")

        assert uuid is not None
        assert manager._message_count == 1

    def test_record_assistant_message(self, manager):
        """Test recording assistant message."""
        manager.start_session(cwd=Path("/tmp/test"))
        uuid = manager.record_assistant_message(
            "Hi there!",
            model="gpt-4o",
        )

        assert uuid is not None
        assert manager._message_count == 1

    def test_record_tool_call(self, manager):
        """Test recording tool call."""
        manager.start_session(cwd=Path("/tmp/test"))
        call_id = manager.record_tool_call(
            "read_file",
            {"path": "/tmp/test.txt"},
        )

        assert call_id.startswith("call_")
        assert manager._tool_call_count == 1

    def test_record_tool_result(self, manager):
        """Test recording tool result."""
        manager.start_session(cwd=Path("/tmp/test"))
        call_id = manager.record_tool_call("read_file", {"path": "/tmp/test.txt"})
        manager.record_tool_result(call_id, "file contents", duration_ms=100)

        # Should not raise any errors

    def test_record_skill_call(self, manager):
        """Test recording skill call."""
        manager.start_session(cwd=Path("/tmp/test"))
        call_id = manager.record_skill_call("commit", "-m 'test'")

        assert call_id.startswith("skill_")
        assert manager._skill_call_count == 1

    def test_record_skill_result(self, manager):
        """Test recording skill result."""
        manager.start_session(cwd=Path("/tmp/test"))
        call_id = manager.record_skill_call("commit", "-m 'test'")
        manager.record_skill_result(call_id, "Committed successfully")

        # Should not raise any errors

    def test_record_error(self, manager):
        """Test recording error."""
        manager.start_session(cwd=Path("/tmp/test"))
        uuid = manager.record_error(
            "ValueError",
            "Invalid input",
            "Traceback...",
        )

        assert uuid is not None

    def test_session_file_created(self, manager, temp_base_dir):
        """Test that session file is created."""
        manager.start_session(cwd=Path("/tmp/test"))
        manager.record_user_message("Hello")
        manager.end_session()

        # Find the session file
        session_files = list(temp_base_dir.glob("**/*.jsonl"))
        assert len(session_files) > 0

    def test_session_file_format(self, manager, temp_base_dir):
        """Test that session file is in JSONL format."""
        manager.start_session(cwd=Path("/tmp/test"))
        manager.record_user_message("Test message")
        manager.end_session()

        # Read and verify JSONL format
        session_files = list(temp_base_dir.glob("**/*.jsonl"))
        with open(session_files[0]) as f:
            for line in f:
                line = line.strip()
                if line:
                    # Should be valid JSON
                    data = json.loads(line)
                    assert "type" in data
                    assert "uuid" in data
                    assert "timestamp" in data


class TestSessionArchiveManagerQueries:
    """Tests for query methods."""

    @pytest.fixture
    def manager_with_session(self, tmp_path):
        """Create a manager with a test session."""
        config = ArchiveConfig(base_dir=tmp_path / "sessions")
        manager = SessionArchiveManager(config)
        manager.start_session(cwd=Path("/tmp/test"))
        manager.record_user_message("Hello")
        manager.record_assistant_message("Hi there!")
        manager.end_session()
        return manager

    def test_list_sessions(self, manager_with_session):
        """Test listing sessions."""
        sessions = manager_with_session.list_sessions()

        assert len(sessions) == 1
        assert sessions[0]["session_id"] is not None

    def test_list_sessions_with_filter(self, manager_with_session):
        """Test listing sessions with date filter."""
        today = datetime.now().strftime("%Y-%m-%d")
        sessions = manager_with_session.list_sessions(date=today)

        assert len(sessions) == 1

    def test_get_session(self, manager_with_session):
        """Test getting session detail."""
        sessions = manager_with_session.list_sessions()
        session_id = sessions[0]["session_id"]

        session = manager_with_session.get_session(session_id)

        assert session is not None
        assert session["session_id"] == session_id
        assert "records" in session

    def test_get_session_not_found(self, manager_with_session):
        """Test getting non-existent session."""
        session = manager_with_session.get_session("non-existent-id")

        assert session is None

    def test_search_sessions(self, manager_with_session):
        """Test searching sessions."""
        results = manager_with_session.search_sessions("Hello")

        assert len(results) > 0
        assert "Hello" in results[0]["content"].get("content", "")

    def test_search_sessions_no_match(self, manager_with_session):
        """Test searching with no match."""
        results = manager_with_session.search_sessions("xyznonexistent")

        assert len(results) == 0

    def test_export_session_markdown(self, manager_with_session):
        """Test exporting session as markdown."""
        sessions = manager_with_session.list_sessions()
        session_id = sessions[0]["session_id"]

        content = manager_with_session.export_session(session_id, format="markdown")

        assert content is not None
        assert "# Session:" in content
        assert "User" in content

    def test_export_session_json(self, manager_with_session):
        """Test exporting session as JSON."""
        sessions = manager_with_session.list_sessions()
        session_id = sessions[0]["session_id"]

        content = manager_with_session.export_session(session_id, format="json")

        assert content is not None
        data = json.loads(content)
        assert "session_id" in data

    def test_export_session_to_file(self, manager_with_session, tmp_path):
        """Test exporting session to file."""
        sessions = manager_with_session.list_sessions()
        session_id = sessions[0]["session_id"]
        output_path = tmp_path / "export.md"

        manager_with_session.export_session(
            session_id,
            format="markdown",
            output_path=output_path,
        )

        assert output_path.exists()
        content = output_path.read_text()
        assert "# Session:" in content


class TestSessionArchiveManagerClean:
    """Tests for cleaning old sessions."""

    def test_clean_old_sessions_dry_run(self, tmp_path):
        """Test cleaning old sessions in dry run mode."""
        config = ArchiveConfig(base_dir=tmp_path / "sessions")
        manager = SessionArchiveManager(config)

        # Create a session
        manager.start_session(cwd=Path("/tmp/test"))
        manager.record_user_message("Test")
        manager.end_session()

        # Dry run with days=30 should not delete recent sessions
        deleted = manager.clean_old_sessions(days=30, dry_run=True)

        # Session is new (within 30 days), should not be deleted
        assert len(deleted) == 0

    def test_clean_old_sessions_with_old_file(self, tmp_path):
        """Test cleaning with an actually old file."""
        base_dir = tmp_path / "sessions"
        config = ArchiveConfig(base_dir=base_dir)
        manager = SessionArchiveManager(config)

        # Create an old session file manually
        old_dir = base_dir / "cli" / "test-project" / "2025-01-01"
        old_dir.mkdir(parents=True, exist_ok=True)
        old_file = old_dir / "old-session.jsonl"
        old_file.write_text('{"type": "session_start", "session_id": "old"}\n')

        # Mock the file's mtime to be old
        import os
        import time
        old_time = time.time() - (60 * 24 * 60 * 60)  # 60 days ago
        os.utime(old_file, (old_time, old_time))

        # Clean sessions older than 30 days
        deleted = manager.clean_old_sessions(days=30, dry_run=True)

        assert len(deleted) == 1
        assert str(old_file) in deleted


class TestChannelSessions:
    """Tests for channel-based sessions."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create a manager with temp directory."""
        config = ArchiveConfig(base_dir=tmp_path / "sessions")
        return SessionArchiveManager(config)

    def test_feishu_channel_session(self, manager, tmp_path):
        """Test session with Feishu channel."""
        session_id = manager.start_session(
            cwd=Path("/tmp/test"),
            channel="feishu",
            channel_id="chat_12345",
        )

        manager.record_user_message("Hello from Feishu")
        manager.end_session()

        # Check file path structure
        session_files = list((tmp_path / "sessions").glob("**/*.jsonl"))
        assert len(session_files) == 1
        assert "channels" in str(session_files[0])
        assert "feishu" in str(session_files[0])
        assert "chat_12345" in str(session_files[0])

    def test_discord_channel_session(self, manager, tmp_path):
        """Test session with Discord channel."""
        session_id = manager.start_session(
            cwd=Path("/tmp/test"),
            channel="discord",
            channel_id="channel_67890",
        )

        manager.record_user_message("Hello from Discord")
        manager.end_session()

        # Check file path structure
        session_files = list((tmp_path / "sessions").glob("**/*.jsonl"))
        assert len(session_files) == 1
        assert "discord" in str(session_files[0])
        assert "channel_67890" in str(session_files[0])
