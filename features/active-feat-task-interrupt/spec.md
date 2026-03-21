# feat-task-interrupt: 任务即时中断机制

## 概述

实现 `/stop` 命令的即时中断机制，参考 nanobot 使用 `asyncio.Task` + `_active_tasks` 模式，让用户能够即时中断正在执行的 LLM 调用或工具执行。

## 背景

当前 `/stop` 命令无法即时中断正在执行的任务，必须等待 `max_iterations` 循环结束才能被处理。这是因为：

1. **AgentLoop** 是处理单元，没有主循环和任务追踪机制
2. **CLI Channel** 在处理消息时阻塞（通过回调 `process` 调用），无法响应新输入
3. **命令处理器** 在消息处理完成后才能被调用

## 用户价值点

### VP1: AgentLoop 中断机制

**能力**: 在 AgentLoop 中添加任务追踪和中断支持

**验收场景**:

```gherkin
Feature: AgentLoop 中断机制

  Scenario: 注册和追踪活动任务
    Given 一个 AgentLoop 实例
    When 创建一个 asyncio.Task 处理消息
    And 调用 register_task("default", task)
    Then _active_tasks["default"] 应该指向该任务

  Scenario: 请求中断正在执行的任务
    Given 一个 AgentLoop 实例正在处理消息
    And 任务已注册到 _active_tasks
    When 调用 request_abort("default")
    Then _abort_flags["default"] 应该被设置为 True
    And 任务应该被 cancel()

  Scenario: 迭代循环中检查中断标志
    Given _run_with_tools 正在执行迭代循环
    And _abort_flags["default"] 为 True
    When 进入下一次迭代
    Then 循环应该立即退出
    And 返回 "任务已被用户中断"
```

### VP2: CLIChannel 直接处理 /stop

**能力**: 在 CLI Channel 的消息处理循环中直接响应 `/stop` 命令

**验收场景**:

```gherkin
Feature: CLIChannel 直接处理 /stop

  Scenario: 直接处理 /stop 命令
    Given CLIChannel 正在运行
    And agent_loop 引用已设置
    When 用户输入 "/stop"
    Then 应该调用 agent_loop.request_abort("default")
    And 显示 "正在停止任务..." 提示

  Scenario: /stop 别名 /abort
    Given CLIChannel 正在运行
    When 用户输入 "/abort"
    Then 应该触发与 /stop 相同的中断逻辑

  Scenario: 没有活动任务时显示提示
    Given CLIChannel 正在运行
    And agent_loop 没有活动任务
    When 用户输入 "/stop"
    Then 显示 "没有正在执行的任务"
```

### VP3: chat 命令集成

**能力**: 在 CLI chat 命令中设置 agent_loop 引用，消息处理作为独立 Task

**验收场景**:

```gherkin
Feature: chat 命令集成

  Scenario: 设置 agent_loop 引用
    Given 运行 anyclaw chat
    When 创建 CLIChannel 实例
    Then 应该调用 channel.set_agent_loop(agent)

  Scenario: 消息处理作为独立 Task
    Given CLIChannel 正在运行
    And 用户发送非命令消息
    When 消息开始处理
    Then 应该创建独立的 asyncio.Task
    And 任务应该被注册到 agent_loop._active_tasks

  Scenario: 任务被取消后显示提示
    Given 消息处理任务正在运行
    When 任务被 /stop 取消
    Then 应该捕获 asyncio.CancelledError
    And 显示 "任务已停止"
```

## 技术设计

### 修改文件

1. **`anyclaw/anyclaw/agent/loop.py`**
   - 添加 `_active_tasks: Dict[str, asyncio.Task]`
   - 添加 `_abort_flags: Dict[str, bool]`
   - 添加 `register_task()`、`unregister_task()`、`request_abort()` 方法
   - 修改 `_run_with_tools()` 在每次迭代检查中断标志

2. **`anyclaw/anyclaw/channels/cli.py`**
   - 添加 `agent_loop: Optional[AgentLoop]` 属性
   - 添加 `set_agent_loop()` 方法
   - 修改 `run()` 和 `run_stream()` 直接处理 `/stop`
   - 修改消息处理为独立 Task 模式

3. **`anyclaw/anyclaw/cli/app.py`**
   - 在 `chat` 命令中调用 `channel.set_agent_loop(agent)`

### 参考

- nanobot 实现: `reference/nanobot/nanobot/agent/loop.py`
  - `_active_tasks: dict[str, list[asyncio.Task]]`
  - `_handle_stop()` 方法
  - `task.cancel()` 中断机制

## 依赖

无

## 优先级

75（中等优先级，用户体验增强）
