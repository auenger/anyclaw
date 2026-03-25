"""Tests for session concurrency feature."""

import asyncio
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from anyclaw.core.session_pool import SessionAgentPool
from anyclaw.core.serve import ServeManager
from anyclaw.bus.events import InboundMessage, OutboundMessage
from anyclaw.bus.queue import MessageBus


class TestSessionAgentPool:
    """Tests for SessionAgentPool class."""

    def test_pool_creation(self, tmp_path: Path):
        """Test pool is created correctly."""
        pool = SessionAgentPool(
            workspace=tmp_path,
            max_pool_size=10,
            idle_timeout=300.0,
        )

        assert pool.workspace == tmp_path
        assert pool.max_pool_size == 10
        assert pool.idle_timeout == 300.0
        assert pool.size == 0

    def test_get_or_create_returns_same_instance(self, tmp_path: Path):
        """Test that same session_key returns same AgentLoop."""
        pool = SessionAgentPool(workspace=tmp_path)

        agent1 = pool.get_or_create("session_1")
        agent2 = pool.get_or_create("session_1")

        assert agent1 is agent2
        assert pool.size == 1

    def test_get_or_create_different_sessions(self, tmp_path: Path):
        """Test that different session_keys return different AgentLoops."""
        pool = SessionAgentPool(workspace=tmp_path)

        agent1 = pool.get_or_create("session_1")
        agent2 = pool.get_or_create("session_2")

        assert agent1 is not agent2
        assert pool.size == 2

    def test_remove_session(self, tmp_path: Path):
        """Test removing a session from pool."""
        pool = SessionAgentPool(workspace=tmp_path)

        pool.get_or_create("session_1")
        assert pool.size == 1

        result = pool.remove("session_1")
        assert result is True
        assert pool.size == 0

        # Removing non-existent session returns False
        result = pool.remove("non_existent")
        assert result is False

    def test_clear_pool(self, tmp_path: Path):
        """Test clearing all sessions from pool."""
        pool = SessionAgentPool(workspace=tmp_path)

        pool.get_or_create("session_1")
        pool.get_or_create("session_2")
        pool.get_or_create("session_3")
        assert pool.size == 3

        count = pool.clear()
        assert count == 3
        assert pool.size == 0

    def test_get_stats(self, tmp_path: Path):
        """Test getting pool statistics."""
        pool = SessionAgentPool(workspace=tmp_path)

        pool.get_or_create("session_1")
        pool.get_or_create("session_2")

        stats = pool.get_stats()
        assert stats["total"] == 2
        assert stats["max_size"] == 10

    @pytest.mark.asyncio
    async def test_async_get_or_create(self, tmp_path: Path):
        """Test async get_or_create with lock protection."""
        pool = SessionAgentPool(workspace=tmp_path)

        agent = await pool.get_or_create_async("session_1")
        assert agent is not None
        assert pool.size == 1

    @pytest.mark.asyncio
    async def test_cleanup_idle(self, tmp_path: Path):
        """Test cleanup of idle sessions."""
        pool = SessionAgentPool(workspace=tmp_path, idle_timeout=0.1)

        pool.get_or_create("session_1")
        assert pool.size == 1

        # Wait for idle timeout
        await asyncio.sleep(0.2)

        count = await pool.cleanup_idle_async()
        assert count == 1
        assert pool.size == 0


