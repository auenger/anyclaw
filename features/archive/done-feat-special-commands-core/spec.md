# 特性规范: Special Commands Core

## 概述

实现用户对话中的特殊指令系统，允许用户通过输入 `/command` 格式的消息来触发特定功能，如新建会话、停止任务、查看状态等。

**参考**: OpenClaw 的 commands-core.ts 实现

## 用户价值点

### VP1: 会话控制命令

用户可以通过对话输入特殊指令来控制会话状态。

**Gherkin 场景:**

```gherkin
Feature: 会话控制命令

  Scenario: 用户输入 /new 创建新会话
    Given 用户正在与 Agent 对话
    When 用户发送 "/new" 或 "/new 介绍一下自己"
    Then 系统创建一个新的会话
    And 原有会话历史被保留
    And 如果有后续文本，则作为新会话的第一条消息处理
    And 返回确认消息 "✅ 新会话已创建"

  Scenario: 用户输入 /reset 重置当前会话
    Given 用户正在与 Agent 对话
    And 会话中有历史消息
    When 用户发送 "/reset"
    Then 系统清空当前会话的历史消息
    And 保留会话配置（模型、Agent等）
    And 返回确认消息 "✅ 会话已重置"

  Scenario: 用户输入 /clear 清屏
    Given 用户正在 CLI Channel 中对话
    When 用户发送 "/clear"
    Then 终端屏幕被清空
    And 显示欢迎信息
```

### VP2: 任务控制命令

用户可以中止正在执行的 Agent 任务。

**Gherkin 场景:**

```gherkin
Feature: 任务控制命令

  Scenario: 用户输入 /stop 停止当前任务
    Given Agent 正在执行一个长时间任务
    When 用户发送 "/stop" 或 "/abort"
    Then 系统中止当前正在执行的 LLM 调用或工具执行
    And 返回确认消息 "⏹️ 任务已停止"
    And 会话保持可用状态

  Scenario: 任务停止后可以继续对话
    Given 用户刚刚执行了 /stop 命令
    When 用户发送新的消息
    Then Agent 正常响应该消息
```

### VP3: 信息查询命令

用户可以查询系统状态和帮助信息。

**Gherkin 场景:**

```gherkin
Feature: 信息查询命令

  Scenario: 用户输入 /help 查看帮助
    Given 用户正在与 Agent 对话
    When 用户发送 "/help"
    Then 系统返回可用命令列表
    And 包含每个命令的简要说明

  Scenario: 用户输入 /status 查看状态
    Given 用户正在与 Agent 对话
    When 用户发送 "/status"
    Then 系统返回当前会话状态
    And 包括: 当前模型、Agent ID、会话 ID、消息数量、Token 使用量

  Scenario: 用户输入 /version 查看版本
    Given 用户正在与 Agent 对话
    When 用户发送 "/version"
    Then 系统返回 AnyClaw 版本号
```

## 支持的 Channel

- ✅ CLI Channel
- ✅ Discord Channel
- ✅ Feishu Channel

## 命令列表

| 命令 | 别名 | 描述 |
|------|------|------|
| `/new [message]` | - | 创建新会话 |
| `/reset` | - | 重置当前会话 |
| `/clear` | - | 清屏（仅 CLI） |
| `/stop` | `/abort` | 停止当前任务 |
| `/help` | - | 显示帮助信息 |
| `/status` | - | 显示会话状态 |
| `/version` | - | 显示版本号 |

## 技术设计

### 命令解析流程

```
用户输入
    ↓
CommandParser.parse(user_input)
    ↓
┌─────────────────────────────┐
│ 是否以 "/" 开头？           │
├─────────────────────────────┤
│ 是 → 解析命令名和参数       │
│     → 查找 CommandHandler   │
│     → 执行 Handler          │
│ 否 → 正常消息处理流程       │
└─────────────────────────────┘
```

### 核心组件

1. **CommandParser** - 解析用户输入，提取命令和参数
2. **CommandRegistry** - 注册和管理所有命令处理器
3. **CommandHandler** - 命令处理基类
4. **CommandContext** - 命令执行上下文（session、channel、config 等）
5. **PermissionManager** - 权限管理（可选，默认所有命令可用）

### 权限系统设计

权限系统采用**细粒度可配置**策略，每个命令都可以单独配置权限。

**权限配置结构：**

```toml
# config.toml
[commands.permissions]
# 默认权限：所有人可用
default = "*"

# 特定命令权限覆盖（在 advanced 特性中使用）
# compact = "*"
# model = "*"
# agent = "*"
```

**权限级别：**

| 值 | 含义 | 示例 |
|----|------|------|
| `"*"` | 所有人可用 | `default = "*"` |
| `"admin"` | 仅管理员可用 | `model = "admin"` |
| `["user1", "user2"]` | 指定用户列表 | `model = ["u_123", "u_456"]` |

**默认行为：**

- **Core 特性中所有命令默认开放**，无需权限配置
- **Advanced 特性**扩展权限配置，支持敏感命令限制

**权限检查流程：**

```
命令分发
    ↓
PermissionManager.check_permission(command, user_id)
    ↓
┌─────────────────────────────────────┐
│ 查找命令特定权限配置                 │
├─────────────────────────────────────┤
│ 找到 → 使用特定配置                  │
│ 未找到 → 使用 default 配置           │
│ default 未配置 → 默认允许 (*)        │
└─────────────────────────────────────┘
    ↓
有权限 → 执行 Handler
无权限 → 返回权限错误
```

### 命令处理器位置

```
anyclaw/
├── commands/
│   ├── __init__.py
│   ├── parser.py          # CommandParser
│   ├── registry.py        # CommandRegistry
│   ├── context.py         # CommandContext
│   ├── base.py            # CommandHandler 基类
│   └── handlers/
│       ├── __init__.py
│       ├── session.py     # /new, /reset
│       ├── task.py        # /stop, /abort
│       ├── info.py        # /help, /status, /version
│       └── clear.py       # /clear
```

### Channel 集成

每个 Channel 在处理消息时调用命令解析器：

```python
# channels/cli.py, channels/discord.py, channels/feishu.py
async def _handle_message(self, sender_id: str, chat_id: str, content: str):
    # 先检查是否是命令
    result = await self.command_dispatcher.dispatch(content, context)
    if result.handled:
        if result.reply:
            await self.send(OutboundMessage(content=result.reply))
        return

    # 正常消息处理
    await self.process_normal_message(content)
```

## 边界条件

1. **命令大小写**: 命令不区分大小写 (`/NEW` = `/new`)
2. **命令参数**: `/new` 后可跟消息，作为新会话的首条消息
3. **并发停止**: 多个停止请求应该被正确处理
4. **Channel 差异**: `/clear` 仅在 CLI 中有效，其他 Channel 返回提示

## 非功能性需求

1. **响应时间**: 命令响应 < 100ms
2. **可用性**: 命令系统不应该影响正常消息处理路径
3. **可扩展性**: 新增命令应该简单（继承 CommandHandler 并注册）

## 后续特性

此特性为 **Part 1**，后续特性 **feat-special-commands-advanced** 将包括：
- `/compact` - 上下文压缩
- `/model` - 切换模型
- `/agent` - 切换 Agent
- `/session` - 会话生命周期管理
