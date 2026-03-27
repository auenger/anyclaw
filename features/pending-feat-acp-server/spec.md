# ACP Server - 被 IDE 连接

> ID: feat-acp-server
> 父特性: feat-acp-integration
> 优先级: 80
> 大小: L
> 依赖: []

## 概述

实现 ACP (Agent Client Protocol) Server 端，使 AnyClaw 能作为 ACP Agent 被 IDE/编辑器（Zed、JetBrains、VS Code）连接。IDE 通过 stdio NDJSON 与 AnyClaw 通信，AnyClaw 直接调用 AgentLoop 处理请求，无需额外的 Gateway 中间层。

## 参考文档

- `docs/ACP_PROTOCOL_ANALYSIS.md` — 完整的 ACP 协议分析和实现方案
- `reference/openclaw/src/acp/` — OpenClaw 的 ACP 实现参考

## 用户价值点

### VP1: 协议类型定义与 NDJSON stdio 服务器

实现 ACP 协议的核心类型定义和 stdio 传输层。

**验收场景:**
```gherkin
Feature: ACP 协议基础通信

  Scenario: IDE 发送 initialize 请求
    Given ACP Server 通过 stdio 运行
    When IDE 发送 initialize 请求 (protocolVersion: "0.16.1")
    Then Server 返回 InitializeResponse
      And 包含 protocolVersion "0.16.1"
      And 包含 serverInfo (name: "anyclaw-acp")
      And 包含 serverCapabilities

  Scenario: IDE 发送未知的 method
    Given ACP Server 已初始化
    When IDE 发送未知 method "foo"
    Then Server 返回 JSON-RPC 错误
      And error.code = -32601 (Method not found)

  Scenario: NDJSON 消息解析
    Given Server 从 stdin 读取消息
    When 收到多个 JSON-RPC 请求（每行一个）
    Then 每个请求独立处理并返回对应响应
    And 响应写入 stdout（NDJSON 格式）
```

### VP2: 协议翻译层 (ACP ↔ AgentLoop)

将 ACP 协议的 initialize/newSession/prompt 等操作翻译为 AnyClaw 内部操作。

**验收场景:**
```gherkin
Feature: ACP 协议翻译

  Scenario: newSession 创建新会话
    Given ACP Server 已初始化
    When IDE 发送 newSession 请求 (cwd: "/project/path")
    Then Server 创建新的 ACP 会话
      And 返回 NewSessionResponse (包含 sessionId)
      And 会话映射到 AnyClaw SessionManager

  Scenario: prompt 处理用户消息
    Given IDE 已创建 ACP 会话
    When IDE 发送 prompt 请求 (prompt: [{type: "text", text: "Hello"}])
    Then Server 构建 InboundMessage (channel: "acp")
      And 通过 AgentLoop 处理消息
      And 返回 PromptResponse (stopReason: "stop")

  Scenario: prompt 支持图片附件
    Given IDE 已创建 ACP 会话
    When IDE 发送 prompt 包含图片内容
      | type  | image.data        | image.mimeType |
      | image | "base64encoded..." | "image/png"     |
    Then Server 提取图片数据
      And 通过 InboundMessage.media 传递给 AgentLoop

  Scenario: cancel 取消当前操作
    Given IDE 正在等待 prompt 响应
    When IDE 发送 cancel 请求
    Then Server 中止当前 AgentLoop 执行
      And 返回取消确认
```

### VP3: 会话管理与映射

ACP 会话到 AnyClaw SessionManager 的映射管理。

**验收场景:**
```gherkin
Feature: ACP 会话管理

  Scenario: 会话映射到 AnyClaw Session
    Given IDE 创建 ACP 会话 (cwd: "/project")
    Then Server 生成 ACP session ID (acp:{uuid})
      And 映射到 AnyClaw session key
      And 记录工作目录

  Scenario: 会话 TTL 自动过期
    Given ACP 会话已创建
    When 超过 24 小时无活动
    Then 会话自动标记为过期
      And 下次请求时返回会话不存在错误

  Scenario: 最大会话数限制
    Given 已有 5000 个活跃 ACP 会话
    When 创建新会话
    Then 最旧的会话被 LRU 驱逐
      And 新会话创建成功

  Scenario: loadSession 恢复会话
    Given IDE 有一个已存在的 ACP session ID
    When IDE 发送 loadSession 请求
    Then Server 恢复会话状态
      And AgentLoop 的对话历史保留
```

### VP4: 流式事件映射

