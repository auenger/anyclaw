# ACP 协议分析与 AnyClaw 实现方案报告

> 日期: 2026-03-27
> 基于: reference/openclaw ACP 实现 (v0.16.1)

## 一、ACP 协议概述

**ACP (Agent Communication Protocol)** 是一个标准化的 Agent 通信协议，主要用于 IDE/编辑器与 AI Agent 之间的集成通信。

### 核心特征

| 特性 | 说明 |
|------|------|
| **传输层** | NDJSON (Newline-Delimited JSON) over stdio |
| **SDK** | `@agentclientprotocol/sdk` v0.16.1 (TypeScript) |
| **架构模式** | Bridge 模式 — IDE ↔ ACP Bridge ↔ Agent Backend |
| **会话管理** | 支持持久化和一次性会话 |
| **流式通信** | 实时工具调用状态更新、消息分块推送 |
| **权限系统** | 工具调用权限审批机制 |

### 协议核心操作

```
initialize()     → 协议握手，能力协商
newSession()     → 创建新会话
loadSession()    → 加载已有会话
prompt()         → 发送用户提示
cancel()         → 取消当前操作
listSessions()   → 列出可用会话
setSessionMode() → 设置会话模式
```

## 二、OpenClaw 的 ACP 实现架构

```
┌──────────┐   stdio/NDJSON   ┌──────────────┐   WebSocket   ┌──────────┐
│  IDE 客户端 │ ◄────────────► │  ACP Bridge   │ ◄──────────► │  Gateway  │
│ (Zed etc)  │                │ (server.ts)   │              │  Server   │
└──────────┘                └──────────────┘              └──────────┘
                                   │
                            ┌──────┴──────┐
                            │ translator  │  协议翻译层
                            │ session     │  会话管理
                            │ event-mapper│  事件映射
                            └─────────────┘
```

### 关键模块

| 模块 | 文件 | 职责 |
|------|------|------|
| **ACP Server** | `src/acp/server.ts` | stdio 入口、Gateway 连接、生命周期管理 |
| **Translator** | `src/acp/translator.ts` | ACP ↔ Gateway 协议翻译、会话映射 |
| **Session** | `src/acp/session.ts` | 内存会话存储、LRU 驱逐、速率限制 |
| **Event Mapper** | `src/acp/event-mapper.ts` | 内容格式转换、工具位置推断、附件处理 |

### 消息流示例

```
# Client → Server (初始化)
{"method":"initialize","params":{"protocolVersion":"0.16.1","clientInfo":{"name":"zed"}}}

# Client → Server (发送提示)
{"method":"prompt","params":{"sessionId":"acp:uuid","prompt":[{"type":"text","text":"Hello"}]}}

# Server → Client (流式响应)
{"method":"session/notification","params":{"update":{"sessionUpdate":"agent_message_chunk","content":{"type":"text","text":"Hi!"}}}}

# Server → Client (工具调用)
{"method":"session/notification","params":{"update":{"sessionUpdate":"tool_call","title":"read_file","status":"running"}}}
```

## 三、AnyClaw 现有架构分析

### 当前通信架构

```
┌──────────┐   ┌──────────┐   ┌──────────┐
│   CLI    │   │  Feishu  │   │ Discord  │  ← Channels
└────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │
     └──────────────┼──────────────┘
                    ▼
              ┌──────────┐         ┌──────────────┐
              │ MessageBus│◄──────►│ Tauri (SSE)  │  ← 桌面应用
              └────┬─────┘         └──────────────┘
                   ▼
             ┌──────────┐
             │ AgentLoop │  ← 核心处理
             └────┬─────┘
                  ▼
        ┌─────────────────┐
        │  ToolRegistry   │  ← 工具执行
        └─────────────────┘
```

### 现有集成点（适合接入 ACP）

| 组件 | 文件 | ACP 集成价值 |
|------|------|-------------|
| **MessageBus** | `anyclaw/bus/queue.py` | 可作为 ACP 消息路由后端 |
| **AgentLoop** | `anyclaw/agent/loop.py` | 可包装为 ACP Agent 接口 |
| **ToolRegistry** | `anyclaw/tools/registry.py` | 工具调用可直接映射为 ACP tool_call |
| **SSE Endpoint** | `anyclaw/api/sse.py` | SSE 事件格式与 ACP sessionUpdate 相似 |
| **Sidecar 模式** | `anyclaw/cli/sidecar_cmd.py` | 已有 HTTP 服务器，ACP 可作为新入口 |
| **SessionManager** | `anyclaw/session/manager.py` | ACP 会话可直接映射 |

