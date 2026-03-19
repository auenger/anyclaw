# AnyClaw 桌面应用集成方案评估

> 基于对 YouClaw (Tauri + React) 架构的分析，评估将 AnyClaw 作为服务层，上层仿制 YouClaw 做 GUI 应用的可行性

## 📋 目录

1. [架构对比](#架构对比)
2. [YouClaw 关键设计](#youclaw-关键设计)
3. [集成可行性分析](#集成可行性分析)
4. [技术方案](#技术方案)
5. [实施路线图](#实施路线图)
6. [风险与挑战](#风险与挑战)
7. [推荐方案](#推荐方案)

---

## 🏗️ 架构对比

### YouClaw 架构

```
┌──────────────────────────────────────────────────────┐
│                Tauri 2 (Rust Shell)                   │
│   ┌──────────────┐    ┌────────────────────────────┐ │
│   │   WebView     │    │   Bun Sidecar              │ │
│   │  Vite+React   │◄──►  Hono API Server           │ │
│   │  shadcn/ui    │ HTTP│  Claude Agent SDK         │ │
│   │               │ SSE │  bun:sqlite               │ │
│   └──────────────┘    └────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
         │                        │
    Tauri Store              EventBus
   (settings)          ┌────────┴────────────┐
                        │                     │
                   Web / API         Multi-Channel
                              ┌───────┼───────┐
                           Telegram DingTalk Feishu
                              QQ    WeCom
                                     │
                              Browser Automation
                               (Playwright)
```

**技术栈**：
- **桌面壳**: Tauri 2 (Rust)
- **前端**: Vite + React + shadcn/ui + Tailwind CSS
- **后端**: Bun + Hono API Server + bun:sqlite
- **Agent SDK**: `@anthropic-ai/claude-agent-sdk`
- **打包大小**: ~27 MB (vs Electron ~338 MB)

### AnyClaw 架构

```
┌──────────────────────────────────────────────────────┐
│                  CLI / Daemon Mode                     │
│                                                       │
│   ┌──────────────┐    ┌────────────────────────────┐ │
│   │   Channels   │    │      Agent Loop            │ │
│   │  Discord     │◄──►  (Multi-Agent, MCP)        │ │
│   │  Feishu      │ Msg │  Session Manager          │ │
│   │  CLI         │ Bus │  Skills System            │ │
│   └──────────────┘    └────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
                        │
                   MessageBus
                  ┌────┴────┐
                  │         │
              CronService  SubAgent
```

**技术栈**：
- **核心**: Python 3.10+
- **包管理**: Poetry
- **配置**: Pydantic + Pydantic Settings
- **CLI**: Typer + Rich
- **模型适配**: LiteLLM (支持多提供商)

---

## 🔑 YouClaw 关键设计

### 1. Sidecar 进程管理

YouClaw 使用 Tauri 的 `tauri-plugin-shell` 来管理 Bun sidecar 进程：

```rust
// src-tauri/src/lib.rs
struct SidecarState(Mutex<Option<tauri_plugin_shell::process::CommandChild>>);

fn spawn_sidecar(app: &AppHandle) -> Result<u16, String> {
    // 1. 从 Tauri Store 读取配置
    let port: u16 = app.store("settings.json").ok()
        .and_then(|store| store.get("preferred_port"))
        .unwrap_or(62601);

    // 2. 设置环境变量
    let mut env_vars: Vec<(String, String)> = vec![];
    env_vars.push(("PORT".into(), port.to_string()));

    // 3. 补充 PATH (Finder/Explorer 启动时 PATH 较少)
    let mut extra_paths: Vec<String> = vec![
        format!("{}/.bun/bin", home),
        format!("{}/.cargo/bin", home),
        "/usr/local/bin".into(),
        "/opt/homebrew/bin".into(),
    ];

    // 4. 启动 sidecar 进程
    let sidecar = tauri_plugin_shell::process::Command::new_sidecar("bun")
        .args(["run", "src/index.ts"])
        .envs(env_vars)
        .spawn()
        .map_err(|e| format!("Failed to spawn sidecar: {}", e))?;

    *sidecar_state.0.lock().unwrap() = Some(sidecar);
    Ok(port)
}
```

**关键点**：
- 使用 Tauri Store 持久化配置（端口、数据目录等）
- 自动补全 PATH（支持 bun, cargo, nvm 等常见路径）
- 跨平台支持（Windows 检测 Git Bash 和 Node.js 路径）
- 进程生命周期绑定到 App（退出时自动终止）

### 2. HTTP API + SSE

YouClaw 使用 Hono (Bun) 提供 REST API 和 SSE 流式更新：

```typescript
// src/routes/index.ts
export function createApp(deps: AppDeps) {
  const app = new Hono()

  // CORS — 允许 Tauri WebView 和 Vite Dev Server
  app.use('/*', cors({
    origin: [
      'http://localhost:5173',
      `http://localhost:${getEnv().PORT}`,
      'tauri://localhost',        // macOS
      'http://tauri.localhost',   // Windows
      'https://tauri.localhost',  // Linux
    ],
    allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
    allowHeaders: ['Content-Type'],
  }))

  // API 路由
  app.route('/api', health)
  app.route('/api', createAgentsRoutes(agentManager))
  app.route('/api', createMessagesRoutes(agentManager, agentQueue, router))
  app.route('/api', createStreamRoutes(eventBus))  // SSE 流式

  return app
}
```

**API 设计**：
- `/api/health` - 健康检查
- `/api/agents` - Agent 管理 (CRUD)
- `/api/messages` - 消息发送
- `/api/stream` - SSE 流式事件（Agent 响应、任务进度等）
- `/api/skills` - Skills 管理
- `/api/memory` - 记忆管理
- `/api/tasks` - 定时任务
- `/api/channels` - 通道管理
- `/api/settings` - 配置管理

### 3. 前端架构

YouClaw 使用 React + shadcn/ui + Tailwind CSS：

```typescript
// web/src/pages/Chat.tsx
export default function Chat() {
  const { agents } = useAgents()
  const { sendMessage, streamMessage } = useMessages()
  const [messages, setMessages] = useState<Message[]>([])

  // SSE 流式接收
  useEffect(() => {
    const eventSource = new EventSource('/api/stream')
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'stream') {
        setMessages(prev => [...prev, data])
      }
    }
    return () => eventSource.close()
  }, [])

  return (
    <div className="flex h-screen">
      <Sidebar agents={agents} />
      <ChatWindow messages={messages} onSend={sendMessage} />
    </div>
  )
}
```

**UI 组件** (shadcn/ui)：
- `Button`, `Input`, `Textarea` - 基础组件
- `Dialog`, `Sheet` - 模态框
- `Table`, `Card`, `Badge` - 数据展示
- `Select`, `Switch`, `Slider` - 表单控件
- `Toast`, `Alert` - 提示组件

### 4. 系统托盘集成

YouClaw 使用 Tauri 的系统托盘：

```rust
// src-tauri/src/lib.rs
fn create_tray_icon(app: &AppHandle) {
  let tray_icon = TrayIconBuilder::new()
    .on_tray_icon_event(|app, event| {
      match event {
        TrayIconEvent::Click {
          button: MouseButton::Left,
          button_state: MouseButtonState::Up,
          ..
        } => {
          // 单击显示/隐藏窗口
          if let Some(window) = app.get_webview_window("main") {
            if window.is_visible().unwrap() {
              window.hide().unwrap();
            } else {
              window.show().unwrap();
              window.set_focus().unwrap();
            }
          }
        }
        TrayIconEvent::DoubleClick { .. } => {
          // 双击启动/停止 sidecar
          toggle_sidecar(app);
        }
        _ => {}
      }
    })
    .menu(&Menu::with_items(app, &[
      &MenuItem::with_id(app, "show", "Show", true, None::<&str>),
      &MenuItem::with_id(app, "hide", "Hide", true, None::<&str>),
      PredefinedMenuItem::separator(),
      &MenuItem::with_id(app, "restart", "Restart Backend", true, None::<&str>),
      &MenuItem::with_id(app, "stop", "Stop Backend", true, None::<&str>),
      PredefinedMenuItem::separator(),
      &MenuItem::with_id(app, "quit", "Quit", true, None::<&str>),
    ]))
    .icon(icon)
    .build(app)
    .unwrap();
}
```

**托盘功能**：
- 单击显示/隐藏窗口
- 双击启动/停止 sidecar
- 右键菜单（显示/隐藏、重启、停止、退出）
- 状态指示（运行中/已停止）

---

## ✅ 集成可行性分析

### ✅ 直接复用的部分

1. **Tauri Shell 框架**
   - ✅ Tauri 可以启动和管理 Python 进程作为 sidecar
   - ✅ 跨平台支持（macOS, Windows, Linux）
   - ✅ WebView + Sidecar 架构通用

2. **前端 UI 组件**
   - ✅ 可以直接使用 shadcn/ui 组件库
   - ✅ React + Tailwind CSS 技术栈成熟
   - ✅ 响应式设计，适配不同屏幕尺寸

3. **配置管理**
   - ✅ Tauri Store 可以存储用户配置
   - ✅ AnyClaw 的 Pydantic Settings 可以通过环境变量加载
   - ✅ 配置同步机制（Tauri Store → Env → Pydantic）

4. **进程生命周期**
   - ✅ AnyClaw 已有 Daemon 模式（参考 `anyclaw/anyclaw/cli/serve_cmd.py`）
   - ✅ 可以包装成 sidecar 进程
   - ✅ PID 文件管理已实现

### 🚧 需要改造的部分

#### 1. HTTP API 层

**现状**：AnyClaw 没有暴露 HTTP API

**改造方案**：
```python
# anyclaw/anyclaw/api/server.py
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
from anyclaw.core.serve import ServeManager
import json
import asyncio

