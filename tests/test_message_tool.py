"""Test MessageTool functionality."""

import asyncio
from pathlib import Path
from anyclaw.agent.tools.message import MessageTool
from anyclaw.bus.events import OutboundMessage


async def mock_send_callback(msg: OutboundMessage) -> None:
    """Mock send callback for testing."""
    print(f"[Mock] Sending message to {msg.channel}:{msg.chat_id}")
    print(f"[Mock] Content: {msg.content}")
    if msg.media:
        print(f"[Mock] Media: {msg.media}")
    if msg.metadata:
        print(f"[Mock] Metadata: {msg.metadata}")


async def test_message_tool_basic():
    """Test basic MessageTool functionality."""
    print("=== Test 1: Basic Message ===")
    tool = MessageTool(
        send_callback=mock_send_callback,
        default_channel="discord",
        default_chat_id="12345",
    )
    tool.set_context("discord", "12345", message_id="98765")

    result = await tool.execute(content="Hello from MessageTool!")
    print(f"Result: {result}")
    assert "Message sent" in result
    assert "discord:12345" in result
    print("✅ Test 1 passed\n")


async def test_message_tool_with_media():
    """Test MessageTool with media attachments."""
    print("=== Test 2: Message with Media ===")
    tool = MessageTool(
        send_callback=mock_send_callback,
        default_channel="discord",
        default_chat_id="12345",
    )
    tool.set_context("discord", "12345")

    result = await tool.execute(
        content="Check this image",
        media=["/tmp/test.png"],
    )
    print(f"Result: {result}")
    assert "Message sent" in result
    assert "with 1 attachments" in result
    print("✅ Test 2 passed\n")


async def test_message_tool_custom_channel():
    """Test MessageTool sending to custom channel."""
    print("=== Test 3: Custom Channel ===")
    tool = MessageTool(
        send_callback=mock_send_callback,
        default_channel="discord",
        default_chat_id="12345",
    )

    result = await tool.execute(
        content="Send to Feishu",
        channel="feishu",
        chat_id="ou_xxx",
    )
    print(f"Result: {result}")
    assert "Message sent" in result
    assert "feishu:ou_xxx" in result
    print("✅ Test 3 passed\n")


async def test_message_tool_no_callback():
    """Test MessageTool without send callback."""
    print("=== Test 4: No Send Callback ===")
    tool = MessageTool(
        send_callback=None,  # No callback
        default_channel="discord",
        default_chat_id="12345",
    )

    result = await tool.execute(content="Hello")
    print(f"Result: {result}")
    assert "Error" in result
    assert "not configured" in result.lower()
    print("✅ Test 4 passed\n")


async def test_message_tool_no_target():
    """Test MessageTool without target."""
    print("=== Test 5: No Target ===")
    tool = MessageTool(
        send_callback=mock_send_callback,
        default_channel="",  # Empty
        default_chat_id="",  # Empty
    )

    result = await tool.execute(content="Hello")
    print(f"Result: {result}")
    assert "Error" in result
    assert "No target" in result
    print("✅ Test 5 passed\n")


async def test_message_tool_turn_tracking():
    """Test MessageTool per-turn tracking."""
    print("=== Test 6: Turn Tracking ===")
    tool = MessageTool(
        send_callback=mock_send_callback,
        default_channel="discord",
        default_chat_id="12345",
    )

    # Start new turn
    tool.start_turn()
    assert not tool._sent_in_turn

    # Send message
    await tool.execute(content="Hello")

    # Should mark as sent
    assert tool._sent_in_turn
    print("✅ Test 6 passed\n")


async def main():
    """Run all tests."""
    print("🧪 MessageTool Tests\n" + "=" * 50)

    await test_message_tool_basic()
    await test_message_tool_with_media()
    await test_message_tool_custom_channel()
    await test_message_tool_no_callback()
    await test_message_tool_no_target()
    await test_message_tool_turn_tracking()

    print("=" * 50)
    print("🎉 All MessageTool tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
