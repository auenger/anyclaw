"""Tests for CronTool and Cron skill integration."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from anyclaw.cron.service import CronService
from anyclaw.cron.tool import CronTool
from anyclaw.cron.types import CronSchedule


class TestCronTool:
    """Tests for CronTool functionality."""

    @pytest.fixture
    def cron_service(self, tmp_path: Path):
        """Create a CronService instance for testing."""
        store_path = tmp_path / "cron_jobs.json"
        return CronService(store_path)

    @pytest.fixture
    def cron_tool(self, cron_service: CronService):
        """Create a CronTool instance for testing."""
        tool = CronTool(cron_service)
        tool.set_context("cli", "test-session")
        return tool

    def test_tool_name_and_description(self, cron_tool: CronTool):
        """Test that tool has correct name and description."""
        assert cron_tool.name == "cron"
        assert "schedule" in cron_tool.description.lower()

    def test_parameters_schema(self, cron_tool: CronTool):
        """Test that parameters schema is valid."""
        params = cron_tool.parameters
        assert params["type"] == "object"
        assert "action" in params["properties"]
        assert "add" in params["properties"]["action"]["enum"]
        assert "list" in params["properties"]["action"]["enum"]
        assert "remove" in params["properties"]["action"]["enum"]

    def test_set_context(self, cron_tool: CronTool):
        """Test setting context."""
        cron_tool.set_context("discord", "chat-123")
        assert cron_tool._channel == "discord"
        assert cron_tool._chat_id == "chat-123"

    @pytest.mark.asyncio
    async def test_add_job_every_seconds(self, cron_tool: CronTool):
        """Test adding a recurring job with every_seconds."""
        result = await cron_tool.execute(
            action="add",
            message="Test reminder",
            every_seconds=3600,
        )
        assert "Created job" in result
        assert "Test reminder" in result

    @pytest.mark.asyncio
    async def test_add_job_at(self, cron_tool: CronTool):
        """Test adding a one-time job with at."""
        result = await cron_tool.execute(
            action="add",
            message="One-time reminder",
            at="2026-12-31T23:59:00",
        )
        assert "Created job" in result
        assert "One-time reminder" in result

    @pytest.mark.asyncio
    async def test_add_job_cron_expr(self, cron_tool: CronTool):
        """Test adding a job with cron expression."""
        result = await cron_tool.execute(
            action="add",
            message="Daily standup",
            cron_expr="0 9 * * *",
            tz="Asia/Shanghai",
        )
        assert "Created job" in result
        assert "Daily standup" in result

    @pytest.mark.asyncio
    async def test_add_job_missing_message(self, cron_tool: CronTool):
        """Test that add requires a message."""
        result = await cron_tool.execute(
            action="add",
            every_seconds=3600,
        )
        assert "Error" in result
        assert "message is required" in result

    @pytest.mark.asyncio
    async def test_add_job_missing_schedule(self, cron_tool: CronTool):
        """Test that add requires a schedule."""
        result = await cron_tool.execute(
            action="add",
            message="Test",
        )
        assert "Error" in result
        assert "required" in result

    @pytest.mark.asyncio
    async def test_add_job_missing_context(self, cron_service: CronService):
        """Test that add requires context."""
        tool = CronTool(cron_service)
        # Don't set context
        result = await tool.execute(
            action="add",
            message="Test",
            every_seconds=3600,
        )
        assert "Error" in result
        assert "no session context" in result

    @pytest.mark.asyncio
    async def test_list_jobs_empty(self, cron_tool: CronTool):
        """Test listing when no jobs exist."""
        result = await cron_tool.execute(action="list")
        assert "No scheduled jobs" in result

    @pytest.mark.asyncio
    async def test_list_jobs_with_jobs(self, cron_tool: CronTool):
        """Test listing existing jobs."""
        # Add a job first
        await cron_tool.execute(
            action="add",
            message="Test job 1",
            every_seconds=3600,
        )
        result = await cron_tool.execute(action="list")
        assert "Test job 1" in result

    @pytest.mark.asyncio
    async def test_remove_job(self, cron_tool: CronTool):
        """Test removing a job."""
        # Add a job first
        add_result = await cron_tool.execute(
            action="add",
            message="Job to remove",
            every_seconds=3600,
        )
        # Extract job ID from result like "Created job 'Job to remove' (id: abc123)"
        import re

        match = re.search(r"\(id: ([a-f0-9]+)\)", add_result)
        assert match, f"Could not find job ID in: {add_result}"
        job_id = match.group(1)

        # Remove the job
        result = await cron_tool.execute(action="remove", job_id=job_id)
        assert "Removed job" in result

        # Verify it's gone
        list_result = await cron_tool.execute(action="list")
        assert "Job to remove" not in list_result

    @pytest.mark.asyncio
    async def test_remove_nonexistent_job(self, cron_tool: CronTool):
        """Test removing a job that doesn't exist."""
        result = await cron_tool.execute(action="remove", job_id="nonexistent")
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_remove_missing_job_id(self, cron_tool: CronTool):
        """Test remove without job_id."""
        result = await cron_tool.execute(action="remove")
        assert "Error" in result
        assert "job_id is required" in result

    @pytest.mark.asyncio
    async def test_unknown_action(self, cron_tool: CronTool):
        """Test unknown action."""
        result = await cron_tool.execute(action="invalid")
        assert "Unknown action" in result