app = FastAPI()

# 注入 ServeManager
serve_manager: ServeManager = None

@app.on_event("startup")
async def startup():
    global serve_manager
    serve_manager = ServeManager()
    serve_manager.initialize()
    await serve_manager.start()

@app.get("/api/health")
async def health():
    return {"status": "ok", "uptime": serve_manager.uptime_seconds}

@app.get("/api/agents")
async def list_agents():
    # 从 AgentManager 获取 Agent 列表
    return {"agents": []}

@app.post("/api/messages")
async def send_message(message: dict):
    # 通过 MessageBus 发送消息
    serve_manager.bus.publish(InboundMessage(...))
    return {"message_id": "..."}

@app.get("/api/stream")
async def stream_events():
    async def event_generator():
        # 订阅 EventBus 事件
        async for event in serve_manager.bus.subscribe():
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**技术选型**：
- **FastAPI**: 最成熟的 Python Web 框架，支持异步、自动生成文档
- **备选**: Hono (Python 版本，但生态不成熟)

#### 2. SSE 流式事件

**现状**：AnyClaw 有 MessageBus，但没有 SSE 端点

**改造方案**：
```python
# anyclaw/anyclaw/api/sse.py
from fastapi import Request
from sse_starlette import EventSourceResponse

@app.get("/api/stream")
async def stream(request: Request):
    async def event_publisher():
        # 订阅所有事件
        async for event in serve_manager.bus.subscribe():
            if await request.is_disconnected():
                break
            yield {
                "event": event["type"],
                "data": json.dumps(event["payload"]),
            }

    return EventSourceResponse(event_publisher())
```