将 AnyClaw 内部事件翻译为 ACP sessionUpdate 事件，实现实时流式推送。

**验收场景:**
```gherkin
Feature: 流式事件映射

  Scenario: 文本分块推送
    Given AgentLoop 正在生成回复
    When 产生 message:outbound 事件
    Then Server 发送 sessionUpdate "agent_message_chunk"
      And 包含 content {type: "text", text: "..."}

  Scenario: 工具调用状态推送
    Given AgentLoop 正在执行工具
    When 产生 tool:start 事件
    Then Server 发送 sessionUpdate "tool_call"
      And 包含 title (工具名称) 和 status "running"
    When 工具执行完成
    Then Server 发送 sessionUpdate "tool_call_update"
      And status 为 "completed" 或 "failed"

  Scenario: Usage 统计推送
    Given AgentLoop 完成一次 LLM 调用
    When Token 使用统计可用
    Then Server 发送 sessionUpdate "usage_update"
      And 包含 used (token 数量)

  Scenario: listSessions 列出会话
    Given 有多个活跃 ACP 会话
    When IDE 发送 listSessions 请求
    Then Server 返回所有活跃会话列表
      And 包含每个会话的 sessionId 和 cwd
```

### VP5: 工具调用权限审批

实现 ACP 工具调用的权限审批机制。

**验收场景:**
```gherkin
Feature: 工具权限审批

  Scenario: 安全工具自动审批
    Given IDE 发送 prompt 请求
    When AgentLoop 调用 read_file 工具
    Then Server 自动批准执行
      And 不发送 requestPermission 给 IDE

  Scenario: 危险工具请求审批
    Given IDE 发送 prompt 请求
    When AgentLoop 调用 exec_command 工具
    Then Server 发送 requestPermission 给 IDE
      And 等待 IDE 返回审批结果
    When IDE 批准
    Then 工具继续执行

  Scenario: IDE 拒绝工具调用
    Given Server 发送 requestPermission 给 IDE
    When IDE 拒绝 (reject_once)
    Then 工具调用被中止
      And AgentLoop 收到权限拒绝错误

  Scenario: 工具位置推断
    Given AgentLoop 调用 read_file (path: "/project/src/main.py")
    Then Server 在 tool_call 事件中包含 ToolCallLocation
      And location.uri = "file:///project/src/main.py"
```

### VP6: CLI 命令入口

提供 `anyclaw acp serve` CLI 命令启动 ACP Server。

**验收场景:**
```gherkin
Feature: CLI 命令

  Scenario: 启动 ACP Server
    When 运行 `anyclaw acp serve`
    Then Server 通过 stdio 等待 ACP 请求
      And 支持 --cwd 参数设置默认工作目录
      And 支持 --session 参数指定默认会话 key
      And 支持 --verbose 参数开启调试日志

  Scenario: 优雅关闭
    Given ACP Server 正在运行
    When 收到 SIGINT 或 SIGTERM 信号
    Then Server 完成当前请求处理
      And 关闭所有活跃会话
      And 退出进程
```

## 技术设计

### 模块结构

```
anyclaw/anyclaw/acp/
├── __init__.py              # 模块导出
├── server.py                # ACP stdio 服务器 (NDJSON 解析)
├── protocol.py              # 协议类型定义 (Pydantic models)
├── translator.py            # ACP ↔ AnyClaw 消息翻译
├── session.py               # ACP 会话管理 (映射到 AnyClaw Session)
├── event_mapper.py          # 事件映射 (tool_call, message_chunk 等)
├── permissions.py           # 工具调用权限管理
└── cli_cmd.py               # CLI 命令入口 (anyclaw acp serve)
```

### 架构

```
┌──────────┐   stdio/NDJSON   ┌──────────────────┐   ┌──────────────┐
│  IDE 客户端 │ ◄────────────► │   ACP Server     │   │  AgentLoop   │
│ (Zed etc)  │                │  (Python 实现)    │──►│  + MessageBus │
└──────────┘                └──────────────────┘   └──────────────┘
                                   │                      │
                            ┌──────┴──────┐        ┌──────┴──────┐
                            │ translator  │        │ ToolRegistry │
                            │ session_mgr │        │ MCP Client   │
                            │ event_mapper│        │ Skills       │
                            └─────────────┘        └─────────────┘
```

### 与 OpenClaw 的差异

- 无需 Gateway 中间层，直接调用 AgentLoop
- 复用现有 MessageBus 的流式能力
- 复用现有 SessionManager 的会话管理
- 复用现有 ToolRegistry 的工具系统
