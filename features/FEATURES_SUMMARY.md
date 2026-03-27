# AnyClaw 特性总结

## 项目状态

**整体进度**: ████████████████████████ **100%** MVP + 扩展特性完成

**最后更新**: 2026-03-27

**测试状态**: 1094+ 个测试通过 ✅

**完成特性数**: 77

## 特性列表

### MVP 核心特性

| 特性 ID | 名称 | 状态 | 完成度 | 优先级 |
|---------|------|------|--------|--------|
| feat-mvp-init | 项目初始化和配置系统 | ✅ completed | 95% | 90 |
| feat-mvp-agent | Agent 引擎核心 | ✅ completed | 95% | 95 |
| feat-mvp-cli | CLI 交互频道 | ✅ completed | 95% | 90 |
| feat-mvp-skills | 技能系统 | ✅ completed | 90% | 85 |
| feat-mvp-integration | 应用集成和测试 | ✅ completed | 85% | 80 |

### nanobot 兼容特性

| 特性 ID | 名称 | 状态 | 完成度 | 优先级 |
|---------|------|------|--------|--------|
| feat-session-manager | SessionManager 会话管理 | ✅ completed | 95% | 85 |
| feat-session-archive | 会话归档系统 | ✅ completed | 95% | 80 |
| feat-subagent | SubAgent 后台任务 | ✅ completed | 95% | 80 |
| feat-message-tool | MessageTool 跨会话消息 | ✅ completed | 95% | 75 |
| feat-cron | Cron 定时任务调度 | ✅ completed | 95% | 70 |

### OpenClaw 兼容特性

| 特性 ID | 名称 | 状态 | 完成度 | 优先级 |
|---------|------|------|--------|--------|
| feat-multi-agent | Multi-Agent 系统 | ✅ completed | 95% | 90 |

### 桌面应用

| 特性 ID | 名称 | 状态 | 完成度 | 优先级 |
|---------|------|------|--------|--------|
| feat-desktop-app | Tauri 桌面应用 (Phase 1-2) | ✅ completed | 80% | 75 |
| feat-desktop-app-phase3 | Tauri 桌面应用 Phase 3 | ✅ completed | 95% | 75 |
| feat-agents-ui | Agent 管理页面 | ✅ completed | 95% | 75 |
| feat-models-panel | Provider 配置面板 | ✅ completed | 95% | 75 |
| feat-tasks-ui | Tasks 定时任务页面 | ✅ completed | 95% | 75 |
| feat-logs-pages | Logs 日志查看页面 | ✅ completed | 95% | 70 |
| feat-memory-pages | Memory 记忆页面 | ✅ completed | 95% | 70 |
| feat-config-editor | 配置编辑器 | ✅ completed | 95% | 80 |
| feat-app-bundle | 应用打包 | ✅ completed | 95% | 70 |
| feat-chat-agent-selector | Chat Agent 选择器 | ✅ completed | 95% | 82 |
| feat-logs-page-refactor | Logs 页面重构 | ✅ completed | 95% | 75 |

### 基础设施与修复

| 特性 ID | 名称 | 状态 | 完成度 | 优先级 |
|---------|------|------|--------|--------|
| feat-config-consistency | 配置系统一致性修复 | ✅ completed | 95% | 75 |
| feat-chat-history-bug | 对话历史持久化 Bug 修复 | ✅ completed | 95% | 90 |
| feat-agent-session-workspace | Agent Session 存储位置修复 | ✅ completed | 95% | 90 |
| feat-log-persistence | 日志文件持久化 | ✅ completed | 95% | 70 |

### 安全特性

| 特性 ID | 名称 | 状态 | 完成度 | 优先级 |
|---------|------|------|--------|--------|
| feat-ssrf-guard | SSRF 防护 | ✅ completed | 95% | 80 |
| feat-exec-security | 执行安全 | ✅ completed | 95% | 80 |
| feat-path-guard | 路径遍历防护 | ✅ completed | 95% | 80 |
| feat-input-sanitizer | 输入验证和净化 | ✅ completed | 95% | 80 |
| feat-credential-vault | 凭证安全管理 | ✅ completed | 95% | 85 |
| feat-security-config-enhancement | 安全配置增强 | ✅ completed | 95% | 80 |