**事件类型**：
- `message:inbound` - 收到新消息
- `message:outbound` - 发送回复
- `tool:start` - 工具调用开始
- `tool:complete` - 工具调用完成
- `agent:thinking` - Agent 思考中
- `cron:scheduled` - 定时任务触发

#### 3. 数据库层

**现状**：AnyClaw 使用文件系统存储（JSONL、Markdown）

**改造方案**：
```python
# anyclaw/anyclaw/db/store.py
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect("data/anyclaw.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# 初始化表
def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                config_json TEXT NOT NULL,
                created_at INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
```

**迁移策略**：
- 保留文件系统作为可选存储（向后兼容）
- SQLite 作为主存储（支持复杂查询）
- 提供数据迁移脚本

#### 4. 进程管理改造

**现状**：AnyClaw Daemon 模式使用 `fork()` 和 PID 文件

**改造方案**：
```python
# anyclaw/anyclaw/cli/sidecar_cmd.py
import asyncio
import signal
import sys
from pathlib import Path

import typer
from rich.console import Console

from anyclaw.core.serve import ServeManager
from anyclaw.config.loader import get_config

app = typer.Typer()
console = Console()

@app.command()
def sidecar(
    port: int = typer.Option(62601, "--port", "-p"),
    data_dir: str = typer.Option(None, "--data-dir", "-d"),
):
    """Run AnyClaw as Tauri sidecar.

    This mode starts:
    1. FastAPI HTTP server (port)
    2. Multi-channel service (Discord, Feishu, etc.)
    3. SSE event stream
    """
    # Setup logging to file (for Tauri to read)
    log_file = Path(data_dir) / "logs" / "sidecar.log" if data_dir else Path.home() / ".anyclaw" / "logs" / "sidecar.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Create serve manager
    config = get_config()
    manager = ServeManager(config=config)

    # Graceful shutdown
    shutdown_event = asyncio.Event()

    def signal_handler(sig, frame):
        console.print("\n[yellow]Shutting down...[/yellow]")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run both API server and channel service
    async def run_all():
        manager.initialize()

        # Start API server
        import uvicorn
        from anyclaw.api.server import app
        from anyclaw.api import set_serve_manager

        set_serve_manager(manager)

        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=port,
            log_file=str(log_file),
        )
        server = uvicorn.Server(config)

        # Start both
        await asyncio.gather(
            manager.start(),
            server.serve(),
        )

    asyncio.run(run_all())

if __name__ == "__main__":
    app()
```

