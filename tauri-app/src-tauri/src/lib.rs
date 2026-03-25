use serde::Serialize;
use tauri::{AppHandle, Emitter, Manager};
use tauri::menu::{Menu, MenuItem, PredefinedMenuItem};
use tauri::tray::{TrayIconBuilder, TrayIconEvent, MouseButton, MouseButtonState};
use tauri::image::Image;
use tauri_plugin_store::StoreExt;
use tauri_plugin_shell::ShellExt;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use std::process::{Child, Command, Stdio};

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
    sidecar_process: Arc<Mutex<Option<Child>>>,
    start_time: Arc<Mutex<Option<Instant>>>,
}

/// 检查是否为生产模式（打包后的应用）
fn is_production_mode() -> bool {
    // 检查 sidecar 可执行文件是否存在
    if let Ok(exe_path) = std::env::current_exe() {
        if let Some(parent) = exe_path.parent() {
            // macOS: AnyClaw.app/Contents/MacOS/AnyClaw
            // Windows: AnyClaw/AnyClaw.exe
            let binaries_dir = if cfg!(target_os = "macos") {
                parent.parent().map(|p| p.join("Resources").join("binaries"))
            } else {
                Some(parent.join("binaries"))
            };

            if let Some(bin_dir) = binaries_dir {
                let sidecar_name = get_sidecar_binary_name();
                if bin_dir.join(&sidecar_name).exists() {
                    return true;
                }
            }
        }
    }
    false
}

/// 获取当前平台的 sidecar 二进制文件名
fn get_sidecar_binary_name() -> String {
    #[cfg(target_os = "macos")]
    {
        #[cfg(target_arch = "x86_64")]
        { "anyclaw-sidecar-x86_64-apple-darwin".to_string() }
        #[cfg(target_arch = "aarch64")]
        { "anyclaw-sidecar-aarch64-apple-darwin".to_string() }
    }
    #[cfg(target_os = "windows")]
    { "anyclaw-sidecar-x86_64-pc-windows-msvc.exe".to_string() }
    #[cfg(target_os = "linux")]
    { "anyclaw-sidecar-x86_64-unknown-linux-gnu".to_string() }
}

// ============ 命令函数 ============

#[tauri::command]
fn get_sidecar_status(app: AppHandle) -> Result<SidecarInfo, String> {
    let state = app.state::<AppState>();
    let status = state.sidecar_status.lock().unwrap().clone();
    let start_time = state.start_time.lock().unwrap();

    // 动态计算 uptime
    let uptime_seconds = if matches!(status.status, SidecarStatus::Running) {
        start_time.map(|t| t.elapsed().as_secs()).unwrap_or(0)
    } else {
        0
    };

    Ok(SidecarInfo {
        uptime_seconds,
        ..status
    })
}

#[tauri::command]
async fn start_sidecar(app: AppHandle) -> Result<String, String> {
    // 更新状态为启动中
    {
        let state = app.state::<AppState>();
        let mut status = state.sidecar_status.lock().unwrap();
        if matches!(status.status, SidecarStatus::Running | SidecarStatus::Starting) {
            return Ok("Sidecar is already running".to_string());
        }
        status.status = SidecarStatus::Starting;
        status.message = "Starting sidecar...".to_string();
        let _ = app.emit("sidecar-status", &*status);
    }

    // 获取配置
    let port: u16 = {
        let store = app.store("settings.json").map_err(|e| e.to_string())?;
        store.get("preferred_port")
            .and_then(|v| v.as_u64())
            .unwrap_or(62601) as u16
    };

    // 先检查端口是否已经有 sidecar 在运行
    if check_existing_sidecar(port).await {
        log::info!("Found existing sidecar on port {}, using it", port);
        // 更新状态为运行中
        {
            let state = app.state::<AppState>();
            let mut status = state.sidecar_status.lock().unwrap();
            status.status = SidecarStatus::Running;
            status.port = port;
            status.pid = None; // 我们没有启动它，所以不知道 PID
            status.uptime_seconds = 0;
            status.message = "Connected to existing sidecar".to_string();
            let _ = app.emit("sidecar-status", &*status);
        }
        return Ok(format!("Connected to existing sidecar on port {}", port));
    }

    // 启动 sidecar
    let pid = spawn_sidecar(&app, port)?;

    // 等待健康检查
    if let Err(e) = wait_for_health(port, 30).await {
        // 更新状态为错误
        {
            let state = app.state::<AppState>();
            let mut status = state.sidecar_status.lock().unwrap();
            status.status = SidecarStatus::Error;
            status.message = format!("Health check failed: {}", e);
            let _ = app.emit("sidecar-status", &*status);
        }
        kill_sidecar(&app);
        return Err(format!("Failed to start sidecar: {}", e));
    }

    // 更新状态为运行中
    {
        let state = app.state::<AppState>();
        let mut status = state.sidecar_status.lock().unwrap();
        status.status = SidecarStatus::Running;
        status.port = port;
        status.pid = Some(pid);
        status.uptime_seconds = 0;
        status.message = "Sidecar is running".to_string();
        let _ = app.emit("sidecar-status", &*status);

        // 记录启动时间
        let mut start_time = state.start_time.lock().unwrap();
        *start_time = Some(Instant::now());
    }

    Ok(format!("Sidecar started on port {}", port))
}

