"""SKILL.md 解析器 - 解析 OpenClaw 兼容的 SKILL.md 文件"""
import re
import shutil
import os
from pathlib import Path
from typing import Optional, Tuple
import yaml

from .models import SkillDefinition, SkillFrontmatter


class SkillParseError(Exception):
    """Skill 解析错误"""
    pass


def parse_skill_md(file_path: Path) -> Optional[SkillDefinition]:
    """
    解析 SKILL.md 文件

    Args:
        file_path: SKILL.md 文件路径

    Returns:
        SkillDefinition 或 None（解析失败时）
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        frontmatter, markdown = extract_frontmatter(content)

        if not frontmatter:
            raise SkillParseError(f"No valid frontmatter in {file_path}")

        # 解析 frontmatter
        fm = SkillFrontmatter.model_validate(frontmatter)

        # 创建 Skill 定义
        skill = SkillDefinition(
            name=fm.name,
            description=fm.description,
            content=markdown,
            frontmatter=fm,
            source_path=str(file_path)
        )

        return skill

    except Exception as e:
        print(f"[SkillParser] Error parsing {file_path}: {e}")
        return None


def extract_frontmatter(content: str) -> Tuple[Optional[dict], str]:
    """
    从 Markdown 内容中提取 YAML frontmatter

    Args:
        content: Markdown 文件内容

    Returns:
        (frontmatter_dict, remaining_markdown)
    """
    # 匹配 --- ... --- 格式的 frontmatter
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return None, content

    yaml_content = match.group(1)
    markdown_content = match.group(2)

    try:
        frontmatter = yaml.safe_load(yaml_content)
        return frontmatter, markdown_content
    except yaml.YAMLError:
        return None, content


def check_bin_dependency(bin_name: str) -> bool:
    """
    检查二进制命令是否可用

    Args:
        bin_name: 命令名称

    Returns:
        是否可用
    """
    return shutil.which(bin_name) is not None


def check_env_dependency(env_var: str) -> bool:
    """
    检查环境变量是否设置

    Args:
        env_var: 环境变量名

    Returns:
        是否设置
    """
    return os.environ.get(env_var) is not None


def check_skill_eligibility(skill: SkillDefinition) -> Tuple[bool, list]:
    """
    检查 Skill 是否满足依赖条件

    Args:
        skill: Skill 定义

    Returns:
        (是否可用, 不可用原因列表)
    """
    reasons = []
    openclaw_meta = skill.get_openclaw_metadata()

    if not openclaw_meta or not openclaw_meta.requires:
        return True, []

    requires = openclaw_meta.requires

    # 检查二进制依赖
    for bin_name in requires.bins:
        if not check_bin_dependency(bin_name):
            reasons.append(f"Missing binary: {bin_name}")

    # 检查环境变量依赖
    for env_var in requires.env:
        if not check_env_dependency(env_var):
            reasons.append(f"Missing environment variable: {env_var}")

    # 检查配置依赖 (暂时跳过，需要配置系统支持)
    # for config_key in requires.config:
    #     pass

    return len(reasons) == 0, reasons


def validate_skill(skill: SkillDefinition) -> SkillDefinition:
    """
    验证 Skill 并更新 eligibility 状态

    Args:
        skill: Skill 定义

    Returns:
        更新后的 Skill 定义
    """
    eligible, reasons = check_skill_eligibility(skill)
    skill.eligible = eligible
    skill.eligibility_reasons = reasons
    return skill