**集成到 Tauri**：
```rust
// src-tauri/src/lib.rs
fn spawn_python_sidecar(app: &AppHandle) -> Result<u16, String> {
    let port: u16 = app.store("settings.json").ok()
        .and_then(|store| store.get("preferred_port"))
        .unwrap_or(62601);

    // 启动 Python sidecar
    let sidecar = tauri_plugin_shell::process::Command::new_sidecar("python")
        .args(["-m", "anyclaw.cli.sidecar_cmd"])
        .args(["--port", &port.to_string()])
        .env("PYTHONUNBUFFERED", "1")  // 禁用缓冲
        .spawn()
        .map_err(|e| format!("Failed to spawn Python sidecar: {}", e))?;

    *sidecar_state.0.lock().unwrap() = Some(sidecar);
    Ok(port)
}
```

---

## 🛠️ 技术方案

### 方案 A：Python Sidecar + Tauri (推荐)

**架构**：
```
┌──────────────────────────────────────────────────────┐
│                Tauri 2 (Rust Shell)                   │
│   ┌──────────────┐    ┌────────────────────────────┐ │
│   │   WebView     │    │   Python Sidecar          │ │
│   │  Vite+React   │◄──►  FastAPI Server           │ │
│   │  shadcn/ui    │ HTTP│  ServeManager            │ │
│   │               │ SSE │  MessageBus              │ │
│   └──────────────┘    └────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
         │                        │
    Tauri Store          Multi-Channel (AnyClaw)
   (settings)          ┌───────┼───────┐
                        │       │       │
                    Discord  Feishu  CLI
```

**技术栈**：
- **Tauri Shell**: Rust 2.x
- **前端**: React + Vite + shadcn/ui + Tailwind CSS
- **Sidecar**: Python 3.10+ + FastAPI + uvicorn
- **数据**: SQLite + 文件系统（可选）
- **进程管理**: tauri-plugin-shell

**优点**：
- ✅ 复用 AnyClaw 现有功能（多通道、MCP、Cron、SubAgent）
- ✅ Tauri 打包体积小（~30-50 MB，包含 Python 运行时）
- ✅ 跨平台支持良好
- ✅ 开发效率高（Python + React 都很成熟）

**缺点**：
- ⚠️ 需要打包 Python 运行时（增加 ~30-40 MB）
- ⚠️ 需要 FastAPI 开发工作
- ⚠️ SSE 流式需要额外开发

**打包体积预估**：
- Tauri Shell: ~5 MB
- Python 运行时: ~30-40 MB
- 前端资源: ~2-3 MB
- **总计**: ~40-50 MB（vs YouClaw 27 MB，但远小于 Electron 的 338 MB）

---

## 📅 实施路线图

### 阶段 1：API 层开发 (2-3 天)

**目标**：暴露 HTTP API 和 SSE 流

