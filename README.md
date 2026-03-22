# AnyClaw 🐾

**AnyClaw** 是一个轻量级、可扩展的 AI 智能体框架，融合了 nanobot 和 OpenClaw 的核心优势。

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 核心特性

### 基础功能
- 🚀 **开箱即用** - 一行命令启动 AI 助手
- 🔧 **Tool Calling** - 支持 OpenAI Function Calling
- 🎯 **多 Provider** - 支持 OpenAI、Anthropic、ZAI/GLM 等
- 💾 **记忆系统** - 长期记忆和上下文管理
- 🎭 **人设系统** - 自定义 Agent 性格和行为
- 📦 **技能系统** - 可扩展的技能框架，支持渐进式加载
- 🌊 **流式输出** - 实时响应流
- 🔌 **MCP 协议** - 连接 MCP Server 生态
- 🔍 **智能文件搜索** - 启发式优先级、上下文关联、动态授权

### 高级功能
- 👥 **Multi-Agent 系统** - 多 Agent 管理、Identity 人设、独立 Workspace
- 📋 **SessionManager** - 会话持久化、归档、工具调用边界检测
- 🤖 **SubAgent** - 后台异步任务执行 (SpawnTool)
- 💬 **MessageTool** - 跨会话消息发送
- ⏰ **Cron** - 定时任务调度 (at/every/cron)
- 💬 **IM 集成** - 飞书、Discord 完整支持
- 🖥️ **桌面应用** - Tauri 跨平台 GUI

### 安全功能
- 🛡️ **SSRF 防护** - 网络请求安全保护
- 🔐 **路径防护** - 路径遍历攻击防护 (PathGuard)
- 🧹 **输入净化** - 输入验证和净化 (Input Sanitizer)
- 🔑 **凭证管理** - 安全凭证存储和日志脱敏 (Credential Vault)
- ⚙️ **安全配置** - 灵活的安全策略配置 (allow_all_access, extra_allowed_dirs)

## 项目状态

- **完成特性**: 42 个
- **测试数量**: 588 个
- **测试状态**: ✅ 全部通过

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
# 方式1: 使用配置文件
anyclaw config init
anyclaw config set zai.api_key your-key
anyclaw config set llm.model glm-4.7

# 方式2: 使用环境变量
export ZAI_API_KEY=your-key
export LLM_MODEL=zai/glm-4.7

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
| `anyclaw serve` | 多通道服务模式 |
| `anyclaw serve --daemon` | 后台守护进程 |
| `anyclaw serve --status` | 查看服务状态 |
| `anyclaw serve --stop` | 停止后台服务 |
| `anyclaw serve --logs` | 查看服务日志 |
| `anyclaw setup` | 初始化工作区 |
| `anyclaw init` | 在当前目录初始化配置 |
| `anyclaw config init` | 初始化配置文件 |
| `anyclaw config show` | 显示当前配置 |
| `anyclaw config set <key> <value>` | 设置配置项 |
| `anyclaw config path` | 显示配置文件路径 |
| `anyclaw config edit` | 编辑配置文件 |
| `anyclaw onboard` | 配置向导 |
| `anyclaw providers` | 列出可用 Provider |
| `anyclaw skill create <name>` | 创建新技能 |
| `anyclaw skill validate <path>` | 验证技能 |
| `anyclaw skill package <path>` | 打包技能 |
| `anyclaw skill list` | 列出所有技能 |
| `anyclaw skill reload [name]` | 热重载技能 |
| `anyclaw mcp list` | 列出 MCP 服务器 |
| `anyclaw mcp test <name>` | 测试 MCP 连接 |
| `anyclaw agent list` | 列出所有 Agent |
| `anyclaw agent create <name>` | 创建新 Agent |
| `anyclaw agent switch <name>` | 切换 Agent |
| `anyclaw token status` | Token 使用状态 |
| `anyclaw memory show` | 显示记忆内容 |
| `anyclaw compress status` | 上下文压缩状态 |
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
| ZAI/GLM | `zai/*` 或 `glm-*` | GLM-4.7, GLM-5 等，默认使用 Coding Plan |
| 自定义 | - | OpenAI 兼容 API |

### ZAI/GLM 配置

```bash
# 使用配置文件
anyclaw config init
anyclaw config set zai.api_key your-key
anyclaw config set llm.model glm-4.7

# 或使用环境变量
export ZAI_API_KEY=your-key
export LLM_MODEL=zai/glm-4.7
```

## MCP 集成

AnyClaw 支持 MCP (Model Context Protocol) 协议，可以连接外部工具服务器：

```yaml
# ~/.anyclaw/mcp_servers.yaml
servers:
  filesystem:
    transport: stdio
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/files"]
    enabled_tools:
      - read_file
      - write_file
```

```bash
# 管理 MCP 服务器
anyclaw mcp list
anyclaw mcp test filesystem
```

## IM Channel 支持

支持多种即时通讯平台：

- **飞书 (Feishu)**: Webhook + REST API
- **Discord**: Gateway + Rate Limit

## 多通道服务模式

同时运行多个 IM 通道：

```bash
# 前台运行所有启用的通道
anyclaw serve

# 调试模式 (详细日志)
anyclaw serve --debug

# 后台守护进程
anyclaw serve --daemon

# 查看服务状态
anyclaw serve --status

# 停止服务
anyclaw serve --stop

# 查看日志
anyclaw serve --logs
```

日志文件位置: `~/.anyclaw/logs/serve.log`

## 桌面应用

AnyClaw 提供 Tauri 跨平台桌面应用：

```bash
cd tauri-app

# 安装依赖
npm install

# 开发模式
npm run tauri:dev

# 构建生产版本
npm run tauri:build
```

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
├── agents/       # Multi-Agent 系统
├── session/      # 会话管理
├── cron/         # 定时任务
├── tools/        # 工具系统 (Tool Calling)
├── skills/       # 技能系统
├── channels/     # 交互频道 (CLI, Feishu, Discord)
├── api/          # FastAPI 服务端
├── mcp/          # MCP 客户端
├── security/     # 安全模块 (SSRF, PathGuard, Sanitizer, Credentials)
├── workspace/    # 工作区管理
├── memory/       # 记忆系统
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
- [x] MCP 协议集成
- [x] IM Channel 支持 (飞书 + Discord)
- [x] Skill 工具链
- [x] 多通道服务模式 (Serve Mode)
- [x] SessionManager 会话管理
- [x] SubAgent 后台任务
- [x] MessageTool 跨会话消息
- [x] Cron 定时任务
- [x] Multi-Agent 系统
- [x] 安全模块 (SSRF/PathGuard/Sanitizer/Credentials)
- [x] Tauri 桌面应用
- [ ] Web UI
- [ ] 插件系统

## 许可证

[MIT License](LICENSE)

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**AnyClaw** - 你的 AI 助手，由你定义 🐾
