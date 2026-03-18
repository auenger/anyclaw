"""测试 Tool 执行器"""
import pytest
import asyncio

from anyclaw.skills.executor import ToolExecutor
from anyclaw.skills.models import SkillDefinition, SkillFrontmatter


class TestToolExecutor:
    """测试 Tool 执行器"""

    @pytest.fixture
    def executor(self):
        """创建执行器实例"""
        return ToolExecutor(timeout=10)

    @pytest.fixture
    def simple_skill(self):
        """创建简单 skill"""
        frontmatter = SkillFrontmatter(
            name="echo_test",
            description="Echo test"
        )
        return SkillDefinition(
            name="echo_test",
            description="Echo test",
            content="""# Echo Test

```bash
echo "{message}"
```
""",
            frontmatter=frontmatter,
            source_path="/test/SKILL.md",
            eligible=True
        )

    @pytest.mark.asyncio
    async def test_execute_simple_command(self, executor, simple_skill):
        """测试执行简单命令"""
        result = await executor.execute(simple_skill, {"message": "hello"})
        assert "hello" in result

    @pytest.mark.asyncio
    async def test_execute_with_special_chars(self, executor, simple_skill):
        """测试执行带特殊字符的命令"""
        result = await executor.execute(simple_skill, {"message": "hello world!"})
        assert "hello world!" in result

    @pytest.mark.asyncio
    async def test_execute_tool_call(self, executor, simple_skill):
        """测试通过 tool call 执行"""
        skills = {"echo_test": simple_skill}
        result = await executor.execute_tool_call(
            "echo_test",
            {"message": "test"},
            skills
        )
        assert "test" in result

    @pytest.mark.asyncio
    async def test_execute_nonexistent_tool(self, executor, simple_skill):
        """测试执行不存在的 tool"""
        skills = {"echo_test": simple_skill}
        result = await executor.execute_tool_call(
            "nonexistent",
            {},
            skills
        )
        assert "Error" in result
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_execute_ineligible_tool(self, executor):
        """测试执行不可用的 tool"""
        frontmatter = SkillFrontmatter(
            name="ineligible",
            description="Ineligible"
        )
        skill = SkillDefinition(
            name="ineligible",
            description="Ineligible",
            content="# Test",
            frontmatter=frontmatter,
            source_path="/test/SKILL.md",
            eligible=False,
            eligibility_reasons=["Missing binary: xyz"]
        )
        skills = {"ineligible": skill}

        result = await executor.execute_tool_call(
            "ineligible",
            {},
            skills
        )
        assert "Error" in result
        assert "not available" in result

    def test_escape_shell_arg(self, executor):
        """测试 shell 参数转义"""
        # 简单字符串不需要转义
        assert executor._escape_shell_arg("hello") == "hello"

        # 带空格的字符串需要转义
        escaped = executor._escape_shell_arg("hello world")
        assert "'" in escaped

    @pytest.mark.asyncio
    async def test_execute_timeout(self):
        """测试执行超时"""
        executor = ToolExecutor(timeout=1)

        frontmatter = SkillFrontmatter(
            name="sleep",
            description="Sleep test"
        )
        skill = SkillDefinition(
            name="sleep",
            description="Sleep test",
            content="""# Sleep

```bash
sleep 10
```
""",
            frontmatter=frontmatter,
            source_path="/test/SKILL.md",
            eligible=True
        )

        result = await executor.execute(skill, {})
        assert "timeout" in result.lower() or "Error" in result


class TestCommandSubstitution:
    """测试命令参数替换"""

    @pytest.fixture
    def executor(self):
        return ToolExecutor()

    def test_substitute_single_arg(self, executor):
        """测试替换单个参数"""
        template = 'echo "{name}"'
        result = executor._substitute_args(template, {"name": "Alice"})
        assert "{name}" not in result
        assert "Alice" in result

    def test_substitute_multiple_args(self, executor):
        """测试替换多个参数"""
        template = 'curl "api.com/{city}/{country}"'
        result = executor._substitute_args(
            template,
            {"city": "Beijing", "country": "China"}
        )
        assert "{city}" not in result
        assert "{country}" not in result
        assert "Beijing" in result
        assert "China" in result
