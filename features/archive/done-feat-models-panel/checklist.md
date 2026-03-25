# 完成检查清单：模型配置页面完善

## 后端实现

- [x] **Provider API 扩展**
  - [x] `GET /api/providers` - 获取 Provider 列表
  - [x] `GET /api/providers/{name}` - 获取单个 Provider 配置
  - [x] `PUT /api/providers/{name}` - 更新 Provider 配置
  - [x] `POST /api/providers/{name}/test` - 测试 Provider 连接
  - [x] 配置更新持久化到 config.toml

- [x] **Provider 连接测试服务**
  - [x] OpenAI Provider 测试实现
  - [x] Anthropic Provider 测试实现
  - [x] ZAI/GLM Provider 测试实现
  - [x] Ollama Provider 测试实现
  - [x] 错误处理和超时控制

## 前端实现

- [x] **类型定义**
  - [x] Provider 接口定义
  - [x] ProviderConfig 接口定义
  - [x] TestResult 接口定义

- [x] **React Hooks**
  - [x] `useProviders()` hook
  - [x] `useProvider()` hook
  - [x] `useUpdateProvider()` hook
  - [x] `useTestProvider()` hook

- [x] **ModelsPanel 重构**
  - [x] 移除 mock 数据
  - [x] 连接后端 API
  - [x] Provider 配置卡片 UI
  - [x] API Key 输入（显示/隐藏）
  - [x] Base URL 输入
  - [x] 连接测试按钮和状态显示
  - [x] 保存按钮

- [x] **ProviderSettings 增强**
  - [x] 配置状态指示器
  - [x] 优化连接测试 UX
  - [x] 错误提示优化

## 国际化

- [x] **i18n 翻译**
  - [x] 中文翻译
  - [x] 英文翻译

## 测试

- [x] **后端测试**
  - [x] Provider 相关测试通过 (18 tests)
  - [x] Config 测试通过 (4 tests)

- [ ] **前端测试** (待完善)
  - [ ] useProviders hook 测试
  - [ ] ModelsPanel 组件测试

## 验收标准

- [x] 用户可以通过 UI 配置 Provider API Key
- [x] 用户可以通过 UI 配置自定义 Base URL
- [x] 用户可以测试 Provider 连接
- [x] 用户可以选择和切换默认模型
- [x] 配置更新后正确持久化到 config.toml
- [x] TypeScript 编译通过
- [x] 前端构建成功

## 文档

- [ ] 更新 CLAUDE.md 中的相关说明
- [ ] 更新 API 文档（如有）
