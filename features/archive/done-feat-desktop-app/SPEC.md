# feat-desktop-app

**状态**: 🔄 进行中 (80%)
**完成时间**: 2026-03-20 (Phase 1-2)
**优先级**: 75
**大小**: XL
**提交**: 02e5a26, af405e3

## 描述

实现 Tauri 跨平台桌面应用，采用 FastAPI + SSE 后端、Tauri 2 Shell 中间层、React 前端的三层架构。

## 价值点

1. **跨平台桌面应用**
   - macOS / Windows / Linux 支持
   - 原生系统集成
   - 系统托盘

2. **FastAPI + SSE 后端**
   - 13 个 API 端点
   - SSE 流式消息推送
   - Sidecar 进程管理

3. **Tauri 2 Shell**
   - Rust 后端
   - Python Sidecar 进程管理
   - 跨平台 Python 路径检测

4. **React 前端**
   - React 18 + Vite 5
   - Tailwind CSS + shadcn/ui
   - 聊天界面 + Agent 管理

## 实现文件

### 后端 (Python)

- `anyclaw/api/__init__.py` - API 模块导出
- `anyclaw/api/server.py` - FastAPI 服务器
- `anyclaw/api/sse.py` - SSE 流式端点
- `anyclaw/api/deps.py` - 依赖注入
- `anyclaw/api/routes/health.py` - 健康检查
- `anyclaw/api/routes/agents.py` - Agent 管理
- `anyclaw/api/routes/messages.py` - 消息处理
- `anyclaw/api/routes/skills.py` - 技能管理
- `anyclaw/api/routes/tasks.py` - 任务管理
- `anyclaw/cli/sidecar_cmd.py` - Sidecar 命令

### 桌面应用 (Tauri + React)

- `tauri-app/src-tauri/src/lib.rs` - Rust Shell 实现
- `tauri-app/src-tauri/src/main.rs` - 入口
- `tauri-app/src-tauri/tauri.conf.json` - Tauri 配置
- `tauri-app/src/App.tsx` - React 主应用
- `tauri-app/src/components/ui/` - UI 组件
- `tauri-app/src/index.css` - Tailwind 样式
- `tauri-app/package.json` - npm 依赖
- `tauri-app/vite.config.ts` - Vite 配置
- `tauri-app/tailwind.config.js` - Tailwind 配置

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Tauri Desktop App                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              React Frontend (Phase 3)                │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │  Chat   │ │ Agents  │ │ Skills  │ │ Settings│   │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   │   │
│  │       │           │           │           │         │   │
│  │       └───────────┴─────┬─────┴───────────┘         │   │
│  │                         │ SSE                       │   │
│  └─────────────────────────┼───────────────────────────┘   │
│                            │                               │
│  ┌─────────────────────────▼───────────────────────────┐   │
│  │           Tauri Shell (Rust) (Phase 2)               │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  Sidecar Manager                             │    │   │
│  │  │  - start_sidecar()   - kill_sidecar()       │    │   │
│  │  │  - wait_for_health() - restart_sidecar()    │    │   │
│  │  │  - find_python()     - System Tray          │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            │ spawn                         │
│  ┌─────────────────────────▼───────────────────────────┐   │
│  │         Python Sidecar (FastAPI) (Phase 1)           │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │ /health │ │ /agents │ │/messages│ │  /sse   │   │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐              │   │
│  │  │ /skills │ │ /tasks  │ │ /config │              │   │
│  │  └─────────┘ └─────────┘ └─────────┘              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/agents` | GET | 列出 Agents |
| `/api/agents/{id}` | GET | 获取 Agent |
| `/api/agents/{id}/chat` | POST | 发送消息 |
| `/api/stream` | GET | SSE 流式消息 |
| `/api/skills` | GET | 列出技能 |
| `/api/skills/{id}` | POST | 执行技能 |
| `/api/tasks` | GET | 列出任务 |
| `/api/tasks/{id}` | GET | 获取任务状态 |
| `/api/config` | GET/PUT | 获取/设置配置 |

## 使用方式

### 开发模式

```bash
# 启动 Sidecar (Python 后端)
cd anyclaw
poetry run python -m anyclaw sidecar --port 62601

# 启动 Tauri 开发模式
cd tauri-app
npm install
npm run tauri:dev
```

### 生产构建

```bash
cd tauri-app
npm run tauri:build
```

## Tauri Commands

```rust
// Rust Shell 命令
#[tauri::command]
fn start_sidecar() -> Result<(), String>;

#[tauri::command]
fn stop_sidecar() -> Result<(), String>;

#[tauri::command]
fn restart_sidecar() -> Result<(), String>;

#[tauri::command]
fn get_settings() -> Result<Settings, String>;

#[tauri::command]
fn set_settings(settings: Settings) -> Result<(), String>;
```

## 依赖

### Python

```toml
fastapi = ">=0.115.0"
uvicorn = ">=0.32.0"
sse-starlette = ">=2.1.0"
httpx = ">=0.25.0"
```

### Node.js

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "@tauri-apps/api": "^2.0.0",
  "tailwindcss": "^3.4.0",
  "lucide-react": "^0.300.0",
  "clsx": "^2.0.0",
  "tailwind-merge": "^2.0.0"
}
```

## 进度

| Phase | 描述 | 状态 | 进度 |
|-------|------|------|------|
| Phase 1 | FastAPI + SSE | ✅ 完成 | 100% |
| Phase 2 | Tauri Shell | ✅ 完成 | 100% |
| Phase 3 | React Frontend | 🔄 进行中 | 80% |

## 待完成

- [ ] SSE 实时消息流
- [ ] Settings 页面
- [ ] Skills 管理页面
- [ ] Tasks 页面
- [ ] 正式图标
- [ ] 跨平台测试

## 测试

```
anyclaw/test_api.py
```
