# feat-workspace-templates: Workspace 模板系统增强

## 概述

增强 AnyClaw 的 workspace 模板系统，创建完整的模板文件结构，包括人设、工具说明、心跳任务、记忆存储等模板文件，支持从包内同步到用户工作区。

## 依赖

- `feat-workspace-init` (已完成) - Workspace 初始化基础

## 用户价值点

### VP1: 完整模板文件结构

**价值**: 提供开箱即用的 workspace 模板，用户无需手动创建配置文件。

**Gherkin 场景**:

```gherkin
Feature: 完整模板文件结构

  Scenario: 创建默认工作区模板
    Given 用户首次运行 "anyclaw setup"
    When 工作区创建完成
    Then 应包含 SOUL.md (Agent 人设)
    And 应包含 USER.md (用户档案)
    And 应包含 AGENTS.md (Agent 指令)
    And 应包含 TOOLS.md (工具说明)
    And 应包含 HEARTBEAT.md (心跳任务)
    And 应包含 memory/MEMORY.md (长期记忆)
    And 应包含 memory/HISTORY.md (历史记录)
    And 应创建 skills/ 目录

  Scenario: 在项目目录初始化
    Given 用户在项目目录中
    When 执行 "anyclaw init"
    Then 应创建 .anyclaw/ 子目录
    And 包含所有模板文件
    And 不影响项目其他文件

  Scenario: 模板同步不覆盖现有文件
    Given 工作区已存在并包含自定义的 USER.md
    When 执行 "anyclaw setup"
    Then 不应覆盖现有的 USER.md
    And 只创建缺失的模板文件
```

### VP2: 模板文件内容

**价值**: 每个模板文件包含有意义的默认内容和说明。

**Gherkin 场景**:

```gherkin
Feature: 模板文件内容

  Scenario: SOUL.md 包含人设定义
    Given 查看 SOUL.md 内容
    Then 应包含 Agent 名称 (AnyClaw)
    Then 应包含性格描述
    Then 应包含价值观
    Then 应包含沟通风格

  Scenario: USER.md 包含用户档案模板
    Given 查看 USER.md 内容
    Then 应包含基本信息字段
    Then 应包含偏好设置选项
    Then 应包含工作背景字段
    Then 应包含编辑说明

  Scenario: TOOLS.md 包含工具使用说明
    Given 查看 TOOLS.md 内容
    Then 应包含 exec 工具说明
    Then 应包含 cron 工具说明
    Then 应包含文件操作工具说明
```

## 技术设计

### 模板目录结构

```
anyclaw/templates/
├── __init__.py
├── SOUL.md         # Agent 人设
├── USER.md         # 用户档案
├── AGENTS.md       # Agent 指令
├── TOOLS.md        # 工具说明
├── HEARTBEAT.md    # 心跳任务
└── memory/
    ├── MEMORY.md   # 长期记忆
    └── HISTORY.md  # 历史记录
```

### 核心函数

```python
# workspace/templates.py

def sync_workspace_templates(workspace: Path, silent: bool = False) -> List[str]:
    """同步模板文件到工作区

    只创建不存在的文件。

    Args:
        workspace: 工作区路径
        silent: 是否静默模式

    Returns:
        创建的文件列表
    """
    from importlib.resources import files as pkg_files

    added: List[str] = []

    def _write(template_name: str, dest: Path):
        if dest.exists():
            return
        try:
            tpl = pkg_files("anyclaw") / "templates" / template_name
            content = tpl.read_text(encoding="utf-8")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            added.append(str(dest.relative_to(workspace)))
        except Exception:
            pass

    # 根目录模板
    for name in ["SOUL.md", "USER.md", "AGENTS.md", "TOOLS.md", "HEARTBEAT.md"]:
        _write(name, workspace / name)

    # memory 目录模板
    for name in ["MEMORY.md", "HISTORY.md"]:
        _write(f"memory/{name}", workspace / "memory" / name)

    # 创建 skills 目录
    (workspace / "skills").mkdir(exist_ok=True)

    return added
```

### CLI 命令

```bash
# 创建完整工作区
anyclaw setup [--workspace PATH] [--force]

# 在当前目录初始化 .anyclaw
anyclaw init
```

### pyproject.toml 配置

```toml
[tool.poetry]
packages = [{include = "anyclaw"}]
include = [
    {path = "anyclaw/templates/**/*", format = ["sdist", "wheel"]},
]
```

## 工作区结构

```
~/.anyclaw/workspace/          # 默认工作区
├── SOUL.md                    # Agent 人设
├── USER.md                    # 用户档案
├── AGENTS.md                  # Agent 指令
├── TOOLS.md                   # 工具说明
├── HEARTBEAT.md               # 心跳任务
├── memory/                    # 记忆存储
│   ├── MEMORY.md              # 长期记忆
│   └── HISTORY.md             # 对话历史
├── skills/                    # 自定义技能
└── .gitignore

.project/.anyclaw/             # 项目级配置
├── (同上结构)
```

## 文件说明

| 文件 | 用途 | 说明 |
|------|------|------|
| SOUL.md | Agent 人设 | 定义 Agent 的性格、价值观、沟通风格 |
| USER.md | 用户档案 | 存储用户信息、偏好设置 |
| AGENTS.md | Agent 指令 | 包含定时提醒、心跳任务的说明 |
| TOOLS.md | 工具说明 | 记录工具使用约束和模式 |
| HEARTBEAT.md | 心跳任务 | 定期执行的任务列表 |
| memory/MEMORY.md | 长期记忆 | 存储重要信息 |
| memory/HISTORY.md | 历史记录 | 对话历史摘要 |
| skills/ | 技能目录 | 存放自定义技能 |

## 验收标准

- [x] 创建 templates 目录和模板文件
- [x] 实现 sync_workspace_templates 函数
- [x] 更新 setup 命令使用模板同步
- [x] 添加 init 命令用于项目级初始化
- [x] pyproject.toml 配置正确包含模板
- [x] 模板同步不覆盖现有文件
- [x] 创建 memory/ 和 skills/ 目录

## 实现文件

```
anyclaw/
├── templates/
│   ├── __init__.py
│   ├── SOUL.md
│   ├── USER.md
│   ├── AGENTS.md
│   ├── TOOLS.md
│   ├── HEARTBEAT.md
│   └── memory/
│       ├── MEMORY.md
│       └── HISTORY.md
├── workspace/
│   ├── __init__.py
│   ├── manager.py
│   ├── templates.py
│   └── bootstrap.py
└── cli/
    └── app.py
```

## 优先级

| 功能 | 优先级 | 理由 |
|------|--------|------|
| 模板文件创建 | P0 | 基础能力 |
| 模板同步函数 | P0 | 核心功能 |
| CLI 命令更新 | P0 | 用户体验 |
| pyproject.toml | P0 | 打包必要 |

## 完成时间

2026-03-18