**任务**：
- [ ] 创建 `anyclaw/api/` 目录
- [ ] 实现 FastAPI 服务器 (`server.py`)
- [ ] 实现 SSE 端点 (`sse.py`)
- [ ] 实现核心 API 路由
  - [ ] `/api/health` - 健康检查
  - [ ] `/api/agents` - Agent 管理
  - [ ] `/api/messages` - 消息发送
  - [ ] `/api/stream` - SSE 流
- [ ] 编写 API 文档（Swagger）

**依赖**：
```toml
[tool.poetry.dependencies]
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
sse-starlette = "^2.1.0"
pydantic = "^2.12.0"
```

### 阶段 2：数据持久化 (1-2 天)

**目标**：实现 SQLite 数据存储

**任务**：
- [ ] 创建 `anyclaw/db/` 目录
- [ ] 实现数据库初始化 (`store.py`)
- [ ] 设计数据表（agents, messages, settings, logs）
- [ ] 实现数据访问层 (DAO)
- [ ] 编写数据迁移脚本（文件系统 → SQLite）

### 阶段 3：Sidecar 模式 (1 天)

**目标**：支持作为 Tauri sidecar 运行

**任务**：
- [ ] 创建 `anyclaw/cli/sidecar_cmd.py`
- [ ] 实现优雅关闭（SIGINT/SIGTERM）
- [ ] 实现日志重定向到文件
- [ ] 添加 `--port` 和 `--data-dir` 参数

### 阶段 4：Tauri Shell (3-4 天)

**目标**：创建 Tauri 桌面应用壳

**任务**：
- [ ] 初始化 Tauri 项目 (`npm create tauri-app@latest`)
- [ ] 配置 shadcn/ui 组件库
- [ ] 实现 sidecar 进程管理（启动/停止/重启）
- [ ] 实现系统托盘（macOS/Windows/Linux）
- [ ] 实现配置持久化（Tauri Store）
- [ ] 实现自动更新（Tauri Updater）

### 阶段 5：前端开发 (5-7 天)

**目标**：实现完整 GUI

**任务**：
- [ ] 实现主页（Agent 列表 + 聊天窗口）
- [ ] 实现 Agent 配置页面
- [ ] 实现 Skills 管理页面
- [ ] 实现 Memory 管理页面
- [ ] 实现定时任务管理页面
- [ ] 实现通道管理页面
- [ ] 实现系统日志页面
- [ ] 实现设置页面（API Key、端口等）

### 阶段 6：集成测试 (2-3 天)

**目标**：端到端测试和优化

**任务**：
- [ ] 编写 E2E 测试（Playwright）
- [ ] 性能优化（启动速度、内存占用）
- [ ] 跨平台测试（macOS, Windows, Linux）
- [ ] 用户文档编写

**总计**：14-20 天

---

## ⚠️ 风险与挑战

### 1. Python 运行时打包

**挑战**：Tauri 需要 Python 运行时在目标系统上可用

**解决方案**：
- 方案 A：使用 PyO3（Python 嵌入到 Rust，减少依赖）
- 方案 B：打包 Python 运行时到 App Bundle（macOS .app, Windows .exe, Linux .AppImage）
- 方案 C：依赖系统 Python（提供安装指南，类似 VS Code）

**推荐**：方案 B，使用 `pyoxidizer` 或 `pyinstaller` 打包

### 2. SSE 流式性能

**挑战**：大量 Agent 并发时 SSE 可能出现性能瓶颈

**解决方案**：
- 使用 Redis Pub/Sub 作为消息代理（支持水平扩展）
- 使用 WebSocket 替代 SSE（双向通信，更高效）
- 限制每个客户端的并发流数量

### 3. 进程间通信

**挑战**：Tauri (Rust) 和 Python sidecar 之间的通信

**解决方案**：
- HTTP API：简单可靠，适合所有平台
- Named Pipes (Windows) / Unix Sockets (macOS/Linux)：性能更好，但实现复杂
- 共享内存 + 文件锁：最快，但复杂度高

**推荐**：HTTP API（简单、跨平台、调试方便）

### 4. 数据一致性

**挑战**：文件系统和 SQLite 之间的数据同步

**解决方案**：
- 迁移策略：一次性迁移文件系统数据到 SQLite
- 读写策略：优先使用 SQLite，文件系统作为备份
- 同步机制：定期同步 SQLite 到文件系统（用于 Git 版本控制）

