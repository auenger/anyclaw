"""技能对话模式测试

测试技能创建、热重载、工具函数等功能
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

from anyclaw.skills.loader import SkillLoader
from anyclaw.tools.skill_tools import (
    CreateSkillTool,
    ReloadSkillTool,
    ValidateSkillTool,
    ShowSkillTool,
    ListSkillsTool,
    register_skill_tools,
)
from anyclaw.tools.registry import ToolRegistry


class TestSkillCreator:
    """测试 skill-creator 内置技能"""

    def test_skill_creator_exists(self):
        """验证 skill-creator 技能存在"""
        builtin_dir = Path(__file__).parent.parent / "anyclaw" / "skills" / "builtin"
        skill_creator_dir = builtin_dir / "skill-creator"

        assert skill_creator_dir.exists(), "skill-creator directory should exist"

        skill_md = skill_creator_dir / "SKILL.md"
        assert skill_md.exists(), "SKILL.md should exist"

    def test_skill_creator_has_valid_frontmatter(self):
        """验证 skill-creator 的 frontmatter 格式正确"""
        from anyclaw.skills.toolkit import validate_skill_dir

        builtin_dir = Path(__file__).parent.parent / "anyclaw" / "skills" / "builtin"
        skill_creator_dir = builtin_dir / "skill-creator"

        result = validate_skill_dir(skill_creator_dir)

        assert result.valid, f"Validation failed: {result.errors}"
        assert result.skill_name == "skill-creator"

    def test_skill_creator_can_be_loaded(self):
        """验证 skill-creator 可以被 SkillLoader 加载"""
        builtin_dir = Path(__file__).parent.parent / "anyclaw" / "skills" / "builtin"

        loader = SkillLoader(skills_dirs=[str(builtin_dir)])
        loader.load_all()

        # 检查是否加载了 skill-creator
        all_skills = list(loader.python_skills.keys()) + list(loader.md_skills.keys())
        assert "skill-creator" in all_skills, f"Loaded skills: {all_skills}"


class TestCreateSkillTool:
    """测试 CreateSkillTool"""

    @pytest.fixture
    def temp_skills_dir(self):
        """创建临时技能目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.mark.asyncio
    async def test_create_skill_basic(self, temp_skills_dir):
        """测试创建基本技能"""
        tool = CreateSkillTool(skills_dir=temp_skills_dir)

        result = await tool.execute(
            name="test-skill",
            description="A test skill for testing"
        )

        assert "[OK]" in result
        assert "test-skill" in result

        # 验证文件已创建
        skill_dir = Path(temp_skills_dir) / "test-skill"
        assert skill_dir.exists()
        assert (skill_dir / "SKILL.md").exists()

    @pytest.mark.asyncio
    async def test_create_skill_with_resources(self, temp_skills_dir):
        """测试创建带资源的技能"""
        tool = CreateSkillTool(skills_dir=temp_skills_dir)

        result = await tool.execute(
            name="resource-skill",
            description="A skill with resources",
            resources=["scripts", "references"]
        )

        assert "[OK]" in result

        # 验证目录已创建
        skill_dir = Path(temp_skills_dir) / "resource-skill"
        assert (skill_dir / "scripts").exists()
        assert (skill_dir / "references").exists()

    @pytest.mark.asyncio
    async def test_create_skill_invalid_name(self, temp_skills_dir):
        """测试无效名称"""
        tool = CreateSkillTool(skills_dir=temp_skills_dir)

        result = await tool.execute(
            name="123-invalid",
            description="Invalid name starting with number"
        )

        # 应该被规范化为 skill-123-invalid
        assert "skill-123-invalid" in result or "[OK]" in result

    @pytest.mark.asyncio
    async def test_create_skill_already_exists(self, temp_skills_dir):
        """测试技能已存在"""
        tool = CreateSkillTool(skills_dir=temp_skills_dir)

        # 第一次创建
        await tool.execute(name="existing-skill", description="First")

        # 第二次创建同名技能
        result = await tool.execute(name="existing-skill", description="Second")

        assert "Error" in result or "already exists" in result.lower()


class TestReloadSkillTool:
    """测试 ReloadSkillTool"""

    @pytest.fixture
    def mock_loader(self):
        """创建模拟的 SkillLoader"""
        loader = MagicMock()
        loader.reload_skill = MagicMock(return_value=True)
        loader.reload_all = MagicMock(return_value={"total": 5, "success": 5, "failed": 0})
        return loader

    @pytest.mark.asyncio
    async def test_reload_all_skills(self, mock_loader):
        """测试重载所有技能"""
        tool = ReloadSkillTool(skill_loader=mock_loader)

        result = await tool.execute()

        assert "[OK]" in result
        assert "5" in result
        mock_loader.reload_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_reload_specific_skill(self, mock_loader):
        """测试重载单个技能"""
        tool = ReloadSkillTool(skill_loader=mock_loader)

        result = await tool.execute(skill_name="my-skill")

        assert "[OK]" in result
        mock_loader.reload_skill.assert_called_once_with("my-skill")

    @pytest.mark.asyncio
    async def test_reload_without_loader(self):
        """测试没有 loader 时的错误"""
        tool = ReloadSkillTool(skill_loader=None)

        result = await tool.execute()

        assert "Error" in result


class TestValidateSkillTool:
    """测试 ValidateSkillTool"""

    @pytest.fixture
    def valid_skill_dir(self):
        """创建有效的技能目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "test-skill"
            skill_dir.mkdir()

            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text("""---
name: test-skill
description: A test skill
---

# Test Skill

