"""Skill 验证器 - 验证 SKILL.md 格式"""
import re
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

import yaml


@dataclass
class ValidationResult:
    """验证结果"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    skill_name: Optional[str] = None
    skill_description: Optional[str] = None

    def __bool__(self) -> bool:
        return self.valid


# 允许的 frontmatter 字段
ALLOWED_FIELDS = {
    "name",
    "description",
    "homepage",
    "license",
    "metadata",
}

# 名称格式规则：小写字母、数字、连字符，最多 64 字符
NAME_PATTERN = re.compile(r'^[a-z][a-z0-9-]{0,63}$')
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024


def _extract_frontmatter(content: str) -> Tuple[Optional[dict], str]:
    """
    从 Markdown 内容中提取 YAML frontmatter

    Args:
        content: Markdown 文件内容

    Returns:
        (frontmatter_dict, remaining_markdown)
    """
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return None, content

    yaml_content = match.group(1)
    markdown_content = match.group(2)

    try:
        frontmatter = yaml.safe_load(yaml_content)
        if not isinstance(frontmatter, dict):
            return None, content
        return frontmatter, markdown_content
    except yaml.YAMLError:
        return None, content


def _validate_name(name: str) -> List[str]:
    """验证 skill 名称"""
    errors = []

    if not name:
        errors.append("name is required")
        return errors

    if not isinstance(name, str):
        errors.append("name must be a string")
        return errors

    if len(name) > MAX_NAME_LENGTH:
        errors.append(f"name is too long (max {MAX_NAME_LENGTH} characters)")

    if not NAME_PATTERN.match(name):
        errors.append("name should be hyphen-case (lowercase letters, numbers, hyphens, must start with letter)")

    return errors


def _validate_description(description: str) -> List[str]:
    """验证描述"""
    errors = []

    if not description:
        errors.append("description is required")
        return errors

    if not isinstance(description, str):
        errors.append("description must be a string")
        return errors

    if len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(f"description is too long (max {MAX_DESCRIPTION_LENGTH} characters)")

    # 检查是否包含 HTML 标签
    if '<' in description or '>' in description:
        errors.append("description should not contain HTML tags")

    return errors


def _validate_fields(frontmatter: dict) -> List[str]:
    """验证只包含允许的字段"""
    errors = []
    unknown_fields = set(frontmatter.keys()) - ALLOWED_FIELDS
    if unknown_fields:
        errors.append(f"unknown fields: {', '.join(sorted(unknown_fields))}")
    return errors


def validate_skill_dir(skill_path: Path) -> ValidationResult:
    """
    验证 skill 目录格式

    Args:
        skill_path: skill 目录路径

    Returns:
        ValidationResult 包含验证结果和错误信息
    """
    result = ValidationResult(valid=True)

    # 检查目录存在
    if not skill_path.exists():
        result.valid = False
        result.errors.append(f"directory does not exist: {skill_path}")
        return result

    if not skill_path.is_dir():
        result.valid = False
        result.errors.append(f"not a directory: {skill_path}")
        return result

    # 检查 SKILL.md 存在
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        result.valid = False
        result.errors.append("SKILL.md not found")
        return result

    # 读取 SKILL.md
    try:
        content = skill_md.read_text(encoding='utf-8')
    except Exception as e:
        result.valid = False
        result.errors.append(f"cannot read SKILL.md: {e}")
        return result

    # 提取 frontmatter
    frontmatter, markdown = _extract_frontmatter(content)

    if frontmatter is None:
        result.valid = False
        result.errors.append("invalid frontmatter format (must start with ---)")
        return result

    # 验证名称
    name = frontmatter.get("name")
    name_errors = _validate_name(name)
    if name_errors:
        result.valid = False
        result.errors.extend(name_errors)
    else:
        result.skill_name = name

    # 验证描述
    description = frontmatter.get("description")
    desc_errors = _validate_description(description)
    if desc_errors:
        result.valid = False
        result.errors.extend(desc_errors)
    else:
        result.skill_description = description

    # 验证字段
    field_errors = _validate_fields(frontmatter)
    if field_errors:
        result.warnings.extend(field_errors)  # 未知字段作为警告

    # 检查是否有实际内容
    if not markdown.strip():
        result.warnings.append("SKILL.md has no content after frontmatter")

    return result


def validate_skill_file(file_path: Path) -> ValidationResult:
    """
    验证单个 SKILL.md 文件

    Args:
        file_path: SKILL.md 文件路径

    Returns:
        ValidationResult
    """
    result = ValidationResult(valid=True)

    if not file_path.exists():
        result.valid = False
        result.errors.append(f"file does not exist: {file_path}")
        return result

    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        result.valid = False
        result.errors.append(f"cannot read file: {e}")
        return result

    frontmatter, markdown = _extract_frontmatter(content)

    if frontmatter is None:
        result.valid = False
        result.errors.append("invalid frontmatter format")
        return result

    # 验证名称
    name = frontmatter.get("name")
    name_errors = _validate_name(name)
    if name_errors:
        result.valid = False
        result.errors.extend(name_errors)
    else:
        result.skill_name = name

    # 验证描述
    description = frontmatter.get("description")
    desc_errors = _validate_description(description)
    if desc_errors:
        result.valid = False
        result.errors.extend(desc_errors)
    else:
        result.skill_description = description

    # 验证字段
    field_errors = _validate_fields(frontmatter)
    if field_errors:
        result.warnings.extend(field_errors)

    return result
