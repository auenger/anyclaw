"""Tests for skill toolkit"""
import pytest
import tempfile
from pathlib import Path

from anyclaw.skills.toolkit import (
    validate_skill_dir,
    init_skill,
    package_skill,
    normalize_skill_name,
)
from anyclaw.skills.toolkit.validator import ValidationResult
from anyclaw.skills.toolkit.packager import unpackage_skill


class TestNormalizeSkillName:
    """测试名称规范化"""

    def test_basic_name(self):
        assert normalize_skill_name("my-skill") == "my-skill"

    def test_spaces_to_hyphens(self):
        assert normalize_skill_name("my skill") == "my-skill"

    def test_underscores_to_hyphens(self):
        assert normalize_skill_name("my_skill") == "my-skill"

    def test_uppercase_to_lowercase(self):
        assert normalize_skill_name("MySkill") == "myskill"

    def test_special_chars_removed(self):
        assert normalize_skill_name("my@skill!") == "myskill"

    def test_starts_with_number(self):
        assert normalize_skill_name("123skill") == "skill-123skill"

    def test_multiple_hyphens_collapsed(self):
        assert normalize_skill_name("my---skill") == "my-skill"


class TestValidateSkillDir:
    """测试 skill 验证"""

    def test_valid_skill(self, tmp_path):
        """验证有效的 skill"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: A test skill
---

# Test Skill

Content here.
""")
        result = validate_skill_dir(skill_dir)
        assert result.valid
        assert result.skill_name == "test-skill"

    def test_missing_skill_md(self, tmp_path):
        """缺少 SKILL.md"""
        result = validate_skill_dir(tmp_path)
        assert not result.valid
        assert "SKILL.md not found" in result.errors

    def test_missing_frontmatter(self, tmp_path):
        """缺少 frontmatter"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("# Test Skill\n\nNo frontmatter.")
        result = validate_skill_dir(skill_dir)
        assert not result.valid
        assert any("frontmatter" in e.lower() for e in result.errors)

    def test_invalid_name_format(self, tmp_path):
        """无效的名称格式"""
        skill_dir = tmp_path / "TestSkill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: Test_Skill!
description: A test skill
---
""")
        result = validate_skill_dir(skill_dir)
        assert not result.valid
        assert any("hyphen-case" in e.lower() for e in result.errors)

    def test_missing_name(self, tmp_path):
        """缺少 name 字段"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
description: A test skill
---
""")
        result = validate_skill_dir(skill_dir)
        assert not result.valid
        assert any("name" in e.lower() for e in result.errors)

    def test_missing_description(self, tmp_path):
        """缺少 description 字段"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
---
""")
        result = validate_skill_dir(skill_dir)
        assert not result.valid
        assert any("description" in e.lower() for e in result.errors)

    def test_description_too_long(self, tmp_path):
        """描述过长"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        long_desc = "x" * 2000
        skill_md.write_text(f"""---
name: test-skill
description: {long_desc}
---
""")
        result = validate_skill_dir(skill_dir)
        assert not result.valid
        assert any("too long" in e.lower() for e in result.errors)

    def test_description_with_html(self, tmp_path):
        """描述包含 HTML 标签"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: A <b>test</b> skill
---
""")
        result = validate_skill_dir(skill_dir)
        assert not result.valid
        assert any("html" in e.lower() for e in result.errors)


class TestInitSkill:
    """测试 skill 创建"""

    def test_basic_creation(self, tmp_path):
        """基本创建"""
        skill_dir = init_skill("my-skill", path=tmp_path)
        assert skill_dir.exists()
        assert (skill_dir / "SKILL.md").exists()

        content = (skill_dir / "SKILL.md").read_text()
        assert "name: my-skill" in content
        assert "description:" in content

    def test_name_normalization(self, tmp_path):
        """名称规范化"""
        skill_dir = init_skill("My Skill Name", path=tmp_path)
        assert skill_dir.name == "my-skill-name"

    def test_with_resources(self, tmp_path):
        """创建资源目录"""
        skill_dir = init_skill(
            "test-skill",
            path=tmp_path,
            resources=["scripts", "references"],
        )
        assert (skill_dir / "scripts").is_dir()
        assert (skill_dir / "references").is_dir()

    def test_with_examples(self, tmp_path):
        """创建示例文件"""
        skill_dir = init_skill(
            "test-skill",
            path=tmp_path,
            resources=["scripts", "references"],
            examples=True,
        )
        assert (skill_dir / "scripts" / "example.sh").exists()
        assert (skill_dir / "references" / "README.md").exists()

    def test_custom_description(self, tmp_path):
        """自定义描述"""
        skill_dir = init_skill(
            "test-skill",
            path=tmp_path,
            description="My custom description",
        )
        content = (skill_dir / "SKILL.md").read_text()
        assert "My custom description" in content

    def test_already_exists(self, tmp_path):
        """目录已存在"""
        init_skill("test-skill", path=tmp_path)
        with pytest.raises(FileExistsError):
            init_skill("test-skill", path=tmp_path)

    def test_invalid_name(self, tmp_path):
        """无效名称 - 只有特殊字符，规范化后为空"""
        with pytest.raises(ValueError):
            init_skill("@#$%", path=tmp_path)  # 规范化后为空字符串


class TestPackageSkill:
    """测试 skill 打包"""

    def test_package_valid_skill(self, tmp_path):
        """打包有效 skill"""
        # 创建 skill
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: A test skill
---

# Test Skill
""")

        # 打包
        output_file = package_skill(skill_dir, output_dir=tmp_path)
        assert output_file.exists()
        assert output_file.suffix == ".skill"

        # 验证是 ZIP 文件
        import zipfile
        assert zipfile.is_zipfile(output_file)

    def test_package_invalid_skill(self, tmp_path):
        """打包无效 skill 应该失败"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        # 没有 SKILL.md

        with pytest.raises(ValueError) as exc_info:
            package_skill(skill_dir, output_dir=tmp_path)
        assert "validation failed" in str(exc_info.value).lower()

    def test_package_with_validation_disabled(self, tmp_path):
        """禁用验证打包"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()

        output_file = package_skill(skill_dir, output_dir=tmp_path, validate=False)
        assert output_file.exists()

    def test_exclude_patterns(self, tmp_path):
        """排除特定文件"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: A test skill
---
""")
        # 创建应排除的文件
        (skill_dir / ".git").mkdir()
        (skill_dir / "__pycache__").mkdir()
        (skill_dir / "test.pyc").write_text("")

        output_file = package_skill(skill_dir, output_dir=tmp_path)

        import zipfile
        with zipfile.ZipFile(output_file, 'r') as zf:
            names = zf.namelist()
            assert ".git/" not in names
            assert "__pycache__/" not in names
            assert "test.pyc" not in names


class TestUnpackageSkill:
    """测试 skill 解压"""

    def test_unpackage(self, tmp_path):
        """解压 .skill 文件"""
        # 创建并打包
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: A test skill
---
""")

        skill_file = package_skill(skill_dir, output_dir=tmp_path)

        # 删除原目录
        import shutil
        shutil.rmtree(skill_dir)

        # 解压
        extracted_dir = unpackage_skill(skill_file, output_dir=tmp_path)
        assert extracted_dir.exists()
        assert (extracted_dir / "SKILL.md").exists()

    def test_invalid_extension(self, tmp_path):
        """无效扩展名"""
        invalid_file = tmp_path / "test.txt"
        invalid_file.write_text("test")

        with pytest.raises(ValueError):
            unpackage_skill(invalid_file)
