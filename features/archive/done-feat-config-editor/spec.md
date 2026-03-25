# 特性：配置编辑器与服务控制

## 概述

在 Tauri 桌面应用中添加配置文件编辑功能，允许用户直接编辑 config.toml 文件，并提供 sidecar 服务的停止/重启控制，以便在修改配置后应用新设置。

## 背景

### 当前状态

1. **Rust 后端**已有 sidecar 控制命令：
   - `start_sidecar` - 启动服务
   - `stop_sidecar` - 停止服务
   - `restart_sidecar` - 重启服务

2. **Python API** 有基础的配置端点：
   - `GET /api/config` - 获取配置（但不完整，且隐藏敏感信息）
   - `PUT /api/config` - 更新配置（但不持久化到文件）

3. **配置文件**存储在 `~/.anyclaw/config.toml`，格式完整且带注释

### 问题

- 用户无法在 app 中查看完整的配置文件（含注释和说明）
- 修改配置需要手动编辑文件，体验不友好
- 修改配置后需要手动重启 sidecar 才能生效

### 目标架构

```
前端配置编辑器
      │
      ├── 读取完整 TOML 内容 ──► Rust/Python API
      │
      ├── 编辑 TOML（Monaco Editor / Textarea）
      │
      ├── 保存 TOML ──► 写入文件
      │        │
      │        └── 验证 TOML 格式
      │
      └── 提示重启 ──► 调用 restart_sidecar
```

## 用户价值点

### 价值点 1：配置文件编辑器

**描述**：用户可以在 app 中直接查看和编辑完整的 config.toml 文件内容，保留注释和格式。

**验收场景**：

```gherkin
Feature: 配置文件编辑器

  Scenario: 查看配置文件
    Given 用户打开设置页面
    When 切换到"配置文件"标签
    Then 显示完整的 config.toml 内容
    And 保留所有注释和格式

  Scenario: 编辑并保存配置
    Given 用户在配置编辑器中修改了内容
    When 点击"保存"按钮
    Then 配置文件被写入磁盘
    And 显示保存成功提示
    And 显示"需要重启服务才能生效"提示

  Scenario: 编辑时格式验证
    Given 用户在配置编辑器中输入了无效的 TOML 内容
    When 尝试保存
    Then 显示格式错误提示
    And 指出错误位置
    And 阻止保存操作

  Scenario: 重置到默认配置
    Given 用户想恢复默认配置
    When 点击"重置为默认"按钮
    Then 显示确认对话框
    And 确认后恢复到默认配置模板
```

### 价值点 2：Sidecar 服务控制

**描述**：用户可以在 app 中停止和重启 sidecar 服务，以便应用新的配置。

**验收场景**：

```gherkin
Feature: Sidecar 服务控制

  Scenario: 查看服务状态
    Given 用户打开设置页面
    Then 显示当前 sidecar 状态（运行中/已停止/启动中）
    And 显示端口号和运行时间

  Scenario: 停止服务
    Given sidecar 服务正在运行
    When 用户点击"停止服务"按钮
    Then 服务停止
    And 状态更新为"已停止"

  Scenario: 启动服务
    Given sidecar 服务已停止
    When 用户点击"启动服务"按钮
    Then 服务启动
    And 状态更新为"运行中"

  Scenario: 重启服务
    Given sidecar 服务正在运行
    When 用户点击"重启服务"按钮
    Then 服务先停止再启动
    And 加载最新的配置文件
    And 状态更新为"运行中"

  Scenario: 保存配置后提示重启
    Given 用户刚保存了配置文件
    When 保存成功
    Then 显示"配置已保存，是否立即重启服务？"提示
    And 提供"重启"和"稍后"两个选项
```

### 价值点 3：API Key 安全处理

**描述**：敏感信息（如 API Key）在显示时有选项可以隐藏/显示。

**验收场景**：

```gherkin
Feature: API Key 安全处理

  Scenario: 默认隐藏 API Key
    Given 配置文件包含 API Key
    When 在编辑器中显示
    Then API Key 字段默认显示为 ****

  Scenario: 显示 API Key
    Given 用户想查看 API Key
    When 点击"显示"按钮
    Then 显示完整的 API Key

  Scenario: 编辑 API Key
    Given 用户正在编辑 API Key 字段
    When 输入新的 API Key
    Then 新值被保存到配置文件
```

## 技术方案

### 前端实现

1. **SettingsDialog 增强**
   - 添加"配置文件"标签页
   - 使用 `<textarea>` 或 Monaco Editor 显示 TOML 内容
   - 添加保存/重置/格式化按钮

2. **服务控制组件**
   - 在设置页面显示服务状态卡片
   - 提供停止/启动/重启按钮
   - 与 Tauri 命令交互

### 后端 API

1. **新增 Rust 命令** (`lib.rs`)
   ```rust
   #[tauri::command]
   fn read_config_file() -> Result<String, String>

   #[tauri::command]
   fn write_config_file(content: String) -> Result<(), String>

   #[tauri::command]
   fn validate_toml(content: String) -> Result<(), String>

   #[tauri::command]
   fn get_config_template() -> Result<String, String>
   ```

2. **Python API 增强**（可选）
   - `GET /api/config/raw` - 返回原始 TOML 内容
   - `PUT /api/config/raw` - 保存原始 TOML 内容

### 配置文件路径

- macOS/Linux: `~/.anyclaw/config.toml`
- Windows: `%USERPROFILE%\.anyclaw\config.toml`

## 优先级

75（中高优先级）- 提升用户体验，但非核心功能

## 依赖

- 无强依赖
- 可选依赖 `feat-ui-pages-i18n`（国际化支持）

## 相关文件

- `tauri-app/src-tauri/src/lib.rs` - 添加 Tauri 命令
- `tauri-app/src/components/SettingsDialog.tsx` - 前端设置对话框
- `anyclaw/api/routes/config.py` - Python API 端点
- `anyclaw/config/loader.py` - 配置加载器
- `anyclaw/config/config.template.toml` - 配置模板
