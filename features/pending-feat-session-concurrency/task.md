# 任务分解：会话并发引擎

## 概述

实现会话级别的并发处理，支持同时处理多个 chat session 的对话。

## 任务列表

### 任务 1：添加并发配置项

**文件**: `anyclaw/config/settings.py`

**描述**: 添加最大并发会话数的配置项

**要点**:
- 在 Settings 类中添加 `max_concurrent_sessions` 字段
- 默认值设为 5
- 支持通过环境变量覆盖

**验收标准**:
- [ ] 配置项可读取
- [ ] 默认值生效
- [ ] 环境变量覆盖生效

---

### 任务 2：实现 SessionAgentPool 类

**文件**: `anyclaw/core/session_pool.py` (新建)

**描述**: 创建会话级别的 AgentLoop 管理池

**要点**:
- 管理多个 AgentLoop 实例（每个会话一个）
- 提供获取/创建/清理接口
- 实现 LRU 淘汰策略（可选，防止内存泄漏）

**核心接口**:
```python
class SessionAgentPool:
    def __init__(self, workspace: Path, max_pool_size: int = 10):
        ...

    def get_or_create(self, session_key: str) -> AgentLoop:
        """获取或创建会话的 AgentLoop"""
        ...

    def remove(self, session_key: str) -> None:
        """移除会话的 AgentLoop"""
        ...

    def clear(self) -> None:
        """清空所有 AgentLoop"""
        ...
```

**验收标准**:
- [ ] 可以创建和获取 AgentLoop
- [ ] 同一 session_key 返回相同实例
- [ ] 可以清理指定/所有实例

---

### 任务 3：实现并发消息处理

**文件**: `anyclaw/core/serve.py`

**描述**: 修改 ServeManager 支持并发处理消息

**要点**:
- 添加 `_session_pool: SessionAgentPool`
- 添加 `_concurrency_semaphore: asyncio.Semaphore`
- 添加 `_active_tasks: Dict[str, asyncio.Task]`
- 修改 `_process_messages()` 使用并发模式

**核心变更**:
```python
async def _process_messages(self) -> None:
    while self._running:
        msg = await self.bus.consume_inbound()

        # 获取会话级别的 AgentLoop
        agent = self._session_pool.get_or_create(msg.session_key)

        # 创建并发任务
        task = asyncio.create_task(
            self._process_with_semaphore(msg, agent)
        )
        self._active_tasks[msg.session_key] = task

async def _process_with_semaphore(self, msg, agent):
    async with self._concurrency_semaphore:
        try:
            response = await agent.process(msg.content)
            # 发送响应...
        finally:
            self._active_tasks.pop(msg.session_key, None)
```

**验收标准**:
- [ ] 多个会话可并行处理
- [ ] 并发数受 semaphore 限制
- [ ] 任务正确追踪和清理

---

### 任务 4：实现优雅关闭

**文件**: `anyclaw/core/serve.py`

**描述**: 确保 stop() 时等待所有活动任务完成

**要点**:
- 收集所有 `_active_tasks`
- 等待任务完成或超时
- 清理 SessionAgentPool

**验收标准**:
- [ ] 关闭时等待活动任务
- [ ] 超时后强制取消
- [ ] 资源正确释放

---

### 任务 5：添加单元测试

**文件**: `tests/test_session_concurrency.py`

**描述**: 测试并发处理逻辑

**测试用例**:
1. `test_concurrent_sessions_process_in_parallel` - 并行处理
2. `test_semaphore_limits_concurrency` - 并发限制
3. `test_session_history_isolation` - 历史隔离
4. `test_graceful_shutdown_waits_for_tasks` - 优雅关闭
5. `test_session_pool_creates_and_reuses` - AgentLoop 复用

**验收标准**:
- [ ] 所有测试通过
- [ ] 覆盖核心场景

---

### 任务 6：更新文档

**文件**: `CLAUDE.md`

**描述**: 更新项目文档说明并发特性

**要点**:
- 在核心特性中添加"会话并发"
- 更新常用命令说明
- 添加配置说明

**验收标准**:
- [ ] 文档已更新
- [ ] 配置说明清晰

---

## 依赖关系

```
任务 1 (配置)
    ↓
任务 2 (SessionPool) ← 任务 3 (并发处理)
                              ↓
                        任务 4 (优雅关闭)
                              ↓
                        任务 5 (测试)
                              ↓
                        任务 6 (文档)
```

## 预估工作量

| 任务 | 预估时间 |
|------|----------|
| 任务 1 | 15 分钟 |
| 任务 2 | 45 分钟 |
| 任务 3 | 1 小时 |
| 任务 4 | 30 分钟 |
| 任务 5 | 1 小时 |
| 任务 6 | 15 分钟 |
| **总计** | **3.5 小时** |
