# AnyClaw 架构设计文档

本文档详细说明 AnyClaw 的系统架构、组件关系和通信机制。

## 目录

- [系统概览](#系统概览)
- [核心组件](#核心组件)
- [服务模式对比](#服务模式对比)
- [通信机制](#通信机制)
- [数据流](#数据流)
- [目录结构](#目录结构)
- [配置管理](#配置管理)
- [启动流程](#启动流程)

---

## 系统概览

```
                              ┌─────────────────────────────────┐
                              │          外部频道               │
                              │  Discord │ 飞书 │ CLI │ API    │
                              └───────────────┬─────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           AnyClaw Core                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      MessageBus (消息总线)                        │   │
│  │                    Inbound ◄────────► Outbound                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  ┌─────────────────────────────────┼───────────────────────────────┐   │
│  │                         Agent System                            │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │   │
│  │  │ AgentLoop │  │ Session  │  │  Memory  │  │  Tools   │       │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      LLM Providers                               │   │
│  │        OpenAI │ Anthropic │ ZAI/GLM │ MCP                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 核心组件

### 1. MessageBus (消息总线)

位置: `anyclaw/bus/queue.py`

消息总线是整个系统的核心，负责解耦频道和 Agent：

```python
class MessageBus:
    """异步消息总线，解耦频道和 Agent 核心"""

    _inbound: Queue[InboundMessage]   # 入站消息队列
    _outbound: Queue[OutboundMessage]  # 出站消息队列

    # 主要方法
    async def publish_inbound(msg)    # 发布入站消息
    async def consume_inbound()       # 消费入站消息
    async def publish_outbound(msg)   # 发布出站消息
    async def subscribe()             # SSE 订阅所有事件
```

### 2. ServeManager (服务管理器)

位置: `anyclaw/core/serve.py`

管理所有频道的生命周期：

```python
class ServeManager:
    """多通道服务管理器"""

    config: AnyClawConfig
    bus: MessageBus
    enabled_channels: list[str]

    def initialize()      # 初始化所有频道
    async def start()     # 启动服务
    async def stop()      # 停止服务
```

### 3. AgentLoop (Agent 处理循环)

位置: `anyclaw/agent/loop.py`

处理消息并调用 LLM：

```python
class AgentLoop:
    """Agent 主处理循环"""

    async def process(message)  # 处理单条消息
    async def run()             # 持续运行循环
```

### 4. FastAPI Server (HTTP API)

位置: `anyclaw/api/server.py`

为桌面应用提供 HTTP API：

```python
def create_app(port: int) -> FastAPI:
    """创建 FastAPI 应用"""

    # 路由
    /api/health              # 健康检查
    /api/stream              # SSE 事件流
    /api/agents              # Agent 列表
    /api/agents/{id}/chat    # 发送消息
    /api/messages            # 消息 API
    /api/skills              # 技能管理
    /api/tasks               # 任务管理
    /api/config              # 配置管理
```

---

## 服务模式对比

AnyClaw 提供两种服务模式：

### 模式对比表

| 特性 | `anyclaw serve` | `anyclaw sidecar` |
|------|-----------------|-------------------|
| **用途** | 后台机器人服务 | 桌面应用后端 |
| **FastAPI** | ❌ 不启动 | ✅ 启动 (端口 62616) |
| **ServeManager** | ✅ 启动 | ✅ 启动 |
| **Discord** | ✅ 可用 | ✅ 可用 |
| **飞书** | ✅ 可用 | ✅ 可用 |
| **CLI** | ✅ 可用 | ✅ 可用 |
| **Tauri App** | ❌ 无法连接 | ✅ 可以连接 |
| **SSE 流** | ❌ 无 | ✅ 有 |

### 架构图对比

#### anyclaw serve

```
┌─────────────────────────────────────────────────────────┐
│                    anyclaw serve                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                 ServeManager                     │   │
│  │                                                  │   │
│  │   ┌───────┐  ┌─────────┐  ┌────────┐           │   │
│  │   │  CLI  │  │ Discord │  │  飞书   │           │   │
│  │   └───┬───┘  └────┬────┘  └───┬────┘           │   │
│  │       │           │            │                 │   │
│  │       └───────────┼────────────┘                 │   │
│  │                   │                              │   │
│  │                   ▼                              │   │
│  │           ┌──────────────┐                       │   │
│  │           │  MessageBus  │                       │   │
│  │           └──────┬───────┘                       │   │
│  │                  │                               │   │
│  │                  ▼                               │   │
│  │           ┌──────────────┐                       │   │
│  │           │  AgentLoop   │                       │   │
│  │           └──────────────┘                       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ❌ 没有 HTTP API                                       │
└─────────────────────────────────────────────────────────┘
```

#### anyclaw sidecar

```
┌─────────────────────────────────────────────────────────┐
│                   anyclaw sidecar                       │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                 ServeManager                     │   │
│  │                                                  │   │
│  │   ┌───────┐  ┌─────────┐  ┌────────┐           │   │
│  │   │  CLI  │  │ Discord │  │  飞书   │           │   │
│  │   └───┬───┘  └────┬────┘  └───┬────┘           │   │
│  │       │           │            │                 │   │
│  │       └───────────┼────────────┘                 │   │
│  │                   │                              │   │
│  │                   ▼                              │   │
│  │           ┌──────────────┐                       │   │
│  │           │  MessageBus  │◄──────────────────┐   │   │
│  │           └──────┬───────┘                   │   │   │
│  │                  │                           │   │   │
│  │                  ▼                           │   │   │
│  │           ┌──────────────┐                   │   │   │
│  │           │  AgentLoop   │                   │   │   │
│  │           └──────────────┘                   │   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                    │    │
│  ┌─────────────────────────────────────────────────┐   │
│  │              FastAPI (端口 62616)               │   │
│  │                                                 │   │
│  │   GET  /api/health      - 健康检查             │   │
│  │   GET  /api/stream      - SSE 事件流 ──────────┘   │
│  │   GET  /api/agents      - Agent 列表               │
│  │   POST /api/agents/{id}/chat - 发送消息            │
│  │   GET  /api/skills      - 技能管理                 │
│  │   GET  /api/tasks       - 任务管理                 │
│  │   GET  /api/config      - 配置管理                 │
│  └─────────────────────────────────────────────────┘   │
│                          ▲                             │
└──────────────────────────┼─────────────────────────────┘
                           │
                           │ HTTP / SSE
                           │
                    ┌──────┴──────┐
                    │  Tauri App  │
                    │  (桌面应用)  │
                    └─────────────┘
```

### 结论

**只需要运行 `sidecar` 就能同时拥有所有功能：**

- ✅ Tauri 桌面应用
- ✅ Discord 机器人
- ✅ 飞书机器人
- ✅ CLI 命令
- ✅ HTTP API

**不需要同时运行 `serve` 和 `sidecar`！**

---

## 通信机制

### 1. 频道 → Agent (入站)

```
用户消息 → Channel → InboundMessage → MessageBus → AgentLoop → LLM
```

```python
# 消息结构
@dataclass
class InboundMessage:
    channel: str          # 来源频道 (discord/feishu/cli/desktop)
    sender_id: str        # 发送者 ID
    chat_id: str          # 会话 ID
    content: str          # 消息内容
    timestamp: datetime   # 时间戳
    media: list[str]      # 附件
    metadata: dict        # 额外元数据
```

### 2. Agent → 频道 (出站)

```
LLM 响应 → AgentLoop → OutboundMessage → MessageBus → Channel → 用户
```

```python
# 响应结构
@dataclass
class OutboundMessage:
    channel: str          # 目标频道
    chat_id: str          # 会话 ID
    content: str          # 响应内容
    reply_to: str         # 回复的消息 ID
    media: list[str]      # 附件
    metadata: dict        # 额外元数据
```

### 3. Tauri App ↔ Sidecar

```
┌────────────────────────────────────────────────────────────┐
│                       Tauri App                            │
│                                                            │
│  ┌────────────────┐              ┌────────────────┐       │
│  │   React UI     │              │   Tauri Rust   │       │
│  │                │              │                │       │
│  │  - 状态管理     │              │  - 进程管理     │       │
│  │  - SSE 订阅    │◄────────────►│  - 系统托盘     │       │
│  │  - HTTP 请求   │              │  - 文件系统     │       │
│  └───────┬────────┘              └───────┬────────┘       │
│          │                               │                 │
└──────────┼───────────────────────────────┼─────────────────┘
           │                               │
           │ HTTP/SSE                      │ spawn
           │                               │
           ▼                               ▼
┌────────────────────────────────────────────────────────────┐
│                      Sidecar 进程                          │
│                                                            │
│  python -m anyclaw.cli.sidecar_cmd --port 62616           │
│                                                            │
│  ┌────────────────┐              ┌────────────────┐       │
│  │   FastAPI      │              │  ServeManager  │       │
│  │                │              │                │       │
│  │  /api/health   │              │  - Discord     │       │
│  │  /api/stream   │◄────────────►│  - 飞书        │       │
│  │  /api/chat     │              │  - CLI         │       │
│  └────────────────┘              └────────────────┘       │
└────────────────────────────────────────────────────────────┘
```

#### 通信协议

| 操作 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 健康检查 | GET | `/api/health` | 检查服务状态 |
| 事件订阅 | GET | `/api/stream` | SSE 长连接 |
| 发送消息 | POST | `/api/agents/{id}/chat` | 发送聊天消息 |
| Agent 列表 | GET | `/api/agents` | 获取 Agent 列表 |
| 技能列表 | GET | `/api/skills` | 获取技能列表 |
| 任务列表 | GET | `/api/tasks` | 获取任务列表 |
| 配置获取 | GET | `/api/config` | 获取配置 |
| 配置更新 | PUT | `/api/config` | 更新配置 |

---

## 数据流

### 完整消息处理流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                           消息处理流程                               │
└─────────────────────────────────────────────────────────────────────┘

1. 消息接收
   ┌──────────┐     ┌──────────────┐     ┌───────────────┐
   │  用户    │────►│   Channel    │────►│ InboundMessage│
   │ (Discord)│     │  (discord.py)│     │   (数据结构)   │
   └──────────┘     └──────────────┘     └───────┬───────┘
                                               │
2. 消息发布                                     ▼
   ┌───────────────────────────────────────────────────────┐
   │                    MessageBus                         │
   │   await bus.publish_inbound(inbound_msg)             │
   └───────────────────────┬───────────────────────────────┘
                           │
3. 消息消费                 ▼
   ┌───────────────────────────────────────────────────────┐
   │                    AgentLoop                          │
   │   msg = await bus.consume_inbound()                  │
   └───────────────────────┬───────────────────────────────┘
                           │
4. 上下文构建               ▼
   ┌───────────────────────────────────────────────────────┐
   │                  ContextBuilder                       │
   │   - 加载 SOUL.md (人设)                               │
   │   - 加载 USER.md (用户档案)                           │
   │   - 加载 Skills Summary (技能摘要)                    │
   │   - 加载对话历史                                      │
   └───────────────────────┬───────────────────────────────┘
                           │
5. LLM 调用                 ▼
   ┌───────────────────────────────────────────────────────┐
   │                  litellm.acompletion()                │
   │   - OpenAI / Anthropic / ZAI                          │
   │   - 工具调用 (Tool Calling)                           │
   └───────────────────────┬───────────────────────────────┘
                           │
6. 工具执行                 ▼
   ┌───────────────────────────────────────────────────────┐
   │                    ToolLoop                           │
   │   - 执行工具调用                                      │
   │   - 返回结果给 LLM                                    │
   │   - 循环直到完成                                      │
   └───────────────────────┬───────────────────────────────┘
                           │
7. 响应发布                 ▼
   ┌───────────────────────────────────────────────────────┐
   │                    MessageBus                         │
   │   await bus.publish_outbound(outbound_msg)           │
   └───────────────────────┬───────────────────────────────┘
                           │
8. 响应发送                 ▼
   ┌───────────────┐     ┌──────────────┐     ┌──────────┐
   │ OutboundMessage│────►│   Channel    │────►│   用户   │
   │   (数据结构)   │     │  (discord.py)│     │(Discord) │
   └───────────────┘     └──────────────┘     └──────────┘
```

### Tauri App 消息流

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Tauri App 消息流                                 │
└─────────────────────────────────────────────────────────────────────┘

1. 用户输入
   ┌──────────┐     POST /api/agents/default/chat     ┌──────────┐
   │  React   │──────────────────────────────────────►│ FastAPI  │
   │   UI     │     {"content": "hello"}              │  Server  │
   └──────────┘                                        └────┬─────┘
                                                            │
2. 消息处理                                                  ▼
   ┌───────────────────────────────────────────────────────────────┐
   │   POST /api/agents/{id}/chat                                  │
   │                                                               │
   │   inbound_msg = InboundMessage(                               │
   │       channel="desktop",                                      │
   │       sender_id="desktop_user",                               │
   │       chat_id=conversation_id,                                │
   │       content=request.content,                                │
   │   )                                                           │
   │   await bus.publish_inbound(inbound_msg)                      │
   └───────────────────────────────────────────────────────────────┘
                                                            │
3. SSE 事件推送                                             ▼
   ┌───────────────────────────────────────────────────────────────┐
   │   GET /api/stream (SSE 长连接)                                │
   │                                                               │
   │   async for event in bus.subscribe():                        │
   │       yield {                                                 │
   │           "event": "message:outbound",                        │
   │           "data": json.dumps(event["payload"])                │
   │       }                                                       │
   └───────────────────────────────────────────────────────────────┘
                                                            │
4. 前端接收                                                 ▼
   ┌───────────────────────────────────────────────────────────────┐
   │   React UI (EventSource)                                      │
   │                                                               │
   │   eventSource.addEventListener('message:outbound', (e) => {   │
   │       const data = JSON.parse(e.data)                         │
   │       setMessages(prev => [...prev, data])                    │
   │   })                                                          │
   └───────────────────────────────────────────────────────────────┘
```

---

## 目录结构

```
anyclaw/
├── anyclaw/                      # 主包
│   ├── agent/                    # Agent 系统
│   │   ├── loop.py               # 主处理循环 (AgentLoop)
│   │   ├── context.py            # 上下文构建器
│   │   ├── history.py            # 对话历史
│   │   ├── tool_loop.py          # 工具调用循环
│   │   └── tools/                # Agent 专用工具
│   │
│   ├── api/                      # HTTP API (sidecar 使用)
│   │   ├── server.py             # FastAPI 应用
│   │   ├── sse.py                # SSE 流式端点
│   │   ├── deps.py               # 依赖注入
│   │   └── routes/               # API 路由
│   │       ├── health.py         # 健康检查
│   │       ├── agents.py         # Agent 管理 + 聊天
│   │       ├── messages.py       # 消息 API
│   │       ├── skills.py         # 技能管理
│   │       ├── tasks.py          # 任务管理
│   │       └── config.py         # 配置管理
│   │
│   ├── bus/                      # 消息总线
│   │   ├── queue.py              # MessageBus (消息队列)
│   │   └── events.py             # 消息类型定义
│   │
│   ├── channels/                 # 频道实现
│   │   ├── base.py               # 频道基类
│   │   ├── cli.py                # CLI 频道
│   │   ├── discord.py            # Discord 频道
│   │   ├── feishu.py             # 飞书频道
│   │   └── manager.py            # 频道管理器
│   │
│   ├── core/                     # 核心服务
│   │   ├── serve.py              # ServeManager
│   │   └── daemon.py             # 守护进程管理
│   │
│   ├── cli/                      # 命令行接口
│   │   ├── app.py                # Typer 应用入口
│   │   ├── serve_cmd.py          # serve 命令
│   │   └── sidecar_cmd.py        # sidecar 命令
│   │
│   └── ...                       # 其他模块
│
└── tauri-app/                    # Tauri 桌面应用
    ├── src/                      # React 前端
    │   ├── App.tsx               # 主应用
    │   ├── components/           # UI 组件
    │   ├── hooks/                # React Hooks
    │   │   └── useSSE.ts         # SSE 连接 Hook
    │   └── lib/                  # 工具库
    │       ├── api.ts            # API 客户端
    │       └── sse.ts            # SSE 客户端
    │
    └── src-tauri/                # Rust 后端
        ├── src/lib.rs            # Tauri 命令
        └── tauri.conf.json       # Tauri 配置
```

---

## 配置管理

### 配置文件

```
~/.anyclaw/
├── config.json          # 主配置文件
├── workspace/           # 工作区
│   ├── SOUL.md         # Agent 人设
│   ├── USER.md         # 用户档案
│   └── memory/         # 记忆存储
└── logs/               # 日志目录
```

### Tauri 配置

```json
// tauri-app/src-tauri/settings.json (Tauri Store)
{
  "preferred_port": 62616   // Sidecar 监听端口
}
```

### 环境变量

```bash
# Python 路径 (可选)
export ANYCLAW_PYTHON=/path/to/python

# AnyClaw 目录 (可选)
export ANYCLAW_DIR=/path/to/anyclaw
```

---

## 启动流程

### Tauri App 启动流程

```
1. 用户点击 Tauri App 图标
        │
        ▼
2. Tauri Rust 初始化
   - 创建系统托盘
   - 初始化状态管理
   - 加载 settings.json
        │
        ▼
3. React 前端加载
   - 调用 get_sidecar_status 获取当前状态
   - 如果 status == "Running"，连接 SSE
   - 如果 status == "Stopped"，显示 "启动" 按钮
        │
        ▼
4. 用户点击 "启动" 按钮
        │
        ▼
5. Tauri 调用 start_sidecar 命令
   │
   ├─── find_anyclaw_dir()
   │    - 检查 ANYCLAW_DIR 环境变量
   │    - 搜索可执行文件相对路径
   │    - 检查当前工作目录
   │    - 检查常见安装位置
   │
   ├─── find_python(anyclaw_dir)
   │    - 检查 ANYCLAW_PYTHON 环境变量
   │    - 检查 Poetry 虚拟环境
   │    - 检查系统 Python
   │
   ├─── spawn sidecar process
   │    python -m anyclaw.cli.sidecar_cmd --port 62616
   │
   └─── wait_for_health(port, max_retries=30)
        - 每 500ms 检查一次 /api/health
        - 通过后更新状态为 "Running"
        │
        ▼
6. Sidecar 进程启动
   │
   ├─── 创建 ServeManager
   │    - 初始化 MessageBus
   │    - 初始化所有频道 (Discord, 飞书, CLI)
   │
   ├─── 启动 FastAPI
   │    - 监听端口 62616
   │    - 注册所有 API 路由
   │
   └─── 启动频道服务
        - Discord bot 连接
        - 飞书 bot 连接
        │
        ▼
7. 前端连接 SSE
   - EventSource 连接 /api/stream
   - 监听 message:outbound 事件
   - 更新 UI 显示响应
```

### 命令行启动流程

```bash
# 方式 1: 后台服务模式 (无 HTTP API)
cd anyclaw
poetry run anyclaw serve

# 方式 2: Sidecar 模式 (有 HTTP API)
cd anyclaw
poetry run anyclaw sidecar --port 62616

# 方式 3: 通过 Tauri App
# - Tauri 自动启动 sidecar
```

---

## API 参考

### REST API

#### 健康检查
```http
GET /api/health

Response:
{
  "status": "ok",
  "uptime_seconds": 120,
  "version": "0.1.0",
  "channels": ["cli", "discord"],
  "messages_processed": 5
}
```

#### 发送消息
```http
POST /api/agents/{agent_id}/chat
Content-Type: application/json

{
  "content": "你好",
  "conversation_id": "conv_123"  // 可选
}

Response:
{
  "message_id": "msg_1234567890",
  "status": "ok"
}
```

#### Agent 列表
```http
GET /api/agents

Response:
[
  {
    "id": "default",
    "name": "Default Agent",
    "model": "glm-4.7",
    "description": "Default AnyClaw agent",
    "is_active": true
  }
]
```

### SSE 事件

```javascript
// 连接 SSE
const eventSource = new EventSource('http://127.0.0.1:62616/api/stream')

// 事件类型
eventSource.addEventListener('message:outbound', (e) => {
  // Agent 响应
  const data = JSON.parse(e.data)
  // { id, content, channel, chat_id }
})

eventSource.addEventListener('agent:thinking', (e) => {
  // Agent 正在思考
})

eventSource.addEventListener('tool:start', (e) => {
  // 工具调用开始
})

eventSource.addEventListener('tool:complete', (e) => {
  // 工具调用完成
})

eventSource.addEventListener('error', (e) => {
  // 错误事件
})
```

---

## 故障排除

### 常见问题

#### 1. Tauri App 显示 "后端服务未运行"

**原因**: Sidecar 未启动

**解决**: 点击 "启动" 按钮，或手动启动 sidecar:
```bash
cd anyclaw
poetry run anyclaw sidecar --port 62616
```

#### 2. SSE 连接错误

**原因**: CORS 配置问题或端口不匹配

**解决**:
- 检查 settings.json 中的 preferred_port
- 确保 sidecar 使用正确的端口启动

#### 3. Discord 重复回复

**原因**: 多个 sidecar 进程同时运行

**解决**:
```bash
# 查看所有 sidecar 进程
ps aux | grep sidecar

# 停止所有 sidecar
pkill -f sidecar_cmd

# 重新启动一个
poetry run anyclaw sidecar --port 62616
```

#### 4. 找不到 Python 路径

**原因**: Tauri 无法定位 Poetry 虚拟环境

**解决**:
```bash
# 设置环境变量
export ANYCLAW_PYTHON=/path/to/poetry/venv/bin/python

# 或在 sidecar_cmd 启动时指定
poetry run python -m anyclaw.cli.sidecar_cmd --port 62616
```

---

## 总结

| 组件 | 启动命令 | HTTP API | 频道服务 | 用途 |
|------|----------|----------|----------|------|
| **serve** | `anyclaw serve` | ❌ | ✅ | 后台机器人服务 |
| **sidecar** | `anyclaw sidecar` | ✅ | ✅ | 桌面应用后端 |
| **Tauri App** | `npm run tauri:dev` | - | - | 桌面应用前端 |

**最佳实践**: 只运行 `sidecar`，即可同时支持桌面应用和所有频道服务。