## 四、AnyClaw ACP 实现方案

### 目标架构

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

### 模块设计

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

### 核心实现要点

#### 1. 协议类型定义 (`protocol.py`)

```python
from pydantic import BaseModel
from enum import Enum
from typing import Any

class SessionUpdateType(str, Enum):
    AGENT_MESSAGE_CHUNK = "agent_message_chunk"
    TOOL_CALL = "tool_call"
    TOOL_CALL_UPDATE = "tool_call_update"
    USAGE_UPDATE = "usage_update"
    AVAILABLE_COMMANDS_UPDATE = "available_commands_update"

class ACPRequest(BaseModel):
    method: str
    id: str | int | None = None
    params: dict[str, Any] = {}

class ACPResponse(BaseModel):
    id: str | int | None = None
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None

class ContentBlock(BaseModel):
    type: str  # "text" | "image" | "resource"
    text: str | None = None
    image: dict[str, str] | None = None  # {data, mimeType}
    resource: dict[str, str] | None = None  # {uri, mimeType}
```

#### 2. NDJSON stdio 服务器 (`server.py`)

```python
import asyncio
import json
import sys
from anyclaw.acp.protocol import ACPRequest
from anyclaw.acp.translator import ACPTranslator

class ACPStdioServer:
    """ACP 协议服务器，通过 stdio NDJSON 通信"""

    def __init__(self, agent_manager, session_manager, tool_registry):
        self.translator = ACPTranslator(agent_manager, session_manager, tool_registry)

    async def run(self):
        """主事件循环：读取 stdin NDJSON，处理后写入 stdout"""
        reader = asyncio.StreamReader()
        loop = asyncio.get_event_loop()

        # 读取 stdin 的后台任务
        def _read_stdin():
            data = sys.stdin.buffer.read()
            loop.call_soon_threadsafe(reader.feed_data, data)
            loop.call_soon_threadsafe(reader.feed_eof)

        asyncio.get_event_loop().run_in_executor(None, _read_stdin)

        # 处理消息循环
        async for line in reader:
            line = line.decode().strip()
            if not line:
                continue
            request = ACPRequest(**json.loads(line))
            response = await self.handle_request(request)
            self._write_response(response)

    async def handle_request(self, request: ACPRequest) -> ACPResponse:
        """路由 ACP 请求到对应的处理器"""
        handlers = {
            "initialize": self.translator.initialize,
            "newSession": self.translator.new_session,
            "loadSession": self.translator.load_session,
            "prompt": self.translator.prompt,
            "cancel": self.translator.cancel,
            "listSessions": self.translator.list_sessions,
        }
        handler = handlers.get(request.method)
        if handler:
            return await handler(request.params)
        return ACPResponse(error={"code": -32601, "message": "Method not found"})

    def _write_response(self, response: ACPResponse):
        """NDJSON 写入 stdout"""
        sys.stdout.write(json.dumps(response.model_dump(exclude_none=True)) + "\n")
        sys.stdout.flush()
```

#### 3. 协议翻译层 (`translator.py`) — 核心桥接

```python
class ACPTranslator:
    """将 ACP 协议消息翻译为 AnyClaw 内部操作"""

    def __init__(self, agent_manager, session_manager, tool_registry):
        self.agent_manager = agent_manager
        self.session_manager = session_manager
        self.tool_registry = tool_registry
        self.sessions: dict[str, AcpSession] = {}
        self.protocol_version = "0.16.1"

    async def initialize(self, params: dict) -> ACPResponse:
        return ACPResponse(result={
            "protocolVersion": self.protocol_version,
            "serverInfo": {"name": "anyclaw-acp", "version": "1.0.0"},
            "serverCapabilities": {}
        })

    async def prompt(self, params: dict) -> ACPResponse:
        """ACP prompt → AgentLoop.process()"""
        session_id = params["sessionId"]
        content_blocks = params["prompt"]

        # 1. 提取文本内容
        text = self._extract_text(content_blocks)

        # 2. 构建 InboundMessage
        message = InboundMessage(
            channel="acp",
            sender_id="ide_user",
            chat_id=session_id,
            content=text,
            timestamp=datetime.now(),
            media=self._extract_media(content_blocks),
            metadata={"acp_session_id": session_id},
        )

        # 3. 通过 AgentLoop 处理
        agent = self.agent_manager.get_agent()
        # 流式处理，同时发送 sessionUpdate 事件
        response = await agent.process(message, stream_callback=self._on_stream)

        return ACPResponse(result={
            "stopReason": "stop",
        })

    def _on_stream(self, event: dict):
        """流式回调：AgentLoop 事件 → ACP sessionUpdate"""
        self._write_notification(event)
```

