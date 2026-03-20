"""Tests for session record types."""

import json
import pytest
from datetime import datetime

from anyclaw.session.records import (
    SessionRecord,
    SessionStart,
    SessionEnd,
    UserMessage,
    AssistantMessage,
    ToolCall,
    ToolResult,
    SkillCall,
    SkillResult,
    Thinking,
    ErrorRecord,
    RECORD_TYPES,
    parse_record,
    parse_record_from_json,
)


class TestSessionStart:
    """Tests for SessionStart record."""

    def test_create_session_start(self):
        """Test creating a session start record."""
        record = SessionStart(
            session_id="test-session-123",
            project_id="test-project",
            cwd="/home/user/project",
            git_branch="main",
            channel="cli",
            version="0.1.0",
        )

        assert record.type == "session_start"
        assert record.session_id == "test-session-123"
        assert record.project_id == "test-project"
        assert record.cwd == "/home/user/project"
        assert record.git_branch == "main"
        assert record.channel == "cli"
        assert record.version == "0.1.0"
        assert record.uuid is not None
        assert record.timestamp is not None

    def test_session_start_to_dict(self):
        """Test converting session start to dict."""
        record = SessionStart(
            session_id="test-123",
            project_id="project-1",
            cwd="/tmp",
        )
        data = record.to_dict()

        assert data["type"] == "session_start"
        assert data["session_id"] == "test-123"
        assert data["project_id"] == "project-1"
        assert data["cwd"] == "/tmp"

    def test_session_start_to_json(self):
        """Test converting session start to JSON."""
        record = SessionStart(
            session_id="test-123",
            project_id="project-1",
            cwd="/tmp",
        )
        json_str = record.to_json()

        # Should be valid JSON
        data = json.loads(json_str)
        assert data["type"] == "session_start"

    def test_session_start_from_dict(self):
        """Test creating session start from dict."""
        data = {
            "type": "session_start",
            "uuid": "test-uuid",
            "timestamp": "2026-03-20T10:00:00",
            "session_id": "test-123",
            "project_id": "project-1",
            "cwd": "/tmp",
            "git_branch": "develop",
            "channel": "feishu",
            "version": "1.0.0",
        }
        record = SessionStart.from_dict(data)

        assert record.uuid == "test-uuid"
        assert record.timestamp == "2026-03-20T10:00:00"
        assert record.session_id == "test-123"
        assert record.project_id == "project-1"
        assert record.cwd == "/tmp"
        assert record.git_branch == "develop"
        assert record.channel == "feishu"


class TestSessionEnd:
    """Tests for SessionEnd record."""

    def test_create_session_end(self):
        """Test creating a session end record."""
        record = SessionEnd(
            session_id="test-123",
            message_count=10,
            tool_call_count=5,
            skill_call_count=2,
            duration_seconds=120.5,
        )

        assert record.type == "session_end"
        assert record.session_id == "test-123"
        assert record.message_count == 10
        assert record.tool_call_count == 5
        assert record.skill_call_count == 2
        assert record.duration_seconds == 120.5


class TestUserMessage:
    """Tests for UserMessage record."""

    def test_create_user_message(self):
        """Test creating a user message record."""
        record = UserMessage(
            content="Hello, world!",
            parent_uuid="parent-123",
            media=["/path/to/file.png"],
        )

        assert record.type == "user_message"
        assert record.content == "Hello, world!"
        assert record.parent_uuid == "parent-123"
        assert len(record.media) == 1

    def test_user_message_with_images(self):
        """Test user message with images."""
        record = UserMessage(
            content="Check this image",
            images=[{"url": "https://example.com/image.png"}],
        )

        assert len(record.images) == 1


class TestAssistantMessage:
    """Tests for AssistantMessage record."""

    def test_create_assistant_message(self):
        """Test creating an assistant message record."""
        record = AssistantMessage(
            content="This is the response",
            model="gpt-4o",
            stop_reason="end_turn",
            parent_uuid="parent-123",
        )

        assert record.type == "assistant_message"
        assert record.content == "This is the response"
        assert record.model == "gpt-4o"
        assert record.stop_reason == "end_turn"


class TestToolCall:
    """Tests for ToolCall record."""

    def test_create_tool_call(self):
        """Test creating a tool call record."""
        record = ToolCall(
            tool_name="read_file",
            tool_input={"path": "/tmp/test.txt"},
            tool_call_id="call_123",
            parent_uuid="parent-456",
        )

        assert record.type == "tool_call"
        assert record.tool_name == "read_file"
        assert record.tool_input["path"] == "/tmp/test.txt"
        assert record.tool_call_id == "call_123"


