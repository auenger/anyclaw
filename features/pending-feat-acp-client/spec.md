# ACP Client - 连接外部 Agent

> ID: feat-acp-client
> 父特性: feat-acp-integration
> 优先级: 75
> 大小: L
> 依赖: [feat-acp-server]

## 概述

实现 ACP Client 模块，使 AnyClaw 能够作为 ACP Client 启动和连接外部 ACP Agent（如 Claude Code、Gemini CLI、Codex CLI），用户可以在 AnyClaw App 中直接与这些外部 Agent 对话。

## 参考文档

- `docs/ACP_PROTOCOL_ANALYSIS.md` — 第七节 7.5 ACP Client 技术架构
- `reference/openclaw/src/acp/client.ts` — OpenClaw 的 ACP Client 参考实现

## 用户价值点

### VP1: ACP Client 核心模块

实现 ACP Client 的核心能力：spawn ACP Agent 子进程、NDJSON 通信、会话管理。

**验收场景:**
```gherkin
Feature: ACP Client 核心通信

  Scenario: 启动 ACP Agent 子进程
    Given AnyClaw 配置了 Claude Code ACP Agent
    When AnyClaw 发起连接请求
    Then AnyClaw spawn claude-code-acp 子进程
      And 通过 stdin/stdout 建立 NDJSON 通信

  Scenario: initialize 握手
    Given ACP Agent 子进程已启动
    When AnyClaw 发送 initialize 请求
    Then Agent 返回 InitializeResponse
      And AnyClaw 记录 Agent 的 capabilities 和 version

  Scenario: 创建会话并发送 prompt
    Given AnyClaw 已与 ACP Agent 握手
    When AnyClaw 发送 newSession + prompt
    Then Agent 处理并返回响应
      And AnyClaw 接收流式 sessionUpdate 事件

  Scenario: Agent 进程异常退出
    Given ACP Agent 子进程正在运行
    When 子进程意外退出 (exit code != 0)
    Then AnyClaw 检测到退出
      And 通知 UI 显示连接断开
      And 支持自动重连 (可选)
```

### VP2: Agent Registry (Agent 注册管理)

管理已注册的外部 ACP Agent 配置。

**验收场景:**
```gherkin
Feature: Agent Registry

  Scenario: 预配置 ACP Agent
    Given 配置文件中定义了 ACP Agent
      | name         | command          | args                          |
      | claude-code  | npx              | ["@zed-industries/claude-code-acp@latest"] |
      | gemini-cli   | gemini           | ["--acp"]                     |
    When AnyClaw 加载配置
    Then Agent Registry 中包含这些 Agent 配置

  Scenario: 列出可用 Agent
    Given Agent Registry 中有 3 个已注册 Agent
    When 用户请求 Agent 列表
    Then 返回所有已注册 Agent 的名称、状态、描述

  Scenario: Agent 健康检查
    Given 注册了 Claude Code Agent
    When 执行健康检查
    Then 验证 claude-code-acp 命令可用
      And 返回 Agent 状态 (available/unavailable)
```

### VP3: Client 端会话管理

管理 AnyClaw 与外部 ACP Agent 之间的会话。

**验收场景:**
```gherkin
Feature: Client 会话管理

  Scenario: 创建直连会话
    Given 用户选择 Claude Code Agent
    When 用户发送第一条消息
    Then AnyClaw 创建新会话 (newSession)
      And 消息直接发送给 Claude Code
      And 不经过 AnyClaw AgentLoop 处理

  Scenario: 会话历史保存
    Given 用户与 Claude Code 进行了 5 轮对话
    When 用户关闭会话
    Then 对话历史保存到 AnyClaw SessionManager
      And 下次打开时可恢复

  Scenario: 跨 Agent 会话切换
    Given 用户正在与 Claude Code 对话
    When 用户切换到 Gemini CLI Agent
    Then Claude Code 会话暂停
      And Gemini CLI 创建新会话
    When 用户切换回 Claude Code
    Then 恢复之前的对话上下文

  Scenario: 会话取消
    Given Claude Code 正在执行任务
    When 用户点击停止按钮
    Then AnyClaw 发送 cancel 请求
      And Claude Code 中止当前操作
```

### VP4: UI 集成 (Tauri 前端)

在 AnyClaw 桌面应用中集成 ACP Client 的 UI。

**验收场景:**
```gherkin
Feature: 桌面应用 UI 集成

  Scenario: Agent 选择器显示外部 Agent
    Given 注册了 Claude Code 和 Gemini CLI
    When 用户打开 Chat 页面
    Then Agent 选择器列表中显示:
      | AnyClaw (内置)     |
      | Claude Code (ACP)  |
      | Gemini CLI (ACP)   |

  Scenario: 选择外部 Agent 对话
    Given 用户在 Agent 选择器中选择 Claude Code
    When 用户输入消息并发送
    Then 消息直接发送给 Claude Code (不经过 AnyClaw Agent)
      And Claude Code 的流式响应实时显示

  Scenario: 工具调用展示
    Given Claude Code 正在执行工具
    When 收到 tool_call 事件
    Then UI 显示工具调用卡片
      And 包含工具名称、状态、文件位置
      And 支持 Follow-Along (自动滚动到对应文件)

  Scenario: 权限审批弹窗
    Given Claude Code 请求执行 exec_command
    When AnyClaw 收到 requestPermission
    Then UI 弹出权限确认对话框
      And 用户可选择批准/拒绝
      And 选择结果发送回 Claude Code
```

## 技术设计

### 模块结构

```
anyclaw/anyclaw/acp/
├── client.py              # ACP Client: 启动/管理 ACP Agent 子进程
├── client_session.py      # Client 端会话管理
├── agent_registry.py      # 已注册 ACP Agent 配置管理
└── ...                    # 与 ACP Server 共享 protocol.py
```

### 架构

```
AnyClaw App (Tauri)
    │
    │ spawn 子进程
    ▼
claude-code-acp (ACP Server, stdio)
    │
    │ NDJSON over stdin/stdout
    ▼
AnyClaw ACP Client 模块
    │
    │ 翻译 & 转发
    ▼
AnyClaw App UI (React)
    ├── 显示文本回复
    ├── 显示工具调用进度 (Follow-Along)
    ├── 显示文件 Diff
    └── 权限确认弹窗
```

### 配置格式

```toml
[acp]
# 启用 ACP Client
enabled = true

[[acp.agents]]
name = "claude-code"
display_name = "Claude Code"
command = "npx"
args = ["@zed-industries/claude-code-acp@latest"]
description = "Anthropic Claude Code coding agent"
icon = "claude"

[[acp.agents]]
name = "gemini-cli"
display_name = "Gemini CLI"
command = "gemini"
args = ["--acp"]
description = "Google Gemini CLI coding agent"
icon = "gemini"
```