#[tauri::command]
async fn stop_sidecar(app: AppHandle) -> Result<String, String> {
    // 更新状态为停止中
    {
        let state = app.state::<AppState>();
        let mut status = state.sidecar_status.lock().unwrap();
        if matches!(status.status, SidecarStatus::Stopped) {
            return Ok("Sidecar is already stopped".to_string());
        }
        status.status = SidecarStatus::Stopping;
        status.message = "Stopping sidecar...".to_string();
        let _ = app.emit("sidecar-status", &*status);
    }

    kill_sidecar(&app);
    tokio::time::sleep(Duration::from_secs(1)).await;

    // 更新状态
    {
        let state = app.state::<AppState>();
        let mut status = state.sidecar_status.lock().unwrap();
        status.status = SidecarStatus::Stopped;
        status.pid = None;
        status.uptime_seconds = 0;
        status.message = "Sidecar stopped".to_string();
        let _ = app.emit("sidecar-status", &*status);

        // 清除启动时间
        let mut start_time = state.start_time.lock().unwrap();
        *start_time = None;
    }

    Ok("Sidecar stopped".to_string())
}

#[tauri::command]
async fn restart_sidecar(app: AppHandle) -> Result<String, String> {
    stop_sidecar(app.clone()).await?;
    tokio::time::sleep(Duration::from_secs(1)).await;
    start_sidecar(app).await
}

#[tauri::command]
fn get_settings(app: AppHandle) -> Result<serde_json::Value, String> {
    let store = app.store("settings.json").map_err(|e| e.to_string())?;
    Ok(store.get("").unwrap_or(serde_json::Value::Object(serde_json::Map::new())))
}

#[tauri::command]
fn set_setting(app: AppHandle, key: String, value: serde_json::Value) -> Result<(), String> {
    let store = app.store("settings.json").map_err(|e| e.to_string())?;
    store.set(key, value);
    Ok(())
}

#[tauri::command]
fn get_platform() -> String {
    #[cfg(target_os = "macos")]
    { "macos".to_string() }
    #[cfg(target_os = "windows")]
    { "windows".to_string() }
    #[cfg(target_os = "linux")]
    { "linux".to_string() }
    #[cfg(not(any(target_os = "macos", target_os = "windows", target_os = "linux")))]
    { "unknown".to_string() }
}

// ============ 配置文件命令 ============

/// 获取配置文件路径
fn get_config_path() -> Result<std::path::PathBuf, String> {
    let home = std::env::var("HOME")
        .or_else(|_| std::env::var("USERPROFILE"))
        .map_err(|_| "Cannot determine home directory")?;
    Ok(std::path::PathBuf::from(home).join(".anyclaw").join("config.toml"))
}

/// 读取配置文件内容
#[tauri::command]
fn read_config_file() -> Result<String, String> {
    let config_path = get_config_path()?;
    if !config_path.exists() {
        return Err("Config file not found. Please run 'anyclaw config init' first.".to_string());
    }
    std::fs::read_to_string(&config_path)
        .map_err(|e| format!("Failed to read config file: {}", e))
}