This is a test skill.
""")
            yield skill_dir

    @pytest.mark.asyncio
    async def test_validate_valid_skill(self, valid_skill_dir):
        """测试验证有效技能"""
        tool = ValidateSkillTool()

        result = await tool.execute(path=str(valid_skill_dir))

        assert "[OK]" in result
        assert "test-skill" in result

    @pytest.mark.asyncio
    async def test_validate_invalid_skill(self):
        """测试验证无效技能"""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "invalid-skill"
            skill_dir.mkdir()

            # 创建无效的 SKILL.md（缺少必需字段）
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text("# Invalid Skill\nNo frontmatter")

            tool = ValidateSkillTool()
            result = await tool.execute(path=str(skill_dir))

            assert "[ERROR]" in result or "failed" in result.lower()

    @pytest.mark.asyncio
    async def test_validate_nonexistent_path(self):
        """测试验证不存在的路径"""
        tool = ValidateSkillTool()

        result = await tool.execute(path="/nonexistent/path")

        assert "Error" in result or "does not exist" in result.lower()


class TestShowSkillTool:
    """测试 ShowSkillTool"""

    @pytest.fixture
    def mock_loader_with_skill(self):
        """创建带有技能的模拟 loader"""
        from anyclaw.skills.loader import SkillSource

        loader = MagicMock()
        loader._skill_sources = {
            "test-skill": SkillSource(
                name="test-skill",
                path=Path("/test/skills/test-skill"),
                source_type="workspace",
                priority=100
            )
        }
        loader.load_skill_content = MagicMock(
            return_value="# Test Skill\n\nThis is a test skill."
        )
        return loader

    @pytest.mark.asyncio
    async def test_show_existing_skill(self, mock_loader_with_skill):
        """测试显示存在的技能"""
        tool = ShowSkillTool(skill_loader=mock_loader_with_skill)

        result = await tool.execute(name="test-skill")

        assert "test-skill" in result
        assert "Test Skill" in result

    @pytest.mark.asyncio
    async def test_show_nonexistent_skill(self):
        """测试显示不存在的技能"""
        loader = MagicMock()
        loader._skill_sources = {}
        loader.get_skill_source = MagicMock(return_value=None)

        tool = ShowSkillTool(skill_loader=loader)

        result = await tool.execute(name="nonexistent")

        assert "Error" in result or "not found" in result.lower()


class TestListSkillsTool:
    """测试 ListSkillsTool"""

    @pytest.mark.asyncio
    async def test_list_skills_empty(self):
        """测试列出空技能列表"""
        loader = MagicMock()
        loader.python_skills = {}
        loader.md_skills = {}

        tool = ListSkillsTool(skill_loader=loader)

        result = await tool.execute()

        assert "No skills" in result

    @pytest.mark.asyncio
    async def test_list_skills_with_skills(self):
        """测试列出有技能的情况"""
        loader = MagicMock()
        loader.python_skills = {"echo": MagicMock()}
        loader.md_skills = {"file": MagicMock()}
        loader.get_skill_source = MagicMock(
            return_value=MagicMock(source_type="bundled")
        )

        tool = ListSkillsTool(skill_loader=loader)

        result = await tool.execute()

        assert "echo" in result
        assert "file" in result


class TestHotReload:
    """测试热重载功能"""

    @pytest.fixture
    def temp_skills_dir(self):
        """创建临时技能目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_get_skills_mtime(self, temp_skills_dir):
        """测试获取技能修改时间"""
        loader = SkillLoader(skills_dirs=[temp_skills_dir])

        mtime = loader.get_skills_mtime()
        assert mtime >= 0

    def test_has_skills_changed_initial(self, temp_skills_dir):
        """测试首次检测变化"""
        loader = SkillLoader(skills_dirs=[temp_skills_dir])

        # 首次调用应该返回 False
        changed = loader.has_skills_changed()
        assert changed is False

    def test_has_skills_changed_after_creation(self, temp_skills_dir):
        """测试创建技能后检测变化"""
        import time

        loader = SkillLoader(skills_dirs=[temp_skills_dir])

        # 首次调用
        loader.has_skills_changed()

        # 等待一小段时间确保时间戳不同
        time.sleep(0.1)

        # 创建新技能
        skill_dir = Path(temp_skills_dir) / "new-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("---\nname: new-skill\ndescription: test\n---\n# New Skill")

        # 检测变化
        changed = loader.has_skills_changed()
        assert changed is True

    def test_auto_reload_if_changed(self, temp_skills_dir):
        """测试自动重载"""
        import time

        loader = SkillLoader(skills_dirs=[temp_skills_dir])
        loader.load_all()

        # 首次调用不应重载
        result = loader.auto_reload_if_changed()
        assert result is None

        # 等待并创建新技能
        time.sleep(0.1)
        skill_dir = Path(temp_skills_dir) / "auto-reload-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("---\nname: auto-reload-skill\ndescription: test\n---\n# Auto Reload")

        # 检测到变化并重载
        result = loader.auto_reload_if_changed()
        assert result is not None
        assert "total" in result


class TestToolRegistration:
    """测试工具注册"""

    def test_register_skill_tools(self):
        """测试注册技能工具"""
        registry = ToolRegistry()
        register_skill_tools(registry)

        # 检查所有工具都已注册
        assert registry.has("create_skill")
        assert registry.has("reload_skill")
        assert registry.has("validate_skill")
        assert registry.has("show_skill")
        assert registry.has("list_skills")

    def test_tool_schemas(self):
        """测试工具 schema"""
        registry = ToolRegistry()
        register_skill_tools(registry)

        definitions = registry.get_definitions()

        # 检查每个工具都有正确的 schema
        for tool_def in definitions:
            assert "type" in tool_def
            assert tool_def["type"] == "function"
            assert "function" in tool_def
            assert "name" in tool_def["function"]
            assert "description" in tool_def["function"]
            assert "parameters" in tool_def["function"]