#### 4. 会话管理 (`session.py`)

```python
class AcpSession:
    """ACP 会话，映射到 AnyClaw Session"""
    session_id: str          # ACP session UUID
    session_key: str         # AnyClaw session key
    cwd: str                 # 工作目录
    created_at: float
    last_touched: float
    abort_controller: asyncio.Event | None  # 取消信号

class AcpSessionManager:
    """ACP 会话管理器"""
    MAX_SESSIONS = 5000
    SESSION_TTL = 86400  # 24小时

    def create_session(self, cwd: str, session_key: str | None = None) -> AcpSession:
        # 映射到 AnyClaw SessionManager
        ...

    def map_to_anyclaw_session(self, acp_session: AcpSession):
        # acp:{uuid} → AnyClaw session key
        ...
```

#### 5. 事件映射 (`event_mapper.py`)

将 AnyClaw 内部事件映射为 ACP sessionUpdate：

| AnyClaw 事件 | ACP sessionUpdate |
|-------------|-------------------|
| `message:outbound` (分块) | `agent_message_chunk` |
| `tool:start` | `tool_call` (status: "running") |
| `tool:complete` | `tool_call_update` (status: "completed") |
| `agent:thinking` | `agent_message_chunk` (stream: "thought") |
| Token 使用统计 | `usage_update` |

#### 6. 权限系统 (`permissions.py`)

```python
# 安全自动审批的工具
AUTO_APPROVE_TOOLS = {"read_file", "list_dir", "search_files", "web_search"}

# 需要手动审批的工具
MANUAL_APPROVE_TOOLS = {"write_file", "exec_command", "delete_file"}

async def check_permission(self, tool_name: str, args: dict) -> bool:
    if tool_name in AUTO_APPROVE_TOOLS:
        return True
    # 发送 requestPermission 给 IDE 客户端
    return await self._request_ide_permission(tool_name, args)
```

## 五、实现路线图

### Phase 1: 基础框架（最小可用）
1. `protocol.py` — 协议类型定义
2. `server.py` — NDJSON stdio 服务器
3. `translator.py` — 基础 initialize + newSession + prompt
4. `cli_cmd.py` — `anyclaw acp serve` 命令

### Phase 2: 会话与流式
5. `session.py` — 会话映射与管理
6. `event_mapper.py` — 流式事件翻译
7. AgentLoop 流式回调集成

### Phase 3: 工具与权限
8. 工具调用 → ACP tool_call 事件映射
9. `permissions.py` — IDE 权限审批流
10. 工具位置推断（文件路径、行号）

### Phase 4: 高级特性
11. loadSession — 会话恢复与历史回放
12. cancel — 运行取消
13. listSessions — 会话列表
14. 图片附件支持
15. Usage 统计

## 六、与 OpenClaw 实现的关键差异

| 维度 | OpenClaw (TypeScript) | AnyClaw (Python) |
|------|----------------------|-----------------|
| **语言** | TypeScript | Python 3.11+ |
| **后端** | Gateway (WebSocket) | AgentLoop (直接调用) |
| **会话** | 映射到 Gateway Session | 映射到 AnyClaw SessionManager |
| **工具系统** | Gateway 内置工具 | ToolRegistry + MCP + Skills |
| **传输** | WebSocket → Gateway | 直接调用 AgentLoop |
| **消息总线** | 无（直接桥接） | MessageBus（可复用） |
| **优势** | Gateway 解耦 | 无需额外进程，更轻量 |

## 七、ACP 能力图谱与使用场景

### 7.1 ACP 为 AnyClaw 解锁的能力

| 能力 | 说明 |
|------|------|
| **IDE 集成** | 在 Zed / JetBrains / VS Code 中直接使用 AnyClaw 作为 AI Agent |
| **跨 Agent 协作** | 通过 ACP-MCP 适配器，调用 Claude Code、Gemini CLI、Codex 等作为 AnyClaw 的外部工具 |
| **文件系统操作** | IDE 提供文件读写能力给 Agent，Agent 可读取未保存的编辑器 buffer |
| **Follow-Along** | IDE 自动跟踪 Agent 正在操作的文件，高亮、滚动到 Agent 正在修改的位置 |
| **权限审批 UI** | IDE 原生弹出权限确认对话框，替代终端里的文本确认 |
| **会话持久化** | 跨 IDE 重启恢复对话，loadSession 恢复历史 |
| **Slash Commands** | Agent 向 IDE 注册自定义命令（/review /refactor /test 等） |
| **远程 Agent** | 支持 stdio (本地) + HTTP/WebSocket (远程) 传输 |
| **ACP Proxy 扩展** | 在 Client 和 Agent 之间插入中间件（日志、策略、审计、内容过滤） |

