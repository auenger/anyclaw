# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

AnyClaw 是一个轻量级、可扩展的 AI 智能体框架，参考 [Nanobot](https://github.com/HKUDS/nanobot) 和 [OpenClaw](https://github.com/openclaw/openclaw) 项目架构。项目采用 Python 3.11+ 开发，使用 Poetry 管理依赖。

## 技术栈

- **语言**: Python 3.11+
- **依赖管理**: Poetry
- **核心依赖**:
  - `pydantic` >= 2.12.0 (数据验证)
  - `pydantic-settings` >= 2.0.0 (配置管理)
  - `typer[all]` >= 0.20.0 (CLI 框架)
  - `rich` >= 14.0.0 (终端美化)
  - `litellm` >= 1.82.1 (LLM 统一接口)
  - `openai` >= 1.0.0 (OpenAI SDK)
- **测试框架**: pytest >= 8.0.0, pytest-asyncio >= 0.23.0
- **代码质量**: Black (格式化), Ruff (检查)

## 核心架构

### 目录结构

```
anyclaw/
├── anyclaw/                   # 主包
│   ├── __init__.py
│   ├── __main__.py            # 入口点
│   ├── agent/                 # Agent 系统
│   │   ├── loop.py            # 主处理循环
│   │   ├── context.py         # 上下文构建器
│   │   └── history.py         # 对话历史
│   ├── channels/              # 频道系统
│   │   └── cli.py             # CLI 频道
│   ├── skills/                # 技能系统
│   │   ├── base.py            # 技能基类
│   │   ├── loader.py          # 技能加载器
│   │   └── builtin/           # 内置技能
│   │       ├── echo/
│   │       └── time/
│   ├── tools/                 # 工具系统
│   │   ├── base.py            # 工具基类
│   │   ├── registry.py        # 工具注册表
│   │   ├── shell.py           # Shell 执行工具
│   │   └── filesystem.py      # 文件系统工具
│   ├── templates/             # 模板文件
│   │   ├── SOUL.md            # Agent 人设模板
│   │   ├── USER.md            # 用户档案模板
│   │   ├── AGENTS.md          # Agent 指令模板
│   │   ├── TOOLS.md           # 工具说明模板
│   │   ├── HEARTBEAT.md       # 心跳任务模板
│   │   └── memory/            # 记忆模板
│   ├── workspace/             # 工作区管理
│   │   ├── manager.py         # 工作区管理器
│   │   ├── templates.py       # 模板同步
│   │   └── bootstrap.py       # 引导系统
│   ├── config/                # 配置系统
│   │   └── settings.py        # Pydantic Settings
│   └── cli/                   # CLI 应用
│       └── app.py             # Typer 应用
├── tests/                     # 测试目录
├── pyproject.toml             # 项目配置
└── .env.example               # 环境变量示例
```

### Agent 处理流程

```
用户输入 → Channel → AgentLoop.process()
    ↓
添加到历史记录 (ConversationHistory)
    ↓
构建上下文 (ContextBuilder)
    ↓
调用 LLM (litellm acompletion)
    ↓
添加响应到历史
    ↓
返回响应
```

## 常用命令

### 依赖安装

```bash
# 使用 Poetry (推荐)
cd anyclaw
poetry install

# 或使用 pip
pip install pydantic pydantic-settings typer rich litellm openai pytest pytest-asyncio
```

### 配置环境

```bash
# 复制环境变量文件
cp anyclaw/.env.example anyclaw/.env

# 编辑 .env 文件，设置必要的 API Key
# OPENAI_API_KEY=sk-your-key-here
```

### 运行应用

```bash
# 从 anyclaw/ 目录运行
cd anyclaw

# 初始化工作区
poetry run python -m anyclaw setup

# 在项目目录初始化
cd /your/project
poetry run python -m anyclaw init

# 启动 CLI 聊天
poetry run python -m anyclaw chat

# 查看配置
poetry run python -m anyclaw config --show

# 查看版本
poetry run python -m anyclaw version
```

### 测试

```bash
cd anyclaw

# 运行所有测试
poetry run pytest tests/ -v

# 运行特定测试
poetry run pytest tests/test_config.py -v
poetry run pytest tests/test_agent.py -v
poetry run pytest tests/test_skills.py -v

# 运行带覆盖率的测试
poetry run pytest --cov=anyclaw tests/
```

### 代码质量检查

```bash
cd anyclaw

# 格式化代码
poetry run black anyclaw/

# 检查代码
poetry run ruff check anyclaw/

# 类型检查 (如使用 mypy)
poetry run mypy anyclaw/
```

## Feature Workflow 工作流

项目使用基于 Git Worktree 的多需求并行开发工作流：

### 核心概念

- **并行开发**: 支持多个需求同时开发，通过 worktree 物理隔离
- **文档驱动**: 每个需求包含 `spec.md`/`task.md`/`checklist.md` 三个文档
- **状态追踪**: 通过 `feature-workflow/queue.yaml` 统一管理需求状态
- **归档策略**: 完成后创建 tag 归档，删除 worktree 和分支

### 常用 Workflow 命令

| 命令 | 说明 |
|------|------|
| `/new-feature` | 创建新需求 |
| `/start-feature <id>` | 启动需求开发 |
| `/implement-feature <id>` | 实现需求代码 |
| `/verify-feature <id>` | 验证需求完成 |
| `/complete-feature <id>` | 完成需求（提交→合并→归档） |
| `/list-features` | 查看所有需求状态 |

### 配置文件

- `feature-workflow/config.yaml` - 项目配置
- `feature-workflow/queue.yaml` - 调度队列
- `features/` - 需求目录 (pending/active/archive)

## 参考项目

- **Nanobot** (`reference/nanobot/`): 主要参考项目，超轻量级 AI 助手
  - 核心架构: agent/channels/skills/providers
  - 技能系统: 基于 Markdown 的技能定义
  - 频道插件: 支持多种消息平台

- **OpenClaw** (`reference/openclaw/`): 架构参考
  - TypeScript/Node.js 实现
  - 丰富的频道支持和扩展系统

## 开发规范

### 代码风格

- 使用 Black 格式化 (line-length=100)
- 使用 Ruff 检查 (E, F, I, N, W 规则)
- Python 3.11+ 语法 (类型提示必需)
- 异步优先: 使用 `async`/`await`

### 配置管理

- 使用 Pydantic Settings 定义配置
- 环境变量优先于默认值
- 配置文件: `anyclaw/.env`

### 技能开发

- 继承 `Skill` 基类
- 实现 `async execute(**kwargs) -> str` 方法
- 将技能放在 `anyclaw/anyclaw/skills/builtin/` 目录
- 每个技能目录包含 `skill.py` 文件

### Workspace 模板系统

AnyClaw 使用模板系统初始化工作区：

```bash
# 创建完整工作区 (~/.anyclaw/workspace)
anyclaw setup

# 在当前目录初始化项目级配置
anyclaw init
```

**工作区结构**:
```
~/.anyclaw/workspace/
├── SOUL.md       # Agent 人设
├── USER.md       # 用户档案
├── AGENTS.md     # Agent 指令
├── TOOLS.md      # 工具说明
├── HEARTBEAT.md  # 心跳任务
├── memory/       # 记忆存储
│   ├── MEMORY.md
│   └── HISTORY.md
└── skills/       # 自定义技能
```

**模板同步**:
- 模板文件位于 `anyclaw/templates/`
- 只创建缺失文件，不覆盖现有
- 通过 `sync_workspace_templates()` 函数实现

### 测试规范

- 单元测试与源代码并列
- 异步测试使用 `@pytest.mark.asyncio` 装饰器
- 目标覆盖率 >80%

## 重要提醒

1. **不要提交敏感信息**: API Key、凭证等应放在 `.env` 文件中
2. **保持依赖同步**: 修改依赖后更新 `pyproject.toml` 和 `poetry.lock`
3. **参考现有代码**: Nanobot 和 OpenClaw 包含大量可复用的模式
4. **异步优先**: Agent 处理、LLM 调用、技能执行都应使用异步
