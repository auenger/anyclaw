# 特性：会话并发引擎

## 概述

当前 AnyClaw 的消息处理是单线程顺序执行的，多个会话的消息会互相阻塞。本特性实现会话级别的并发处理，支持同时处理多个 chat session 的对话。

## 背景

### 问题分析

当前 `_process_messages()` 是一个 async 循环，当收到消息后，`await self.agent.process(content)` 会阻塞直到完成：

```
消息队列: [Msg A] [Msg B] [Msg C]
              ↓
         单线程处理:
         1. 处理 Msg A (30秒) ← 阻塞
         2. 处理 Msg B (等待 A 完成)
         3. 处理 Msg C (等待 B 完成)
```

### 限制

1. **一个 AgentLoop 实例** - 共享一个 `self.history`
2. **单消息处理循环** - `_process_messages()` 是一个 async 循环
3. **串行处理** - `await self.agent.process(content)` 阻塞直到完成

### 目标架构

```
消息队列: [Msg A] [Msg B] [Msg C]
              ↓
         并发处理:
         ├── Task A (独立 AgentLoop)
         ├── Task B (独立 AgentLoop)
         └── Task C (独立 AgentLoop)
              ↓
         SSE 广播到各自会话
```

## 用户价值点

### 价值点 1：多会话并行处理

**描述**：用户可以同时与多个对话进行交互，不同会话的响应不会互相阻塞。

**验收场景**：

```gherkin
Feature: 多会话并行处理

  Scenario: 两个会话同时发送消息
    Given 用户在会话 A 和会话 B 中分别发送消息
    When 两个消息同时进入队列
    Then 两个会话的处理任务并行启动
    And 会话 A 和会话 B 的响应同时生成
    And 两个会话的 SSE 事件正确路由到各自的前端

  Scenario: 长时间任务不阻塞其他会话
    Given 会话 A 的消息需要 30 秒处理
    And 会话 B 的消息需要 5 秒处理
    When 两个消息同时进入队列
    Then 会话 B 在 5 秒内完成响应
    And 会话 A 在 30 秒内完成响应
    And 会话 B 不需要等待会话 A 完成
```

### 价值点 2：会话状态隔离

**描述**：每个会话有独立的 history、session key 和处理状态，互不干扰。

**验收场景**：

```gherkin
Feature: 会话状态隔离

  Scenario: 会话历史独立
    Given 会话 A 有 10 条历史消息
    And 会话 B 有 5 条历史消息
    When 同时处理两个会话的新消息
    Then 会话 A 的 LLM 调用包含 10 条历史
    And 会话 B 的 LLM 调用包含 5 条历史
    And 两个会话的历史不会混淆

  Scenario: 会话处理状态独立
    Given 会话 A 正在处理中
    When 用户在会话 B 发送消息
    Then 会话 B 立即开始处理
    And 会话 A 的处理状态不影响会话 B
```

### 价值点 3：资源控制

**描述**：支持配置最大并发数，避免资源耗尽。

**验收场景**：

```gherkin
Feature: 资源控制

  Scenario: 最大并发数限制
    Given 配置 max_concurrent_sessions = 3
    When 同时有 5 个消息进入队列
    Then 最多 3 个会话并行处理
    And 其余 2 个消息在队列中等待
    When 其中一个处理完成
    Then 等待的消息开始处理

  Scenario: 并发数配置动态调整
    Given 当前最大并发数为 3
    When 配置更新为 max_concurrent_sessions = 5
    Then 新的并发限制立即生效
```

## 技术方案

### 方案选择

| 方案 | 描述 | 优点 | 缺点 |
|------|------|------|------|
| 多 AgentLoop | 每个会话一个 AgentLoop 实例 | 完全隔离，实现简单 | 内存占用较高 |
| 任务池 | asyncio.create_task 并行 | 改动小 | 需要会话隔离的 history |
| 多 Worker | 多个消费协程 | 灵活 | 需要协调机制 |

**推荐方案**：任务池 + 会话级别 AgentLoop 池

### 实现要点

1. **SessionAgentPool** - 管理会话级别的 AgentLoop 实例
2. **并发控制** - 使用 `asyncio.Semaphore` 限制最大并发数
3. **任务追踪** - 使用 `_active_tasks: Dict[str, asyncio.Task]` 追踪进行中的任务
4. **优雅关闭** - 等待所有活动任务完成

### 核心代码变更

```python
class ServeManager:
    def __init__(self, ...):
        self._session_pool: Dict[str, AgentLoop] = {}
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._concurrency_semaphore = asyncio.Semaphore(max_concurrent)

    async def _process_messages(self):
        while self._running:
            msg = await self.bus.consume_inbound()

            # 获取或创建会话级别的 AgentLoop
            agent = self._get_or_create_agent(msg.session_key)

            # 并发处理消息
            task = asyncio.create_task(
                self._process_with_semaphore(msg, agent)
            )
            self._active_tasks[msg.session_key] = task

    async def _process_with_semaphore(self, msg, agent):
        async with self._concurrency_semaphore:
            try:
                response = await agent.process(msg.content)
                # ... 发送响应
            finally:
                self._active_tasks.pop(msg.session_key, None)
```

## 优先级

80（高优先级）- 影响多用户场景的用户体验

## 依赖

无

## 相关文件

- `anyclaw/core/serve.py` - 主要修改
- `anyclaw/agent/loop.py` - 可能需要会话隔离支持
- `anyclaw/config/settings.py` - 添加并发配置
