# Feature: workspace 写入限制

## 概述

增加 `restrict_to_workspace` 配置项，控制文件写入权限，限制工具只能在 workspace 目录内写入文件，提升 AnyClaw 的安全性。

## 背景

当前 AnyClaw 的 `WriteFileTool` 虽然有 `allowed_dir` 参数，但 `_resolve_path()` 方法完全没有使用这个参数来做权限检查。绝对路径直接返回，相对路径解析到 workspace，没有任何限制。

这导致 LLM 可能自行判断说没有权限，但实际上代码层面并没有限制。需要实现真正的权限控制机制。

## 用户价值点

### VP1: 配置项支持

用户可以通过配置控制是否启用 workspace 限制。

```gherkin
Feature: restrict_to_workspace 配置项

  Scenario: 默认启用限制
    Given 用户未配置 restrict_to_workspace
    When 系统加载配置
    Then restrict_to_workspace 默认值为 true

  Scenario: 通过配置文件禁用限制
    Given 配置文件 ~/.anyclaw/config.json 存在
    And 配置内容为 {"security": {"restrict_to_workspace": false}}
    When 系统加载配置
    Then restrict_to_workspace 为 false

  Scenario: 通过环境变量配置
    Given 环境变量 ANYCLAW_RESTRICT_TO_WORKSPACE=false
    When 系统加载配置
    Then restrict_to_workspace 为 false
```

### VP2: 路径检查逻辑

`WriteFileTool` 在写入文件前检查路径是否在允许范围内。

```gherkin
Feature: 写入路径检查

  Scenario: 允许写入 workspace 内的文件
    Given restrict_to_workspace = true
    And workspace = /Users/test/.anyclaw/workspace
    When 用户尝试写入 /Users/test/.anyclaw/workspace/hello.md
    Then 写入成功

  Scenario: 允许写入 workspace 子目录内的文件
    Given restrict_to_workspace = true
    And workspace = /Users/test/.anyclaw/workspace
    When 用户尝试写入 /Users/test/.anyclaw/workspace/memory/test.md
    Then 写入成功

  Scenario: 阻止写入 workspace 外的文件
    Given restrict_to_workspace = true
    And workspace = /Users/test/.anyclaw/workspace
    When 用户尝试写入 /etc/passwd
    Then 返回权限错误 "路径超出 workspace 范围"
    And 文件未被写入

  Scenario: 禁用限制时允许任意路径写入
    Given restrict_to_workspace = false
    And workspace = /Users/test/.anyclaw/workspace
    When 用户尝试写入 /tmp/test.md
    Then 写入成功（如果系统权限允许）

  Scenario: 处理符号链接
    Given restrict_to_workspace = true
    And workspace = /Users/test/.anyclaw/workspace
    And /Users/test/.anyclaw/workspace/link -> /etc
    When 用户尝试写入 /Users/test/.anyclaw/workspace/link/passwd
    Then 返回权限错误 "路径超出 workspace 范围"
```

### VP3: 错误提示

提供清晰友好的错误提示。

```gherkin
Feature: 权限错误提示

  Scenario: 显示清晰的权限错误
    Given restrict_to_workspace = true
    And workspace = /Users/test/.anyclaw/workspace
    When 用户尝试写入 /tmp/test.md
    Then 返回错误信息包含:
      """
      权限错误: 路径 /tmp/test.md 超出 workspace 范围
      允许的目录: /Users/test/.anyclaw/workspace
      提示: 设置 restrict_to_workspace=false 可禁用此限制
      """
```

## 涉及文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `anyclaw/config/settings.py` | 修改 | 添加 `restrict_to_workspace` 配置项 |
| `anyclaw/tools/filesystem.py` | 修改 | 实现路径检查逻辑 |
| `anyclaw/agent/loop.py` | 修改 | 传递配置到工具 |
| `anyclaw/templates/TOOLS.md` | 修改 | 更新文档说明 |

## 配置示例

```json
{
  "security": {
    "restrict_to_workspace": true
  }
}
```

## 安全考虑

1. **默认启用**: 默认值应为 `true`，确保开箱即用的安全性
2. **符号链接处理**: 使用 `resolve()` 解析真实路径，防止通过符号链接绕过
3. **路径遍历**: 处理 `../` 等路径遍历尝试
