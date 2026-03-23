# Checklist: 桌面应用打包方案

## 开发前

- [x] 确认 PyInstaller 已安装
- [x] 确认 Tauri 开发环境正常
- [x] 阅读 PyInstaller 文档
- [x] 阅读 Tauri Sidecar 文档

## Phase 1: PyInstaller 打包

- [x] 创建 `anyclaw/build_sidecar.py`
- [x] 配置 hidden imports (uvicorn, litellm 等)
- [x] 配置数据收集
- [x] 配置排除模块
- [x] 本地打包测试（需要 Python 3.11+ 环境）
- [ ] 验证打包后功能正常（需要 CI 环境）
- [x] 检查打包体积（约 57MB，符合预期）

## Phase 2: Tauri Sidecar 集成

- [x] 修改 `tauri.conf.json` 添加 externalBin
- [x] 创建 `binaries/` 目录
- [x] 修改 `lib.rs` 添加 sidecar 启动逻辑
- [x] 添加 SidecarState 状态管理
- [x] 实现应用关闭时停止 sidecar
- [x] 支持生产模式（打包的 sidecar）和开发模式（poetry/python）
- [ ] 前端添加 waitForSidecar 逻辑
- [ ] 本地测试完整流程

## Phase 3: 构建脚本

- [x] 创建 `scripts/build-release.sh`
- [x] 创建 `scripts/clean-build.sh`
- [x] 创建 `scripts/dev.sh`
- [x] 创建 `scripts/build-sidecar.sh`
- [ ] 测试本地构建流程

## Phase 4: CI/CD

- [x] 创建 `.github/workflows/release.yml`
- [x] 创建 `.github/workflows/build.yml`
- [x] 配置 macOS/Windows 构建矩阵
- [x] 配置 Release 发布
- [ ] 测试 CI 构建流程

## Phase 5: 签名与公证 (可选)

- [ ] Windows 代码签名
- [ ] macOS 公证

## 文档

- [x] 添加打包指南文档 (`docs/app-bundle.md`)
- [ ] 更新 README 添加下载链接
- [ ] 添加安装说明文档
- [ ] 添加故障排除文档