### 技能系统

| 特性 ID | 名称 | 状态 | 完成度 | 优先级 |
|---------|------|------|--------|--------|
| feat-bundled-skills | 内置技能包 | ✅ completed | 95% | 85 |
| feat-builtin-skills-v2 | 内置技能扩展 V2 | ✅ completed | 95% | 78 |
| feat-skill-toolkit | 技能工具链 | ✅ completed | 95% | 80 |
| feat-skill-dynamic-loader | 技能动态加载 | ✅ completed | 95% | 80 |
| feat-skill-progressive-loading | 技能渐进式加载 | ✅ completed | 95% | 80 |
| feat-skill-conversation-mode | 技能对话模式 | ✅ completed | 95% | 75 |

### 扩展特性

| 特性 ID | 名称 | 状态 | 完成度 | 优先级 |
|---------|------|------|--------|--------|
| feat-smart-file-search | 智能文件搜索 | ✅ completed | 95% | 75 |
| feat-serve-mode | 多通道服务模式 | ✅ completed | 95% | 80 |
| feat-im-channels | IM Channel (飞书+Discord) | ✅ completed | 95% | 65 |
| feat-tool-calling | Tool Calling 核心框架 | ✅ completed | 95% | 95 |
| feat-zai-provider | ZAI/GLM CodePlan Provider | ✅ completed | 95% | 90 |
| feat-toml-config | TOML 配置支持 | ✅ completed | 95% | 85 |
| feat-workspace-init | Workspace 初始化和引导 | ✅ completed | 90% | 88 |
| feat-workspace-templates | Workspace 模板系统增强 | ✅ completed | 95% | 85 |
| feat-workspace-restrict | Workspace 写入限制 | ✅ completed | 95% | 80 |
| feat-token-counter | Token 计数与限制 | ✅ completed | 90% | 85 |
| feat-agent-persona | 智能体人设系统 | ✅ completed | 90% | 82 |
| feat-context-compression | 智能上下文压缩 | ✅ completed | 90% | 80 |
| feat-memory-system | 记忆系统 | ✅ completed | 90% | 78 |
| feat-streaming-output | 流式输出支持 | ✅ completed | 90% | 76 |
| feat-config-and-memory | 配置与记忆集成 | ✅ completed | 95% | 80 |
| feat-mcp-client | MCP 客户端 | ✅ completed | 95% | 75 |

### ACP 协议 (规划中)

| 特性 ID | 名称 | 状态 | 大小 | 优先级 |
|---------|------|------|------|--------|
| feat-acp-server | ACP Server - 被 IDE 连接 | pending | L | 80 |
| feat-acp-client | ACP Client - 连接外部 Agent | pending | L | 75 |
| feat-acp-mcp-bridge | ACP-MCP 桥接 | pending | S | 70 |

## 特性依赖关系

```
feat-mvp-init (初始化) ✅
    ├─→ feat-mvp-agent (Agent 核心) ✅
    │       ├─→ feat-mvp-skills (技能系统) ✅
    │       │       ├─→ feat-bundled-skills (内置技能) ✅
    │       │       ├─→ feat-skill-toolkit (工具链) ✅
    │       │       ├─→ feat-skill-dynamic-loader (动态加载) ✅
    │       │       ├─→ feat-skill-progressive-loading (渐进式加载) ✅
    │       │       └─→ feat-builtin-skills-v2 (技能扩展) ✅
    │       ├─→ feat-tool-calling (Tool Calling) ✅
    │       │       └─→ feat-zai-provider (ZAI Provider) ✅
    │       ├─→ feat-token-counter (Token 计数) ✅
    │       │       └─→ feat-context-compression (上下文压缩) ✅
    │       └─→ feat-streaming-output (流式输出) ✅
    ├─→ feat-mvp-cli (CLI 频道) ✅
    │       ├─→ feat-streaming-output (流式输出) ✅
    │       └─→ feat-serve-mode (多通道服务) ✅
    │               └─→ feat-im-channels (IM 频道) ✅
    ├─→ feat-workspace-init (Workspace 初始化) ✅
    │       ├─→ feat-workspace-templates (模板系统) ✅
    │       ├─→ feat-workspace-restrict (写入限制) ✅
    │       ├─→ feat-agent-persona (人设系统) ✅
    │       └─→ feat-memory-system (记忆系统) ✅
    └─→ feat-mvp-integration (集成测试) ✅
```