### 7.2 ACP 与 MCP 的关系

```
ACP: Agent ↔ Editor/IDE 通信（"在任何编辑器里用任何 Agent"）
MCP: Agent ↔ External Tool/Server 通信（"让 Agent 调用外部工具/API"）

两者互补，可同时使用。
```

### 7.3 两条集成路径

#### 路径 1: MCP 工具调用（零代码，配置级）

通过已有的 `acp-mcp` 适配器，AnyClaw 通过 MCP 调用 Claude Code 等外部 Agent：

```
用户 → AnyClaw Agent → [判断要不要调 Claude Code] → Claude Code
```

- AnyClaw 是中间人，控制权在 AnyClaw 的 Agent
- 只需 MCP 配置，无需写代码
- 适合：AnyClaw 智能编排多个 Agent 协作

```bash
# 配置示例
anyclaw config set mcp.servers.claude-code.command "npx"
anyclaw config set mcp.servers.claude-code.args '["@i-am-bee/acp-mcp","--agent","claude-code"]'
```

#### 路径 2: ACP Client 直连（完整体验）

AnyClaw 实现 ACP Client，直接 stdio 启动 Claude Code 进程，用户直接与 Claude Code 对话：

```
用户 → AnyClaw App UI → Claude Code (直连对话)
```

- 用户直接跟 Claude Code 对话，AnyClaw 只是个壳
- 完整的流式工具调用展示、权限弹窗、会话管理
- 适合：用户直接使用某个 Agent 的完整能力

```
┌─ AnyClaw Desktop ──────────────────────────┐
│  Agent: [Claude Code ▼]   会话: #3          │
│─────────────────────────────────────────────│
│  你: 帮我看看这个 bug                       │
│                                            │
│  Claude Code: 让我看看...                   │
│                                            │
│  ⏺ 读取 src/api/handler.py (line 42-58)    │
│  ⏺ 读取 src/utils/parser.py (line 15-30)   │
│  ⏺ 运行 python -m pytest tests/test_api.py │
│                                            │
│  找到问题了，handler.py 第 45 行的异常处理    │
│  没有捕获 TimeoutError。要我修复吗？          │
└─────────────────────────────────────────────┘
```

#### 两条路径对比

| | 路径 1 (MCP 工具) | 路径 2 (ACP 直连) |
|---|---|---|
| **谁在思考** | AnyClaw Agent 决定调不调 | Claude Code 直接思考 |
| **对话体验** | AnyClaw 转述 | 原汁原味的 Claude Code |
| **工具调用展示** | 简单的文本描述 | 完整的实时流式展示 |
| **权限控制** | AnyClaw 的权限系统 | IDE/AnyClaw 原生弹窗 |
| **实现成本** | 零代码（配置级） | 需要实现 ACP Client 模块 |
| **适合场景** | 编排多个 Agent | 直接使用某个 Agent |

### 7.4 多 Agent 统一前端

实现 ACP Client 后，AnyClaw 成为多 Agent 统一管理平台：

```
┌─ AnyClaw Desktop ──────────────────────────┐
│                                            │
│  Agent 列表:                                 │
│  ┌─────────────────────────────────────┐    │
│  │ 🤖 AnyClaw (内置, GLM/ZAI)         │ ← 自己的 Agent
│  │ 🤖 Claude Code (ACP Client)        │ ← 本地 Claude Code
│  │ 🤖 Gemini CLI (ACP Client)         │ ← 本地 Gemini CLI
│  │ 🤖 Codex (ACP Client)              │ ← 本地 Codex
│  │ 🤖 远程 Agent (HTTP)               │ ← 云端部署的
│  └─────────────────────────────────────┘    │
│                                            │
│  共享能力:                                   │
│  - 会话历史 (所有 Agent 统一管理)            │
│  - 文件上下文 (自动传递工作目录)              │
│  - MCP 工具 (AnyClaw 的 MCP 工具可共享)     │
│  - 记忆系统 (跨 Agent 共享用户偏好)          │
└─────────────────────────────────────────────┘
```

### 7.5 ACP Client 技术架构

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

ACP Client 模块设计：

