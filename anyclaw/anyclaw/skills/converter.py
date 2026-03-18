"""Tool Definition 转换器 - 将 Skill 转换为 LLM 兼容的 Tool Definition"""
from typing import Dict, List, Any, Optional

from .models import SkillDefinition


def skill_to_tool_definition(skill: SkillDefinition) -> Dict[str, Any]:
    """
    将 Skill 转换为 OpenAI 兼容的 Tool Definition

    Args:
        skill: Skill 定义

    Returns:
        Tool Definition 字典
    """
    parameters = skill.get_parameters()

    # 确保参数格式正确
    if not parameters:
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }

    return {
        "type": "function",
        "function": {
            "name": skill.name,
            "description": skill.description,
            "parameters": parameters
        }
    }


def skills_to_tools(skills: List[SkillDefinition]) -> List[Dict[str, Any]]:
    """
    批量转换 Skills 为 Tool Definitions

    Args:
        skills: Skill 列表

    Returns:
        Tool Definition 列表（仅包含可用的 skills）
    """
    tools = []
    for skill in skills:
        if skill.eligible:
            tools.append(skill_to_tool_definition(skill))
    return tools


def infer_parameters_from_commands(commands: List[str]) -> Dict[str, Any]:
    """
    从命令模板推断参数定义

    Args:
        commands: 命令模板列表

    Returns:
        参数定义字典
    """
    import re

    properties = {}
    required = []

    # 匹配 {param} 格式的参数
    param_pattern = r'\{(\w+)\}'

    for cmd in commands:
        matches = re.findall(param_pattern, cmd)
        for param in matches:
            if param not in properties:
                properties[param] = {
                    "type": "string",
                    "description": f"{param} parameter"
                }
                required.append(param)

    return {
        "type": "object",
        "properties": properties,
        "required": required
    }


def merge_parameter_definitions(
    inferred: Dict[str, Any],
    manual: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    合并推断的参数和手动定义的参数

    手动定义的参数优先级更高

    Args:
        inferred: 推断的参数
        manual: 手动定义的参数

    Returns:
        合并后的参数定义
    """
    if not manual:
        return inferred

    # 如果只有手动定义，直接使用
    if not inferred.get("properties"):
        return manual

    # 合并 properties
    merged_properties = inferred.get("properties", {}).copy()
    merged_properties.update(manual.get("properties", {}))

    # 合并 required
    inferred_required = set(inferred.get("required", []))
    manual_required = set(manual.get("required", []))
    merged_required = list(inferred_required | manual_required)

    return {
        "type": "object",
        "properties": merged_properties,
        "required": merged_required
    }