## 已实现功能

### 核心功能
- ✅ Pydantic Settings 配置系统 (35+ 配置字段)
- ✅ TOML/JSON 配置文件支持
- ✅ AgentLoop 主处理循环（同步 + 流式）
- ✅ ConversationHistory 对话历史管理
- ✅ ContextBuilder 上下文构建
- ✅ litellm 集成 (支持多种 LLM)
- ✅ 异步处理支持
- ✅ Tool Calling 支持
- ✅ ZAI/GLM Provider 支持
- ✅ 流式输出支持

### CLI 功能
- ✅ `anyclaw chat` - 交互式聊天（支持 --stream/--no-stream）
- ✅ `anyclaw serve` - 多通道服务模式
- ✅ `anyclaw serve --daemon` - 后台守护进程
- ✅ `anyclaw serve --status` - 查看服务状态
- ✅ `anyclaw serve --stop` - 停止服务
- ✅ `anyclaw serve --logs` - 查看日志
- ✅ `anyclaw config --show` - 查看配置
- ✅ `anyclaw config show --provider zai` - 查看 ZAI 配置
- ✅ `anyclaw onboard` - 配置向导
- ✅ `anyclaw onboard --list-auth-choices` - 列出认证选项
- ✅ `anyclaw onboard detect-zai` - 自动检测 ZAI endpoint
- ✅ `anyclaw providers` - 列出可用 providers
- ✅ `anyclaw version` - 显示版本
- ✅ `anyclaw setup` - 初始化工作区
- ✅ `anyclaw token` - Token 管理
- ✅ `anyclaw persona` - 人设管理
- ✅ `anyclaw compress` - 上下文压缩
- ✅ `anyclaw memory` - 记忆管理
- ✅ 特殊命令 (exit, quit, clear)
- ✅ Rich 美化输出

### Provider 系统
- ✅ Provider 抽象基类
- ✅ ZAIProvider 实现
- ✅ 4 种 endpoint 支持 (coding-global, coding-cn, global, cn)
- ✅ 自动 endpoint 检测
- ✅ 模型前缀路由 (zai/glm-5, gpt-*, claude-*)

### 技能系统
- ✅ Skill 抽象基类
- ✅ SkillLoader 动态加载
- ✅ 渐进式技能加载
- ✅ 技能工具链
- ✅ 技能对话模式
- ✅ Tool Calling 集成

#### 内置技能（17 个）

| 技能 | 功能 |
|------|------|
| `echo` | 回显输入消息 |
| `time` | 获取当前时间 |
| `calc` | 数学计算 |
| `file` | 文件操作 |
| `http` | HTTP 请求 |
| `weather` | 天气查询 |
| `code_exec` | 代码执行 |
| `process` | 进程管理 |
| `text` | 文本处理 |
| `system` | 系统信息 |
| `data` | 数据处理 |
| `cron` | 定时任务调度 |
| `skill-creator` | 技能创建与管理 |
| `docx` | Word 文档处理 |
| `pdf` | PDF 文档处理 |
| `xlsx` | Excel 电子表格处理 |
| `pptx` | PowerPoint 演示文稿处理 |

