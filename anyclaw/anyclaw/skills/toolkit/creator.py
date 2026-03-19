"""Skill 创建器 - 创建 skill 模板"""
import re
from pathlib import Path
from typing import List, Optional

from .validator import NAME_PATTERN


# SKILL.md 模板
SKILL_TEMPLATE = '''---
name: {name}
description: {description}
---

# {title}

TODO: Add skill instructions here.

## Usage

```bash
# Example command
echo "Hello from {name}"
```

## Parameters

This skill accepts the following parameters:

- `param1`: Description of param1

## Examples

### Example 1: Basic usage

```bash
# Describe what this example does
```
'''

# 带示例的 SKILL.md 模板
SKILL_TEMPLATE_WITH_EXAMPLES = '''---
name: {name}
description: {description}
---

# {title}

TODO: Add skill instructions here.

## Usage

```bash
# Example command with parameter
echo "Hello from {name}: {{param1}}"
```

## Parameters

This skill accepts the following parameters:

- `param1`: Description of param1 (required)
- `param2`: Description of param2 (optional)

## Examples

### Example 1: Basic usage

```bash
# Basic example
{name} --help
```

### Example 2: With parameters

```bash
# Example with parameters
{name} --param1 value1 --param2 value2
```

## Resources

The following resources are available:

- `scripts/` - Helper scripts
- `references/` - Reference documents
'''

# 示例脚本
EXAMPLE_SCRIPT = '''#!/bin/bash
# Example helper script for {name}
# Usage: ./example.sh <arg>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <arg>"
    exit 1
fi

echo "Processing: $1"
'''


def normalize_skill_name(name: str) -> str:
    """
    将名称规范化为 hyphen-case

    Args:
        name: 原始名称

    Returns:
        规范化后的名称
    """
    # 转小写
    name = name.lower()
    # 替换空格和下划线为连字符
    name = re.sub(r'[\s_]+', '-', name)
    # 移除非字母数字字符（保留连字符）
    name = re.sub(r'[^a-z0-9-]', '', name)
    # 确保以字母开头
    if name and not name[0].isalpha():
        name = 'skill-' + name
    # 移除连续的连字符
    name = re.sub(r'-+', '-', name)
    # 移除首尾的连字符
    name = name.strip('-')
    return name


def create_resource_dirs(skill_dir: Path, resources: List[str], examples: bool = False) -> List[str]:
    """
    创建资源目录

    Args:
        skill_dir: skill 目录
        resources: 资源目录列表
        examples: 是否创建示例文件

    Returns:
        创建的目录列表
    """
    created = []

    for resource in resources:
        resource_dir = skill_dir / resource
        if not resource_dir.exists():
            resource_dir.mkdir(parents=True)
            created.append(resource)

        # 创建示例文件
        if examples and resource == "scripts":
            example_script = resource_dir / "example.sh"
            if not example_script.exists():
                skill_name = skill_dir.name
                example_script.write_text(EXAMPLE_SCRIPT.format(name=skill_name))
                example_script.chmod(0o755)
                created.append(f"{resource}/example.sh")

        elif examples and resource == "references":
            readme = resource_dir / "README.md"
            if not readme.exists():
                readme.write_text(f"# References\n\nAdd reference documents here.\n")
                created.append(f"{resource}/README.md")

    return created


def init_skill(
    name: str,
    path: Optional[Path] = None,
    resources: Optional[List[str]] = None,
    examples: bool = False,
    description: Optional[str] = None,
) -> Path:
    """
    初始化一个新的 skill 目录

    Args:
        name: skill 名称（会被规范化）
        path: 输出目录（默认当前目录）
        resources: 资源目录列表（如 ['scripts', 'references']）
        examples: 是否创建示例文件
        description: skill 描述

    Returns:
        创建的 skill 目录路径

    Raises:
        ValueError: 名称无效
        FileExistsError: 目录已存在
    """
    # 规范化名称
    normalized_name = normalize_skill_name(name)

    # 验证名称
    if not NAME_PATTERN.match(normalized_name):
        raise ValueError(
            f"Invalid skill name '{normalized_name}'. "
            "Name must start with a letter and contain only lowercase letters, numbers, and hyphens."
        )

    # 确定输出目录
    if path is None:
        path = Path.cwd()
    else:
        path = Path(path).resolve()

    skill_dir = path / normalized_name

    # 检查目录是否存在
    if skill_dir.exists():
        raise FileExistsError(f"Directory already exists: {skill_dir}")

    # 创建目录
    skill_dir.mkdir(parents=True)

    # 生成描述
    if description is None:
        description = f"A skill named {normalized_name}"

    # 生成标题
    title = normalized_name.replace('-', ' ').title()

    # 选择模板
    template = SKILL_TEMPLATE_WITH_EXAMPLES if examples else SKILL_TEMPLATE

    # 生成 SKILL.md 内容
    skill_md_content = template.format(
        name=normalized_name,
        description=description,
        title=title,
    )

    # 写入 SKILL.md
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(skill_md_content)

    # 创建资源目录
    created_resources = []
    if resources:
        created_resources = create_resource_dirs(skill_dir, resources, examples)

    return skill_dir