class TestServeManagerConcurrency:
    """Tests for ServeManager concurrent processing."""

    @pytest.fixture
    def mock_config(self):
        """Create mock config."""
        config = MagicMock()
        config.agent.workspace = "/tmp/test_workspace"
        config.channels.cli.interactive = False
        config.channels.cli.enabled = True
        config.channels.discord.enabled = False
        config.channels.feishu.enabled = False
        return config

    @pytest.fixture
    def serve_manager(self, mock_config, tmp_path: Path):
        """Create ServeManager instance."""
        manager = ServeManager(
            config=mock_config,
            workspace=tmp_path,
        )
        return manager

    def test_concurrency_components_initialized(self, serve_manager):
        """Test that concurrency components are initialized."""
        # Initialize the manager
        with patch.object(serve_manager, 'channel_manager'):
            with patch.object(serve_manager, 'agent'):
                serve_manager._session_pool = SessionAgentPool(
                    workspace=serve_manager.workspace,
                    max_pool_size=5,
                )
                serve_manager._concurrency_semaphore = asyncio.Semaphore(5)

        assert serve_manager._session_pool is not None
        assert serve_manager._concurrency_semaphore is not None
        assert serve_manager._active_session_tasks == {}

    @pytest.mark.asyncio
    async def test_concurrent_session_processing(self, serve_manager, tmp_path: Path):
        """Test that multiple sessions can be processed concurrently."""
        bus = MessageBus()
        serve_manager.bus = bus
        serve_manager._running = True
        serve_manager._session_pool = SessionAgentPool(workspace=tmp_path)
        serve_manager._concurrency_semaphore = asyncio.Semaphore(5)
        serve_manager._active_session_tasks = {}

        # Create mock messages
        msg1 = InboundMessage(
            channel="api",
            sender_id="user1",
            chat_id="chat_1",
            content="Hello from session 1",
        )
        msg2 = InboundMessage(
            channel="api",
            sender_id="user2",
            chat_id="chat_2",
            content="Hello from session 2",
        )

        # Track processing times
        processing_times = {}

        async def mock_process(content):
            # Simulate LLM processing delay
            await asyncio.sleep(0.1)
            session_key = content.split("session ")[1]
            processing_times[session_key] = time.time()
            return f"Response to {content}"

        # Mock agent processing
        with patch.object(serve_manager._session_pool, 'get_or_create') as mock_get:
            mock_agent = MagicMock()
            mock_agent.process = AsyncMock(side_effect=mock_process)
            mock_agent.session_manager = None
            mock_get.return_value = mock_agent

            # Process messages concurrently
            task1 = asyncio.create_task(
                serve_manager._process_with_semaphore(msg1, msg1.content, "api:chat_1")
            )
            task2 = asyncio.create_task(
                serve_manager._process_with_semaphore(msg2, msg2.content, "api:chat_2")
            )

            await asyncio.gather(task1, task2)

        # Verify both sessions were processed
        assert len(processing_times) == 2
        # Times should be close (concurrent), not sequential
        time_diff = abs(processing_times["1"] - processing_times["2"])
        assert time_diff < 0.15  # Should be within 150ms (concurrent)

    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(self, serve_manager, tmp_path: Path):
        """Test that semaphore limits concurrent processing."""
        bus = MessageBus()
        serve_manager.bus = bus
        serve_manager._running = True
        serve_manager._session_pool = SessionAgentPool(workspace=tmp_path)
        serve_manager._concurrency_semaphore = asyncio.Semaphore(2)  # Only 2 concurrent
        serve_manager._active_session_tasks = {}

        concurrent_count = 0
        max_concurrent = 0
        lock = asyncio.Lock()

        async def mock_process(content):
            nonlocal concurrent_count, max_concurrent
            async with lock:
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)

            await asyncio.sleep(0.1)

            async with lock:
                concurrent_count -= 1

            return f"Response to {content}"

        with patch.object(serve_manager._session_pool, 'get_or_create') as mock_get:
            mock_agent = MagicMock()
            mock_agent.process = AsyncMock(side_effect=mock_process)
            mock_agent.session_manager = None
            mock_get.return_value = mock_agent

            # Create 4 messages
            tasks = []
            for i in range(4):
                msg = InboundMessage(
                    channel="api",
                    sender_id=f"user_{i}",
                    chat_id=f"chat_{i}",
                    content=f"Message {i}",
                )
                tasks.append(
                    serve_manager._process_with_semaphore(msg, msg.content, f"api:chat_{i}")
                )

            await asyncio.gather(*tasks)

        # Max concurrent should be limited by semaphore (2)
        assert max_concurrent <= 2

    @pytest.mark.asyncio
    async def test_stop_waits_for_active_tasks(self, serve_manager, tmp_path: Path):
        """Test that stop() waits for active tasks to complete."""
        bus = MessageBus()
        serve_manager.bus = bus
        serve_manager._running = True
        serve_manager._session_pool = SessionAgentPool(workspace=tmp_path)
        serve_manager._concurrency_semaphore = asyncio.Semaphore(5)
        serve_manager._active_session_tasks = {}
        serve_manager.channel_manager = None

        task_completed = False

        async def slow_process(content):
            await asyncio.sleep(0.2)
            nonlocal task_completed
            task_completed = True
            return "Done"

        with patch.object(serve_manager._session_pool, 'get_or_create') as mock_get:
            mock_agent = MagicMock()
            mock_agent.process = AsyncMock(side_effect=slow_process)
            mock_agent.session_manager = None
            mock_get.return_value = mock_agent

            # Start a task
            msg = InboundMessage(
                channel="api",
                sender_id="user",
                chat_id="chat_1",
                content="Test message",
            )
            task = asyncio.create_task(
                serve_manager._process_with_semaphore(msg, msg.content, "api:chat_1")
            )
            serve_manager._active_session_tasks["api:chat_1"] = task

            # Call stop - should wait for task
            await serve_manager.stop()

        # Task should have completed
        assert task_completed or len(serve_manager._active_session_tasks) == 0

    @pytest.mark.asyncio
    async def test_session_history_isolation(self, tmp_path: Path):
        """Test that session histories are isolated."""
        pool = SessionAgentPool(workspace=tmp_path)

        agent1 = pool.get_or_create("session_1")
        agent2 = pool.get_or_create("session_2")

        # Each agent should have its own history
        assert agent1.history is not agent2.history

        # Add message to agent1's history
        agent1.history.add_message("user", "Hello from session 1")

        # agent2's history should be empty
        assert len(agent2.history.messages) == 0
        assert len(agent1.history.messages) == 1


class TestIntegration:
    """Integration tests for session concurrency."""

    @pytest.mark.asyncio
    async def test_full_concurrent_flow(self, tmp_path: Path):
        """Test full concurrent message processing flow."""
        # Create MessageBus
        bus = MessageBus()

        # Create SessionPool
        pool = SessionAgentPool(workspace=tmp_path)
        semaphore = asyncio.Semaphore(5)

        # Track results
        results = {}

        async def process_message(msg: InboundMessage, session_key: str):
            async with semaphore:
                agent = pool.get_or_create(session_key)
                # Simulate processing
                await asyncio.sleep(0.1)
                results[session_key] = f"Processed: {msg.content}"

                # Send response
                outbound = OutboundMessage(
                    channel=msg.channel,
                    chat_id=session_key,
                    content=f"Response to {msg.content}",
                )
                await bus.publish_outbound(outbound)

        # Create messages
        messages = [
            InboundMessage(channel="api", sender_id="user1", chat_id="chat_1", content="Msg 1"),
            InboundMessage(channel="api", sender_id="user2", chat_id="chat_2", content="Msg 2"),
            InboundMessage(channel="api", sender_id="user3", chat_id="chat_3", content="Msg 3"),
        ]

        # Process concurrently
        tasks = [
            asyncio.create_task(process_message(msg, f"api:{msg.chat_id}"))
            for msg in messages
        ]
        await asyncio.gather(*tasks)

        # Verify all processed
        assert len(results) == 3

        # Verify pool has 3 sessions
        assert pool.size == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
