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
        .plugin(tauri_plugin_log::Builder::new().build())
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

/// 获取 sidecar 状态
#[tauri::command]
pub fn get_sidecar_status(app: AppHandle) -> Result<SidecarInfo, String> {
    let state = app.state::<AppState>();
    let status = state.sidecar_status.lock().unwrap();

    Ok(status.clone())
}

/// 启动 sidecar
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

    // TODO: 启动 Python sidecar 进程
    // 这里需要实现进程启动逻辑

    // 更新状态
    status.status = SidecarStatus::Running;
    status.port = 62601;
    status.pid = None;
    status.uptime_seconds = 0;
    status.message = "Sidecar is running".to_string();

    app.emit("sidecar-status", &*status).unwrap();

    Ok(format!("Sidecar started on port {}", 62601))
}

/// 停止 sidecar
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

    // TODO: 停止 Python sidecar 进程
    // 这里需要实现进程停止逻辑

    status.status = SidecarStatus::Stopped;
    status.pid = None;
    status.uptime_seconds = 0;
    status.message = "Sidecar stopped".to_string();

    app.emit("sidecar-status", &*status).unwrap();

    Ok("Sidecar stopped".to_string())
}

/// 重启 sidecar
#[tauri::command]
pub async fn restart_sidecar(app: AppHandle) -> Result<String, String> {
    // 先停止
    stop_sidecar(app.clone()).await?;

    // 等待 1 秒
    tokio::time::sleep(Duration::from_secs(1)).await;

    // 再启动
    start_sidecar(app).await
}

/// 获取所有设置
#[tauri::command]
pub fn get_settings(app: AppHandle) -> Result<serde_json::Value, String> {
    let store = app.store("settings.json").unwrap();
    Ok(store.get("").unwrap_or(serde_json::Value::Object(serde_json::Map::new())))
}

/// 设置单个配置项
#[tauri::command]
pub fn set_setting(app: AppHandle, key: String, value: serde_json::Value) -> Result<(), String> {
    let store = app.store("settings.json").unwrap();
    store.set(key, value).unwrap();
    Ok(())
}

/// 创建系统托盘图标
fn create_tray_icon(app: &AppHandle) {
    use tauri::{
        menu::{Menu, MenuItem, PredefinedMenuItem},
        tray::{TrayIconBuilder, TrayIconEvent, MouseButton, MouseButtonState},
        image::Image,
    };

    // 创建托盘图标（TODO: 添加实际图标文件）
    let icon = Image::from_bytes(include_bytes!("../icons/tray.png")).unwrap();

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
    match get_sidecar_status(app.clone()) {
        Ok(status) => {
            if matches!(status.status, SidecarStatus::Running) {
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
        &MenuItem::with_id(app, "quit", "Quit", true, None::<&str>),
    ])
}