class TestToolResult:
    """Tests for ToolResult record."""

    def test_create_tool_result(self):
        """Test creating a tool result record."""
        record = ToolResult(
            tool_call_id="call_123",
            output="File contents here",
            duration_ms=150,
            success=True,
        )

        assert record.type == "tool_result"
        assert record.tool_call_id == "call_123"
        assert record.output == "File contents here"
        assert record.duration_ms == 150
        assert record.success is True

    def test_tool_result_failure(self):
        """Test tool result with failure."""
        record = ToolResult(
            tool_call_id="call_456",
            output="Error: File not found",
            duration_ms=10,
            success=False,
        )

        assert record.success is False


class TestSkillCall:
    """Tests for SkillCall record."""

    def test_create_skill_call(self):
        """Test creating a skill call record."""
        record = SkillCall(
            skill_name="commit",
            skill_args="-m 'test commit'",
            skill_call_id="skill_123",
        )

        assert record.type == "skill_call"
        assert record.skill_name == "commit"
        assert record.skill_args == "-m 'test commit'"


class TestSkillResult:
    """Tests for SkillResult record."""

    def test_create_skill_result(self):
        """Test creating a skill result record."""
        record = SkillResult(
            skill_call_id="skill_123",
            output="Commit created successfully",
            success=True,
        )

        assert record.type == "skill_result"
        assert record.skill_call_id == "skill_123"
        assert record.success is True


class TestThinking:
    """Tests for Thinking record."""

    def test_create_thinking(self):
        """Test creating a thinking record."""
        record = Thinking(
            content="Let me analyze this problem...",
            parent_uuid="parent-123",
        )

        assert record.type == "thinking"
        assert record.content == "Let me analyze this problem..."


class TestErrorRecord:
    """Tests for ErrorRecord."""

    def test_create_error_record(self):
        """Test creating an error record."""
        record = ErrorRecord(
            error_type="ValueError",
            message="Invalid input",
            traceback="Traceback (most recent call last):\n  ...",
        )

        assert record.type == "error"
        assert record.error_type == "ValueError"
        assert record.message == "Invalid input"
        assert record.traceback is not None


class TestParseRecord:
    """Tests for parse_record function."""

    def test_parse_session_start(self):
        """Test parsing session start record."""
        data = {
            "type": "session_start",
            "session_id": "test-123",
            "project_id": "project-1",
            "cwd": "/tmp",
        }
        record = parse_record(data)

        assert isinstance(record, SessionStart)
        assert record.session_id == "test-123"

    def test_parse_user_message(self):
        """Test parsing user message record."""
        data = {
            "type": "user_message",
            "content": "Hello",
        }
        record = parse_record(data)

        assert isinstance(record, UserMessage)
        assert record.content == "Hello"

    def test_parse_tool_call(self):
        """Test parsing tool call record."""
        data = {
            "type": "tool_call",
            "tool_name": "read_file",
            "tool_input": {"path": "/tmp/test.txt"},
        }
        record = parse_record(data)

        assert isinstance(record, ToolCall)
        assert record.tool_name == "read_file"

    def test_parse_unknown_type(self):
        """Test parsing unknown record type."""
        data = {"type": "unknown_type"}
        record = parse_record(data)

        assert record is None


class TestParseRecordFromJson:
    """Tests for parse_record_from_json function."""

    def test_parse_valid_json(self):
        """Test parsing valid JSON string."""
        json_str = '{"type": "user_message", "content": "Hello"}'
        record = parse_record_from_json(json_str)

        assert isinstance(record, UserMessage)
        assert record.content == "Hello"

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON string."""
        json_str = "not valid json"
        record = parse_record_from_json(json_str)

        assert record is None


class TestRecordTypes:
    """Tests for RECORD_TYPES mapping."""

    def test_all_types_registered(self):
        """Test that all record types are registered."""
        expected_types = [
            "session_start",
            "session_end",
            "user_message",
            "assistant_message",
            "tool_call",
            "tool_result",
            "skill_call",
            "skill_result",
            "thinking",
            "error",
        ]

        for type_name in expected_types:
            assert type_name in RECORD_TYPES

    def test_record_types_are_classes(self):
        """Test that record types are correct classes."""
        assert RECORD_TYPES["session_start"] == SessionStart
        assert RECORD_TYPES["user_message"] == UserMessage
        assert RECORD_TYPES["tool_call"] == ToolCall