/// 写入配置文件内容
#[tauri::command]
fn write_config_file(content: String) -> Result<(), String> {
    // 先验证 TOML 格式
    validate_toml(content.clone())?;

    let config_path = get_config_path()?;

    // 确保目录存在
    if let Some(parent) = config_path.parent() {
        std::fs::create_dir_all(parent)
            .map_err(|e| format!("Failed to create config directory: {}", e))?;
    }

    // 写入文件
    std::fs::write(&config_path, &content)
        .map_err(|e| format!("Failed to write config file: {}", e))?;

    log::info!("Config file saved to {:?}", config_path);
    Ok(())
}

/// 验证 TOML 格式
#[tauri::command]
fn validate_toml(content: String) -> Result<(), String> {
    content.parse::<toml::Value>()
        .map(|_| ())
        .map_err(|e| format!("TOML parse error at line {}, column {}: {}",
            e.span().map(|s| s.start).unwrap_or(0) / 100 + 1,
            e.span().map(|s| s.start).unwrap_or(0) % 100 + 1,
            e.message()))
}

/// 获取配置文件路径（字符串形式）
#[tauri::command]
fn get_config_path_string() -> Result<String, String> {
    get_config_path()
        .map(|p| p.to_string_lossy().to_string())
}

/// 检查配置文件是否存在
#[tauri::command]
fn config_file_exists() -> bool {
    get_config_path().map(|p| p.exists()).unwrap_or(false)
}

// ============ 辅助函数 ============

/// 查找可用的 Python 环境
/// 优先级：Poetry > Homebrew > pyenv > 系统 Python
fn find_python() -> Result<(String, Vec<(String, String)>), String> {
    // 获取项目根目录（向上查找 pyproject.toml）
    let project_root = find_project_root();

    // 1. 尝试 Poetry 环境
    if let Some(root) = &project_root {
        // 检查 poetry.lock 是否存在
        let poetry_lock = root.join("poetry.lock");
        if poetry_lock.exists() {
            // 尝试使用 poetry run
            if let Ok(output) = std::process::Command::new("poetry")
                .args(["env", "info", "--executable"])
                .current_dir(root)
                .output()
            {
                if output.status.success() {
                    let python_path = String::from_utf8_lossy(&output.stdout).trim().to_string();
                    if !python_path.is_empty() {
                        log::info!("Found Poetry Python: {}", python_path);
                        return Ok((python_path, vec![]));
                    }
                }
            }

            // 尝试直接使用 poetry run
            if let Ok(_) = std::process::Command::new("poetry")
                .arg("--version")
                .output()
            {
                log::info!("Using poetry run to execute sidecar");
                return Ok(("poetry".to_string(), vec![("POETRY_RUN".to_string(), "1".to_string())]));
            }
        }
    }

    // 2. 尝试 Homebrew Python (3.11, 3.12, 3.13) - Intel 和 Apple Silicon 路径
    let homebrew_paths = vec![
        // Apple Silicon (M1/M2)
        "/opt/homebrew/opt/python@3.13/bin/python3.13",
        "/opt/homebrew/opt/python@3.12/bin/python3.12",
        "/opt/homebrew/opt/python@3.11/bin/python3.11",
        "/opt/homebrew/bin/python3.13",
        "/opt/homebrew/bin/python3.12",
        "/opt/homebrew/bin/python3.11",
        // Intel Mac
        "/usr/local/opt/python@3.13/bin/python3.13",
        "/usr/local/opt/python@3.12/bin/python3.12",
        "/usr/local/opt/python@3.11/bin/python3.11",
        "/usr/local/bin/python3.13",
        "/usr/local/bin/python3.12",
        "/usr/local/bin/python3.11",
    ];

    for path in homebrew_paths {
        if std::path::Path::new(path).exists() {
            if let Ok(output) = std::process::Command::new(path).arg("--version").output() {
                if output.status.success() {
                    let version = String::from_utf8_lossy(&output.stdout);
                    if version.contains("3.1") || version.contains("3.2") {
                        log::info!("Found Homebrew Python: {}", path);
                        return Ok((path.to_string(), vec![]));
                    }
                }
            }
        }
    }

    // 3. 尝试 pyenv Python
    if let Ok(home) = std::env::var("HOME") {
        let pyenv_versions = vec!["3.13", "3.12", "3.11", "3.10"];
        for version in pyenv_versions {
            let pyenv_path = format!("{}/.pyenv/versions/{}/bin/python3", home, version);
            if std::path::Path::new(&pyenv_path).exists() {
                log::info!("Found pyenv Python: {}", pyenv_path);
                return Ok((pyenv_path, vec![]));
            }
        }
        // 尝试 pyenv shims
        let pyenv_shim = format!("{}/.pyenv/shims/python3", home);
        if std::path::Path::new(&pyenv_shim).exists() {
            if let Ok(output) = std::process::Command::new(&pyenv_shim).arg("--version").output() {
                if output.status.success() {
                    log::info!("Found pyenv shim Python: {}", pyenv_shim);
                    return Ok((pyenv_shim, vec![]));
                }
            }
        }
    }

    // 4. 尝试系统 Python
    let system_pythons = vec!["python3", "python", "/usr/bin/python3", "/usr/local/bin/python3"];
    for cmd in system_pythons {
        if let Ok(output) = std::process::Command::new(cmd).arg("--version").output() {
            if output.status.success() {
                let version = String::from_utf8_lossy(&output.stdout);
                // 检查版本是否 >= 3.10
                if version.contains("3.1") || version.contains("3.2") || version.contains("3.3") {
                    log::info!("Found system Python: {}", cmd);
                    return Ok((cmd.to_string(), vec![]));
                }
            }
        }
    }

    Err("Python 3.10+ not found. Please install Python 3.10 or later, or use Poetry.".to_string())
}

