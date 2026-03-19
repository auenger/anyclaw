"""技能工具 - Agent 可调用的技能管理工具"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Tool


# 技能名称验证模式
NAME_PATTERN = re.compile(r'^[a-z][a-z0-9-]*$')


class CreateSkillTool(Tool):
    """创建新技能"""

    def __init__(self, skills_dir: Optional[str] = None):
        """
        初始化工具

        Args:
            skills_dir: 技能目录路径（默认使用配置中的路径）
        """
        self._skills_dir = skills_dir

    @property
    def name(self) -> str:
        return "create_skill"

    @property
    def description(self) -> str:
        return (
            "Create a new skill directory with SKILL.md template. "
            "Use this when you need to create a new skill for the agent to use. "
            "The skill will be created in the skills directory and can be used immediately after reload."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Skill name (lowercase letters, numbers, hyphens only, e.g., 'my-helper')"
                },
                "description": {
                    "type": "string",
                    "description": "Clear description of what the skill does and when to use it"
                },
                "resources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional: Resource directories to create (e.g., ['scripts', 'references', 'assets'])"
                },
                "examples": {
                    "type": "boolean",
                    "description": "Whether to create example files (default: false)"
                }
            },
            "required": ["name", "description"]
        }

    async def execute(
        self,
        name: str,
        description: str,
        resources: Optional[List[str]] = None,
        examples: bool = False,
        **kwargs
    ) -> str:
        """执行工具"""
        from anyclaw.skills.toolkit import init_skill, normalize_skill_name
        from anyclaw.config.settings import settings

        # 规范化名称
        normalized_name = normalize_skill_name(name)

        # 确定输出目录
        if self._skills_dir:
            output_path = Path(self._skills_dir)
        else:
            output_path = Path(settings.skills_dir) if settings.skills_dir else Path.cwd() / "skills"

        # 创建技能
        try:
            skill_dir = init_skill(
                name=normalized_name,
                path=output_path,
                resources=resources,
                examples=examples,
                description=description,
            )

            result = f"[OK] Created skill: {skill_dir}\n"
            result += f"  Name: {normalized_name}\n"
            result += f"  Description: {description}\n"
            result += "\nNext steps:\n"
            result += f"1. Edit {skill_dir}/SKILL.md to add instructions\n"
            result += "2. Use reload_skill tool to make it available\n"
            return result

        except FileExistsError as e:
            return f"Error: {e}"
        except ValueError as e:
            return f"Error: {e}"


class ReloadSkillTool(Tool):
    """重载技能"""

    def __init__(self, skill_loader=None):
        """
        初始化工具

        Args:
            skill_loader: SkillLoader 实例
        """
        self._skill_loader = skill_loader

    @property
    def name(self) -> str:
        return "reload_skill"

    @property
    def description(self) -> str:
        return (
            "Reload all skills or a specific skill. "
            "Use this after creating or modifying a skill to make it available. "
            "If no skill_name is provided, all skills will be reloaded."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "Optional: Name of specific skill to reload. If omitted, reloads all skills."
                }
            }
        }

    async def execute(self, skill_name: Optional[str] = None, **kwargs) -> str:
        """执行工具"""
        if not self._skill_loader:
            return "Error: SkillLoader not configured. Please provide skill_loader instance."

        if skill_name:
            # 重载单个技能
            success = self._skill_loader.reload_skill(skill_name)
            if success:
                return f"[OK] Reloaded skill: {skill_name}"
            else:
                return f"[ERROR] Failed to reload skill: {skill_name}"
        else:
            # 重载所有技能
            stats = self._skill_loader.reload_all()
            result = f"[OK] Reloaded all skills:\n"
            result += f"  Total: {stats['total']}\n"
            result += f"  Success: {stats['success']}\n"
            result += f"  Failed: {stats['failed']}"
            return result


class ValidateSkillTool(Tool):
    """验证技能格式"""

    @property
    def name(self) -> str:
        return "validate_skill"

    @property
    def description(self) -> str:
        return (
            "Validate a skill's format and structure. "
            "Use this to check if a skill directory has a valid SKILL.md with proper frontmatter."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to skill directory or SKILL.md file"
                }
            },
            "required": ["path"]
        }

    async def execute(self, path: str, **kwargs) -> str:
        """执行工具"""
        from anyclaw.skills.toolkit import validate_skill_dir

        skill_path = Path(path).resolve()
        result = validate_skill_dir(skill_path)

        if result.valid:
            output = "[OK] Skill is valid!\n"
            if result.skill_name:
                output += f"  Name: {result.skill_name}\n"
            if result.skill_description:
                desc = result.skill_description[:100] + "..." if len(result.skill_description) > 100 else result.skill_description
                output += f"  Description: {desc}"
            return output
        else:
            output = "[ERROR] Validation failed:\n"
            for error in result.errors:
                output += f"  - {error}\n"
            if result.warnings:
                output += "\nWarnings:\n"
                for warning in result.warnings:
                    output += f"  - {warning}"
            return output


class ShowSkillTool(Tool):
    """显示技能详情"""

    def __init__(self, skill_loader=None):
        """
        初始化工具

        Args:
            skill_loader: SkillLoader 实例
        """
        self._skill_loader = skill_loader

    @property
    def name(self) -> str:
        return "show_skill"

    @property
    def description(self) -> str:
        return (
            "Show detailed information about a skill. "
            "Use this to view a skill's content, structure, and metadata."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the skill to show"
                }
            },
            "required": ["name"]
        }

    async def execute(self, name: str, **kwargs) -> str:
        """执行工具"""
        if not self._skill_loader:
            return "Error: SkillLoader not configured."

        # 查找技能
        source = self._skill_loader.get_skill_source(name)
        if not source:
            available = list(self._skill_loader._skill_sources.keys())
            return f"Error: Skill '{name}' not found.\nAvailable skills: {', '.join(available) if available else 'none'}"

        # 获取技能内容
        skill_content = self._skill_loader.load_skill_content(name)

        output = f"Skill: {name}\n"
        output += f"Path: {source.path}\n"
        output += f"Source: {source.source_type}\n"
        output += f"Priority: {source.priority}\n"
        output += "\n--- Content Preview ---\n"

        if skill_content:
            # 限制预览长度
            preview = skill_content[:1500]
            if len(skill_content) > 1500:
                preview += "\n... (truncated)"
            output += preview
        else:
            output += "(No content available)"

        return output


class ListSkillsTool(Tool):
    """列出所有技能"""

    def __init__(self, skill_loader=None):
        """
        初始化工具

        Args:
            skill_loader: SkillLoader 实例
        """
        self._skill_loader = skill_loader

    @property
    def name(self) -> str:
        return "list_skills"

    @property
    def description(self) -> str:
        return (
            "List all available skills. "
            "Use this to see what skills are currently loaded."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }

    async def execute(self, **kwargs) -> str:
        """执行工具"""
        if not self._skill_loader:
            return "Error: SkillLoader not configured."

        python_skills = list(self._skill_loader.python_skills.keys())
        md_skills = list(self._skill_loader.md_skills.keys())
        all_skills = sorted(set(python_skills + md_skills))

        if not all_skills:
            return "No skills loaded."

        output = f"Loaded Skills ({len(all_skills)}):\n"
        for skill_name in all_skills:
            source = self._skill_loader.get_skill_source(skill_name)
            source_type = source.source_type if source else "unknown"
            output += f"  - {skill_name} ({source_type})\n"

        return output.rstrip()


def register_skill_tools(registry, skill_loader=None, skills_dir: Optional[str] = None):
    """
    注册所有技能工具到注册表

    Args:
        registry: ToolRegistry 实例
        skill_loader: SkillLoader 实例（可选）
        skills_dir: 技能目录路径（可选）
    """
    registry.register(CreateSkillTool(skills_dir=skills_dir))
    registry.register(ReloadSkillTool(skill_loader=skill_loader))
    registry.register(ValidateSkillTool())
    registry.register(ShowSkillTool(skill_loader=skill_loader))
    registry.register(ListSkillsTool(skill_loader=skill_loader))
