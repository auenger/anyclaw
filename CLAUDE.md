# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

AnyClaw 是一个轻量级、可扩展的 AI 智能体框架，融合了 nanobot 和 OpenClaw 的核心优势。项目采用 Python 3.11+ 开发，使用 Poetry 管理依赖，同时提供 Tauri 跨平台桌面应用。

**项目状态**: 77 个特性完成，1094+ 个测试通过 ✅

### 核心特性

**基础功能**
- ✅ **Tool Calling** - OpenAI Function Calling 支持
- ✅ **多 Provider** - OpenAI、Anthropic、ZAI/GLM 等
- ✅ **记忆系统** - 长期记忆和上下文管理
- ✅ **技能系统** - 可扩展的技能框架，渐进式加载
- ✅ **MCP 协议** - 连接 MCP Server 生态
- ✅ **智能文件搜索** - 启发式优先级、上下文关联、动态授权

**nanobot 兼容**
- ✅ **SessionManager** - 会话持久化、归档、工具调用边界检测
- ✅ **SubAgent** - 后台异步任务执行 (SpawnTool)
- ✅ **MessageTool** - 跨会话消息发送
- ✅ **Cron** - 定时任务调度 (at/every/cron)
- ✅ **Channel 集成** - CLI、Discord、飞书

**OpenClaw 兼容**
- ✅ **Multi-Agent 系统** - 多 Agent 管理、Identity 人设、独立 Workspace

**桌面应用**
- ✅ **Tauri 桌面应用** - 跨平台 GUI (Phase 1-4 完成)
- ✅ **配置编辑器** - 桌面端配置编辑和服务控制
- ✅ **日志查看** - 会话和系统日志查看
- ✅ **任务管理** - Tasks 定时任务管理页面
- ✅ **Provider 配置** - Provider 配置面板

**安全功能**
- ✅ **SSRF 防护** - 网络请求安全保护
- ✅ **路径防护** - 路径遍历攻击防护 (PathGuard)
- ✅ **输入净化** - 输入验证和净化 (Input Sanitizer)
- ✅ **凭证管理** - 安全凭证存储和日志脱敏 (Credential Vault)
- ✅ **安全配置增强** - 灵活的安全策略配置 (allow_all_access, extra_allowed_dirs)

**高级功能**
- ✅ **会话并发** - 会话级并发消息处理
- ✅ **Cron API** - 完整的 Cron 管理 REST API
- ✅ **Cron 弹性** - 退避、卡住检测、日志
- ✅ **日志持久化** - 文件持久化、按日期查看、自动清理

**ACP 协议 (规划中)**
- 📋 **ACP Server** - 被 IDE (Zed/JetBrains) 连接，作为 ACP Agent
- 📋 **ACP Client** - 连接外部 Agent (Claude Code/Gemini CLI)
- 📋 **ACP-MCP 桥接** - 通过 MCP 调用外部 ACP Agent 作为工具

## 技术栈

### 后端 (Python)

- **语言**: Python 3.11+ (内置 tomllib)
- **依赖管理**: Poetry
- **核心依赖**:
  - `pydantic` >= 2.12.0 (数据验证)
  - `pydantic-settings` >= 2.0.0 (配置管理)
  - `typer[all]` >= 0.20.0 (CLI 框架)
  - `rich` >= 14.0.0 (终端美化)
  - `litellm` >= 1.82.1 (LLM 统一接口)
  - `openai` >= 1.0.0 (OpenAI SDK)
  - `fastapi` >= 0.115.0 (API 服务器)
  - `uvicorn` >= 0.32.0 (ASGI 服务器)
  - `sse-starlette` >= 2.1.0 (SSE 流式)
- **测试框架**: pytest >= 8.0.0, pytest-asyncio >= 0.23.0
- **代码质量**: Black (格式化), Ruff (检查)

### 桌面应用 (Tauri + React)

