"""Tests for skill dynamic loading"""
import pytest
import sys
import tempfile
from pathlib import Path

from anyclaw.skills.loader import (
    SkillLoader,
    MultiDirectorySkillLoader,
    SkillSource,
)
from anyclaw.skills.base import Skill


class TestDynamicLoading:
    """测试动态加载功能"""

    def test_load_skill_from_arbitrary_path(self, tmp_path):
        """从任意路径加载 Python skill"""
        # 创建一个简单的 skill
        skill_dir = tmp_path / "my-test-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "skill.py"
        skill_file.write_text('''
from anyclaw.skills.base import Skill

class MyTestSkill(Skill):
    """A test skill"""
    async def execute(self, **kwargs):
        return "test executed"
''')

        # 加载
        loader = SkillLoader(skills_dirs=[str(tmp_path)])
        loader.load_all()

        # 验证
        assert "MyTestSkill" in loader.python_skills
        skill = loader.python_skills["MyTestSkill"]
        assert skill.name == "MyTestSkill"

    def test_load_multiple_skills(self, tmp_path):
        """加载多个 skills"""
        # 创建两个 skills
        for i in range(2):
            skill_dir = tmp_path / f"skill-{i}"
            skill_dir.mkdir()
            skill_file = skill_dir / "skill.py"
            skill_file.write_text(f'''
from anyclaw.skills.base import Skill

class Skill{i}(Skill):
    """Skill {i}"""
    async def execute(self, **kwargs):
        return "skill{i}"
''')

        loader = SkillLoader(skills_dirs=[str(tmp_path)])
        skills = loader.load_all()

        assert len(skills) == 2

    def test_skill_source_tracking(self, tmp_path):
        """跟踪 skill 来源"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "skill.py"
        skill_file.write_text('''
from anyclaw.skills.base import Skill

class TrackedSkill(Skill):
    async def execute(self, **kwargs):
        return "tracked"
''')

        loader = SkillLoader(
            skills_dirs=[str(tmp_path)],
            skills_dir_types={str(tmp_path): "workspace"}
        )
        loader.load_all()

        source = loader.get_skill_source("TrackedSkill")
        assert source is not None
        assert source.source_type == "workspace"
        assert source.priority == 100  # workspace priority


class TestPriorityMerging:
    """测试优先级合并"""

    def test_workspace_overrides_bundled(self, tmp_path):
        """workspace 覆盖 bundled"""
        bundled_dir = tmp_path / "bundled"
        workspace_dir = tmp_path / "workspace"
        bundled_dir.mkdir()
        workspace_dir.mkdir()

        # 创建 bundled skill
        bundled_skill = bundled_dir / "override-test"
        bundled_skill.mkdir()
        (bundled_skill / "skill.py").write_text('''
from anyclaw.skills.base import Skill

class OverrideTest(Skill):
    source = "bundled"
    async def execute(self, **kwargs):
        return "bundled"
''')

        # 创建 workspace skill (同名)
        workspace_skill = workspace_dir / "override-test"
        workspace_skill.mkdir()
        (workspace_skill / "skill.py").write_text('''
from anyclaw.skills.base import Skill

class OverrideTest(Skill):
    source = "workspace"
    async def execute(self, **kwargs):
        return "workspace"
''')

        loader = MultiDirectorySkillLoader(
            bundled_dir=str(bundled_dir),
            workspace_dir=str(workspace_dir),
        )
        loader.load_all()

        # 应该使用 workspace 版本
        skill = loader.get_python_skill("OverrideTest")
        assert skill is not None
        assert hasattr(skill, 'source')
        assert skill.source == "workspace"

    def test_priority_order(self, tmp_path):
        """优先级顺序正确"""
        bundled_dir = tmp_path / "bundled"
        managed_dir = tmp_path / "managed"
        workspace_dir = tmp_path / "workspace"

        for d in [bundled_dir, managed_dir, workspace_dir]:
            d.mkdir()

        loader = MultiDirectorySkillLoader(
            bundled_dir=str(bundled_dir),
            managed_dir=str(managed_dir),
            workspace_dir=str(workspace_dir),
        )

        # 检查目录类型
        assert loader.skills_dir_types[str(bundled_dir)] == "bundled"
        assert loader.skills_dir_types[str(managed_dir)] == "managed"
        assert loader.skills_dir_types[str(workspace_dir)] == "workspace"


class TestHotReload:
    """测试热重载"""

    def test_reload_single_skill(self, tmp_path):
        """重载单个 skill - 验证重载流程正常"""
        skill_dir = tmp_path / "reload-test"
        skill_dir.mkdir()
        skill_file = skill_dir / "skill.py"
        skill_file.write_text('''
from anyclaw.skills.base import Skill

class ReloadTest(Skill):
    version = 1
    async def execute(self, **kwargs):
        return "v1"
''')

        loader = SkillLoader(skills_dirs=[str(tmp_path)])
        loader.load_all()

        # 检查初始加载
        skill = loader.get_python_skill("ReloadTest")
        assert skill is not None
        assert skill.version == 1
        old_id = id(skill)

        # 重载（即使文件未修改，也应该创建新实例）
        success = loader.reload_skill("ReloadTest")
        assert success

        # 检查重载后是新实例
        skill = loader.get_python_skill("ReloadTest")
        assert skill is not None
        # 验证是新实例（ID 不同）
        assert id(skill) != old_id

    def test_reload_all(self, tmp_path):
        """重载所有 skills"""
        # 创建多个 skills
        for i in range(3):
            skill_dir = tmp_path / f"skill-{i}"
            skill_dir.mkdir()
            (skill_dir / "skill.py").write_text(f'''
from anyclaw.skills.base import Skill

class Skill{i}(Skill):
    async def execute(self, **kwargs):
        return "{i}"
''')

        loader = SkillLoader(skills_dirs=[str(tmp_path)])
        loader.load_all()

        assert len(loader.python_skills) == 3

        # 重载所有
        stats = loader.reload_all()
        assert stats["total"] == 3
        assert stats["success"] == 3
        assert stats["failed"] == 0


class TestMDLoading:
    """测试 SKILL.md 加载"""

    def test_load_md_skill(self, tmp_path):
        """加载 SKILL.md 格式的 skill"""
        skill_dir = tmp_path / "md-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text('''---
name: md-test-skill
description: A markdown skill
---

# MD Test Skill

This is a test skill in markdown format.
''')

        loader = SkillLoader(skills_dirs=[str(tmp_path)])
        loader.load_all()

        assert "md-test-skill" in loader.md_skills
        skill = loader.md_skills["md-test-skill"]
        assert skill.name == "md-test-skill"
        assert skill.description == "A markdown skill"

    def test_md_skill_source_tracking(self, tmp_path):
        """MD skill 来源跟踪"""
        skill_dir = tmp_path / "md-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text('''---
name: source-test
description: Test source tracking
---
''')

        loader = SkillLoader(
            skills_dirs=[str(tmp_path)],
            skills_dir_types={str(tmp_path): "managed"}
        )
        loader.load_all()

        source = loader.get_skill_source("source-test")
        assert source is not None
        assert source.source_type == "managed"
