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


class TestProgressiveLoading:
    """测试渐进式加载功能"""

    def test_build_skills_summary(self, tmp_path):
        """测试构建 XML 格式的 skills summary"""
        # 创建 MD skill
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text('''---
name: summary-test
description: Test skill summary
---
# Summary Test
''')

        loader = SkillLoader(skills_dirs=[str(tmp_path)])
        loader.load_all()

        summary = loader.build_skills_summary()

        # 验证 XML 格式
        assert "<skills>" in summary
        assert "</skills>" in summary
        assert "<name>summary-test</name>" in summary
        assert "<description>Test skill summary</description>" in summary
        assert 'available="true"' in summary

    def test_load_skills_for_context(self, tmp_path):
        """测试批量加载技能内容"""
        skill_dir = tmp_path / "context-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text('''---
name: context-test
description: Test context loading
---
# Context Test

This is the skill body.
''')

        loader = SkillLoader(skills_dirs=[str(tmp_path)])
        loader.load_all()

        content = loader.load_skills_for_context(["context-test"])

        assert "## Skill: context-test" in content
        assert "# Context Test" in content
        assert "---" not in content  # frontmatter 应被去除

    def test_strip_frontmatter(self, tmp_path):
        """测试去除 frontmatter"""
        loader = SkillLoader()

        content_with_frontmatter = '''---
name: test
description: test
---
# Body
Content here'''

        result = loader._strip_frontmatter(content_with_frontmatter)

        assert "---" not in result
        assert "# Body" in result
        assert "Content here" in result

    def test_check_requirements_bins(self, tmp_path):
        """测试二进制依赖检查"""
        from anyclaw.skills.models import OpenClawRequires

        loader = SkillLoader()
        requires = OpenClawRequires(bins=["ls", "nonexistent_cmd_xyz"])

        available, missing = loader._check_requirements(requires)

        # ls 应该存在，nonexistent_cmd_xyz 不存在
        assert available == False
        assert len(missing) == 1
        assert "nonexistent_cmd_xyz" in missing[0]

    def test_check_requirements_env(self, tmp_path):
        """测试环境变量依赖检查"""
        from anyclaw.skills.models import OpenClawRequires

        loader = SkillLoader()
        requires = OpenClawRequires(env=["PATH", "NONEXISTENT_ENV_XYZ"])

        available, missing = loader._check_requirements(requires)

        # PATH 应该存在，NONEXISTENT_ENV_XYZ 不存在
        assert available == False
        assert len(missing) == 1
        assert "NONEXISTENT_ENV_XYZ" in missing[0]

    def test_get_always_skills(self, tmp_path):
        """测试获取 always skills"""
        # 创建 always skill
        always_dir = tmp_path / "always-skill"
        always_dir.mkdir()
        always_md = always_dir / "SKILL.md"
        always_md.write_text('''---
name: always-test
description: Always loaded skill
metadata:
  openclaw:
    always: true
---
# Always Test
''')

        # 创建普通 skill
        normal_dir = tmp_path / "normal-skill"
        normal_dir.mkdir()
        normal_md = normal_dir / "SKILL.md"
        normal_md.write_text('''---
name: normal-test
description: Normal skill
---
# Normal Test
''')

        loader = SkillLoader(skills_dirs=[str(tmp_path)])
        loader.load_all()

        always_skills = loader.get_always_skills()

        assert "always-test" in always_skills
        assert "normal-test" not in always_skills

    def test_always_skill_with_unmet_requirements(self, tmp_path):
        """测试依赖不满足的 always skill 不被加载"""
        skill_dir = tmp_path / "unmet-always"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text('''---
name: unmet-always
description: Always skill with unmet requirements
metadata:
  openclaw:
    always: true
    requires:
      bins: [nonexistent_cmd_xyz]
---
# Unmet Always
''')

        loader = SkillLoader(skills_dirs=[str(tmp_path)])
        loader.load_all()

        always_skills = loader.get_always_skills()

        # 依赖不满足，不应被包含
        assert "unmet-always" not in always_skills

    def test_summary_marks_unavailable(self, tmp_path):
        """测试 summary 正确标记不可用的 skill"""
        skill_dir = tmp_path / "unavailable-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text('''---