- **框架**: Tauri 2.0 (Rust Shell)
- **前端**: React 18 + Vite + TypeScript
- **样式**: Tailwind CSS + shadcn/ui
- **API**: FastAPI + SSE (13 个端点)
- **状态**: Phase 1-3 完成

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
│   │   ├── history.py         # 对话历史
│   │   ├── tool_loop.py       # 工具调用循环
│   │   ├── subagent.py        # SubAgent 管理器
│   │   └── tools/             # Agent 工具
│   │       ├── message.py     # MessageTool
│   │       └── spawn.py       # SpawnTool
│   ├── agents/                # Multi-Agent 系统
│   │   ├── manager.py         # AgentManager
│   │   ├── identity.py        # IdentityManager
│   │   └── cli/               # Agent CLI 命令
│   ├── session/               # 会话管理
│   │   ├── manager.py         # SessionManager
│   │   ├── archive.py         # SessionArchiver
│   │   └── models.py          # 会话模型
│   ├── cron/                  # 定时任务
│   │   ├── service.py         # CronService
│   │   ├── tool.py            # CronTool
│   │   └── types.py           # Cron 类型
│   ├── tools/                 # 工具系统
│   │   ├── base.py            # 工具基类
│   │   ├── registry.py        # 工具注册表
│   │   ├── shell.py           # Shell 执行工具
│   │   ├── filesystem.py      # 文件系统工具
│   │   ├── message.py         # MessageTool
│   │   └── cron.py            # Cron 定时任务
│   ├── channels/              # 频道系统
│   │   ├── cli.py             # CLI 频道
│   │   ├── base.py            # 频道基类
│   │   ├── feishu.py          # 飞书 Channel
│   │   ├── discord.py         # Discord Channel
│   │   ├── manager.py         # ChannelManager
│   │   └── bus.py             # 消息路由
│   ├── api/                   # API 服务
│   │   ├── server.py          # FastAPI 服务器
│   │   ├── sse.py             # SSE 流式端点
│   │   ├── deps.py            # 依赖注入
│   │   └── routes/            # API 路由
│   │       ├── health.py      # 健康检查
│   │       ├── agents.py      # Agent 管理
│   │       ├── messages.py    # 消息处理
│   │       ├── skills.py      # 技能管理
│   │       └── tasks.py       # 任务管理
│   ├── acp/                   # ACP 协议 (规划中)
│   ├── mcp/                   # MCP 客户端
│   │   ├── client.py          # MCP 连接管理
│   │   ├── wrapper.py         # MCPToolWrapper
│   │   └── config.py          # MCP 配置
│   ├── skills/                # 技能系统
│   │   ├── base.py            # 技能基类
│   │   ├── loader.py          # 技能加载器 (动态+渐进式)
│   │   ├── executor.py        # 脚本执行器
│   │   ├── toolkit.py         # 技能工具链
│   │   ├── conversation.py    # 技能对话模式
│   │   ├── models.py          # 数据模型
│   │   ├── parser.py          # SKILL.md 解析
│   │   └── builtin/           # 内置技能 (17 个)
│   ├── security/              # 安全模块
│   │   ├── network.py         # SSRF 防护
│   │   ├── path_guard.py      # 路径遍历防护
│   │   ├── sanitizer.py       # 输入净化
│   │   └── credentials.py     # 凭证管理
│   ├── core/                  # 核心服务
│   │   ├── serve.py           # 多通道服务管理
│   │   └── daemon.py          # 守护进程管理
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
│   │   ├── bootstrap.py       # 引导系统
│   │   └── restrict.py        # 写入限制
│   ├── memory/                # 记忆系统
│   │   ├── manager.py         # 记忆管理器
│   │   └── automation.py      # 记忆自动化
│   ├── providers/             # LLM Provider
│   │   ├── zai.py             # ZAI/GLM Provider
│   │   └── zai_detect.py      # Endpoint 检测
│   ├── utils/                 # 工具模块
│   │   └── logging_config.py  # 日志配置
│   ├── config/                # 配置系统 (40+ 字段)
│   │   ├── settings.py        # Pydantic Settings
│   │   ├── loader.py          # TOML/JSON 加载器
│   │   └── config.template.toml  # 配置模板
│   └── cli/                   # CLI 应用
│       ├── app.py             # Typer 应用
│       ├── serve_cmd.py       # serve 命令
│       └── sidecar_cmd.py     # sidecar 命令
├── tauri-app/                 # Tauri 桌面应用
│   ├── src/                   # React 前端
│   │   ├── App.tsx            # 主应用
│   │   ├── components/        # UI 组件
│   │   └── index.css          # Tailwind 样式
│   ├── src-tauri/             # Rust 后端
│   │   ├── src/lib.rs         # Shell 实现
│   │   └── tauri.conf.json    # Tauri 配置
│   ├── package.json           # npm 依赖
│   └── vite.config.ts         # Vite 配置
├── tests/                     # 测试目录 (965 个测试)
├── docs/                      # 文档目录
├── features/                  # Feature 归档 (60 个特性)
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
    ├── 加载 SOUL.md / USER.md / AGENTS.md
    ├── 加载 Skills Summary
    ├── 加载 Always Skills
    └── 智能压缩 (如需要)
    ↓
