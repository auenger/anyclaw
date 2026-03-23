# AnyClaw 桌面应用打包指南

本文档说明如何将 AnyClaw 打包成开箱即用的桌面应用。

## 概述

AnyClaw 使用 **PyInstaller + Tauri Sidecar** 方案打包：

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

## 支持平台

| 平台 | 架构 | 状态 |
|------|------|------|
| macOS | Apple Silicon (M1/M2/M3) | ✅ 支持 |
| macOS | Intel (x86_64) | ✅ 支持 |
| Windows | x86_64 | ✅ 支持 |
| Linux | x86_64 | 🚧 计划中 |

## 开发环境要求

### macOS
- Python 3.11+
- Node.js 18+
- Rust (via rustup)
- Xcode Command Line Tools

### Windows
- Python 3.11+
- Node.js 18+
- Rust (via rustup)
- Visual Studio Build Tools

## 本地构建

### 1. 安装依赖

```bash
# 安装 Python 依赖
cd anyclaw
pip install pyinstaller
pip install -e .

# 安装前端依赖
cd ../tauri-app
npm install
```

### 2. 构建 Sidecar

```bash
# 从项目根目录
./scripts/build-sidecar.sh

# 或指定平台
./scripts/build-sidecar.sh --platform macos-arm64
./scripts/build-sidecar.sh --platform windows-x64
```

### 3. 构建完整应用

```bash
# 一键构建（sidecar + Tauri）
./scripts/build-release.sh
```

构建产物位于：
- macOS: `tauri-app/src-tauri/target/release/bundle/dmg/`
- Windows: `tauri-app/src-tauri/target/release/bundle/msi/`

## CI/CD 自动构建

### Release 构建

创建新的 git tag 会自动触发构建：

```bash
# 创建并推送 tag
git tag v0.1.0
git push origin v0.1.0
```

GitHub Actions 会自动：
1. 构建 macOS (Intel + Apple Silicon) 和 Windows 版本
2. 创建 GitHub Release
3. 上传安装包

### PR 构建

每个 Pull Request 会触发构建验证，确保代码可以正常打包。

## 目录结构

```
anyclaw/
├── anyclaw/
│   ├── build_sidecar.py     # PyInstaller 打包脚本
│   └── anyclaw/              # Python 包
│       └── __main__.py       # 入口点
├── tauri-app/
│   ├── src/                  # React 前端
│   └── src-tauri/
│       ├── src/lib.rs        # Rust 代码（sidecar 管理）
│       ├── binaries/         # Sidecar 可执行文件
│       └── tauri.conf.json   # Tauri 配置
├── scripts/
│   ├── build-release.sh      # 完整构建脚本
│   ├── build-sidecar.sh      # Sidecar 构建脚本
│   ├── clean-build.sh        # 清理脚本
│   └── dev.sh                # 开发脚本
└── .github/workflows/
    ├── release.yml           # Release 构建
    └── build.yml             # PR 构建
```

## 运行模式

应用支持两种运行模式：

### 开发模式
- 使用 poetry 或系统 Python 启动 sidecar
- 支持热重载
- 需要完整的开发环境

### 生产模式
- 使用打包的 sidecar 可执行文件
- 无需 Python 环境
- 开箱即用

模式自动检测：应用启动时会检查 sidecar 可执行文件是否存在，存在则使用生产模式。

## 故障排除

### 打包失败：找不到模块

添加隐藏导入到 `build_sidecar.py`：

```python
HIDDEN_IMPORTS = [
    # ...
    "your.module.name",
]
```

### 打包体积过大

1. 添加排除模块到 `EXCLUDE_MODULES`
2. 使用 UPX 压缩（Windows）

### macOS 无法打开应用

需要代码签名和公证。临时解决：
```bash
xattr -cr AnyClaw.app
```

### Windows SmartScreen 警告

需要代码签名证书。

## 签名与公证（可选）

### macOS 公证

```bash
# 构建
npm run tauri:build

# 签名
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" src-tauri/target/release/bundle/macos/AnyClaw.app

# 公证
xcrun notarytool submit src-tauri/target/release/bundle/dmg/AnyClaw.dmg --apple-id "your@email.com" --password "@keychain:AC_PASSWORD" --team-id "TEAM_ID" --wait
```

### Windows 签名

需要购买代码签名证书，然后配置 GitHub Actions secrets。

## 更新此文档

如果打包流程有变化，请更新此文档。
