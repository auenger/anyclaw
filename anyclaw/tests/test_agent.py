"""Agent 核心单元测试"""
import pytest
from anyclaw.agent.history import ConversationHistory


@pytest.mark.asyncio
async def test_agent_process():
    """测试 Agent 处理"""
    from anyclaw.agent.loop import AgentLoop

    agent = AgentLoop()
    # 需要 API Key 才能测试
    # response = await agent.process("Hello")
    # assert response
    print("Agent 测试需要配置 OPENAI_API_KEY")


def test_history():
    """测试对话历史"""
    history = ConversationHistory(max_length=3)

    history.add_user_message("Hello")
    history.add_assistant_message("Hi there!")

    assert len(history) == 2
    messages = history.get_history()
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"


def test_history_max_length():
    """测试历史最大长度"""
    history = ConversationHistory(max_length=2)

    history.add_user_message("1")
    history.add_user_message("2")
    history.add_user_message("3")

    assert len(history) == 2  # 超过最大长度


def test_history_clear():
    """测试清空历史"""
    history = ConversationHistory()

    history.add_user_message("Hello")
    history.clear()

    assert len(history) == 0
