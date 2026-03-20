# feat-task-interrupt: 任务分解

## 任务列表

### Task 1: AgentLoop 添加中断机制

**文件**: `anyclaw/anyclaw/agent/loop.py`

**步骤**:
1. 在 `__init__` 中添加:
   ```python
   self._active_tasks: Dict[str, asyncio.Task] = {}
   self._abort_flags: Dict[str, bool] = {}
   ```

2. 添加中断管理方法:
   ```python
   def register_task(self, session_key: str, task: asyncio.Task) -> None
   def unregister_task(self, session_key: str) -> None
   def request_abort(self, session_key: str = "default") -> bool
   ```

3. 修改 `_run_with_tools()` 方法:
   - 添加 `session_key` 参数（默认 "default"）
   - 在每次迭代开始检查 `_abort_flags[session_key]`
   - 如果中断标志为 True，清除标志并返回中断消息

**预计工作量**: 30 分钟

---

### Task 2: CLIChannel 添加中断支持

**文件**: `anyclaw/anyclaw/channels/cli.py`

**步骤**:
1. 在 `__init__` 中添加:
   ```python
   self.agent_loop: Optional[AgentLoop] = None
   self._current_task: Optional[asyncio.Task] = None
   ```

2. 添加 `set_agent_loop()` 方法

3. 修改 `run()` 方法:
   - 在消息循环开始时检查 `/stop` 命令
   - 直接调用 `_handle_stop_direct()`
   - 消息处理改为 `_dispatch_with_tracking()`

4. 添加 `_handle_stop_direct()` 方法:
   ```python
   async def _handle_stop_direct(self) -> None:
       if self.agent_loop:
           aborted = self.agent_loop.request_abort("default")
           if aborted:
               self.console.print("[yellow]⏹️ 正在停止任务...[/yellow]")
           else:
               self.console.print("[dim]没有正在执行的任务[/dim]")
       else:
           self.console.print("[dim]没有正在执行的任务[/dim]")
   ```

5. 添加 `_dispatch_with_tracking()` 方法

6. 同样修改 `run_stream()` 方法

**预计工作量**: 45 分钟

---

### Task 3: chat 命令集成

**文件**: `anyclaw/anyclaw/cli/app.py`

**步骤**:
1. 在 `chat()` 函数中，创建 CLIChannel 后添加:
   ```python
   channel.set_agent_loop(agent)
   ```

**预计工作量**: 5 分钟

---

### Task 4: 更新 StopCommandHandler

**文件**: `anyclaw/anyclaw/commands/handlers/task.py`

**步骤**:
1. 修改 `StopCommandHandler.execute()` 方法:
   - 使用新的 `request_abort()` 方法
   - 保持向后兼容

**预计工作量**: 10 分钟

---

### Task 5: 编写测试

**文件**: `tests/test_task_interrupt.py`

**测试用例**:
1. `test_register_task` - 测试任务注册
2. `test_unregister_task` - 测试任务取消注册
3. `test_request_abort_sets_flag` - 测试中断标志设置
4. `test_request_abort_cancels_task` - 测试任务取消
5. `test_run_with_tools_checks_abort_flag` - 测试迭代循环检查中断
6. `test_cli_channel_handles_stop_directly` - 测试 CLI 直接处理 /stop
7. `test_dispatch_with_tracking_registers_task` - 测试任务追踪

**预计工作量**: 30 分钟

---

## 依赖关系

```
Task 1 (AgentLoop) ──┐
                      ├──> Task 5 (测试)
Task 2 (CLIChannel) ─┤
                      │
Task 3 (chat 集成) ───┘
                      │
Task 4 (命令处理器) ──┘
```

## 总预计工作量

~2 小时
