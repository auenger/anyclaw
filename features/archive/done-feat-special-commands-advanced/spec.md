# 特性规范: Special Commands Advanced

## 概述

实现高级特殊指令，包括上下文压缩、模型切换、Agent 切换等功能。此特性依赖 `feat-special-commands-core` 提供的命令框架。

**前置依赖**: `feat-special-commands-core`

## 用户价值点

### VP1: 上下文压缩命令

用户可以手动触发上下文压缩，在保持关键信息的同时减少 Token 使用。

**Gherkin 场景:**

```gherkin
Feature: 上下文压缩命令

  Scenario: 用户输入 /compact 压缩上下文
    Given 用户正在与 Agent 对话
    And 会话中有 20+ 条消息
    When 用户发送 "/compact"
    Then 系统使用智能压缩算法总结历史消息
    And 压缩后的摘要替换原有历史
    And 返回压缩结果 "⚙️ Compacted (15K → 3K tokens)"

  Scenario: 用户输入 /compact 带自定义指令
    Given 用户正在与 Agent 对话
    When 用户发送 "/compact 重点保留工具调用结果"
    Then 系统根据自定义指令进行压缩
    And 返回压缩结果
```

### VP2: 模型切换命令

用户可以在对话中切换当前使用的 LLM 模型。

**Gherkin 场景:**

```gherkin
Feature: 模型切换命令

  Scenario: 用户查看当前模型
    Given 用户正在与 Agent 对话
    When 用户发送 "/model"
    Then 系统返回当前使用的模型名称
    And 返回可用模型列表

  Scenario: 用户切换模型
    Given 用户正在与 Agent 对话
    And 当前模型为 "glm-4-flash"
    When 用户发送 "/model glm-4-plus"
    Then 系统切换到指定模型
    And 后续请求使用新模型
    And 返回确认 "✅ 模型已切换到 glm-4-plus"

  Scenario: 用户切换到无效模型
    Given 用户正在与 Agent 对话
    When 用户发送 "/model invalid-model"
    Then 系统返回错误提示
    And 显示可用模型列表

  Scenario: 权限不足切换模型
    Given 配置中 /model 命令限制为管理员
    And 当前用户不是管理员
    When 用户发送 "/model glm-4-plus"
    Then 系统返回权限错误 "⛔ 你没有权限执行此命令"
```

### VP3: Agent 切换命令

用户可以在对话中切换当前 Agent。

**Gherkin 场景:**

```gherkin
Feature: Agent 切换命令

  Scenario: 用户查看当前 Agent
    Given 用户正在与 Agent 对话
    When 用户发送 "/agent"
    Then 系统返回当前 Agent ID 和名称
    And 返回可用 Agent 列表

  Scenario: 用户切换 Agent
    Given 用户正在与 Agent 对话
    And 当前 Agent 为 "default"
    When 用户发送 "/agent coder"
    Then 系统切换到指定 Agent
    And 加载新 Agent 的人设和配置
    And 返回确认 "✅ 已切换到 Agent: coder"

  Scenario: 用户切换到不存在的 Agent
    Given 用户正在与 Agent 对话
    When 用户发送 "/agent nonexistent"
    Then 系统返回错误提示
    And 显示可用 Agent 列表
```

### VP4: 会话生命周期命令

用户可以配置会话的超时和过期策略（主要用于 IM Channel）。

**Gherkin 场景:**

