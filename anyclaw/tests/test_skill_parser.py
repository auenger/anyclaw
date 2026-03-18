"""测试 SKILL.md 解析器"""
import pytest
from pathlib import Path
import tempfile

from anyclaw.skills.parser import (
    parse_skill_md,
    extract_frontmatter,
    check_bin_dependency,
    check_env_dependency,
    check_skill_eligibility,
    validate_skill,
)
from anyclaw.skills.models import SkillDefinition, SkillFrontmatter


class TestExtractFrontmatter:
    """测试 frontmatter 提取"""

    def test_extract_valid_frontmatter(self):
        """测试提取有效的 frontmatter"""
        content = """---
name: test-skill
description: A test skill
metadata:
  openclaw:
    emoji: "🔧"
---

# Test Skill

This is the content.
"""
        frontmatter, markdown = extract_frontmatter(content)

        assert frontmatter is not None
        assert frontmatter["name"] == "test-skill"
        assert frontmatter["description"] == "A test skill"
        assert "# Test Skill" in markdown

    def test_extract_no_frontmatter(self):
        """测试没有 frontmatter 的情况"""
        content = "# Just Markdown\n\nNo frontmatter here."
        frontmatter, markdown = extract_frontmatter(content)

        assert frontmatter is None
        assert markdown == content


class TestParseSkillMd:
    """测试 SKILL.md 解析"""

    def test_parse_valid_skill(self, tmp_path):
        """测试解析有效的 SKILL.md"""
        skill_content = """---
name: weather
description: "Get weather info"
metadata:
  openclaw:
    emoji: "☔"
    requires:
      bins:
        - curl
---

# Weather Skill

```bash
curl "wttr.in/{location}?format=3"
```
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        skill = parse_skill_md(skill_file)

        assert skill is not None
        assert skill.name == "weather"
        assert skill.description == "Get weather info"
        assert "# Weather Skill" in skill.content
        assert len(skill.get_commands()) == 1

    def test_parse_skill_with_parameters(self, tmp_path):
        """测试解析带参数的 skill"""
        skill_content = """---
name: test
description: "Test skill"
---

# Test

```bash
echo "{arg1} {arg2}"
```
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        skill = parse_skill_md(skill_file)

        params = skill.get_parameters()
        assert "arg1" in params["properties"]
        assert "arg2" in params["properties"]
        assert "arg1" in params["required"]


class TestDependencyCheck:
    """测试依赖检查"""

    def test_check_bin_exists(self):
        """测试检查存在的命令"""
        # ls 在所有 Unix 系统上存在
        assert check_bin_dependency("ls") is True

    def test_check_bin_not_exists(self):
        """测试检查不存在的命令"""
        assert check_bin_dependency("nonexistent_command_xyz") is False

    def test_check_env_set(self, monkeypatch):
        """测试检查设置的环境变量"""
        monkeypatch.setenv("TEST_VAR", "value")
        assert check_env_dependency("TEST_VAR") is True

    def test_check_env_not_set(self):
        """测试检查未设置的环境变量"""
        assert check_env_dependency("NONEXISTENT_VAR_XYZ") is False


class TestSkillEligibility:
    """测试 Skill 可用性检查"""

    def test_eligible_skill_no_requires(self, tmp_path):
        """测试无依赖要求的 skill"""
        skill_content = """---
name: simple
description: "Simple skill"
---

# Simple
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        skill = parse_skill_md(skill_file)
        eligible, reasons = check_skill_eligibility(skill)

        assert eligible is True
        assert len(reasons) == 0

    def test_eligible_skill_with_satisfied_requires(self, tmp_path):
        """测试依赖满足的 skill"""
        skill_content = """---
name: test
description: "Test"
metadata:
  openclaw:
    requires:
      bins:
        - ls
---
# Test
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        skill = parse_skill_md(skill_file)
        eligible, reasons = check_skill_eligibility(skill)

        assert eligible is True
        assert len(reasons) == 0

    def test_not_eligible_skill_missing_bin(self, tmp_path):
        """测试缺少二进制依赖的 skill"""
        skill_content = """---
name: test
description: "Test"
metadata:
  openclaw:
    requires:
      bins:
        - nonexistent_command_xyz
---
# Test
"""
        skill_file = tmp_path / "SKILL.md"
        skill_file.write_text(skill_content)

        skill = parse_skill_md(skill_file)
        eligible, reasons = check_skill_eligibility(skill)

        assert eligible is False
        assert "Missing binary: nonexistent_command_xyz" in reasons
