# 配置系统一致性修复

## 背景

在调试 sidecar 启动问题时发现，Python `loader.py` 的 `Config` 模型与前端 `configSchema.ts` 以及 `config.template.toml` 模板之间存在不一致，导致某些配置字段无法被正确加载。

## 问题分析

### 1. 缺失的字段定义

| 字段 | config.template.toml | loader.py | configSchema.ts |
|------|---------------------|----------|-----------------|
| `[commands]` | ✅ 有定义 | ❌ 缺失 | ❌ 缺失 |
| `[channels.*]` | ✅ 有定义 | ✅ 有定义 | ❌ 缺失 |
| `[mcp_servers]` | ✅ 有定义 | ✅ 有定义 | ❌ 缺失 |

### 2. 具体问题

1. **`[commands]` section 未在 Python Config 中定义**
   - 模板中有 `[commands]` 和 `[commands.permissions]`
   - `loader.py` 没有对应的 Pydantic 模型
   - 加载时会静默忽略这些配置

2. **`[channels]` 配置未在 Tauri 表单中展示**
   - 前端 `configSchema.ts` 没有定义 channels 相关字段
   - 用户无法通过表单编辑 channels 配置

3. **`[mcp_servers]` 未在 Tauri 表单中展示**
   - 前端 `configSchema.ts` 没有定义 mcp_servers 相关字段
   - 用户无法通过表单编辑 MCP 服务器配置

## 用户价值点

### VP-1: 配置模型一致性

**描述**: Python Config 类与前端 configSchema.ts 字段完全对齐，支持所有配置项的加载和编辑

**验收场景** (Gherkin):

```gherkin
Feature: 配置模型一致性
  As a 开发者
  I want to 所有配置字段都能被正确加载和编辑
  So that 配置文件中的任何配置都不会丢失

  Scenario: Python 加载所有配置字段
    Given 配置文件包含 [session] section
    When Python 加载配置
    Then config.session.max_concurrent_sessions 应该被正确解析
    And 不应该抛出验证错误

  Scenario: Python 加载 commands 配置
    Given 配置文件包含 [commands] section
    When Python 加载配置
    Then config.commands 应该被正确解析
    And 不应该静默忽略这些配置

  Scenario: 前端表单显示 channels 配置
    Given 用户打开配置编辑页面
    Then 应该能看到 channels 配置分组
    And 可以编辑 cli, feishu, discord 通道配置

  Scenario: 前端表单显示 mcp_servers 配置
    Given 用户打开配置编辑页面
    Then 应该能看到 mcp_servers 配置分组
    And 可以添加/编辑/删除 MCP 服务器配置
```

## 影响范围

### Python 后端 (loader.py)
- 添加 `CommandsConfig` 类
- 添加 `CommandsPermissionsConfig` 类
- 在 `Config` 类中添加 `commands` 字段

### Tauri 前端 (configSchema.ts)
- 添加 channels 配置字段
- 添加 mcp_servers 配置字段
- 添加对应的 i18n 翻译键

## 非目标
- 不修改现有配置的默认值
- 不改变配置文件格式
- 保持向后兼容