### 安全功能
- ✅ SSRF 防护 (网络请求安全)
- ✅ 路径遍历防护 (PathGuard)
- ✅ 输入验证和净化
- ✅ 执行安全控制
- ✅ 凭证安全管理 (加密存储、日志脱敏)
- ✅ 安全配置增强 (allow_all_access, extra_allowed_dirs)

### 会话管理
- ✅ SessionManager 会话持久化
- ✅ 会话归档系统
- ✅ 工具调用边界检测
- ✅ 跨会话消息发送 (MessageTool)
- ✅ SubAgent 后台任务执行
- ✅ Cron 定时任务调度 (完整 5 字段 cron)
- ✅ 会话级并发消息处理
- ✅ Cron API REST 端点

### Multi-Agent 系统
- ✅ 多 Agent 管理
- ✅ Identity 人设管理
- ✅ 独立 Workspace
- ✅ Agent CLI 命令

### 桌面应用 (Tauri)
- ✅ Phase 1: 基础架构 (FastAPI + SSE)
- ✅ Phase 2: 核心功能 (会话、消息、Agent 管理)
- ✅ Phase 3: 完整 UI (聊天界面、Agent 切换、设置面板)
- ✅ Phase 4: 高级功能 (Agent API、Cron API、日志、配置编辑器)
- ✅ Provider 配置面板
- ✅ Tasks 定时任务管理页面
- ✅ Logs 日志查看页面
- ✅ Memory 记忆管理页面
- ✅ 配置编辑器和服务控制
- ✅ 应用打包支持
- ✅ Chat Agent 选择器
- ✅ Logs 页面重构

### 基础设施
- ✅ 配置系统一致性修复 (Python/Tauri)
- ✅ 对话历史持久化 Bug 修复
- ✅ Agent Session 存储位置修复
- ✅ 日志文件持久化 (后台线程、JSONL、自动清理)

### 记忆系统
- ✅ 长期记忆 (MEMORY.md)
- ✅ 每日日志 (YYYY-MM-DD.md)
- ✅ 记忆自动化（偏好、笔记、决策识别）
- ✅ 记忆搜索和导出

### ACP 协议 (规划中)
- 📋 ACP Server — 被 IDE (Zed/JetBrains/VS Code) 连接
- 📋 ACP Client — 连接 Claude Code、Gemini CLI 等外部 Agent
- 📋 ACP-MCP 桥接 — 通过 MCP 调用外部 ACP Agent
- 📋 详见 `docs/ACP_PROTOCOL_ANALYSIS.md`

### 人设系统
- ✅ 多人设支持
- ✅ 人设切换
- ✅ 人设模板

### 流式输出
- ✅ AgentLoop.process_stream() async generator
- ✅ CLIChannel.run_stream() 流式显示
- ✅ --stream/--no-stream CLI 选项
- ✅ 流式中断支持 (Ctrl+C)

### 测试覆盖
- ✅ 1094 个测试全部通过
- ✅ test_config.py
- ✅ test_agent.py
- ✅ test_skills.py
- ✅ test_skills_extended.py
- ✅ test_streaming.py
- ✅ test_memory.py
- ✅ test_zai_provider.py
- ✅ test_zai_detect.py
- ✅ test_onboard.py
- ✅ test_security.py
- ✅ test_session.py
- ✅ test_subagent.py
- ✅ test_cron.py
- ✅ test_special_commands.py
- ✅ test_docx_skill.py
- ✅ test_pdf_skill.py
- ✅ test_xlsx_skill.py
- ✅ test_pptx_skill.py
- ✅ test_feishu_channel.py
- ✅ test_agents_api.py
- ✅ test_cron_api.py

## 快速启动

```bash
cd anyclaw
pip install pydantic pydantic-settings typer rich litellm pytest pytest-asyncio
cp .env.example .env
# 编辑 .env 设置 OPENAI_API_KEY 或 ZAI_API_KEY
python3 -m anyclaw chat
```

### 使用 ZAI/GLM 模型