name: unavailable-test
description: Skill with unmet requirements
metadata:
  openclaw:
    requires:
      bins: [nonexistent_cmd_xyz]
---
# Unavailable
''')

        loader = SkillLoader(skills_dirs=[str(tmp_path)])
        loader.load_all()

        summary = loader.build_skills_summary()

        assert 'available="false"' in summary
        assert "nonexistent_cmd_xyz" in summary


class TestSkillScriptExecutor:
    """测试脚本执行器"""

    @pytest.fixture
    def loader_with_scripts(self, tmp_path):
        """创建带有脚本的 skill loader"""
        skill_dir = tmp_path / "script-skill"
        skill_dir.mkdir()

        # 创建 SKILL.md
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text('''---
name: script-test
description: Skill with scripts
---
# Script Test
''')

        # 创建 scripts 目录
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()

        # 创建 Python 脚本
        py_script = scripts_dir / "hello.py"
        py_script.write_text('print("Hello from Python")')

        # 创建 Shell 脚本
        sh_script = scripts_dir / "hello.sh"
        sh_script.write_text('''#!/bin/bash
echo "Hello from Bash"
''')

        # 创建 references 目录
        refs_dir = skill_dir / "references"
        refs_dir.mkdir()
        ref_file = refs_dir / "api.md"
        ref_file.write_text("# API Reference\n\nThis is the API reference.")

        loader = SkillLoader(skills_dirs=[str(tmp_path)])
        loader.load_all()
        return loader

    @pytest.mark.asyncio
    async def test_execute_python_script(self, loader_with_scripts):
        """测试执行 Python 脚本"""
        from anyclaw.skills.executor import SkillScriptExecutor

        executor = SkillScriptExecutor(loader_with_scripts)
        result = await executor.execute_script(
            "script-test",
            "scripts/hello.py"
        )

        assert "Hello from Python" in result

    @pytest.mark.asyncio
    async def test_execute_shell_script(self, loader_with_scripts):
        """测试执行 Shell 脚本"""
        from anyclaw.skills.executor import SkillScriptExecutor

        executor = SkillScriptExecutor(loader_with_scripts)
        result = await executor.execute_script(
            "script-test",
            "scripts/hello.sh"
        )

        assert "Hello from Bash" in result

    @pytest.mark.asyncio
    async def test_execute_nonexistent_script(self, loader_with_scripts):
        """测试执行不存在的脚本"""
        from anyclaw.skills.executor import SkillScriptExecutor

        executor = SkillScriptExecutor(loader_with_scripts)
        result = await executor.execute_script(
            "script-test",
            "scripts/nonexistent.py"
        )

        assert "Error" in result
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_execute_nonexistent_skill(self, loader_with_scripts):
        """测试执行不存在的 skill 脚本"""
        from anyclaw.skills.executor import SkillScriptExecutor

        executor = SkillScriptExecutor(loader_with_scripts)
        result = await executor.execute_script(
            "nonexistent-skill",
            "scripts/hello.py"
        )

        assert "Error" in result
        assert "not found" in result

    def test_list_scripts(self, loader_with_scripts):
        """测试列出脚本"""
        from anyclaw.skills.executor import SkillScriptExecutor

        executor = SkillScriptExecutor(loader_with_scripts)
        scripts = executor.list_scripts("script-test")

        assert len(scripts) == 2
        assert any("hello.py" in s for s in scripts)
        assert any("hello.sh" in s for s in scripts)

    def test_list_references(self, loader_with_scripts):
        """测试列出参考文档"""
        from anyclaw.skills.executor import SkillScriptExecutor

        executor = SkillScriptExecutor(loader_with_scripts)
        refs = executor.list_references("script-test")

        assert len(refs) == 1
        assert any("api.md" in r for r in refs)

    def test_read_reference(self, loader_with_scripts):
        """测试读取参考文档"""
        from anyclaw.skills.executor import SkillScriptExecutor

        executor = SkillScriptExecutor(loader_with_scripts)
        content = executor.read_reference("script-test", "references/api.md")

        assert content is not None
        assert "API Reference" in content


