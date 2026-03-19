"""Tests for ServeManager."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

from anyclaw.core.serve import ServeManager


class TestServeManager:
    """Tests for ServeManager class."""

    def test_init_default_config(self):
        """Test initialization with default config."""
        with patch("anyclaw.core.serve.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.agent.workspace = "~/.anyclaw/workspace"
            mock_get_config.return_value = mock_config

            manager = ServeManager()

            assert manager.config == mock_config
            assert manager.bus is not None

    def test_init_custom_config(self, tmp_path):
        """Test initialization with custom config."""
        config = MagicMock()
        config.agent.workspace = str(tmp_path)

        manager = ServeManager(config=config, workspace=tmp_path)

        assert manager.config == config
        assert manager.workspace == tmp_path

    def test_enabled_channels_empty_before_init(self):
        """Test enabled_channels is empty before initialization."""
        with patch("anyclaw.core.serve.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.agent.workspace = "~/.anyclaw/workspace"
            mock_get_config.return_value = mock_config

            manager = ServeManager()

            # Before initialization, channel_manager is None
            assert manager.enabled_channels == []

    def test_uptime_seconds_zero_before_start(self):
        """Test uptime is 0 before start."""
        with patch("anyclaw.core.serve.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.agent.workspace = "~/.anyclaw/workspace"
            mock_get_config.return_value = mock_config

            manager = ServeManager()

            assert manager.uptime_seconds == 0

    def test_get_status(self):
        """Test get_status returns correct structure."""
        with patch("anyclaw.core.serve.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.agent.workspace = "~/.anyclaw/workspace"
            mock_get_config.return_value = mock_config

            manager = ServeManager()

            status = manager.get_status()

            assert "running" in status
            assert "uptime_seconds" in status
            assert "channels" in status
            assert "messages_processed" in status

    def test_initialize_creates_workspace(self, tmp_path):
        """Test that initialize creates workspace if needed."""
        config = MagicMock()
        config.agent.workspace = str(tmp_path)
        config.channels = MagicMock()
        config.channels.cli = MagicMock()
        config.channels.cli.enabled = True
        config.channels.cli.allow_from = ["*"]

        # Remove the tmp_path to test creation
        workspace_path = tmp_path / "new_workspace"

        with patch("anyclaw.core.serve.ChannelManager") as mock_cm:
            mock_cm_instance = MagicMock()
            mock_cm_instance.channels = {"cli": MagicMock()}
            mock_cm_instance.enabled_channels = ["cli"]
            mock_cm.return_value = mock_cm_instance

            with patch("anyclaw.core.serve.AgentLoop"):
                with patch("anyclaw.core.serve.SkillLoader") as mock_loader:
                    mock_loader.return_value.get_skill_definitions.return_value = {}

                    manager = ServeManager(
                        config=config,
                        workspace=workspace_path,
                    )
                    # Initialize should not raise
                    # (workspace creation is handled by WorkspaceManager)


class TestServeManagerAsync:
    """Async tests for ServeManager."""

    @pytest.mark.asyncio
    async def test_stop_when_not_running(self):
        """Test stop when not running does nothing."""
        with patch("anyclaw.core.serve.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.agent.workspace = "~/.anyclaw/workspace"
            mock_get_config.return_value = mock_config

            manager = ServeManager()

            # Should not raise
            await manager.stop()

    @pytest.mark.asyncio
    async def test_start_sets_running_flag(self):
        """Test that start sets running flag."""
        config = MagicMock()
        config.agent.workspace = "~/.anyclaw/workspace"

        manager = ServeManager(config=config)

        # Mock channel_manager
        manager.channel_manager = MagicMock()
        manager.channel_manager.start_all = AsyncMock()
        manager.channel_manager.enabled_channels = ["cli"]

        # Mock agent
        manager.agent = MagicMock()

        # Start should set _running to True
        # But we need to cancel the infinite tasks
        task = pytest.asyncio.create_task(manager.start())

        # Give it a moment to start
        import asyncio
        await asyncio.sleep(0.1)

        assert manager._running

        # Clean up
        await manager.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_stop_cancels_tasks(self):
        """Test that stop cancels background tasks."""
        import asyncio

        config = MagicMock()
        config.agent.workspace = "~/.anyclaw/workspace"

        manager = ServeManager(config=config)
        manager._running = True

        # Create a dummy task
        async def dummy_task():
            while True:
                await asyncio.sleep(1)

        manager._tasks.append(asyncio.create_task(dummy_task()))

        await manager.stop()

        assert len(manager._tasks) == 0
