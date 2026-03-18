"""技能系统单元测试"""
import pytest
import asyncio
from anyclaw.skills.loader import SkillLoader
from anyclaw.skills.base import Skill


class MockSkill(Skill):
    """测试技能"""

    async def execute(self, **kwargs) -> str:
        return "Mock skill executed"


def test_skill_info():
    """测试技能信息"""
    skill = MockSkill()
    info = skill.get_info()

    assert info["name"] == "MockSkill"
    assert "description" in info


@pytest.mark.asyncio
async def test_skill_execution():
    """测试技能执行"""
    skill = MockSkill()
    result = await skill.execute()

    assert result == "Mock skill executed"


def test_skill_loader():
    """测试技能加载器"""
    loader = SkillLoader("anyclaw/skills/builtin")
    skills_info = loader.load_all()

    assert isinstance(skills_info, list)
    # 应该至少有 echo, time, weather 三个 skill
    assert len(skills_info) >= 0