### 5. 跨平台兼容性

**挑战**：Windows, macOS, Linux 的进程管理差异

**解决方案**：
- Tauri 提供抽象层（tauri-plugin-shell）
- 使用跨平台库（`psutil` 用于进程管理）
- 平台特定代码（条件编译）

---

## 🎯 推荐方案

### 最终推荐：**方案 A (Python Sidecar + Tauri)**

**理由**：

1. **复用度高**
   - ✅ 100% 复用 AnyClaw 现有功能
   - ✅ 最少改造（只需添加 HTTP API 层）
   - ✅ 向后兼容（保留 CLI 和 Daemon 模式）

2. **开发效率高**
   - ✅ Python 生态成熟（FastAPI, Pydantic）
   - ✅ Tauri 文档完善，社区活跃
   - ✅ shadcn/ui 组件库开箱即用

3. **用户体验好**
   - ✅ 轻量级（40-50 MB，远小于 Electron）
   - ✅ 原生性能（Rust shell + WebView）
   - ✅ 系统托盘支持（后台运行）

4. **维护成本低**
   - ✅ 单一代码库（Python + React）
   - ✅ 自动更新支持（Tauri Updater）
   - ✅ 跨平台打包简单

### 实施优先级

**P0 (必须)**：
1. HTTP API 层（FastAPI + uvicorn）
2. SSE 流式事件
3. Tauri Shell + sidecar 进程管理
4. 基础前端页面（聊天窗口 + Agent 列表）

**P1 (重要)**：
5. SQLite 数据持久化
6. 系统托盘集成
7. 配置管理（API Key、端口等）
8. Skills 管理

**P2 (优化)**：
9. Memory 管理
10. 定时任务管理
11. 通道管理
12. 日志查看

### 快速启动方案

如果想在 1 周内看到效果：

**Day 1-2**: 实现 FastAPI API 层 + SSE
**Day 3-4**: 实现 Tauri Shell（复用 YouClaw 代码）
**Day 5-7**: 实现前端基础页面（复用 shadcn/ui + YouClaw 布局）

**最小可行产品 (MVP)**：
- ✅ 聊天窗口（发送消息 + 接收回复）
- ✅ Agent 列表（切换 Agent）
- ✅ 配置管理（API Key、模型）
- ✅ 系统托盘（启动/停止）

### 长期演进方向

**Phase 2 (1-2 个月)**：
- Skills 市场（在线下载）
- 多人协作（云端同步）
- 浏览器自动化集成（Playwright）

**Phase 3 (3-6 个月)**：
- Agent 编排（Multi-Agent 工作流）
- 知识库 RAG（向量检索）
- 插件系统（第三方扩展）

---

## 📚 参考资源

### YouClaw 参考代码

```
~/mycode/AnyClaw/reference/youclaw/
├── src-tauri/src/lib.rs         # Rust shell 实现
├── src/index.ts                 # 后端入口
├── src/routes/                  # API 路由
├── web/src/pages/               # 前端页面
└── web/src/components/          # UI 组件
```

### 技术文档

- [Tauri 2 Documentation](https://v2.tauri.app/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [SSE (Server-Sent Events)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

### 类似项目

- **Cursor**: Tauri + React（代码编辑器）
- **Obsidian**: Electron + TypeScript（笔记应用）
- **Linear**: React + Rust（项目管理）

---

## 🤔 总结

**可行性**：✅ **高度可行**

**关键优势**：
1. 100% 复用 AnyClaw 现有功能
2. Tauri 轻量级（vs Electron）
3. 跨平台支持良好
4. 开发效率高

**主要挑战**：
1. Python 运行时打包（有解决方案）
2. HTTP API 层开发（工作量不大）
3. SSE 流式事件（技术成熟）

**推荐方案**：Python Sidecar + Tauri

**预计时间**：14-20 天（完成 MVP）

**下一步行动**：
1. 创建 `anyclaw/api/` 目录
2. 实现 FastAPI 服务器
3. 初始化 Tauri 项目
4. 复制 YouClaw 前端代码作为起点

---

**记录时间**: 2026-03-20 04:00 (Asia/Shanghai)
**状态**: ✅ 评估完成，准备实施
