# Checklist: 桌面应用打包方案

## 开发前

- [ ] 确认 PyInstaller 已安装
- [ ] 确认 Tauri 开发环境正常
- [ ] 阅读 PyInstaller 文档
- [ ] 阅读 Tauri Sidecar 文档

## Phase 1: PyInstaller 打包

- [ ] 创建 `anyclaw/build_sidecar.py`
- [ ] 配置 hidden imports (uvicorn, litellm 等)
- [ ] 配置数据收集
- [ ] 配置排除模块
- [ ] 本地打包测试
- [ ] 验证打包后功能正常
- [ ] 检查打包体积

## Phase 2: Tauri Sidecar 集成

- [ ] 修改 `tauri.conf.json` 添加 externalBin
- [ ] 创建 `binaries/` 目录
- [ ] 修改 `lib.rs` 添加 sidecar 启动逻辑
- [ ] 添加 SidecarState 状态管理
- [ ] 实现应用关闭时停止 sidecar
- [ ] 前端添加 waitForSidecar 逻辑
- [ ] 本地测试完整流程

## Phase 3: 构建脚本

- [ ] 创建 `scripts/build-release.sh`
- [ ] 创建 `scripts/clean-build.sh`
- [ ] 创建 `scripts/dev.sh`
- [ ] 测试本地构建流程

## Phase 4: CI/CD

- [ ] 创建 `.github/workflows/release.yml`
- [ ] 创建 `.github/workflows/build.yml`
- [ ] 配置三平台构建矩阵
- [ ] 配置 Release 发布
- [ ] 测试 CI 构建流程

## Phase 5: 签名与公证 (可选)

- [ ] Windows 代码签名
- [ ] macOS 公证

## 验收测试

### 功能测试

- [ ] Windows 安装包安装成功
- [ ] macOS 安装包安装成功
- [ ] Linux AppImage 运行成功
- [ ] 应用启动后 sidecar 自动运行
- [ ] 健康检查端点正常
- [ ] 聊天功能正常
- [ ] 设置功能正常
- [ ] 应用关闭无残留进程

### 用户体验测试

- [ ] 安装过程简单明了
- [ ] 首次启动无需配置
- [ ] 界面响应流畅
- [ ] 错误提示友好

### 体积测试

- [ ] Windows 安装包 < 100MB
- [ ] macOS 安装包 < 100MB
- [ ] Linux AppImage < 100MB

## 文档

- [ ] 更新 README 添加下载链接
- [ ] 添加安装说明文档
- [ ] 添加故障排除文档

## 完成确认

- [ ] 所有测试通过
- [ ] 代码已合并到 main
- [ ] Release 已发布
- [ ] 文档已更新
