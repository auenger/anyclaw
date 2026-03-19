"""配置系统单元测试"""
import pytest
from anyclaw.config.settings import settings


def test_default_agent_name():
    """测试默认 Agent 名称"""
    assert settings.agent_name == "AnyClaw"


def test_get_system_prompt():
    """测试获取系统提示词"""
    prompt = settings.get_system_prompt()
    assert "AnyClaw" in prompt


def test_llm_model():
    """测试 LLM 模型配置"""
    # 配置从 ~/.anyclaw/config.json 加载，检查模型是否已设置
    # 默认值是 gpt-4o-mini，但可能被配置文件覆盖
    assert settings.llm_model in ["gpt-4o-mini", "glm-4.7", "glm-5"]


def test_llm_temperature():
    """测试 LLM 温度参数"""
    assert settings.llm_temperature == 0.7


def test_llm_timeout():
    """测试 LLM 超时配置"""
    assert settings.llm_timeout == 60
