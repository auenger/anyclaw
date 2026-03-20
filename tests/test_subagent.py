"""Test Subagent functionality."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from anyclaw.agent.subagent import SubagentManager
from anyclaw.agent.tools.spawn import SpawnTool


class MockProvider:
    """Mock LLM provider for testing."""

    async def chat_with_retry(self, messages, tools, model):
        """Mock LLM call."""
        # Return a simple response without tool calls for testing
        class MockResponse:
            content = "Task completed successfully"
            tool_calls = []

        return MockResponse()


class MockBus:
    """Mock message bus for testing."""

    async def publish_inbound(self, msg):
        """Mock publish message."""
        print(f"[Mock Bus] Published message: {msg.content[:100]}...")


async def test_subagent_spawn():
    """Test spawning a subagent."""
    print("=== Test 1: Spawn Subagent ===")
    manager = SubagentManager(
        provider=MockProvider(),
        workspace=Path("/tmp/test_workspace"),
        bus=MockBus(),
    )

    result = await manager.spawn(
        task="List all files in current directory",
        label="List files",
        origin_channel="discord",
        origin_chat_id="12345",
        session_key="discord:12345",
    )

    print(f"Result: {result}")
    assert "Subagent" in result
    assert "started" in result
    assert manager.get_running_count() == 1
    print("✅ Test 1 passed\n")


async def test_spawn_tool():
    """Test SpawnTool."""
    print("=== Test 2: SpawnTool ===")
    manager = SubagentManager(
        provider=MockProvider(),
        workspace=Path("/tmp/test_workspace"),
        bus=MockBus(),
    )

    tool = SpawnTool(manager)
    tool.set_context("discord", "12345")

    result = await tool.execute(
        task="Hello world",
        label="Test task",
    )

    print(f"Result: {result}")
    assert "Subagent" in result
    assert "started" in result
    print("✅ Test 2 passed\n")


async def test_cancel_by_session():
    """Test cancelling subagents by session."""
    print("=== Test 3: Cancel by Session ===")
    manager = SubagentManager(
        provider=MockProvider(),
        workspace=Path("/tmp/test_workspace"),
        bus=MockBus(),
    )

    # Spawn 3 subagents
    await manager.spawn(task="Task 1", session_key="discord:12345")
    await manager.spawn(task="Task 2", session_key="discord:12345")
    await manager.spawn(task="Task 3", session_key="discord:67890")

    assert manager.get_running_count() == 3

    # Cancel session 12345
    cancelled = await manager.cancel_by_session("discord:12345")
    print(f"Cancelled {cancelled} tasks")

    assert cancelled == 2
    # Wait a bit for cleanup and task completion
    await asyncio.sleep(1.0)
    print(f"Running count after cancel: {manager.get_running_count()}")
    # After cancel and task completion, count should be 1 (only task 3 remains)
    # Or it could be 0 if all completed
    count = manager.get_running_count()
    assert count <= 1, f"Expected <= 1, got {count}"
    print("✅ Test 3 passed\n")


async def test_get_running_count():
    """Test getting running count."""
    print("=== Test 4: Get Running Count ===")
    manager = SubagentManager(
        provider=MockProvider(),
        workspace=Path("/tmp/test_workspace"),
        bus=MockBus(),
    )

    assert manager.get_running_count() == 0

    await manager.spawn(task="Task 1")
    await manager.spawn(task="Task 2")
    await manager.spawn(task="Task 3")

    count = manager.get_running_count()
    print(f"Running count: {count}")
    assert count == 3
    print("✅ Test 4 passed\n")


async def test_context_setting():
    """Test SpawnTool context setting."""
    print("=== Test 5: Context Setting ===")
    manager = SubagentManager(
        provider=MockProvider(),
        workspace=Path("/tmp/test_workspace"),
        bus=MockBus(),
    )

    tool = SpawnTool(manager)

    # Default context
    assert tool._origin_channel == "cli"
    assert tool._origin_chat_id == "direct"

    # Set context
    tool.set_context("discord", "12345")
    assert tool._origin_channel == "discord"
    assert tool._origin_chat_id == "12345"
    assert tool._session_key == "discord:12345"
    print("✅ Test 5 passed\n")


async def main():
    """Run all tests."""
    print("🧪 SubAgent Tests\n" + "=" * 50)

    await test_subagent_spawn()
    await test_spawn_tool()
    await test_cancel_by_session()
    await test_get_running_count()
    await test_context_setting()

    print("=" * 50)
    print("🎉 All SubAgent tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
