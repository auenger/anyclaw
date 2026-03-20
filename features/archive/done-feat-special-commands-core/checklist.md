# 完成检查清单: Special Commands Core

## 特性信息

- **ID**: feat-special-commands-core
- **名称**: Special Commands Core
- **优先级**: 70
- **依赖**: 无

---

## 实现检查

### T1: 命令框架基础设施
- [ ] `anyclaw/commands/__init__.py` 创建
- [ ] `CommandParser` 实现完成
  - [ ] 解析 `/command` 格式
  - [ ] 支持命令参数提取
  - [ ] 大小写不敏感
- [ ] `CommandRegistry` 实现完成
  - [ ] 命令注册
  - [ ] 别名支持
  - [ ] 命令查找
- [ ] `CommandContext` 数据类定义
- [ ] `CommandHandler` 基类定义
- [ ] `CommandDispatcher` 实现完成

### T2: 会话控制命令
- [ ] `NewCommandHandler` 实现
  - [ ] 创建新会话
  - [ ] 支持带参数（首条消息）
- [ ] `ResetCommandHandler` 实现
  - [ ] 清空会话历史
  - [ ] 保留配置
- [ ] `ClearCommandHandler` 实现
  - [ ] CLI 清屏
  - [ ] 非 CLI 返回提示

### T3: 任务控制命令
- [ ] `StopCommandHandler` 实现
  - [ ] 停止 LLM 调用
  - [ ] 停止工具执行
- [ ] 任务追踪机制
  - [ ] AgentLoop 集成
  - [ ] abort() 方法

### T4: 信息查询命令
- [ ] `HelpCommandHandler` 实现
  - [ ] 命令列表
  - [ ] 格式化输出
- [ ] `StatusCommandHandler` 实现
  - [ ] 模型信息
  - [ ] 会话信息
  - [ ] Token 统计
- [ ] `VersionCommandHandler` 实现

### T5: Channel 集成
- [ ] CLIChannel 集成
- [ ] DiscordChannel 集成
- [ ] FeishuChannel 集成
- [ ] ChannelManager 初始化

### T6: 测试与文档
- [ ] 框架单元测试
- [ ] 处理器单元测试
- [ ] 集成测试
- [ ] CLAUDE.md 更新

---

## 验收测试

### 会话控制
- [ ] `输入 /new` → 创建新会话
- [ ] `输入 /new 你好` → 创建新会话并发送消息
- [ ] `输入 /reset` → 清空历史
- [ ] `输入 /clear (CLI)` → 清屏
- [ ] `输入 /clear (Discord)` → 返回提示

### 任务控制
- [ ] `LLM 生成中 /stop` → 停止生成
- [ ] `工具执行中 /stop` → 停止执行
- [ ] `停止后发送消息` → 正常响应

### 信息查询
- [ ] `输入 /help` → 显示命令列表
- [ ] `输入 /status` → 显示状态
- [ ] `输入 /version` → 显示版本

### 边界条件
- [ ] `输入 /NEW` (大写) → 正常识别
- [ ] `输入 /unknown` → 作为普通消息处理
- [ ] `输入 /new` 无会话管理器 → 优雅降级

---

## 代码质量

- [ ] 所有新文件有 docstring
- [ ] 类型注解完整
- [ ] 无 Ruff 警告
- [ ] 测试覆盖率 > 80%

---

## 文档更新

- [ ] CLAUDE.md 添加命令列表
- [ ] 添加命令使用示例

---

## 完成标准

- [ ] 所有测试通过 (`poetry run pytest tests/ -v`)
- [ ] 代码检查通过 (`poetry run ruff check anyclaw/`)
- [ ] 功能演示成功
- [ ] 文档已更新

---

## 签署

- 实现者: ________________
- 审核者: ________________
- 完成日期: ________________