```bash
# 方式 1: 环境变量
export ZAI_API_KEY=your-key
export ZAI_ENDPOINT=coding-global
anyclaw chat --model zai/glm-5

# 方式 2: 使用 onboard 命令
anyclaw onboard --auth-choice zai-coding-global

# 方式 3: 自动检测 endpoint
anyclaw onboard detect-zai --api-key your-key --save
```

### 使用流式输出

```bash
# 启用流式（默认）
anyclaw chat --stream

# 禁用流式
anyclaw chat --no-stream
```

## 文档位置

- 归档特性: `features/archive/done-feat-*/`
  - `spec.md` - 功能规格
  - `task.md` - 任务列表
  - `checklist.md` - 完成检查清单

- 队列管理: `feature-workflow/`
  - `queue.yaml` - 调度队列
  - `archive-log.yaml` - 归档日志
  - `config.yaml` - 工作流配置

## 当前队列状态

```yaml
pending: 4 个需求 (feat-acp-server, feat-acp-client, feat-acp-mcp-bridge, feat-remove-litellm)
deferred: 1 个需求 (feat-context-shuttle)
active:  []   # 无活跃需求
completed: 77 个特性
```

## 统计

| 指标 | 数值 |
|------|------|
| 完成特性数 | 77 |
| 规划中特性 | 3 (ACP Server/Client/Bridge) |
| 内置技能数 | 17 |
| 测试数量 | 1094+ |
| 配置项数量 | 40+ |
| CLI 命令数 | 30+ |
| API 端点数 | 20+ |

## 最近完成