```gherkin
Feature: 会话生命周期命令

  Scenario: 用户查看会话生命周期设置
    Given 用户在 Discord Channel 中对话
    When 用户发送 "/session"
    Then 系统返回当前会话的生命周期设置
    And 包括: 空闲超时、最大存活时间、下次过期时间

  Scenario: 用户设置空闲超时
    Given 用户在 Discord Channel 中对话
    When 用户发送 "/session idle 24h"
    Then 系统设置会话空闲超时为 24 小时
    And 返回确认 "✅ 空闲超时已设置为 24h"

  Scenario: 用户禁用空闲超时
    Given 用户在 Discord Channel 中对话
    When 用户发送 "/session idle off"
    Then 系统禁用会话空闲超时
    And 返回确认 "✅ 空闲超时已禁用"

  Scenario: 用户设置最大存活时间
    Given 用户在 Discord Channel 中对话
    When 用户发送 "/session max-age 7d"
    Then 系统设置会话最大存活时间为 7 天
    And 返回确认 "✅ 最大存活时间已设置为 7d"
```

## 支持的 Channel

- ✅ CLI Channel
- ✅ Discord Channel
- ✅ Feishu Channel

## 命令列表

| 命令 | 描述 | 权限级别 |
|------|------|----------|
| `/compact [instructions]` | 压缩上下文 | 所有人 |
| `/model [name]` | 查看/切换模型 | 可配置 |
| `/agent [name]` | 查看/切换 Agent | 可配置 |
| `/session idle <duration>` | 设置空闲超时 | 所有人 |
| `/session max-age <duration>` | 设置最大存活时间 | 所有人 |

## 权限配置

权限控制在配置文件中定义，支持细粒度配置：

```toml
# config.toml
[commands.permissions]
# 默认权限：所有人可用
default = "*"

# 特定命令权限覆盖
compact = "*"           # 所有人可用
model = "admin"         # 仅管理员
agent = "admin"         # 仅管理员
session = "*"           # 所有人可用

# 管理员列表
admins = ["user_123", "user_456"]
```

### 权限级别

| 值 | 含义 |
|----|------|
| `"*"` | 所有人可用 |
| `"admin"` | 仅管理员可用 |
| `["user1", "user2"]` | 指定用户列表 |

## 技术设计

### 命令处理器位置

```
anyclaw/commands/handlers/
├── compact.py       # /compact
├── model.py         # /model
├── agent.py         # /agent
└── session.py       # /session idle, /session max-age
```

### 上下文压缩流程

```
/compact 命令
    ↓
CompactCommandHandler.execute()
    ↓
ConversationHistory.compress()
    ├── 提取关键信息（用户意图、重要结论、工具结果摘要）
    ├── 生成压缩摘要
    └── 替换历史消息
    ↓
返回压缩结果
```

### 模型切换流程

```
/model <name> 命令
    ↓
ModelCommandHandler.execute()
    ↓
┌─────────────────────────────┐
│ 权限检查                     │
├─────────────────────────────┤
│ 无权限 → 返回错误            │
│ 有权限 → 继续               │
└─────────────────────────────┘
    ↓
ConfigManager.set("llm.model", name)
    ↓
返回确认消息
```

### Agent 切换流程

```
/agent <name> 命令
    ↓
AgentCommandHandler.execute()
    ↓
┌─────────────────────────────┐
│ 权限检查                     │
├─────────────────────────────┤
│ 无权限 → 返回错误            │
│ 有权限 → 继续               │
└─────────────────────────────┘
    ↓
AgentManager.switch(name)
    ├── 加载 Agent 配置
    ├── 加载 Agent 人设
    └── 重置会话上下文
    ↓
返回确认消息
```

## 边界条件

1. **压缩中任务**: 压缩时如果有正在执行的任务，先停止再压缩
2. **模型验证**: 切换模型前验证模型名称有效性
3. **Agent 验证**: 切换 Agent 前验证 Agent 存在性
4. **CLI 会话命令**: `/session` 在 CLI 中返回提示（主要用于 IM）

## 非功能性需求

1. **压缩性能**: 压缩操作 < 5s
2. **切换响应**: 模型/Agent 切换 < 500ms
3. **权限检查**: 权限验证 < 10ms

## 依赖

- `feat-special-commands-core` - 命令框架基础设施
- `feat-context-compression` - 上下文压缩算法（已实现）
- `feat-agent-persona` - Agent 人设系统（已实现）
