"""测试 Tool Definition 转换器"""
import pytest

from anyclaw.skills.converter import (
    skill_to_tool_definition,
    skills_to_tools,
    infer_parameters_from_commands,
)
from anyclaw.skills.models import SkillDefinition, SkillFrontmatter


class TestSkillToToolDefinition:
    """测试 Skill 转换为 Tool Definition"""

    def test_convert_simple_skill(self):
        """测试转换简单 skill"""
        frontmatter = SkillFrontmatter(
            name="test",
            description="A test skill"
        )
        skill = SkillDefinition(
            name="test",
            description="A test skill",
            content="# Test",
            frontmatter=frontmatter,
            source_path="/test/SKILL.md"
        )

        tool_def = skill_to_tool_definition(skill)

        assert tool_def["type"] == "function"
        assert tool_def["function"]["name"] == "test"
        assert tool_def["function"]["description"] == "A test skill"
        assert "parameters" in tool_def["function"]

    def test_convert_skill_with_inferred_params(self):
        """测试转换带推断参数的 skill"""
        frontmatter = SkillFrontmatter(
            name="weather",
            description="Get weather"
        )
        skill = SkillDefinition(
            name="weather",
            description="Get weather",
            content="""# Weather

```bash
curl "wttr.in/{location}?format=3"
```
""",
            frontmatter=frontmatter,
            source_path="/test/SKILL.md"
        )

        tool_def = skill_to_tool_definition(skill)

        params = tool_def["function"]["parameters"]
        assert params["type"] == "object"
        assert "location" in params["properties"]
        assert "location" in params["required"]


class TestSkillsToTools:
    """测试批量转换"""

    def test_convert_multiple_skills(self):
        """测试转换多个 skills"""
        skills = []
        for i in range(3):
            frontmatter = SkillFrontmatter(
                name=f"skill{i}",
                description=f"Skill {i}"
            )
            skill = SkillDefinition(
                name=f"skill{i}",
                description=f"Skill {i}",
                content="# Content",
                frontmatter=frontmatter,
                source_path=f"/test/skill{i}/SKILL.md",
                eligible=True
            )
            skills.append(skill)

        tools = skills_to_tools(skills)

        assert len(tools) == 3
        names = [t["function"]["name"] for t in tools]
        assert "skill0" in names
        assert "skill1" in names
        assert "skill2" in names

    def test_filter_ineligible_skills(self):
        """测试过滤不可用的 skills"""
        frontmatter = SkillFrontmatter(
            name="test",
            description="Test"
        )

        eligible_skill = SkillDefinition(
            name="eligible",
            description="Eligible",
            content="# Test",
            frontmatter=frontmatter,
            source_path="/test/SKILL.md",
            eligible=True
        )

        ineligible_skill = SkillDefinition(
            name="ineligible",
            description="Ineligible",
            content="# Test",
            frontmatter=frontmatter,
            source_path="/test/SKILL.md",
            eligible=False,
            eligibility_reasons=["Missing binary: xyz"]
        )

        tools = skills_to_tools([eligible_skill, ineligible_skill])

        assert len(tools) == 1
        assert tools[0]["function"]["name"] == "eligible"


class TestInferParameters:
    """测试参数推断"""

    def test_infer_single_param(self):
        """测试推断单个参数"""
        commands = ['echo "{name}"']
        params = infer_parameters_from_commands(commands)

        assert "name" in params["properties"]
        assert params["properties"]["name"]["type"] == "string"
        assert "name" in params["required"]

    def test_infer_multiple_params(self):
        """测试推断多个参数"""
        commands = ['curl "api.com/{city}/{country}"']
        params = infer_parameters_from_commands(commands)

        assert "city" in params["properties"]
        assert "country" in params["properties"]
        assert len(params["required"]) == 2

    def test_infer_no_params(self):
        """测试没有参数的命令"""
        commands = ['echo "hello"']
        params = infer_parameters_from_commands(commands)

        assert len(params["properties"]) == 0
        assert len(params["required"]) == 0
