# 实施计划 Phase 2: Tauri Shell

> **目标**：创建 Tauri 桌面应用壳，集成 Python sidecar 进程，提供系统托盘和原生窗口管理

## 📋 概述

**时间估算**：3-4 天
**优先级**：P0（必须）
**依赖**：Phase 1 (FastAPI + SSE) 完成

## 🎯 核心目标

1. ✅ 初始化 Tauri 2 项目
2. ✅ 实现系统托盘（macOS/Windows/Linux）
3. ✅ 实现进程管理（启动/停止/重启 Python sidecar）
4. ✅ 实现配置持久化（Tauri Store）
5. ✅ 实现自动更新（Tauri Updater）

---

## 📂 目录结构

```
tauri-app/                        # Tauri 应用根目录
├── src-tauri/                     # Rust 后端
│   ├── src/
│   │   ├── lib.rs                # Tauri 插件注册
│   │   ├── main.rs               # Rust 入口
│   │   ├── sidecar.rs            # Python sidecar 进程管理
│   │   └── tray.rs               # 系统托盘
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   └── build.rs
├── src/                          # React 前端（占位，Phase 3 完善）
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── web/                          # 前端资源（可选）
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

## 🔧 技术栈

### 前端依赖

```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "@tauri-apps/api": "^2.0.0",
    "@tauri-apps/plugin-shell": "^2.0.0",
    "@tauri-apps/plugin-store": "^2.0.0",
    "@tauri-apps/plugin-updater": "^2.0.0"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2.0.0",
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "@types/react": "^18.3.0"
  }
}
```

### Rust 依赖

```toml
[dependencies]
tauri = { version = "2", features = ["tray-icon", "image-png", "devtools"] }
tauri-plugin-shell = "2"
tauri-plugin-store = "2"
tauri-plugin-window-state = "2"
tauri-plugin-updater = "2"
tauri-plugin-process = "2"
tauri-plugin-dialog = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tokio = { version = "1", features = ["time"] }
log = "0.4"
```

---

## 📝 详细任务清单

### Task 2.1: 初始化 Tauri 项目

**命令**：

```bash
# 创建 Tauri 项目
cd ~/mycode/AnyClaw
npm create tauri-app@latest tauri-app -- --template vanilla-ts

# 进入项目目录
cd tauri-app

# 安装依赖
npm install
```

**文件**：`tauri-app/package.json`

```json
{
  "name": "anyclaw-desktop",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "tauri": "tauri",
    "tauri:dev": "tauri dev",
    "tauri:build": "tauri build"
  },
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "@tauri-apps/api": "^2.0.0"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2.0.0",
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0"
  }
}
```

---

### Task 2.2: 配置 Tauri

**文件**：`tauri-app/src-tauri/tauri.conf.json`

```json
{
  "$schema": "https://schema.tauri.app/config/2.0.0",
  "productName": "AnyClaw",
  "version": "0.1.0",
  "identifier": "com.anyclaw.desktop",
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devUrl": "http://localhost:5173",
    "frontendDist": "../dist"
  },
  "app": {
    "withGlobalTauri": true,
    "windows": [
      {
        "title": "AnyClaw",
        "width": 1200,
        "height": 800,
        "resizable": true,
        "fullscreen": false,
        "label": "main",
        "titleBarStyle": "Overlay",
        "hiddenTitle": true
      }
    ],
    "security": {
      "csp": null
    },
    "trayIcon": {
      "iconPath": "icons/tray.png",
      "iconAsTemplate": true
    }
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ]
  },
  "plugins": {
    "shell": {
      "open": true
    },
    "store": {
      "autoSave": true
    },
    "updater": {
      "endpoints": [
        "https://github.com/your-org/AnyClaw/releases/latest/download/latest.json"
      ],
      "dialog": true,
      "pubkey": "YOUR_PUBLIC_KEY"
    }
  }
}
```

---

### Task 2.3: 实现 Rust 结构体

**文件**：`tauri-app/src-tauri/src/lib.rs`

```rust
use serde::Serialize;
use tauri::{AppHandle, Emitter, Listener, Manager};
use tauri_plugin_store::StoreExt;
use std::sync::{Arc, Mutex};
use std::time::Duration;

