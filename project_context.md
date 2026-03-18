# AnyClaw 项目上下文

## 项目概述

AnyClaw 是一个轻量级、可扩展的 AI 智能体框架，采用 Python 3.9+ 开发。项目提供完整的 Agent 系统、工具调用、技能系统和记忆管理能力。

## 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.9+ |
| 依赖管理 | Poetry |
| 配置管理 | Pydantic Settings |
| CLI 框架 | Typer + Rich |
| LLM 接口 | litellm |
| 测试框架 | pytest + pytest-asyncio |

## 核心模块

### Agent 系统 (`anyclaw/agent/`)
- `loop.py` - AgentLoop 主处理循环
- `context.py` - ContextBuilder 上下文构建
- `history.py` - ConversationHistory 对话历史

### Tools 系统 (`anyclaw/tools/`)
- `base.py` - Tool 抽象基类
- `registry.py` - ToolRegistry 工具注册
- `shell.py` - ExecTool 命令执行
- `filesystem.py` - 文件系统工具

### Skills 系统 (`anyclaw/skills/`)
- `base.py` - Skill 抽象基类
- `loader.py` - SkillLoader 动态加载
- `builtin/` - 内置技能 (echo, time, calc 等)

### Workspace 系统 (`anyclaw/workspace/`)
- `manager.py` - WorkspaceManager 工作区管理
- `templates.py` - 模板同步
- `bootstrap.py` - 引导系统

### Templates (`anyclaw/templates/`)
- `SOUL.md` - Agent 人设模板
- `USER.md` - 用户档案模板
- `AGENTS.md` - Agent 指令模板
- `TOOLS.md` - 工具说明模板
- `HEARTBEAT.md` - 心跳任务模板
- `memory/` - 记忆模板目录

## CLI 命令

```bash
# 核心命令
anyclaw chat              # 交互式聊天
anyclaw setup             # 初始化工作区
anyclaw init              # 项目级初始化
anyclaw config --show     # 查看配置

# 子命令
anyclaw onboard           # 配置向导
anyclaw token             # Token 管理
anyclaw persona           # 人设管理
anyclaw memory            # 记忆管理
anyclaw compress          # 上下文压缩
anyclaw workspace         # 工作区管理
```

## 工作区结构

```
~/.anyclaw/
├── workspace/            # 默认工作区
│   ├── SOUL.md
│   ├── USER.md
│   ├── AGENTS.md
│   ├── TOOLS.md
│   ├── HEARTBEAT.md
│   ├── memory/
│   │   ├── MEMORY.md
│   │   └── HISTORY.md
│   └── skills/
├── anyclaw.json          # 全局配置
└── credentials/          # 凭证存储

.project/.anyclaw/        # 项目级配置
└── (同 workspace 结构)
```

## 已完成特性 (16个)

1. MVP 核心特性 (5个)
   - feat-mvp-init - 项目初始化
   - feat-mvp-agent - Agent 引擎
   - feat-mvp-cli - CLI 频道
   - feat-mvp-skills - 技能系统
   - feat-mvp-integration - 集成测试

2. 扩展特性 (11个)
   - feat-tool-calling - Tool Calling
   - feat-zai-provider - ZAI Provider
   - feat-workspace-init - Workspace 初始化
   - feat-workspace-templates - 模板系统
   - feat-token-counter - Token 计数
   - feat-agent-persona - 人设系统
   - feat-context-compression - 上下文压缩
   - feat-memory-system - 记忆系统
   - feat-builtin-skills-v2 - 技能扩展
   - feat-bundled-skills - 内置技能
   - feat-streaming-output - 流式输出

## 开发规范

1. **代码风格**: Black (line-length=100), Ruff (E,F,I,N,W)
2. **类型提示**: 必需
3. **异步优先**: 使用 async/await
4. **配置管理**: Pydantic Settings + 环境变量

## 快速启动

```bash
cd anyclaw
pip install pydantic pydantic-settings typer rich litellm openai
cp .env.example .env
# 编辑 .env 设置 API Key
python3 -m anyclaw setup
python3 -m anyclaw chat
```

## 最近更新

### 2026-03-18
- 完成 feat-workspace-templates: Workspace 模板系统增强
  - 创建完整的模板文件结构
  - 实现 sync_workspace_templates() 函数
  - 添加 `anyclaw init` 命令
  - 更新 pyproject.toml 打包配置
