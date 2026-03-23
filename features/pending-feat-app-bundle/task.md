# Task: 桌面应用打包方案

## 任务分解

### Phase 1: PyInstaller 打包 (P1)

- [ ] **1.1 创建 PyInstaller 打包脚本**
  - 文件: `anyclaw/build_sidecar.py`
  - 配置 hidden imports
  - 配置数据收集
  - 配置排除模块

- [ ] **1.2 本地验证打包**
  - 在开发机运行打包
  - 验证可执行文件功能
  - 检查体积

- [ ] **1.3 处理常见问题**
  - 动态导入问题
  - 数据文件缺失
  - 权限问题

### Phase 2: Tauri Sidecar 集成 (P1)

- [ ] **2.1 配置 tauri.conf.json**
  - 添加 externalBin 配置
  - 配置 shell plugin

- [ ] **2.2 创建 binaries 目录结构**
  - 按平台命名规范组织文件

- [ ] **2.3 实现 Rust 启动逻辑**
  - 文件: `tauri-app/src-tauri/src/lib.rs`
  - setup 中启动 sidecar
  - 窗口关闭时停止 sidecar
  - 进程状态管理

- [ ] **2.4 前端等待逻辑**
  - 文件: `tauri-app/src/lib/api.ts`
  - waitForSidecar 函数
  - 自动重连机制

### Phase 3: 构建脚本 (P2)

- [ ] **3.1 创建构建脚本**
  - 文件: `scripts/build-release.sh`
  - 检测平台
  - 构建 sidecar
  - 构建 Tauri

- [ ] **3.2 创建清理脚本**
  - 文件: `scripts/clean-build.sh`

- [ ] **3.3 创建开发脚本**
  - 文件: `scripts/dev.sh`
  - 开发模式下启动 sidecar + tauri

### Phase 4: CI/CD (P2)

- [ ] **4.1 创建 GitHub Actions Workflow**
  - 文件: `.github/workflows/release.yml`
  - 触发条件: tag v*.*.*
  - 并行构建三平台

- [ ] **4.2 配置构建矩阵**
  - Windows: windows-latest
  - macOS: macos-latest (x64 + arm64)
  - Linux: ubuntu-latest

- [ ] **4.3 配置 Release 发布**
  - 上传安装包
  - 生成 Release Notes

- [ ] **4.4 PR 构建验证**
  - 文件: `.github/workflows/build.yml`
  - PR 触发构建测试

### Phase 5: 签名与公证 (P3)

- [ ] **5.1 Windows 代码签名**
  - 申请证书
  - 配置 signtool

- [ ] **5.2 macOS 公证**
  - 配置 Apple Developer
  - notarize 流程

## 技术要点

### PyInstaller 注意事项

```python
# 常见 hidden imports
"--hidden-import=uvicorn.logging",
"--hidden-import=uvicorn.loops.auto",
"--hidden-import=uvicorn.protocols.http.auto",
"--hidden-import=uvicorn.protocols.websockets.auto",
"--hidden-import=uvicorn.lifespan.on",

# litellm 需要收集数据
"--collect-data=litellm",
```

### Tauri Sidecar 命名规范

```
{bin_name}-{target_triple}
例如:
- anyclaw-sidecar-x86_64-pc-windows-msvc.exe
- anyclaw-sidecar-x86_64-apple-darwin
- anyclaw-sidecar-aarch64-apple-darwin
- anyclaw-sidecar-x86_64-unknown-linux-gnu
```

### GitHub Actions 构建矩阵

```yaml
strategy:
  matrix:
    include:
      - os: windows-latest
        target: x86_64-pc-windows-msvc
      - os: macos-latest
        target: x86_64-apple-darwin
      - os: macos-latest
        target: aarch64-apple-darwin
      - os: ubuntu-latest
        target: x86_64-unknown-linux-gnu
```

## 估算

| 阶段 | 工作量 | 优先级 |
|------|--------|--------|
| Phase 1: PyInstaller | 4h | P1 |
| Phase 2: Tauri 集成 | 4h | P1 |
| Phase 3: 构建脚本 | 2h | P2 |
| Phase 4: CI/CD | 3h | P2 |
| Phase 5: 签名公证 | 4h | P3 |
| **总计** | **17h** | - |

## 验证清单

- [ ] 在无 Python 的 Windows 机器上运行成功
- [ ] 在无 Python 的 macOS 机器上运行成功
- [ ] 在无 Python 的 Linux 机器上运行成功
- [ ] 应用启动时 sidecar 自动启动
- [ ] 应用关闭时 sidecar 自动停止
- [ ] 安装包体积 < 100MB
- [ ] CI 构建成功
