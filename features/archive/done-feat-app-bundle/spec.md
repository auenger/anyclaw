# Feature: 桌面应用打包方案

> 将 AnyClaw 打包成开箱即用的桌面应用，用户无需安装 Python 环境即可使用。

## 概述

**ID**: feat-app-bundle
**优先级**: 60
**大小**: L (4 个价值点)
**状态**: pending

## 背景

当前 AnyClaw 桌面应用需要用户：
1. 安装 Python 3.11+ 环境
2. 安装 Poetry 并配置依赖
3. 手动启动 sidecar 服务
4. 再启动 Tauri 应用

这对非技术用户非常不友好。我们需要实现"下载即用"的体验。

## 目标方案

采用 **PyInstaller + Tauri Sidecar** 方案：

```
┌─────────────────────────────────────┐
│         Tauri App (Shell)           │
│  ┌───────────────────────────────┐  │
│  │      React Frontend           │  │
│  └───────────────────────────────┘  │
│                ↓ HTTP/SSE            │
│  ┌───────────────────────────────┐  │
│  │  Sidecar: anyclaw-sidecar     │  │
│  │  (PyInstaller 打包的 exe)     │  │
│  │  - 内嵌 Python 3.11 运行时     │  │
│  │  - 内嵌所有 pip 依赖          │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## 用户价值点

### 价值点 1: PyInstaller 打包 Sidecar

**描述**: 将 Python sidecar 服务打包成独立可执行文件，内嵌 Python 运行时和所有依赖。

**验收场景**:

```gherkin
Feature: PyInstaller Sidecar 打包

Scenario: 打包 Windows 版本
  Given 开发者在 Windows 环境下
  When 运行打包脚本
  Then 生成 anyclaw-sidecar-x86_64-pc-windows-msvc.exe
  And 文件大小在 50-150MB 范围内
  And 在无 Python 环境的 Windows 机器上可直接运行

Scenario: 打包 macOS 版本
  Given 开发者在 macOS 环境下
  When 运行打包脚本
  Then 生成 anyclaw-sidecar-x86_64-apple-darwin
  And anyclaw-sidecar-aarch64-apple-darwin (M1/M2)
  And 在无 Python 环境的 macOS 机器上可直接运行

Scenario: 打包 Linux 版本
  Given 开发者在 Linux 环境下
  When 运行打包脚本
  Then 生成 anyclaw-sidecar-x86_64-unknown-linux-gnu
  And 在无 Python 环境的 Linux 机器上可直接运行

Scenario: Sidecar 正常启动
  Given 已打包的 sidecar 可执行文件
  When 运行 ./anyclaw-sidecar sidecar --port 62601
  Then 服务在 localhost:62601 启动
  And /health 端点返回 200 OK
  And 所有 API 端点正常工作
```

### 价值点 2: Tauri Sidecar 集成

**描述**: 配置 Tauri 应用自动启动和管理 sidecar 进程。

**验收场景**:

```gherkin
Feature: Tauri Sidecar 集成

Scenario: 应用启动时自动启动 Sidecar
  Given 用户双击启动 AnyClaw 应用
  When Tauri 应用初始化完成
  Then Sidecar 进程自动在后台启动
  And Sidecar 监听 localhost:62601
  And 前端可以通过 API 与 Sidecar 通信

Scenario: 应用关闭时自动停止 Sidecar
  Given AnyClaw 应用正在运行
  And Sidecar 进程正在运行
  When 用户关闭应用窗口
  Then Sidecar 进程被正确终止
  And 无残留进程

Scenario: 前端等待 Sidecar 就绪
  Given 应用刚启动
  And Sidecar 正在启动中
  When 前端尝试连接 API
  Then 前端自动重试连接
  And 最多等待 5 秒
  And Sidecar 就绪后正常工作

Scenario: Sidecar 启动失败处理
  Given Sidecar 因端口占用无法启动
  When Tauri 检测到启动失败
  Then 显示友好错误提示
  And 提供重试选项
```

### 价值点 3: 跨平台构建脚本

**描述**: 提供自动化脚本，支持本地和 CI 环境下构建三个平台的安装包。

**验收场景**:

```gherkin
Feature: 跨平台构建脚本

Scenario: 本地构建脚本
  Given 开发者在项目根目录
  When 运行 ./scripts/build-release.sh
  Then 自动检测当前平台
  And 构建 Sidecar
  And 构建 Tauri 应用
  And 生成安装包到 release/ 目录

