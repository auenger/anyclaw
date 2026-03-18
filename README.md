# AnyClaw 🐾

**AnyClaw** 是一个轻量级、可扩展的 AI 智能体框架，让你可以快速构建自己的 AI 助手。

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 特性

- 🚀 **开箱即用** - 一行命令启动 AI 助手
- 🔧 **Tool Calling** - 支持 OpenAI Function Calling
- 🎯 **多 Provider** - 支持 OpenAI、Anthropic、ZAI/GLM 等
- 💾 **记忆系统** - 长期记忆和上下文管理
- 🎭 **人设系统** - 自定义 Agent 性格和行为
- 📦 **技能系统** - 可扩展的技能框架
- 🌊 **流式输出** - 实时响应流

## 快速开始

### 安装

```bash
# 使用 pip
pip install anyclaw

# 或从源码安装
git clone https://github.com/anyclaw/anyclaw.git
cd anyclaw/anyclaw
pip install -e .
```

### 配置

```bash
# 设置 API Key
export OPENAI_API_KEY=your-key
# 或使用 ZAI/GLM
export ZAI_API_KEY=your-key
export ZAI_ENDPOINT=coding-global

# 初始化工作区
anyclaw setup
```

### 使用

```bash
# 启动交互式聊天
anyclaw chat

# 使用特定模型
anyclaw chat --model gpt-4o

# 流式输出
anyclaw chat --stream
```

## CLI 命令

| 命令 | 说明 |
|------|------|
| `anyclaw chat` | 启动交互式聊天 |
| `anyclaw setup` | 初始化工作区 |
| `anyclaw init` | 在当前目录初始化配置 |
| `anyclaw config` | 查看配置 |
| `anyclaw onboard` | 配置向导 |
| `anyclaw providers` | 列出可用 Provider |
| `anyclaw version` | 显示版本 |

## 工作区结构

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

## 支持的 Provider

| Provider | 模型前缀 | 说明 |
|----------|----------|------|
| OpenAI | `gpt-*` / `openai/*` | GPT-4, GPT-3.5 等 |
| Anthropic | `claude-*` / `anthropic/*` | Claude 3 系列 |
| ZAI/GLM | `zai/*` | GLM-4, GLM-5 等 |
| 自定义 | - | OpenAI 兼容 API |

## 开发

### 环境设置

```bash
cd anyclaw
pip install poetry
poetry install
```

### 运行测试

```bash
poetry run pytest tests/ -v
```

### 代码检查

```bash
poetry run black anyclaw/
poetry run ruff check anyclaw/
```

## 架构

```
anyclaw/
├── agent/        # Agent 核心引擎
├── tools/        # 工具系统 (Tool Calling)
├── skills/       # 技能系统
├── channels/     # 交互频道 (CLI, etc.)
├── workspace/    # 工作区管理
├── templates/    # 模板文件
├── providers/    # LLM Provider
├── config/       # 配置系统
└── cli/          # CLI 应用
```

## 路线图

- [x] MVP 核心功能
- [x] Tool Calling 支持
- [x] 多 Provider 支持
- [x] 记忆系统
- [x] 流式输出
- [ ] Web UI
- [ ] 插件系统
- [ ] 多 Agent 协作

## 许可证

[MIT License](LICENSE)

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**AnyClaw** - 你的 AI 助手，由你定义 🐾
