# 任务分解: Special Commands Core

## 任务概览

| 任务 ID | 任务描述 | 依赖 | 估算 |
|---------|----------|------|------|
| T1 | 命令框架基础设施 | - | 2h |
| T2 | 会话控制命令 | T1 | 1.5h |
| T3 | 任务控制命令 | T1 | 1.5h |
| T4 | 信息查询命令 | T1 | 1h |
| T5 | Channel 集成 | T1-T4 | 2h |
| T6 | 测试与文档 | T1-T5 | 1h |

**总估算**: 9h

---

## T1: 命令框架基础设施

### 目标
建立可扩展的命令处理框架，包含权限系统基础。

### 子任务
- [ ] 创建 `anyclaw/commands/` 目录结构
- [ ] 实现 `CommandParser` 类
  - 解析 `/command [args]` 格式
  - 支持命令别名
  - 大小写不敏感
- [ ] 实现 `CommandRegistry` 类
  - 注册命令处理器
  - 按命令名/别名查找处理器
- [ ] 实现 `CommandContext` 数据类
  - session_key, agent_id, channel, config, user_id 等
- [ ] 实现 `CommandHandler` 基类
  - `async execute(context: CommandContext) -> CommandResult`
- [ ] 实现 `CommandDispatcher` 类
  - 集成 Parser + Registry
  - 提供 `dispatch(content, context)` 方法
- [ ] 实现 `PermissionManager` 基础版
  - 从配置加载权限规则
  - `check_permission(command, user_id) -> bool`
  - **默认所有命令可用**（细粒度控制在 advanced 特性）
- [ ] 更新 `config.template.toml`
  - 添加 `[commands.permissions]` 配置段
  - 默认 `default = "*"`

### 验收标准
- [ ] 可以注册和查找命令
- [ ] 可以解析各种格式的命令输入
- [ ] 权限系统可工作（默认全部允许）
- [ ] 框架单元测试通过

### 关键文件
```
anyclaw/commands/
├── __init__.py
├── parser.py
├── registry.py
├── context.py
├── base.py
├── dispatcher.py
└── permission.py       # 权限管理

anyclaw/config/
└── config.template.toml # 添加权限配置段
```

---

## T2: 会话控制命令

### 目标
实现 `/new`, `/reset`, `/clear` 命令。

### 子任务
- [ ] 实现 `NewCommandHandler`
  - 创建新会话
  - 支持带参数（作为首条消息）
- [ ] 实现 `ResetCommandHandler`
  - 清空当前会话历史
  - 保留会话配置
- [ ] 实现 `ClearCommandHandler`
  - 仅 CLI Channel 有效
  - 清空终端屏幕

### 验收标准
- [ ] `/new` 创建新会话，返回确认
- [ ] `/new 你好` 创建新会话并处理消息
- [ ] `/reset` 清空历史
- [ ] `/clear` 清屏（CLI only）
- [ ] 非CLI Channel 调用 `/clear` 返回提示

### 关键文件
```
anyclaw/commands/handlers/
├── __init__.py
└── session.py
```

---

## T3: 任务控制命令

### 目标
实现 `/stop`, `/abort` 命令。

### 子任务
- [ ] 实现 `StopCommandHandler`
  - 中止当前 LLM 调用
  - 中止当前工具执行
  - 返回确认消息
- [ ] 添加任务追踪机制
  - 在 AgentLoop 中追踪当前任务
  - 提供 `abort()` 方法

### 验收标准
- [ ] `/stop` 在 LLM 生成中可以停止
- [ ] `/stop` 在工具执行中可以停止
- [ ] 停止后会话保持可用
- [ ] `/abort` 与 `/stop` 行为一致

### 关键文件
```
anyclaw/commands/handlers/
└── task.py

anyclaw/agent/
└── abort.py (或修改 loop.py)
```

---

## T4: 信息查询命令

### 目标
实现 `/help`, `/status`, `/version` 命令。

### 子任务
- [ ] 实现 `HelpCommandHandler`
  - 返回所有可用命令列表
  - 包含简要说明
- [ ] 实现 `StatusCommandHandler`
  - 显示当前模型
  - 显示 Agent ID
  - 显示会话 ID
  - 显示消息数量
  - 显示 Token 使用量
- [ ] 实现 `VersionCommandHandler`
  - 返回 AnyClaw 版本号

### 验收标准
- [ ] `/help` 返回格式化的命令列表
- [ ] `/status` 返回完整状态信息
- [ ] `/version` 返回版本号

### 关键文件
```
anyclaw/commands/handlers/
└── info.py
```

---

## T5: Channel 集成

### 目标
将命令系统集成到所有 Channel。

### 子任务
- [ ] 修改 `CLIChannel`
  - 在消息处理前检查命令
  - 特殊处理 `/clear`
- [ ] 修改 `DiscordChannel`
  - 集成命令分发
- [ ] 修改 `FeishuChannel`
  - 集成命令分发
- [ ] 修改 `ChannelManager`
  - 初始化 CommandDispatcher
  - 共享给所有 Channel

### 验收标准
- [ ] CLI 中所有命令正常工作
- [ ] Discord 中所有命令正常工作
- [ ] 飞书中所有命令正常工作
- [ ] `/clear` 在非 CLI 返回友好提示

### 关键文件
```
anyclaw/channels/
├── cli.py
├── discord.py
├── feishu.py
└── manager.py
```

---

## T6: 测试与文档

### 目标
编写测试并更新文档。

### 子任务
- [ ] 命令框架单元测试
  - parser_test.py
  - registry_test.py
  - dispatcher_test.py
- [ ] 命令处理器测试
  - handlers/session_test.py
  - handlers/task_test.py
  - handlers/info_test.py
- [ ] 集成测试
  - CLI 命令测试
  - Channel 命令测试
- [ ] 更新 CLAUDE.md
  - 添加命令列表说明

### 验收标准
- [ ] 所有测试通过
- [ ] 测试覆盖率 > 80%
- [ ] 文档已更新

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| `/stop` 实现复杂 | 高 | 先实现简单版本，仅停止 LLM 调用 |
| Channel 差异处理 | 中 | 使用 CommandContext 传递 Channel 类型 |
| 命令与消息冲突 | 低 | 使用严格的 `/` 前缀匹配 |
