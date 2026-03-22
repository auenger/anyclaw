use serde::Serialize;
use tauri::{AppHandle, Emitter, Manager};
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
        .plugin(tauri_plugin_window_state::Builder::new().build())
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
            if !store.has("preferred_port") {
                store.set("preferred_port", 62616_u16);
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

/// 查找 Python 可执行文件路径
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

/// 启动 sidecar
async fn spawn_sidecar(app: &AppHandle, port: u16) -> Result<u32, String> {
    use tauri_plugin_shell::ShellExt;

    // 查找 Python
    let python = find_python().map_err(|e| format!("Failed to find Python: {}", e))?;

    // 准备环境变量
    let mut env_vars: Vec<(String, String)> = vec![];
    env_vars.push(("PORT".into(), port.to_string()));
    env_vars.push(("PYTHONUNBUFFERED".into(), "1".into()));

    // 设置数据目录
    if let Ok(data_dir) = app.path().app_data_dir() {
        env_vars.push(("DATA_DIR".into(), data_dir.to_string_lossy().to_string()));
    }

    // 启动进程
    let mut cmd = app.shell().command(&python);
    cmd = cmd.args([
        "-m",
        "anyclaw.cli.sidecar_cmd",
        "sidecar",
        "--port",
        &port.to_string(),
    ]);

    for (key, val) in env_vars {
        cmd = cmd.env(key, val);
    }

    let (mut rx, child) = cmd
        .spawn()
        .map_err(|e| format!("Failed to spawn sidecar: {}", e))?;

    // 获取 PID
    let pid = child.pid();
    log::info!("Sidecar spawned with PID: {}", pid);

    // 在后台处理输出事件
    tokio::spawn(async move {
        use tauri_plugin_shell::process::CommandEvent;
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) => {
                    log::info!("[sidecar stdout] {}", String::from_utf8_lossy(&line));
                }
                CommandEvent::Stderr(line) => {
                    log::warn!("[sidecar stderr] {}", String::from_utf8_lossy(&line));
                }
                CommandEvent::Error(err) => {
                    log::error!("[sidecar error] {}", err);
                }
                CommandEvent::Terminated(payload) => {
                    log::info!("[sidecar] terminated with code: {:?}", payload.code);
                    break;
                }
                _ => {}
            }
        }
    });

    Ok(pid)
}

/// 等待后端健康检查
async fn wait_for_health(port: u16, max_retries: u32) -> Result<(), String> {
    let addr = format!("127.0.0.1:{}", port);

    for i in 0..max_retries {
        if let Ok(mut stream) = std::net::TcpStream::connect_timeout(
            &addr.parse().unwrap(),
            Duration::from_millis(500),
        ) {
            use std::io::{Read, Write};
            let req = format!("GET /api/health HTTP/1.0\r\nHost: localhost:{}\r\n\r\n", port);
            if stream.write_all(req.as_bytes()).is_ok() {
                let mut buf = [0u8; 256];
                if let Ok(n) = stream.read(&mut buf) {
                    let resp = String::from_utf8_lossy(&buf[..n]);
                    if resp.contains("200") || resp.contains("ok") {
                        log::info!("Backend health check passed after {} attempts", i + 1);
                        return Ok(());
                    }
                }
            }
        }
        tokio::time::sleep(Duration::from_millis(500)).await;
    }

    Err("Backend health check failed after max retries".into())
}

/// 杀死 sidecar 进程
fn kill_sidecar(app: &AppHandle) {
    let state = app.state::<AppState>();
    let mut guard = state.sidecar_status.lock().unwrap();
    
    if let Some(pid) = guard.pid {
        #[cfg(target_os = "windows")]
        {
            use std::os::windows::process::CommandExt;
            const CREATE_NO_WINDOW: u32 = 0x08000000;
            let _ = std::process::Command::new("taskkill")
                .args(["/PID", &pid.to_string(), "/T", "/F"])
                .creation_flags(CREATE_NO_WINDOW)
                .output();
            log::info!("Sidecar process tree killed (PID: {})", pid);
        }
        #[cfg(not(target_os = "windows"))]
        {
            let _ = std::process::Command::new("pkill")
                .args(["-KILL", "-P", &pid.to_string()])
                .output();
            log::info!("Sidecar process tree killed (PID: {})", pid);
        }
        
        guard.pid = None;
    }
}

/// 获取 sidecar 状态
#[tauri::command]
fn get_sidecar_status(app: AppHandle) -> Result<SidecarInfo, String> {
    let state = app.state::<AppState>();
    let status = state.sidecar_status.lock().unwrap();

    Ok(status.clone())
}