```
anyclaw/anyclaw/acp/
├── client.py          # ACP Client: 启动/管理 ACP Agent 子进程
├── client_session.py  # Client 端会话管理 (连接到外部 ACP Agent)
├── agent_registry.py  # 已注册的 ACP Agent 配置 (Claude Code, Gemini CLI 等)
└── ...                # 与 ACP Server 共享 protocol.py, event_mapper.py
```

### 7.6 ACP 生态现状 (2026)

**已支持 ACP 的 Agent (Server 端)**:
- Claude Code (via `@zed-industries/claude-code-acp`)
- Gemini CLI (参考实现)
- OpenAI Codex CLI
- Goose (Block)
- OpenHands
- OpenCode
- Augment Code
- Qwen Code
- Kimi CLI

**已支持 ACP 的 IDE/编辑器 (Client 端)**:
- Zed (发起者，最完整支持)
- JetBrains IDEs
- VS Code (via 扩展)
- Neovim (CodeCompanion)
- Emacs (社区适配器)

**跨协议桥接**:
- `acp-mcp` 适配器: ACP Agent ↔ MCP Client 互通

### 7.7 实现优先级

```
P0 (核心价值):
  ├── ACP Server 实现 (Phase 1-2)
  │   └── 让 Zed/JetBrains 能直接用 AnyClaw
  │
  └── acp-mcp 集成 (配置级)
      └── AnyClaw 通过 MCP 调用 Claude Code 等

P1 (增强体验):
  ├── ACP Client 实现
  │   └── AnyClaw 直连 Claude Code / Gemini CLI
  ├── Client-side Tools (文件读写)
  ├── Follow-Along 支持
  └── 权限审批流

P2 (生态完善):
  ├── Agent Registry (多 Agent 配置管理)
  ├── Slash Commands 注册
  └── 远程 HTTP/WebSocket 传输
```

## 八、结论

AnyClaw 已具备了实现 ACP 协议的**所有基础设施**：
- **AgentLoop** 可直接作为 ACP Agent 后端（无需额外的 Gateway 层）
- **MessageBus + SSE** 已有流式通信能力
- **SessionManager** 可直接映射 ACP 会话
- **ToolRegistry** 工具调用可映射为 ACP tool_call 事件
- **Sidecar 模式** 证明 AnyClaw 已有进程间通信经验

### 双向集成策略

**推荐策略**: 同时实现 ACP Server + ACP Client，使 AnyClaw 成为完整的 Agent 平台：

1. **ACP Server (被连接)**: 让 Zed、JetBrains 等 IDE 能直接使用 AnyClaw 作为 AI Agent
2. **ACP Client (主动连接)**: 让 AnyClaw 能直连 Claude Code、Gemini CLI 等外部 Agent，用户在 AnyClaw App 里直接与它们对话
3. **MCP 桥接 (零代码)**: 通过 `acp-mcp` 适配器，AnyClaw 的 Agent 能调用其他 ACP Agent 作为工具

采用"直接集成"模式而非 OpenClaw 的"Bridge"模式。由于 AnyClaw 的 AgentLoop 本身就是完整的 Agent 运行时，ACP Server 可以直接调用 AgentLoop，省去 Gateway 中间层，使架构更简洁、启动更快、延迟更低。

### 最终定位

**AnyClaw = Agent 平台** — 既当 Agent（ACP Server），也当 Agent 管理器（ACP Client），还当 Agent 编排器（MCP 桥接）。

**预估工作量**:
- Phase 1-2 (ACP Server): 约 3-4 个特性
- ACP-MCP 集成: 配置级，零代码
- Phase 3 (ACP Client): 约 2-3 个特性
- Phase 4 (高级特性): 可后续迭代

### 参考资料

- [ACP 官方文档](https://agentclientprotocol.com/get-started/introduction)
- [Zed ACP 页面](https://zed.dev/acp)
- [Claude Code ACP 支持 (GitHub Issue)](https://github.com/anthropics/claude-code/issues/6686)
- [@zed-industries/claude-code-acp (NPM)](https://www.npmjs.com/package/@zed-industries/claude-code-acp)
- [ACP-MCP 适配器 (GitHub)](https://github.com/i-am-bee/acp-mcp)
- [Zed 博客: Claude Code via ACP](https://zed.dev/blog/claude-code-via-acp)
- [JetBrains ACP 文档](https://www.jetbrains.com/zh-cn/help/ai-assistant/acp.html)
- [ACP Progress Report](https://zed.dev/blog/acp-progress-report)
