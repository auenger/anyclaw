# 任务分解：配置编辑器与服务控制

## 概述

在 Tauri 桌面应用中添加配置文件编辑和 sidecar 服务控制功能。

## 任务列表

### 任务 1：添加 Rust 配置文件读写命令

**文件**: `tauri-app/src-tauri/src/lib.rs`

**描述**: 添加读取和写入配置文件的 Tauri 命令

**要点**:
- `read_config_file()` - 读取 `~/.anyclaw/config.toml` 内容
- `write_config_file(content)` - 写入配置文件
- `validate_toml(content)` - 验证 TOML 格式
- `get_config_template()` - 获取默认配置模板
- `get_config_path()` - 获取配置文件路径

**代码示例**:
```rust
#[tauri::command]
fn read_config_file(app: AppHandle) -> Result<String, String> {
    let config_path = get_config_path(&app)?;
    if !config_path.exists() {
        return Err("Config file not found".to_string());
    }
    std::fs::read_to_string(&config_path)
        .map_err(|e| format!("Failed to read config: {}", e))
}

#[tauri::command]
fn write_config_file(app: AppHandle, content: String) -> Result<(), String> {
    let config_path = get_config_path(&app)?;
    config_path.parent()
        .map(|p| std::fs::create_dir_all(p))
        .transpose()
        .map_err(|e| format!("Failed to create config dir: {}", e))?;
    std::fs::write(&config_path, &content)
        .map_err(|e| format!("Failed to write config: {}", e))
}

#[tauri::command]
fn validate_toml(content: String) -> Result<(), String> {
    // 使用 toml crate 解析验证
    content.parse::<toml::Value>()
        .map(|_| ())
        .map_err(|e| format!("TOML parse error: {}", e))
}

fn get_config_path(app: &AppHandle) -> Result<std::path::PathBuf, String> {
    let data_dir = app.path().app_data_dir()
        .map_err(|e| format!("Failed to get data dir: {}", e))?;
    Ok(data_dir.parent()
        .unwrap_or(&data_dir)
        .join(".anyclaw")
        .join("config.toml"))
}
```

**验收标准**:
- [ ] 可以读取配置文件内容
- [ ] 可以写入配置文件
- [ ] 可以验证 TOML 格式
- [ ] 错误处理完善

---

### 任务 2：创建配置编辑器组件

**文件**: `tauri-app/src/components/settings/ConfigEditor.tsx` (新建)

**描述**: 创建配置文件编辑器 React 组件

**要点**:
- 使用 `<textarea>` 显示 TOML 内容（或 Monaco Editor）
- 添加行号显示
- 添加保存/重置按钮
- 添加格式验证反馈
- 处理 API Key 显示/隐藏

**组件接口**:
```tsx
interface ConfigEditorProps {
  onSaved?: () => void;
}

function ConfigEditor({ onSaved }: ConfigEditorProps) {
  const [content, setContent] = useState('');
  const [originalContent, setOriginalContent] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // 加载配置
  // 保存配置
  // 重置配置
  // 验证格式
}
```

**验收标准**:
- [ ] 可以显示配置内容
- [ ] 可以编辑内容
- [ ] 保存前验证格式
- [ ] 显示保存状态和错误

---

### 任务 3：创建服务控制组件

**文件**: `tauri-app/src/components/settings/ServiceControl.tsx` (新建)

**描述**: 创建 sidecar 服务控制组件

**要点**:
- 显示服务状态（运行中/已停止/启动中/停止中）
- 显示端口号和运行时间
- 提供启动/停止/重启按钮
- 显示操作进度

**组件接口**:
```tsx
interface ServiceControlProps {
  sidecarStatus: SidecarStatus;
  onStart: () => void;
  onStop: () => void;
  onRestart: () => void;
  isOperating?: boolean;
}

function ServiceControl({
  sidecarStatus,
  onStart,
  onStop,
  onRestart,
  isOperating
}: ServiceControlProps) {
  // 渲染状态卡片
  // 渲染控制按钮
}
```

**验收标准**:
- [ ] 正确显示服务状态
- [ ] 按钮交互正常
- [ ] 状态变化有动画反馈

---

### 任务 4：更新设置对话框

**文件**: `tauri-app/src/components/SettingsDialog.tsx`

**描述**: 集成配置编辑器和服务控制到设置对话框

**要点**:
- 添加"配置文件"标签页
- 添加"服务控制"标签页
- 保存配置后提示重启

**UI 结构**:
```
设置对话框
├── LLM 设置（现有）
├── 配置文件（新增）
│   └── ConfigEditor
└── 服务控制（新增）
    └── ServiceControl
```

**验收标准**:
- [ ] 新标签页正常显示
- [ ] 切换流畅
- [ ] 样式与现有页面一致

---

### 任务 5：添加保存后重启提示

**文件**: `tauri-app/src/components/settings/ConfigEditor.tsx`

**描述**: 配置保存成功后提示用户重启服务

**要点**:
- 保存成功后显示 AlertDialog
- 提供"立即重启"和"稍后"选项
- 点击"立即重启"调用 `restart_sidecar`

**验收标准**:
- [ ] 保存成功后显示提示
- [ ] 可以立即重启
- [ ] 可以稍后重启

---

### 任务 6：添加单元测试

**文件**: `tauri-app/src/components/settings/__tests__/ConfigEditor.test.tsx`

**描述**: 测试配置编辑器和服务控制组件

**测试用例**:
1. `test_loads_config_on_mount` - 组件挂载时加载配置
2. `test_saves_config_on_button_click` - 点击保存按钮保存配置
3. `test_shows_error_on_invalid_toml` - 无效 TOML 显示错误
4. `test_shows_restart_prompt_after_save` - 保存后显示重启提示
5. `test_service_control_buttons_work` - 服务控制按钮正常

**验收标准**:
- [ ] 所有测试通过
- [ ] 覆盖核心场景

---

## 依赖关系

```
任务 1 (Rust 命令)
    ↓
任务 2 (ConfigEditor) ← 任务 3 (ServiceControl)
              ↓
        任务 4 (集成)
              ↓
        任务 5 (重启提示)
              ↓
        任务 6 (测试)
```

## 预估工作量

| 任务 | 预估时间 |
|------|----------|
| 任务 1 | 45 分钟 |
| 任务 2 | 1 小时 |
| 任务 3 | 45 分钟 |
| 任务 4 | 30 分钟 |
| 任务 5 | 30 分钟 |
| 任务 6 | 45 分钟 |
| **总计** | **4 小时** |