/// 启动 sidecar
#[tauri::command]
async fn start_sidecar(app: AppHandle) -> Result<String, String> {
    let state = app.state::<AppState>();

    // 检查是否已在运行，并更新状态为启动中
    {
        let mut status = state.sidecar_status.lock().unwrap();
        if matches!(status.status, SidecarStatus::Running | SidecarStatus::Starting) {
            return Ok("Sidecar is already running".to_string());
        }
        status.status = SidecarStatus::Starting;
        status.message = "Starting sidecar...".to_string();
        app.emit("sidecar-status", &*status).unwrap();
    }

    // 获取配置
    let store = app.store("settings.json").unwrap();
    let port: u16 = store
        .get("preferred_port")
        .and_then(|v| v.as_u64())
        .unwrap_or(62601) as u16;

    // 启动 sidecar
    let pid = spawn_sidecar(&app, port).await?;

    // 等待健康检查
    if let Err(e) = wait_for_health(port, 30).await {
        log::error!("Health check failed: {}", e);

        {
            let mut status = state.sidecar_status.lock().unwrap();
            status.status = SidecarStatus::Error;
            status.message = format!("Health check failed: {}", e);
            app.emit("sidecar-status", &*status).unwrap();
        }

        // 杀死进程
        kill_sidecar(&app);

        return Err(format!("Failed to start sidecar: {}", e));
    }

    // 更新状态为运行中
    {
        let mut status = state.sidecar_status.lock().unwrap();
        status.status = SidecarStatus::Running;
        status.port = port;
        status.pid = Some(pid);
        status.uptime_seconds = 0;
        status.message = "Sidecar is running".to_string();
        app.emit("sidecar-status", &*status).unwrap();
    }

    Ok(format!("Sidecar started on port {}", port))
}

/// 停止 sidecar
#[tauri::command]
async fn stop_sidecar(app: AppHandle) -> Result<String, String> {
    let state = app.state::<AppState>();

    // 检查是否已停止，并更新状态为停止中
    {
        let mut status = state.sidecar_status.lock().unwrap();
        if matches!(status.status, SidecarStatus::Stopped) {
            return Ok("Sidecar is already stopped".to_string());
        }
        status.status = SidecarStatus::Stopping;
        status.message = "Stopping sidecar...".to_string();
        app.emit("sidecar-status", &*status).unwrap();
    }

    // 杀死进程
    kill_sidecar(&app);

    // 等待 1 秒
    tokio::time::sleep(Duration::from_secs(1)).await;

    // 更新状态
    {
        let mut status = state.sidecar_status.lock().unwrap();
        status.status = SidecarStatus::Stopped;
        status.pid = None;
        status.uptime_seconds = 0;
        status.message = "Sidecar stopped".to_string();
        app.emit("sidecar-status", &*status).unwrap();
    }

    Ok("Sidecar stopped".to_string())
}

/// 重启 sidecar
#[tauri::command]
async fn restart_sidecar(app: AppHandle) -> Result<String, String> {
    // 先停止
    stop_sidecar(app.clone()).await?;

    // 等待 1 秒
    tokio::time::sleep(Duration::from_secs(1)).await;

    // 再启动
    start_sidecar(app).await
}

/// 获取所有设置
#[tauri::command]
fn get_settings(app: AppHandle) -> Result<serde_json::Value, String> {
    let store = app.store("settings.json").unwrap();
    Ok(store.get("").unwrap_or(serde_json::Value::Object(serde_json::Map::new())))
}

/// 设置单个配置项
#[tauri::command]
fn set_setting(app: AppHandle, key: String, value: serde_json::Value) -> Result<(), String> {
    let store = app.store("settings.json").unwrap();
    store.set(key, value);
    Ok(())
}

/// 创建系统托盘图标
fn create_tray_icon(app: &AppHandle) {
    use tauri::{
        tray::{TrayIconBuilder, TrayIconEvent, MouseButton, MouseButtonState},
        image::Image,
    };

    // 创建托盘图标（TODO: 添加实际图标文件）
    let icon = Image::from_bytes(include_bytes!("../icons/tray.png")).unwrap();

    let tray_icon = TrayIconBuilder::new()
        .on_tray_icon_event(|tray, event| {
            match event {
                TrayIconEvent::Click {
                    button: MouseButton::Left,
                    button_state: MouseButtonState::Up,
                    ..
                } => {
                    // 左键单击：显示/隐藏窗口
                    toggle_window(tray.app_handle());
                }
                TrayIconEvent::DoubleClick { .. } => {
                    // 双击：启动/停止 sidecar
                    let app = tray.app_handle().clone();
                    tokio::spawn(async move {
                        toggle_sidecar(&app).await;
                    });
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
fn create_tray_menu(app: &AppHandle) -> tauri::menu::Menu<tauri::Wry> {
    use tauri::menu::{Menu, MenuItem, PredefinedMenuItem};

    let show = MenuItem::with_id(app, "show", "Show", true, None::<&str>).unwrap();
    let hide = MenuItem::with_id(app, "hide", "Hide", true, None::<&str>).unwrap();
    let separator = PredefinedMenuItem::separator(app).unwrap();
    let start = MenuItem::with_id(app, "start_sidecar", "Start Backend", true, None::<&str>).unwrap();
    let stop = MenuItem::with_id(app, "stop_sidecar", "Stop Backend", true, None::<&str>).unwrap();
    let restart = MenuItem::with_id(app, "restart_sidecar", "Restart Backend", true, None::<&str>).unwrap();
    let separator2 = PredefinedMenuItem::separator(app).unwrap();
    let settings = MenuItem::with_id(app, "settings", "Settings", true, None::<&str>).unwrap();
    let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>).unwrap();

    Menu::with_items(app, &[
        &show,
        &hide,
        &separator,
        &start,
        &stop,
        &restart,
        &separator2,
        &settings,
        &quit,
    ]).expect("Failed to create tray menu")
}