| 日期 | 特性 | 价值点 |
|------|------|--------|
| 2026-03-27 | feat-logs-page-refactor | Logs 页面重构：移除会话归档，日期选择器 |
| 2026-03-27 | feat-log-persistence | 日志文件持久化（后台线程、JSONL、21 个测试） |
| 2026-03-26 | feat-agent-session-workspace | 非 Agent session 存储到对应 workspace |
| 2026-03-26 | feat-chat-agent-selector | Chat Agent 切换功能 |
| 2026-03-26 | feat-chat-history-bug | 对话历史持久化 Bug 修复 |
| 2026-03-26 | feat-config-consistency | 配置系统一致性修复 |
| 2026-03-25 | feat-tasks-ui | Tasks 页面实现，用于 cron 任务管理 |
| 2026-03-25 | feat-models-panel | Provider 配置 UI 与 API 集成 |
| 2026-03-25 | feat-cron-api | Cron 管理的完整 REST API |
| 2026-03-25 | feat-agents-ui | Agents 页面完整 CRUD 操作 |
| 2026-03-25 | feat-cron-resilience | cron 弹性特性：退避、卡住检测、日志 |
| 2026-03-25 | feat-agents-api | 完整的 Agent API 端点 |
| 2026-03-25 | feat-cron-parser-enhance | 升级到完整的 5 字段 cron 表达式解析器 |
| 2026-03-25 | feat-logs-pages | Logs 页面，支持会话和系统日志查看 |
| 2026-03-25 | feat-session-concurrency | 会话级并发消息处理 |
| 2026-03-25 | feat-config-editor | 配置文件编辑器和服务控制 |
| 2026-03-25 | feat-app-bundle | 应用打包支持 |
| 2026-03-25 | feat-memory-pages | Memory 页面实现 |
| 2026-03-23 | feat-pptx-skill | PPTX 演示文稿处理技能 (python-pptx, 模板分析, 缩略图) |
| 2026-03-23 | feat-feishu-outbound | 飞书出站消息支持 (_outbound_loop 实现) |
| 2026-03-23 | feat-xlsx-skill | XLSX 电子表格处理技能 (openpyxl, pandas, 公式重算) |
| 2026-03-23 | feat-pdf-skill | PDF 文档处理技能 (reportlab, pypdf, pdfplumber) |
| 2026-03-23 | feat-docx-skill | DOCX 文档处理技能 (python-docx, OOXML 编辑) |
| 2026-03-23 | feat-chat-message-render | 对话历史消息渲染增强 (tool_calls 渲染) |
| 2026-03-22 | feat-chat-history-refactor | 对话历史列表重构 (session key 统一) |
| 2026-03-22 | feat-chat-history | 聊天历史与 Agent 管理 (SidePanel, 持久化) |
| 2026-03-22 | feat-cron-skill | Cron 技能实现 (CronTool 注册到 AgentLoop) |
| 2026-03-22 | feat-task-interrupt | 任务即时中断机制 (/stop 即时中断) |
| 2026-03-21 | feat-ui-design-core | UI 设计系统 + 布局组件 (oklch 颜色, AppSidebar) |
| 2026-03-21 | feat-model-config-fix | /model 命令配置传递修复 |
| 2026-03-21 | feat-session-cwd | 会话级工作目录 + 文件工具权限统一 |
| 2026-03-21 | feat-llm-resilience | LLM 响应韧性增强 (空响应检测与恢复) |
| 2026-03-21 | feat-iteration-summary | 迭代限制智能汇报 |
| 2026-03-20 | feat-smart-file-search | 智能文件搜索 (启发式优先级, 授权机制) |
| 2026-03-20 | feat-special-commands-advanced | 高级特殊指令 (/compact /model /agent /session) |
| 2026-03-20 | feat-special-commands-core | 核心特殊指令 (/new /reset /stop /help /status) |
| 2026-03-20 | feat-security-config-enhancement | 安全配置增强 (allow_all_access, extra_allowed_dirs) |
| 2026-03-20 | feat-desktop-app-phase3 | Tauri 桌面应用 Phase 3 完成 |
| 2026-03-20 | feat-session-archive | 会话归档系统 |
| 2026-03-20 | feat-input-sanitizer | 输入验证和净化系统 |
| 2026-03-20 | feat-path-guard | 路径遍历防护 |
| 2026-03-20 | feat-credential-vault | 凭证安全管理 |
| 2026-03-20 | feat-skill-conversation-mode | 技能对话模式 |
| 2026-03-20 | feat-skill-progressive-loading | 技能渐进式加载 |
| 2026-03-20 | feat-skill-dynamic-loader | 技能动态加载 |
| 2026-03-20 | feat-desktop-app | Tauri 桌面应用 (Phase 1-2 完成) |
| 2026-03-20 | feat-multi-agent | Multi-Agent 系统 (OpenClaw-style) |
| 2026-03-20 | feat-session-manager | SessionManager (nanobot 兼容) |
| 2026-03-20 | feat-subagent | SubAgent 后台任务 (SpawnTool) |
| 2026-03-20 | feat-message-tool | MessageTool 跨会话消息 |
| 2026-03-20 | feat-cron | Cron 定时任务 (at/every/cron) |
| 2026-03-20 | feat-im-channels | Channel 集成 (Discord/飞书) |
| 2026-03-19 | feat-serve-mode | 多通道并行服务、守护进程、日志轮转 |
| 2026-03-19 | feat-ssrf-guard | SSRF 防护模块 |

## nanobot / OpenClaw 兼容性

| 功能 | nanobot | OpenClaw | AnyClaw | 状态 |
|------|---------|----------|---------|------|
| SessionManager | ✅ | - | ✅ | 完全兼容 |
| Session Archive | ✅ | - | ✅ | 完全兼容 |
| SubAgent/SpawnTool | ✅ | - | ✅ | 完全兼容 |
| MessageTool | ✅ | - | ✅ | 完全兼容 |
| Cron (at/every/cron) | ✅ | - | ✅ | 完全兼容 |
| Multi-Agent | - | ✅ | ✅ | 完全兼容 |
| Identity 管理 | - | ✅ | ✅ | 完全兼容 |
| 独立 Workspace | - | ✅ | ✅ | 完全兼容 |
| Channel (Discord/飞书) | ✅ | - | ✅ | 完全兼容 |