/// Sidecar 进程状态
#[derive(Clone, Serialize)]
pub enum SidecarStatus {
    Stopped,
    Starting,
    Running,
    Stopping,
    Error,
}

/// Sidecar 进程信息
#[derive(Clone, Serialize)]
pub struct SidecarInfo {
    pub status: SidecarStatus,
    pub port: u16,
    pub pid: Option<u32>,
    pub uptime_seconds: u64,
    pub message: String,
}

/// 全局状态
struct AppState {
    sidecar_status: Arc<Mutex<SidecarInfo>>,
}

/// 初始化 Tauri 应用
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        .plugin(tauri_plugin_window_state::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            // 初始化状态
            let sidecar_status = Arc::new(Mutex::new(SidecarInfo {
                status: SidecarStatus::Stopped,
                port: 62601,
                pid: None,
                uptime_seconds: 0,
                message: String::new(),
            }));

            app.manage(AppState {
                sidecar_status,
            });

            // 创建系统托盘
            create_tray_icon(app.handle());

            // 初始化设置
            let store = app.store("settings.json").unwrap();
            if !store.has("preferred_port").unwrap() {
                store.set("preferred_port", 62616_u16).unwrap();
            }

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_sidecar_status,
            start_sidecar,
            stop_sidecar,
            restart_sidecar,
            get_settings,
            set_setting,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

### Task 2.4: 实现进程管理

**文件**：`tauri-app/src-tauri/src/sidecar.rs`

```rust
use crate::{SidecarInfo, SidecarStatus, AppState};
use tauri::{AppHandle, Emitter, Manager};
use tauri_plugin_shell::process::CommandChild;
use std::sync::Arc;
use std::time::Instant;

/// 全局 sidecar 进程句柄
struct SidecarState(Arc<Mutex<Option<CommandChild>>>);

/// 获取 Python 可执行文件路径
fn find_python() -> Result<String, String> {
    // 1. 检查 PYTHONPATH 环境变量
    if let Ok(py) = std::env::var("PYTHONPATH") {
        if !py.is_empty() {
            return Ok(py);
        }
    }

    // 2. 检查常见 Python 安装路径
    let candidates = vec![
        "python3",           // Unix
        "python",            // Windows
        "/usr/bin/python3", // macOS/Linux
        "/usr/local/bin/python3",
        "C:\\Python312\\python.exe",  // Windows
        "C:\\Python311\\python.exe",
    ];

    for cmd in candidates {
        if let Ok(output) = std::process::Command::new(cmd)
            .arg("--version")
            .output()
        {
            if output.status.success() {
                return Ok(cmd.to_string());
            }
        }
    }

    Err("Python not found in PATH".to_string())
}

/// 启动 Python sidecar
#[tauri::command]
pub async fn start_sidecar(app: AppHandle) -> Result<String, String> {
    let state = app.state::<AppState>();
    let mut status = state.sidecar_status.lock().unwrap();

    // 检查是否已在运行
    if matches!(status.status, SidecarStatus::Running | SidecarStatus::Starting) {
        return Ok("Sidecar is already running".to_string());
    }

    // 更新状态为启动中
    status.status = SidecarStatus::Starting;
    status.message = "Starting sidecar...".to_string();
    app.emit("sidecar-status", &*status).unwrap();

    // 获取配置
    let store = app.store("settings.json").unwrap();
    let port: u16 = store
        .get("preferred_port")
        .and_then(|v| v.as_u64())
        .unwrap_or(62601) as u16;

    // 查找 Python
    let python = find_python().map_err(|e| format!("Failed to find Python: {}", e))?;

    // 启动 sidecar 进程
    let mut cmd = tauri_plugin_shell::process::Command::new(&python);
    cmd.args([
        "-m",
        "anyclaw.cli.sidecar_cmd",
        "sidecar",
        "--port",
        &port.to_string(),
    ]);

    // 设置环境变量
    if let Ok(data_dir) = app.path().app_data_dir() {
        cmd.env("DATA_DIR", data_dir.to_string_lossy().to_string());
    }
    cmd.env("PYTHONUNBUFFERED", "1");

    // 启动进程
    let child = cmd
        .spawn()
        .map_err(|e| format!("Failed to spawn sidecar: {}", e))?;

    // 更新状态
    status.status = SidecarStatus::Running;
    status.port = port;
    status.pid = Some(child.pid());
    status.uptime_seconds = 0;
    status.message = "Sidecar is running".to_string();

    app.emit("sidecar-status", &*status).unwrap();

    Ok(format!("Sidecar started on port {}", port))
}

/// 停止 Python sidecar
#[tauri::command]
pub async fn stop_sidecar(app: AppHandle) -> Result<String, String> {
    let state = app.state::<AppState>();
    let mut status = state.sidecar_status.lock().unwrap();

    // 检查是否已停止
    if matches!(status.status, SidecarStatus::Stopped) {
        return Ok("Sidecar is already stopped".to_string());
    }

    // 更新状态为停止中
    status.status = SidecarStatus::Stopping;
    status.message = "Stopping sidecar...".to_string();
    app.emit("sidecar-status", &*status).unwrap();

    // TODO: 停止 sidecar 进程
    // 这里需要存储进程句柄，然后调用 kill()

    status.status = SidecarStatus::Stopped;
    status.pid = None;
    status.uptime_seconds = 0;
    status.message = "Sidecar stopped".to_string();

    app.emit("sidecar-status", &*status).unwrap();

    Ok("Sidecar stopped".to_string());
}

/// 重启 Python sidecar
#[tauri::command]
pub async fn restart_sidecar(app: AppHandle) -> Result<String, String> {
    // 先停止
    stop_sidecar(app.clone()).await?;

    // 等待 1 秒
    tokio::time::sleep(Duration::from_secs(1)).await;

    // 再启动
    start_sidecar(app).await
}

/// 获取 sidecar 状态
#[tauri::command]
pub fn get_sidecar_status(app: AppHandle) -> Result<SidecarInfo, String> {
    let state = app.state::<AppState>();
    let status = state.sidecar_status.lock().unwrap();

    Ok(status.clone())
}
```

---

### Task 2.5: 实现系统托盘

**文件**：`tauri-app/src-tauri/src/tray.rs`

```rust
use tauri::{
    AppHandle,
    menu::{Menu, MenuItem, PredefinedMenuItem},
    tray::{TrayIconBuilder, TrayIconEvent, MouseButton, MouseButtonState},
    image::Image,
};

/// 创建系统托盘图标
pub fn create_tray_icon(app: &AppHandle) {
    // 加载图标
    let icon = Image::from_bytes(include_bytes!("../icons/tray.png")).unwrap();

    // 创建托盘图标
    let tray_icon = TrayIconBuilder::new()
        .on_tray_icon_event(|app, event| {
            match event {
                TrayIconEvent::Click {
                    button: MouseButton::Left,
                    button_state: MouseButtonState::Up,
                    ..
                } => {
                    // 左键单击：显示/隐藏窗口
                    toggle_window(app);
                }
                TrayIconEvent::DoubleClick { .. } => {
                    // 双击：启动/停止 sidecar
                    toggle_sidecar(app);
                }
                TrayIconEvent::Enter { .. } => {
                    // 鼠标悬停：显示提示
                    // TODO: 实现悬停提示
                }
                _ => {}
            }
        })
        .menu(&create_tray_menu(app))
        .icon(icon)
        .icon_as_template(true)
        .build(app)
        .expect("Failed to create tray icon");

    app.manage(tray_icon);
}

/// 切换窗口显示/隐藏
fn toggle_window(app: &AppHandle) {
    if let Some(window) = app.get_webview_window("main") {
        if window.is_visible().unwrap() {
            window.hide().unwrap();
        } else {
            window.show().unwrap();
            window.set_focus().unwrap();
        }
    }
}

/// 切换 sidecar 启动/停止
async fn toggle_sidecar(app: &AppHandle) {
    use crate::sidecar::{get_sidecar_status, start_sidecar, stop_sidecar};

    match get_sidecar_status(app.clone()) {
        Ok(status) => {
            if matches!(status.status, crate::SidecarStatus::Running) {
                let _ = stop_sidecar(app.clone()).await;
            } else {
                let _ = start_sidecar(app.clone()).await;
            }
        }
        Err(_) => {
            let _ = start_sidecar(app.clone()).await;
        }
    }
}

/// 创建托盘菜单
fn create_tray_menu(app: &AppHandle) -> Menu {
    Menu::with_items(app, &[
        &MenuItem::with_id(app, "show", "Show", true, None::<&str>),
        &MenuItem::with_id(app, "hide", "Hide", true, None::<&str>),
        &PredefinedMenuItem::separator(app),
        &MenuItem::with_id(app, "start_sidecar", "Start Backend", true, None::<&str>),
        &MenuItem::with_id(app, "stop_sidecar", "Stop Backend", true, None::<&str>),
        &MenuItem::with_id(app, "restart_sidecar", "Restart Backend", true, None::<&str>),
        &PredefinedMenuItem::separator(app),
        &MenuItem::with_id(app, "settings", "Settings", true, None::<&str>),
        &MenuItem::with_id(app, "check_update", "Check for Updates", true, None::<&str>),
        &PredefinedMenuItem::separator(app),
        &MenuItem::with_id(app, "quit", "Quit", true, None::<&str>),
    ])
}
```

---

### Task 2.6: 实现配置管理

**文件**：`tauri-app/src-tauri/src/settings.rs`

```rust
use tauri::AppHandle;
use serde_json::Value;

/// 获取所有设置
#[tauri::command]
pub fn get_settings(app: AppHandle) -> Result<Value, String> {
    let store = app.store("settings.json").unwrap();
    Ok(store.get("").unwrap_or(Value::Object(serde_json::Map::new())))
}

/// 设置单个配置项
#[tauri::command]
pub fn set_setting(app: AppHandle, key: String, value: Value) -> Result<(), String> {
    let store = app.store("settings.json").unwrap();
    store.set(key, value).unwrap();
    Ok(())
}
```

---

### Task 2.7: 创建前端占位页面

**文件**：`tauri-app/src/App.tsx`

```tsx
import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';

interface SidecarStatus {
  status: 'Stopped' | 'Starting' | 'Running' | 'Stopping' | 'Error';
  port: number;
  pid: number | null;
  uptime_seconds: number;
  message: string;
}

function App() {
  const [sidecarStatus, setSidecarStatus] = useState<SidecarStatus>({
    status: 'Stopped',
    port: 62601,
    pid: null,
    uptime_seconds: 0,
    message: '',
  });

  const [isSidecarRunning, setIsSidecarRunning] = useState(false);

  useEffect(() => {
    // 获取初始状态
    invoke<SidecarStatus>('get_sidecar_status')
      .then(setSidecarStatus)
      .catch(console.error);

    // 监听状态变化
    const unlisten = invoke('listen', { event: 'sidecar-status' })
      .then((unlisten: any) => {
        return unlisten;
      })
      .catch(console.error);

    return () => {
      unlisten.then((fn: any) => fn?.());
    };
  }, []);

  const handleStart = async () => {
    try {
      await invoke('start_sidecar');
    } catch (error) {
      console.error('Failed to start sidecar:', error);
    }
  };

  const handleStop = async () => {
    try {
      await invoke('stop_sidecar');
    } catch (error) {
      console.error('Failed to stop sidecar:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto p-8">
        <h1 className="text-3xl font-bold mb-8">AnyClaw Desktop</h1>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Backend Status</h2>

          <div className="space-y-4">
            <div>
              <span className="text-gray-400">Status:</span>
              <span className={`ml-2 font-semibold ${
                sidecarStatus.status === 'Running' ? 'text-green-400' :
                sidecarStatus.status === 'Error' ? 'text-red-400' :
                'text-yellow-400'
              }`}>
                {sidecarStatus.status}
              </span>
            </div>

            <div>
              <span className="text-gray-400">Port:</span>
              <span className="ml-2">{sidecarStatus.port}</span>
            </div>

            <div>
              <span className="text-gray-400">PID:</span>
              <span className="ml-2">{sidecarStatus.pid || 'N/A'}</span>
            </div>

            <div>
              <span className="text-gray-400">Uptime:</span>
              <span className="ml-2">{sidecarStatus.uptime_seconds}s</span>
            </div>

            <div>
              <span className="text-gray-400">Message:</span>
              <span className="ml-2">{sidecarStatus.message}</span>
            </div>
          </div>

          <div className="mt-6 flex gap-4">
            <button
              onClick={handleStart}
              disabled={sidecarStatus.status === 'Running'}
              className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Start Backend
            </button>
            <button
              onClick={handleStop}
              disabled={sidecarStatus.status !== 'Running'}
              className="px-4 py-2 bg-red-600 rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Stop Backend
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
```

**文件**：`tauri-app/src/main.tsx`

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

---

### Task 2.8: 准备图标资源

**命令**：

```bash
# 创建图标目录
cd tauri-app/src-tauri
mkdir -p icons

# 复制图标（需要准备 16x16, 32x32, 128x128, 256x256 等尺寸）
# 可以使用 https://www.favicon-generator.org/ 或类似工具生成
```

---

### Task 2.9: 配置自动更新

**文件**：`tauri-app/src-tauri/tauri.conf.json`（修改）

```json
{
  "plugins": {
    "updater": {
      "endpoints": [
        "https://github.com/your-org/AnyClaw/releases/latest/download/latest.json"
      ],
      "dialog": true,
      "pubkey": "YOUR_PUBLIC_KEY_HERE"
    }
  }
}
```

**生成密钥对**：

```bash
# 生成密钥对
cargo tauri signer generate

# 输出：密钥对和 latest.json 模板
```

---

### Task 2.10: 构建和测试

**开发模式**：

```bash
cd tauri-app
npm run tauri:dev
```

**生产构建**：

```bash
cd tauri-app
npm run tauri:build
```

**输出位置**：

- macOS: `src-tauri/target/release/bundle/macos/AnyClaw.app`
- Windows: `src-tauri/target/release/bundle/msi/AnyClaw_0.1.0_x64_en-US.msi`
- Linux: `src-tauri/target/release/bundle/appimage/AnyClaw_0.1.0_amd64.AppImage`

---

## 🧪 测试计划

### 功能测试

- [ ] 系统托盘图标正常显示
- [ ] 左键单击切换窗口显示/隐藏
- [ ] 双击启动/停止 sidecar
- [ ] 右键菜单功能正常
- [ ] 启动 sidecar 进程成功
- [ ] 停止 sidecar 进程成功
- [ ] 重启 sidecar 进程成功
- [ ] 状态实时更新（通过 Tauri Events）
- [ ] 配置保存和加载正常

### 跨平台测试

- [ ] macOS (Intel + Apple Silicon)
- [ ] Windows 10/11
- [ ] Linux (Ubuntu, Fedora)

### 性能测试

- [ ] 应用启动时间 < 3 秒
- [ ] 内存占用 < 100MB (空闲时)
- [ ] 系统托盘不占用 CPU

---

## ✅ 验收标准

### 功能验收

- [ ] Tauri 应用可以正常启动
- [ ] 系统托盘功能完整
- [ ] Python sidecar 进程管理正常
- [ ] 配置持久化工作正常
- [ ] 跨平台打包成功

### 性能验收

- [ ] 应用启动时间 < 3 秒
- [ ] 内存占用 < 100MB (空闲时)
- [ ] Sidecar 启动时间 < 5 秒

### 代码质量

- [ ] Rust 代码通过 `cargo clippy`
- [ ] TypeScript 代码通过 `tsc --noEmit`
- [ ] 所有功能有错误处理

---

## 📅 时间线

| 任务 | 预计时间 | 状态 |
|------|---------|------|
| Task 2.1: 初始化 Tauri 项目 | 1h | ⬜ 待开始 |
| Task 2.2: 配置 Tauri | 1h | ⬜ 待开始 |
| Task 2.3: 实现 Rust 结构体 | 2h | ⬜ 待开始 |
| Task 2.4: 实现进程管理 | 4h | ⬜ 待开始 |
| Task 2.5: 实现系统托盘 | 3h | ⬜ 待开始 |
| Task 2.6: 实现配置管理 | 1h | ⬜ 待开始 |
| Task 2.7: 创建前端占位页面 | 2h | ⬜ 待开始 |
| Task 2.8: 准备图标资源 | 1h | ⬜ 待开始 |
| Task 2.9: 配置自动更新 | 1h | ⬜ 待开始 |
| Task 2.10: 构建和测试 | 4h | ⬜ 待开始 |

**总计**: ~20 小时 (2.5 工作日)

---

## 🚀 下一步

完成 Phase 2 后，继续：

**Phase 3**: 前端 UI 开发（参考 YouClaw 设计）

---

**记录时间**: 2026-03-20 04:20 (Asia/Shanghai)
**状态**: ✅ 计划完成，准备实施