/// 查找项目根目录（包含 pyproject.toml 的目录）
fn find_project_root() -> Option<std::path::PathBuf> {
    let mut current = std::env::current_dir().ok()?;

    for _ in 0..10 {
        let pyproject = current.join("pyproject.toml");
        if pyproject.exists() {
            return Some(current);
        }
        if !current.pop() {
            break;
        }
    }

    None
}

fn spawn_sidecar(app: &AppHandle, port: u16) -> Result<u32, String> {
    // 检查是否为生产模式
    if is_production_mode() {
        spawn_bundled_sidecar(app, port)
    } else {
        spawn_dev_sidecar(app, port)
    }
}

/// 启动打包后的 sidecar（生产模式）
fn spawn_bundled_sidecar(app: &AppHandle, port: u16) -> Result<u32, String> {
    log::info!("Starting bundled sidecar in production mode");

    // 获取 sidecar 路径
    let exe_path = std::env::current_exe().map_err(|e| format!("Failed to get exe path: {}", e))?;
    let exe_dir = exe_path.parent().ok_or("Failed to get exe directory")?;

    // macOS: AnyClaw.app/Contents/MacOS/AnyClaw -> Contents/Resources/binaries/
    // Windows: AnyClaw/AnyClaw.exe -> AnyClaw/binaries/
    let binaries_dir = if cfg!(target_os = "macos") {
        exe_dir.parent()
            .map(|p| p.join("Resources").join("binaries"))
            .ok_or("Failed to get Resources directory")?
    } else {
        exe_dir.join("binaries")
    };

    let sidecar_name = get_sidecar_binary_name();
    let sidecar_path = binaries_dir.join(&sidecar_name);

    if !sidecar_path.exists() {
        return Err(format!("Sidecar binary not found at: {:?}", sidecar_path));
    }

    log::info!("Sidecar path: {:?}", sidecar_path);

    let mut cmd = Command::new(&sidecar_path);
    cmd.args(["sidecar", "--port", &port.to_string()])
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .env("PORT", port.to_string())
        .env("PYTHONUNBUFFERED", "1");

    // 设置数据目录
    if let Ok(data_dir) = app.path().app_data_dir() {
        cmd.env("DATA_DIR", data_dir.to_string_lossy().to_string());
    }

    let child = cmd.spawn().map_err(|e| format!("Failed to spawn sidecar: {}", e))?;
    let pid = child.id();

    // 保存进程句柄
    {
        let state = app.state::<AppState>();
        let mut proc = state.sidecar_process.lock().unwrap();
        *proc = Some(child);
    }

    log::info!("Bundled sidecar spawned with PID: {}", pid);
    Ok(pid)
}

