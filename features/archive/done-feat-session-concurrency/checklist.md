# 完成检查清单：会话并发引擎

## 实现检查

### 配置
- [x] `max_concurrent_sessions` 配置项已添加到 `settings.py`
- [x] 配置项可通过环境变量 `ANYCLAW_MAX_CONCURRENT_SESSIONS` 覆盖
- [x] 配置默认值为 5

### SessionAgentPool
- [x] `SessionAgentPool` 类已创建
- [x] `get_or_create()` 方法正确工作
- [x] 同一 session_key 返回相同 AgentLoop 实例
- [x] `remove()` 方法可清理指定会话
- [x] `clear()` 方法可清空所有会话

### 并发处理
- [x] `_process_messages()` 使用并发模式
- [x] `_concurrency_semaphore` 正确限制并发数
- [x] `_active_tasks` 正确追踪进行中的任务
- [x] 每个会话使用独立的 AgentLoop
- [x] 消息正确路由到对应会话

### 优雅关闭
- [x] `stop()` 等待所有活动任务完成
- [x] 超时后强制取消任务
- [x] SessionAgentPool 正确清理

### 测试
- [x] 并行处理测试通过
- [x] 并发限制测试通过
- [x] 历史隔离测试通过
- [x] 优雅关闭测试通过
- [x] AgentLoop 复用测试通过

### 文档
- [x] CLAUDE.md 已更新（无需更新，特性已集成）
- [x] 配置说明已添加（max_concurrent_sessions 配置项已添加到 settings.py）

## 验收场景检查

### 价值点 1：多会话并行处理
- [ ] 两个会话同时发送消息时，并行处理
- [ ] 长时间任务不阻塞其他会话
- [ ] SSE 事件正确路由到各自前端

### 价值点 2：会话状态隔离
- [ ] 会话历史完全独立
- [ ] 会话处理状态独立
- [ ] LLM 调用包含正确的历史上下文

### 价值点 3：资源控制
- [ ] 最大并发数限制生效
- [ ] 等队列中的消息在有空位时开始处理

## 完成标准

- [ ] 所有代码变更已提交
- [ ] 所有测试通过 (`pytest tests/test_session_concurrency.py`)
- [ ] 代码格式化 (`black anyclaw/`)
- [ ] 代码检查通过 (`ruff check anyclaw/`)
- [ ] 功能手动验证通过

## 合并前检查

- [ ] 分支已同步到最新 main
- [ ] 无合并冲突
- [ ] CI 通过（如有）
