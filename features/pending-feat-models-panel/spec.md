# 特性：模型配置页面完善

## 概述

完善 Tauri 桌面应用的模型配置页面（ModelsPanel），连接后端 API，实现 Provider 配置管理和模型选择功能，使用户能够通过 UI 完成不同 LLM Provider 的接入配置。

## 背景

### 当前状态

1. **已完成 `feat-config-editor`**：
   - 原始 TOML 配置文件编辑器（适合高级用户）
   - Sidecar 服务控制（启动/停止/重启）

2. **当前 `ModelsPanel.tsx` 问题**：
   - 使用 mock 数据，没有连接后端 API
   - 模型配置无法持久化
   - 缺少针对不同 Provider 的差异化配置界面
   - 没有模型连接测试功能

3. **后端 API 现状**：
   - `GET /api/config` - 获取配置（但隐藏 API Key）
   - `PUT /api/config` - 更新配置（但不持久化到文件）
   - 缺少 Provider 级别的连接测试 API

### 问题

- 普通用户无法通过友好的 UI 配置不同 Provider
- 需要手动编辑 TOML 文件才能添加新的 Provider
- 无法在 UI 中测试 Provider 连接是否正常

### 目标架构

```
前端 ModelsPanel
      │
      ├── 获取 Provider 列表 ──► GET /api/providers
      │
      ├── 获取 Provider 配置 ──► GET /api/providers/{name}
      │
      ├── 更新 Provider 配置 ──► PUT /api/providers/{name}
      │        │
      │        └── 持久化到 config.toml
      │
      ├── 测试 Provider 连接 ──► POST /api/providers/{name}/test
      │
      └── 获取可用模型列表 ──► GET /api/providers/{name}/models
```

## 用户价值点

### 价值点 1：Provider 配置管理

**描述**：用户可以为不同的 LLM Provider（OpenAI、Anthropic、ZAI、DeepSeek、Ollama 等）配置 API Key 和自定义 Endpoint。

**验收场景**：

```gherkin
Feature: Provider 配置管理

  Scenario: 查看 Provider 列表
    Given 用户打开设置页面的"模型"标签
    When 页面加载完成
    Then 显示所有支持的 Provider 列表
    And 显示每个 Provider 的配置状态（已配置/未配置）

  Scenario: 配置 Provider API Key
    Given 用户选择了一个 Provider（如 OpenAI）
    When 输入 API Key 并保存
    Then API Key 被安全存储到配置文件
    And Provider 状态更新为"已配置"
    And API Key 默认隐藏显示

  Scenario: 配置自定义 Endpoint
    Given 用户需要使用自定义 API 端点
    When 输入 Base URL 并保存
    Then 自定义端点被保存到配置文件
    And 后续请求使用自定义端点

  Scenario: 显示/隐藏 API Key
    Given Provider 已配置 API Key
    When 点击"显示"按钮
    Then 显示完整的 API Key
    When 点击"隐藏"按钮
    Then API Key 显示为 ****
```

### 价值点 2：模型选择与切换

**描述**：用户可以在已配置的 Provider 中选择和切换默认使用的模型。

**验收场景**：

```gherkin
Feature: 模型选择与切换

  Scenario: 查看可用模型
    Given 用户已配置至少一个 Provider
    When 打开模型选择下拉框
    Then 显示该 Provider 支持的所有模型
    And 显示当前选中的默认模型

  Scenario: 切换默认模型
    Given 用户选择了一个模型
    When 点击"设为默认"按钮
    Then 该模型被设置为默认模型
    And 配置文件中的 llm.model 被更新

  Scenario: 添加自定义模型
    Given 用户想使用 Provider 官方列表外的模型
    When 输入自定义模型 ID 并保存
    Then 自定义模型被添加到可用列表
    And 可以设置为默认模型
```

### 价值点 3：Provider 连接测试

**描述**：用户可以在配置完成后测试 Provider 连接是否正常，验证 API Key 和 Endpoint 是否有效。

**验收场景**：

```gherkin
Feature: Provider 连接测试

  Scenario: 测试 Provider 连接
    Given 用户已配置 Provider 的 API Key
    When 点击"测试连接"按钮
    Then 发送测试请求到 Provider API
    And 显示测试结果（成功/失败）
    And 成功时显示可用模型数量
    And 失败时显示错误原因

  Scenario: 测试失败诊断
    Given Provider 连接测试失败
    When 显示错误信息
    Then 提供可能的失败原因（API Key 无效、网络问题、Endpoint 错误）
    And 提供解决建议
```

## 技术方案

### 后端 API 扩展

1. **新增 Provider API 端点** (`anyclaw/api/routes/providers.py`)
   ```python
   # 获取所有 Provider 配置
   GET /api/providers

   # 获取单个 Provider 配置
   GET /api/providers/{name}

   # 更新 Provider 配置（并持久化）
   PUT /api/providers/{name}

   # 测试 Provider 连接
   POST /api/providers/{name}/test

   # 获取 Provider 可用模型
   GET /api/providers/{name}/models
   ```

2. **配置持久化增强**
   - 修改 `PUT /api/config` 支持持久化到 config.toml
   - 或创建专门的配置持久化服务

### 前端实现

1. **ModelsPanel 重构** (`tauri-app/src/components/settings/ModelsPanel.tsx`)
   - 移除 mock 数据，连接后端 API
   - Provider 配置卡片（API Key、Base URL）
   - 模型选择下拉框
   - 连接测试按钮和状态显示

2. **新增 Hooks** (`tauri-app/src/hooks/useProviders.ts`)
   - `useProviders()` - Provider 列表管理
   - `useProviderTest()` - Provider 连接测试

3. **类型定义** (`tauri-app/src/types/providers.ts`)
   ```typescript
   interface Provider {
     name: string
     display_name: string
     api_key?: string
     base_url?: string
     is_configured: boolean
     models: string[]
   }
   ```

## 优先级

75（中高优先级）- 提升用户体验，是设置页面的核心功能

## 依赖

- `feat-config-editor`（已完成）- 配置文件读写基础

## 相关文件

- `tauri-app/src/components/settings/ModelsPanel.tsx` - 模型配置面板
- `tauri-app/src/components/settings/ProviderSettings.tsx` - Provider 配置组件（已存在，需增强）
- `tauri-app/src/components/settings/LLMSettings.tsx` - LLM 参数配置组件（已存在）
- `anyclaw/api/routes/config.py` - 配置 API（需扩展）
- `anyclaw/config/loader.py` - 配置加载器
- `anyclaw/config/settings.py` - 配置模型