/// 启动开发模式的 sidecar（使用 poetry/python）
fn spawn_dev_sidecar(app: &AppHandle, port: u16) -> Result<u32, String> {
    log::info!("Starting sidecar in development mode");

    let (python, extra_env) = find_python()?;

    // 获取项目根目录
    let project_root = find_project_root();

    let mut cmd = if python == "poetry" {
        // 使用 poetry run
        let mut c = Command::new("poetry");
        c.args(["run", "python", "-m", "anyclaw.cli.sidecar_cmd", "--port", &port.to_string()]);
        if let Some(root) = &project_root {
            c.current_dir(root);
        }
        c
    } else {
        // 直接使用 Python
        let mut c = Command::new(&python);
        c.args(["-m", "anyclaw.cli.sidecar_cmd", "--port", &port.to_string()]);
        c
    };

    // 设置环境变量
    cmd.env("PORT", port.to_string())
        .env("PYTHONUNBUFFERED", "1")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    // 添加额外环境变量
    for (key, val) in extra_env {
        cmd.env(key, val);
    }

    // 设置数据目录
    if let Ok(data_dir) = app.path().app_data_dir() {
        cmd.env("DATA_DIR", data_dir.to_string_lossy().to_string());
    }

    // 如果在项目目录中运行，设置工作目录
    if let Some(root) = &project_root {
        if python != "poetry" {
            cmd.current_dir(root);
        }
    }

    let child = cmd.spawn().map_err(|e| format!("Failed to spawn sidecar: {}", e))?;
    let pid = child.id();

    // 保存进程句柄
    {
        let state = app.state::<AppState>();
        let mut proc = state.sidecar_process.lock().unwrap();
        *proc = Some(child);
    }

    log::info!("Dev sidecar spawned with PID: {}", pid);
    Ok(pid)
}

async fn wait_for_health(port: u16, max_retries: u32) -> Result<(), String> {
    use std::io::{Read, Write};
    let addr = format!("127.0.0.1:{}", port);

    for _i in 0..max_retries {
        if let Ok(mut stream) = std::net::TcpStream::connect_timeout(
            &addr.parse().unwrap(),
            Duration::from_millis(500),
        ) {
            let req = format!("GET /api/health HTTP/1.0\r\nHost: localhost:{}\r\n\r\n", port);
            if stream.write_all(req.as_bytes()).is_ok() {
                let mut buf = [0u8; 256];
                if let Ok(n) = stream.read(&mut buf) {
                    let resp = String::from_utf8_lossy(&buf[..n]);
                    if resp.contains("200") || resp.contains("ok") {
                        return Ok(());
                    }
                }
            }
        }
        tokio::time::sleep(Duration::from_millis(500)).await;
    }
    Err("Health check failed".into())
}

/// 检查是否已有 sidecar 在指定端口运行
async fn check_existing_sidecar(port: u16) -> bool {
    use std::io::{Read, Write};
    let addr = format!("127.0.0.1:{}", port);

    // 尝试连接并进行健康检查
    if let Ok(mut stream) = std::net::TcpStream::connect_timeout(
        &addr.parse().unwrap(),
        Duration::from_millis(1000),
    ) {
        let req = format!("GET /api/health HTTP/1.0\r\nHost: localhost:{}\r\n\r\n", port);
        if stream.write_all(req.as_bytes()).is_ok() {
            let mut buf = [0u8; 512];
            if let Ok(n) = stream.read(&mut buf) {
                let resp = String::from_utf8_lossy(&buf[..n]);
                // 检查是否是 AnyClaw sidecar 的健康响应
                if resp.contains("200") || resp.contains("ok") || resp.contains("AnyClaw") {
                    log::info!("Found existing AnyClaw sidecar on port {}", port);
                    return true;
                }
            }
        }
    }
    false
}