Scenario: 构建 Windows 安装包
  Given 构建脚本在 Windows 环境运行
  When 构建完成
  Then 生成 AnyClaw-Setup-{version}.exe
  And 安装包包含 Tauri 应用和 Sidecar
  And 安装后可直接使用

Scenario: 构建 macOS 安装包
  Given 构建脚本在 macOS 环境运行
  When 构建完成
  Then 生成 AnyClaw-{version}.dmg
  And 支持 Intel 和 Apple Silicon 双架构
  And 安装后可直接使用

Scenario: 构建 Linux 安装包
  Given 构建脚本在 Linux 环境运行
  When 构建完成
  Then 生成 AnyClaw-{version}.AppImage
  And AppImage 可直接运行无需安装
```

### 价值点 4: CI/CD 自动化

**描述**: 配置 GitHub Actions 自动构建和发布。

**验收场景**:

```gherkin
Feature: CI/CD 自动化

Scenario: 创建 Release Tag 触发构建
  Given 仓库有新的 tag v*.*.*
  When GitHub Actions 被触发
  Then 并行构建 Windows/macOS/Linux 三个平台
  And 所有构建产物上传到 Release
  And Release 包含版本说明

Scenario: PR 构建验证
  Given 有新的 Pull Request
  When GitHub Actions 被触发
  Then 构建所有平台
  And 运行测试
  And 构建成功才能合并

Scenario: 构建产物完整性
  Given CI 构建完成
  When 下载安装包
  Then 安装包包含所有必要文件
  And 签名正确 (macOS/Windows)
  And 可在对应平台正常安装运行
```

## 用户体验对比

| 环节 | 当前体验 | 打包后体验 |
|------|---------|-----------|
| 安装 | 需装 Python、Poetry、依赖 | 双击安装包，一键完成 |
| 配置 | 需配置 .env、config.json | 首次启动自动初始化 |
| 启动 | 命令行启动 sidecar + App | 双击图标，自动完成 |
| 升级 | git pull、poetry install | 下载新版覆盖安装 |
| 卸载 | 手动清理多个目录 | 正常卸载程序 |

## 体积预估

| 组件 | 大小 |
|------|------|
| Tauri App (Rust + 前端) | ~10 MB |
| Sidecar (PyInstaller 打包) | 40-80 MB |
| **总计** | **50-90 MB** |

## 技术方案详情

### 1. PyInstaller 配置

```python
# anyclaw/build_sidecar.py
PyInstaller.__main__.run([
    "anyclaw/__main__.py",
    "--name=anyclaw-sidecar",
    "--onefile",
    "--console",
    "--clean",
    "--noconfirm",
    # 隐藏导入
    "--hidden-import=uvicorn.logging",
    "--hidden-import=uvicorn.loops.auto",
    "--hidden-import=uvicorn.protocols.http.auto",
    # 收集数据
    "--collect-data=litellm",
    "--collect-data=pydantic",
    # 排除不需要的模块
    "--exclude-module=tkinter",
    "--exclude-module=matplotlib",
])
```

### 2. Tauri 配置

```json
// tauri-app/src-tauri/tauri.conf.json
{
  "bundle": {
    "externalBin": ["binaries/anyclaw-sidecar"]
  },
  "plugins": {
    "shell": {
      "sidecar": true,
      "scope": [{"name": "binaries/anyclaw-sidecar", "sidecar": true}]
    }
  }
}
```

### 3. Sidecar 目录结构

```
tauri-app/src-tauri/binaries/
├── anyclaw-sidecar-x86_64-pc-windows-msvc.exe
├── anyclaw-sidecar-x86_64-apple-darwin
├── anyclaw-sidecar-aarch64-apple-darwin
└── anyclaw-sidecar-x86_64-unknown-linux-gnu
```

### 4. Rust 启动代码

```rust
// tauri-app/src-tauri/src/lib.rs
fn start_sidecar(app: &tauri::AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    let shell = app.shell();
    let (mut rx, child) = shell
        .sidecar("anyclaw-sidecar")?
        .args(["sidecar", "--port", "62601"])
        .spawn()?;
    // 保存进程句柄，监听输出...
}
```

## 依赖

- 无前置依赖

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| PyInstaller 打包体积大 | 下载慢 | 使用 UPX 压缩，排除不必要模块 |
| 跨平台兼容性问题 | 部分用户无法使用 | 充分测试各平台，提供多种格式 |
| 签名成本 | macOS/Windows 警告 | 申请开发者证书，正确签名 |
| 更新机制缺失 | 用户使用旧版本 | 后续添加自动更新功能 |

## 后续扩展

- 自动更新功能
- 便携版（Portable）
- 静默安装参数
- 企业部署支持