调用 LLM (litellm acompletion)
    ↓
处理 Tool Calls (如有)
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
# ZAI_API_KEY=your-zai-key
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

# 技能管理
poetry run python -m anyclaw skill create my-skill
poetry run python -m anyclaw skill validate ./my-skill
poetry run python -m anyclaw skill list
poetry run python -m anyclaw skill reload

# MCP 管理
poetry run python -m anyclaw mcp list
poetry run python -m anyclaw mcp test filesystem

# 多通道服务模式
poetry run python -m anyclaw serve              # 前台运行
poetry run python -m anyclaw serve --debug      # 调试模式
poetry run python -m anyclaw serve --daemon     # 后台守护进程
poetry run python -m anyclaw serve --status     # 查看状态
poetry run python -m anyclaw serve --stop       # 停止服务
poetry run python -m anyclaw serve --logs       # 查看日志

# API Sidecar 模式 (供桌面应用调用)
poetry run python -m anyclaw sidecar --port 62601
poetry run python -m anyclaw sidecar --help

# Agent 管理 (Multi-Agent)
poetry run python -m anyclaw agent list
poetry run python -m anyclaw agent create <name>
poetry run python -m anyclaw agent switch <name>

# ACP 协议 (被 IDE 连接)
poetry run python -m anyclaw acp serve              # 启动 ACP Server
poetry run python -m anyclaw acp serve --cwd /path  # 指定工作目录
poetry run python -m anyclaw acp list               # 列出 ACP Agent
poetry run python -m anyclaw acp add <name>         # 添加 ACP Agent
poetry run python -m anyclaw acp test <name>        # 测试 ACP Agent
```

### 桌面应用开发

```bash
cd tauri-app

# 安装依赖
npm install

# 开发模式
npm run tauri:dev

# 构建生产版本
npm run tauri:build
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
poetry run pytest tests/test_skill_loader.py -v
poetry run pytest tests/test_security.py -v
poetry run pytest tests/test_session.py -v
poetry run pytest tests/test_subagent.py -v
poetry run pytest tests/test_cron.py -v

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

## 开发规范

### 代码风格

- 使用 Black 格式化 (line-length=100)
- 使用 Ruff 检查 (E, F, I, N, W 规则)
- Python 3.11+ 语法 (类型提示必需)
- 异步优先: 使用 `async`/`await`

### 配置管理

配置优先级：环境变量 > 配置文件 > 默认值

**配置文件位置**: `~/.anyclaw/config.json`

```bash
# 初始化配置
anyclaw config init

# 设置 API Key
anyclaw config set zai.api_key your-key

# 设置模型
anyclaw config set llm.model glm-4.7

# 查看配置
anyclaw config show
```

**配置文件格式**:
```json
{
  "llm": {
    "model": "glm-4.7",
    "provider": "zai"
  },
  "providers": {
    "zai": {
      "api_key": "your-key"
    }
  }
}
```

### 技能开发

- 继承 `Skill` 基类
- 实现 `async execute(**kwargs) -> str` 方法
- 将技能放在 `anyclaw/anyclaw/skills/builtin/` 目录
- 每个技能目录包含 `skill.py` 文件
- 支持 SKILL.md 格式 (frontmatter + body)

### 技能渐进式加载

- `build_skills_summary()` - 生成 XML 格式技能摘要
- `load_skills_for_context()` - 按需加载技能内容
- `get_always_skills()` - 获取自动加载的技能
- `_check_requirements()` - 检查 bins/env 依赖

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

### Workspace 安全限制

- `restrict_to_workspace` 配置项（默认启用）
- PathGuard 路径验证
- 符号链接解析防绕过
- `allow_all_access` 快捷开关（开发/测试环境）
- `extra_allowed_dirs` 额外允许的目录配置

### 测试规范

- 单元测试与源代码并列
- 异步测试使用 `@pytest.mark.asyncio` 装饰器
- 目标覆盖率 >80%

## 重要提醒

1. **不要提交敏感信息**: API Key、凭证等应放在配置文件或环境变量中
2. **保持依赖同步**: 修改依赖后更新 `pyproject.toml` 和 `poetry.lock`
3. **异步优先**: Agent 处理、LLM 调用、技能执行都应使用异步
4. **配置优先级**: 环境变量 > 配置文件 > 默认值
5. **安全第一**: 使用 PathGuard 验证路径，使用 CredentialVault 保护凭证