fn kill_sidecar(app: &AppHandle) {
    let state = app.state::<AppState>();

    // 首先尝试使用进程句柄（生产模式）
    {
        let mut proc_guard = state.sidecar_process.lock().unwrap();
        if let Some(mut child) = proc_guard.take() {
            log::info!("Killing sidecar process via handle");
            let _ = child.kill();
            let _ = child.wait();
        }
    }

    // 然后尝试通过 PID 终止（兼容旧逻辑）
    {
        let mut guard = state.sidecar_status.lock().unwrap();
        if let Some(pid) = guard.pid {
            #[cfg(target_os = "windows")]
            {
                use std::os::windows::process::CommandExt;
                const CREATE_NO_WINDOW: u32 = 0x08000000;
                let _ = Command::new("taskkill")
                    .args(["/PID", &pid.to_string(), "/T", "/F"])
                    .creation_flags(CREATE_NO_WINDOW)
                    .output();
            }
            #[cfg(not(target_os = "windows"))]
            {
                let _ = Command::new("pkill")
                    .args(["-KILL", "-P", &pid.to_string()])
                    .output();
                // 也尝试直接杀死 PID
                let _ = Command::new("kill")
                    .args(["-9", &pid.to_string()])
                    .output();
            }
            guard.pid = None;
        }
    }
}

fn create_tray_icon(app: &AppHandle) {
    let icon = Image::from_bytes(include_bytes!("../icons/tray.png")).unwrap();
    let app_handle = app.clone();

    let tray = TrayIconBuilder::new()
        .on_tray_icon_event(move |tray, event| {
            let app = tray.app_handle();
            match event {
                TrayIconEvent::Click { button: MouseButton::Left, button_state: MouseButtonState::Up, .. } => {
                    toggle_window(app);
                }
                TrayIconEvent::DoubleClick { .. } => {
                    let app = app.clone();
                    tokio::spawn(async move { toggle_sidecar(app).await; });
                }
                _ => {}
            }
        })
        .menu(&create_tray_menu(&app_handle))
        .icon(icon)
        .build(app)
        .expect("Failed to create tray");

    app.manage(tray);
}

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

async fn toggle_sidecar(app: AppHandle) {
    match get_sidecar_status(app.clone()) {
        Ok(status) if matches!(status.status, SidecarStatus::Running) => {
            let _ = stop_sidecar(app.clone()).await;
        }
        _ => {
            let _ = start_sidecar(app.clone()).await;
        }
    }
}

fn create_tray_menu(app: &AppHandle) -> Menu<tauri::Wry> {
    Menu::with_items(app, &[
        &MenuItem::with_id(app, "show", "Show", true, None::<&str>).unwrap(),
        &MenuItem::with_id(app, "hide", "Hide", true, None::<&str>).unwrap(),
        &PredefinedMenuItem::separator(app).unwrap(),
        &MenuItem::with_id(app, "start", "Start Backend", true, None::<&str>).unwrap(),
        &MenuItem::with_id(app, "stop", "Stop Backend", true, None::<&str>).unwrap(),
        &MenuItem::with_id(app, "restart", "Restart Backend", true, None::<&str>).unwrap(),
        &PredefinedMenuItem::separator(app).unwrap(),
        &MenuItem::with_id(app, "settings", "Settings", true, None::<&str>).unwrap(),
        &MenuItem::with_id(app, "quit", "Quit", true, None::<&str>).unwrap(),
    ]).unwrap()
}

// ============ 应用入口 ============

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
            let sidecar_status = Arc::new(Mutex::new(SidecarInfo {
                status: SidecarStatus::Stopped,
                port: 62601,
                pid: None,
                uptime_seconds: 0,
                message: String::new(),
            }));

            app.manage(AppState {
                sidecar_status,
                sidecar_process: Arc::new(Mutex::new(None)),
                start_time: Arc::new(Mutex::new(None)),
            });

            create_tray_icon(app.handle());

            let store = app.store("settings.json").unwrap();
            if !store.has("preferred_port") {
                store.set("preferred_port", 62616_u16);
            }

            // 检测运行模式并记录日志
            if is_production_mode() {
                log::info!("Running in production mode (bundled sidecar)");
            } else {
                log::info!("Running in development mode (poetry/python sidecar)");
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
            get_platform,
            read_config_file,
            write_config_file,
            validate_toml,
            get_config_path_string,
            config_file_exists,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