class TestCronSkillLoading:
    """Tests for cron skill loading."""

    def test_skill_md_exists(self):
        """Test that SKILL.md exists."""
        skill_path = (
            Path(__file__).parent.parent
            / "anyclaw"
            / "skills"
            / "builtin"
            / "cron"
            / "SKILL.md"
        )
        assert skill_path.exists(), f"SKILL.md not found at {skill_path}"

    def test_skill_can_be_loaded(self):
        """Test that cron skill can be loaded by SkillLoader."""
        from anyclaw.skills.loader import SkillLoader

        bundled_dir = Path(__file__).parent.parent / "anyclaw" / "skills" / "builtin"
        loader = SkillLoader(skills_dirs=[str(bundled_dir)])
        loader.load_all()

        assert "cron" in loader.md_skills, "cron skill not loaded"

    def test_skill_has_required_fields(self):
        """Test that skill has required metadata."""
        from anyclaw.skills.loader import SkillLoader

        bundled_dir = Path(__file__).parent.parent / "anyclaw" / "skills" / "builtin"
        loader = SkillLoader(skills_dirs=[str(bundled_dir)])
        loader.load_all()

        skill = loader.md_skills.get("cron")
        assert skill is not None
        assert skill.name == "cron"
        assert skill.description
        assert "定时" in skill.description or "schedule" in skill.description.lower()

    def test_skill_in_summary(self):
        """Test that cron skill appears in skills summary."""
        from anyclaw.skills.loader import SkillLoader

        bundled_dir = Path(__file__).parent.parent / "anyclaw" / "skills" / "builtin"
        loader = SkillLoader(skills_dirs=[str(bundled_dir)])
        loader.load_all()

        summary = loader.build_skills_summary()
        assert "cron" in summary, "cron not in skills summary"


class TestCronService:
    """Tests for CronService functionality."""

    @pytest.fixture
    def cron_service(self, tmp_path: Path):
        """Create a CronService instance for testing."""
        store_path = tmp_path / "cron_jobs.json"
        return CronService(store_path)

    def test_add_job(self, cron_service: CronService):
        """Test adding a job to the service."""
        schedule = CronSchedule(kind="every", every_ms=60000)
        job = cron_service.add_job(
            name="Test job",
            schedule=schedule,
            message="Test message",
            deliver=True,
            channel="cli",
            to="test-session",
        )
        assert job.id
        assert job.name == "Test job"
        assert job.enabled is True

    def test_list_jobs(self, cron_service: CronService):
        """Test listing jobs."""
        schedule = CronSchedule(kind="every", every_ms=60000)
        cron_service.add_job(
            name="Job 1",
            schedule=schedule,
            message="Message 1",
        )
        cron_service.add_job(
            name="Job 2",
            schedule=schedule,
            message="Message 2",
        )
        jobs = cron_service.list_jobs()
        assert len(jobs) == 2

    def test_remove_job(self, cron_service: CronService):
        """Test removing a job."""
        schedule = CronSchedule(kind="every", every_ms=60000)
        job = cron_service.add_job(
            name="Job to remove",
            schedule=schedule,
            message="Message",
        )
        assert cron_service.remove_job(job.id) is True
        assert len(cron_service.list_jobs()) == 0

    def test_remove_nonexistent_job(self, cron_service: CronService):
        """Test removing a nonexistent job."""
        assert cron_service.remove_job("nonexistent") is False

    @pytest.mark.asyncio
    async def test_service_lifecycle(self, cron_service: CronService):
        """Test starting and stopping the service."""
        await cron_service.start()
        assert cron_service._running is True

        cron_service.stop()
        assert cron_service._running is False
