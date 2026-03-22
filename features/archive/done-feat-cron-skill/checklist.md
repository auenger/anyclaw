# Cron 技能实现 - 检查清单

## 开发前准备

- [x] 分析现有 cron 实现
- [x] 确定实现方案（工具+技能双轨制）
- [x] 创建特性目录和文档

## 核心实现

### AgentLoop 集成

- [ ] 在 `agent/loop.py` 中导入 CronService 和 CronTool
- [ ] 在 `__init__` 中初始化 CronService
- [ ] 在 `_register_default_tools()` 中注册 CronTool
- [ ] 添加 `_cron_service` 和 `_cron_tool` 属性
- [ ] 添加 `start_cron_service()` 异步方法
- [ ] 添加 `stop_cron_service()` 异步方法
- [ ] 添加 `set_cron_context()` 方法

### Cron 内置技能

- [ ] 创建 `skills/builtin/cron/` 目录
- [ ] 创建 `SKILL.md` 文件（包含功能说明和使用示例）
- [ ] 可选：创建 `skill.py` 包装器

### Channel 集成

- [ ] 在 CLI Channel 启动时调用 `start_cron_service()`
- [ ] 在 CLI Channel 中调用 `set_cron_context()`
- [ ] 在 CLI Channel 关闭时调用 `stop_cron_service()`

## 测试验证

### 单元测试

- [ ] 测试 CronTool 被正确注册
- [ ] 测试 CronTool 上下文设置
- [ ] 测试 CronService 生命周期
- [ ] 测试 cron 技能被加载

### 集成测试

- [ ] 测试 Agent 可以通过 function calling 使用 cron
- [ ] 测试定时任务可以正确触发
- [ ] 测试消息投递到正确的 channel

### 手动测试

- [ ] 启动 CLI chat
- [ ] 请求 Agent 创建一个定时任务
- [ ] 验证任务在 skills 列表中可见
- [ ] 验证任务能正确触发

## 文档更新

- [ ] 更新 CLAUDE.md 中的内置技能列表
- [ ] 更新相关 API 文档（如有）

## 完成标准

- [ ] 所有代码修改完成
- [ ] 所有测试通过
- [ ] 手动测试验证通过
- [ ] 代码已格式化 (black)
- [ ] 代码检查通过 (ruff)
- [ ] 提交 commit
