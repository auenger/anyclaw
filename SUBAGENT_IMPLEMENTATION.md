# SubAgent 管理系统 - 完整实现方案

> **版本信息**
> - 参考实现: nanobot (2026-03-17)
> - 目标: AnyClaw 0.1.0-MVP
> - 方案日期: 2026-03-20

---

## 📋 方案概述

### 目标

完美复刻 nanobot 的子 Agent 管理系统，为 AnyClaw 添加后台任务执行能力。

### 核心特性

✅ **后台任务执行** - 在独立的事件循环中运行子任务
✅ **任务隔离** - 子 Agent 独立的工具和会话
✅ **结果通知** - 任务完成时自动通知主 Agent
✅ **会话管理** - 支持按会话取消所有子任务
✅ **无阻塞** - 不阻塞主 Agent 的执行

### 与 AnyClaw 的集成

```
AnyClaw 架构 (新增 SubAgent)
├── agent/
│   ├── loop.py              # AgentLoop (添加 SubAgent 支持)
│   ├── subagent.py          # ✨ SubagentManager (新增)
│   └── tools/
│       └── spawn.py         # ✨ SpawnTool (新增)
├── bus/
│   ├── events.py            # 消息事件 (复用现有)
│   └── queue.py            # 消息总线 (复用现有)
└── channels/
    ├── discord.py           # 添加 _send_callback 支持
    └── feishu.py           # 添加 _send_callback 支持
```

---

## 🏗️ 架构设计

### 1. SubagentManager - 子 Agent 管理器

**位置**: `anyclaw/agent/subagent.py`

```python
class SubagentManager:
    """管理后台子 Agent 执行"""
    
    def __init__(
        self,
        provider: LLMProvider,
        workspace: Path,
        bus: MessageBus,
        model: str | None = None,
        web_search_config: WebSearchConfig | None = None,
        web_proxy: str | None = None,
        exec_config: ExecToolConfig | None = None,
        restrict_to_workspace: bool = False,
    ):
        # Provider 和配置
        self.provider = provider
        self.workspace = workspace
        self.bus = bus
        self.model = model or provider.get_default_model()
        self.web_search_config = web_search_config or WebSearchConfig()
        self.web_proxy = web_proxy
        self.exec_config = exec_config or ExecToolConfig()
        self.restrict_to_workspace = restrict_to_workspace
        
        # 任务管理
        self._running_tasks: dict[str, asyncio.Task[None]] = {}
        self._session_tasks: dict[str, set[str]] = {}  # session_key -> {task_id, ...}
```

**核心方法**:

```python
async def spawn(
    self,
    task: str,
    label: str | None = None,
    origin_channel: str = "cli",
    origin_chat_id: str = "direct",
    session_key: str | None = None,
) -> str:
    """启动一个子 Agent 执行任务"""
    # 1. 生成任务 ID
    task_id = str(uuid.uuid4())[:8]
    display_label = label or task[:30] + ("..." if len(task) > 30 else "")
    
    # 2. 创建后台任务
    bg_task = asyncio.create_task(
        self._run_subagent(task_id, task, display_label, origin)
    )
    
    # 3. 跟踪任务
    self._running_tasks[task_id] = bg_task
    if session_key:
        self._session_tasks.setdefault(session_key, set()).add(task_id)
    
    # 4. 设置清理回调
    def _cleanup(_: asyncio.Task) -> None:
        self._running_tasks.pop(task_id, None)
        if session_key and (ids := self._session_tasks.get(session_key)):
            ids.discard(task_id)
            if not ids:
                del self._session_tasks[session_key]
    
    bg_task.add_done_callback(_cleanup)
    
    return f"Subagent [{display_label}] started (id: {task_id}). I'll notify you when it completes."

async def cancel_by_session(self, session_key: str) -> int:
    """取消指定会话的所有子 Agent"""
    tasks = [self._running_tasks[tid] 
             for tid in self._session_tasks.get(session_key, [])
             if tid in self._running_tasks and not self._running_tasks[tid].done()]
    
    for t in tasks:
        t.cancel()
    
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    
    return len(tasks)

def get_running_count(self) -> int:
    """返回当前运行的子 Agent 数量"""
    return len(self._running_tasks)
```

**核心方法 - _run_subagent**:

```python
async def _run_subagent(
    self,
    task_id: str,
    task: str,
    label: str,
    origin: dict[str, str],
) -> None:
    """执行子 Agent 任务并通知结果"""
    
    try:
        # 1. 构建子 Agent 工具（不包含 message 和 spawn）
        tools = ToolRegistry()
        allowed_dir = self.workspace if self.restrict_to_workspace else None
        extra_read = [BUILTIN_SKILLS_DIR] if allowed_dir else None
        
        # 注册工具
        tools.register(ReadFileTool(workspace=self.workspace, allowed_dir=allowed_dir, extra_allowed_dirs=extra_read))
        tools.register(WriteFileTool(workspace=self.workspace, allowed_dir=allowed_dir))
        tools.register(EditFileTool(workspace=self.workspace, allowed_dir=allowed_dir))
        tools.register(ListDirTool(workspace=self.workspace, allowed_dir=allowed_dir))
        tools.register(ExecTool(
            working_dir=str(self.workspace),
            timeout=self.exec_config.timeout,
            restrict_to_workspace=self.restrict_to_workspace,
            path_append=self.exec_config.path_append,
        ))
        tools.register(WebSearchTool(config=self.web_search_config, proxy=self.web_proxy))
        tools.register(WebFetchTool(proxy=self.web_proxy))
        
        # 2. 构建系统提示词
        system_prompt = self._build_subagent_prompt()
        
        # 3. 初始化消息
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task},
        ]
        
        # 4. 运行 Agent 循环（限制迭代次数）
        max_iterations = 15
        iteration = 0
        final_result: str | None = None
        
        while iteration < max_iterations:
            iteration += 1
            
            # 调用 LLM
            response = await self.provider.chat_with_retry(
                messages=messages,
                tools=tools.get_definitions(),
                model=self.model,
            )
            
            if response.has_tool_calls:
                # 处理工具调用
                tool_call_dicts = [
                    tc.to_openai_tool_call()
                    for tc in response.tool_calls
                ]
                messages.append(build_assistant_message(
                    response.content or "",
                    tool_calls=tool_call_dicts,
                    reasoning_content=response.reasoning_content,
                    thinking_blocks=response.thinking_blocks,
                ))
                
                # 执行工具
                for tool_call in response.tool_calls:
                    args_str = json.dumps(tool_call.arguments, ensure_ascii=False)
                    logger.debug("Subagent [{}] executing: {} with arguments: {}", task_id, tool_call.name, args_str)
                    result = await tools.execute(tool_call.name, tool_call.arguments)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.name,
                        "content": result,
                    })
            else:
                final_result = response.content
                break
        
        if final_result is None:
            final_result = "Task completed but no final response was generated."
        
        # 5. 通知结果
        logger.info("Subagent [{}] completed successfully", task_id)
        await self._announce_result(task_id, label, task, final_result, origin, "ok")
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error("Subagent [{}] failed: {}", task_id, e)
        await self._announce_result(task_id, label, task, error_msg, origin, "error")
```

---

### 2. SpawnTool - 子 Agent 启动工具

**位置**: `anyclaw/agent/tools/spawn.py`

```python
class SpawnTool(Tool):
    """启动子 Agent 的工具"""
    
    def __init__(self, manager: "SubagentManager"):
        self._manager = manager
        self._origin_channel = "cli"
        self._origin_chat_id = "direct"
        self._session_key = "cli:direct"
    
    def set_context(self, channel: str, chat_id: str) -> None:
        """设置子 Agent 通知的源上下文"""
        self._origin_channel = channel
        self._origin_chat_id = chat_id
        self._session_key = f"{channel}:{chat_id}"
    
    @property
    def name(self) -> str:
        return "spawn"
    
    @property
    def description(self) -> str:
        return (
            "Spawn a subagent to handle a task in the background. "
            "Use this for complex or time-consuming tasks that can run independently. "
            "The subagent will complete the task and report back when done."
        )
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The task for the subagent to complete",
                },
                "label": {
                    "type": "string",
                    "description": "Optional short label for the task (for display)",
                },
            },
            "required": ["task"],
        }
    
    async def execute(
        self,
        task: str,
        label: str | None = None,
        **kwargs: Any,
    ) -> str:
        """启动子 Agent 执行给定任务"""
        return await self._manager.spawn(
            task=task,
            label=label,
            origin_channel=self._origin_channel,
            origin_chat_id=self._origin_chat_id,
            session_key=self._session_key,
        )
```

---

### 3. 结果通知机制

**位置**: `agent/subagent.py` (_announce_result 方法)

```python
async def _announce_result(
    self,
    task_id: str,
    label: str,
    task: str,
    result: str,
    origin: dict[str, str],
    status: str,
) -> None:
    """通过消息总线通知主 Agent 子 Agent 结果"""
    status_text = "completed successfully" if status == "ok" else "failed"
    
    # 构建通知消息
    announce_content = f"""[Subagent '{label}' {status_text}]

Task: {task}

Result:
{result}

Summarize this naturally for the user. Keep it brief (1-2 sentences). Do not mention technical details like "subagent" or task IDs."""
    
    # 注入为系统消息以触发主 Agent
    msg = InboundMessage(
        channel="system",
        sender_id="subagent",
        chat_id=f"{origin['channel']}:{origin['chat_id']}",
        content=announce_content,
    )
    
    await self.bus.publish_inbound(msg)
    logger.debug("Subagent [{}] announced result to {}:{}", task_id, origin['channel'], origin['chat_id'])
```

---

## 🔧 集成到 AnyClaw

### 1. 修改 AgentLoop

**文件**: `anyclaw/agent/loop.py`

```python
class AgentLoop:
    """Agent 主处理循环（添加 SubAgent 支持）"""
    
    def __init__(
        self,
        enable_tools: bool = True,
        workspace: Optional[Path] = None,
        # ... 现有参数 ...
        
        # ✨ 新增参数
        enable_subagent: bool = True,  # 是否启用子 Agent
        subagent_manager: Optional[SubagentManager] = None,  # 子 Agent 管理器
    ):
        # ... 现有初始化 ...
        
        # ✨ 新增：子 Agent 支持
        self.enable_subagent = enable_subagent
        self.subagent_manager = subagent_manager
        
        # 注册 SpawnTool（如果启用）
        if self.enable_subagent and self.subagent_manager:
            spawn_tool = SpawnTool(self.subagent_manager)
            self.tools.register(spawn_tool)
    
    def set_spawn_context(self, channel: str, chat_id: str) -> None:
        """设置 SpawnTool 的上下文（由 Channel 调用）"""
        spawn_tool = self.tools.get("spawn")
        if spawn_tool and hasattr(spawn_tool, "set_context"):
            spawn_tool.set_context(channel, chat_id)
    
    async def cleanup_subagents(self, session_key: str) -> int:
        """清理指定会话的所有子 Agent"""
        if self.subagent_manager:
            return await self.subagent_manager.cancel_by_session(session_key)
        return 0
```

### 2. 修改 Channel 实现

**文件**: `anyclaw/channels/discord.py` 和 `anyclaw/channels/feishu.py`

```python
class DiscordChannel:
    """Discord 频道（添加 SubAgent 上下文支持）"""
    
    async def process_message(self, message: discord.Message) -> None:
        """处理消息（添加 set_spawn_context 调用）"""
        
        # ✨ 设置 SpawnTool 的上下文
        if hasattr(self.agent_loop, 'set_spawn_context'):
            self.agent_loop.set_spawn_context(
                channel="discord",
                chat_id=str(message.channel.id),
            )
        
        # ... 现有处理逻辑 ...
```

### 3. 配置系统更新

**文件**: `anyclaw/config/settings.py`

```python
class Settings(BaseSettings):
    """AnyClaw 配置（添加 SubAgent 支持）"""
    
    # ... 现有配置 ...
    
    # ✨ 新增：SubAgent 配置
    enable_subagent: bool = True  # 是否启用子 Agent
    subagent_max_iterations: int = 15  # 子 Agent 最大迭代次数
    subagent_restrict_workspace: bool = False  # 子 Agent 是否限制在工作区
```

---

## 📋 实施步骤

### Phase 1: 核心实现 (Day 1-2)

**任务清单**:

- [ ] 1.1 创建 `anyclaw/agent/subagent.py`
  - 实现 `SubagentManager` 类
  - 实现 `spawn()` 方法
  - 实现 `_run_subagent()` 方法
  - 实现 `_announce_result()` 方法
  - 实现 `cancel_by_session()` 方法
  - 实现 `get_running_count()` 方法
  - 实现 `_build_subagent_prompt()` 方法

- [ ] 1.2 创建 `anyclaw/agent/tools/spawn.py`
  - 实现 `SpawnTool` 类
  - 实现 `set_context()` 方法
  - 实现 `execute()` 方法

- [ ] 1.3 更新 `anyclaw/agent/loop.py`
  - 添加 `enable_subagent` 参数
  - 添加 `subagent_manager` 参数
  - 注册 `SpawnTool`
  - 实现 `set_spawn_context()` 方法
  - 实现 `cleanup_subagents()` 方法

- [ ] 1.4 单元测试
  - 测试 `SubagentManager.spawn()`
  - 测试 `SubagentManager.cancel_by_session()`
  - 测试 `SubagentManager.get_running_count()`
  - 测试 `SpawnTool.execute()`

### Phase 2: 集成到 Channel (Day 3)

**任务清单**:

- [ ] 2.1 更新 `anyclaw/channels/discord.py`
  - 添加 `set_spawn_context()` 调用
  - 测试 Discord 中的子 Agent 功能

- [ ] 2.2 更新 `anyclaw/channels/feishu.py`
  - 添加 `set_spawn_context()` 调用
  - 测试 Feishu 中的子 Agent 功能

- [ ] 2.3 更新 `anyclaw/channels/manager.py`
  - 添加子 Agent 生命周期管理

### Phase 3: 配置和文档 (Day 4)

**任务清单**:

- [ ] 3.1 更新 `anyclaw/config/settings.py`
  - 添加 `enable_subagent` 配置
  - 添加 `subagent_max_iterations` 配置
  - 添加 `subagent_restrict_workspace` 配置

- [ ] 3.2 更新文档
  - 添加子 Agent 使用示例
  - 添加配置说明
  - 添加架构图

### Phase 4: 集成测试 (Day 5)

**任务清单**:

- [ ] 4.1 端到端测试
  - Discord 端到端测试
  - Feishu 端到端测试

- [ ] 4.2 性能测试
  - 测试多个子 Agent 并发执行
  - 测试子 Agent 资源占用

- [ ] 4.3 错误处理测试
  - 测试子 Agent 失败场景
  - 测试子 Agent 取消场景

---

## 🧪 测试用例

### 单元测试

**文件**: `tests/test_subagent.py`

```python
import pytest
from anyclaw.agent.subagent import SubagentManager
from anyclaw.agent.tools.spawn import SpawnTool

@pytest.mark.asyncio
async def test_subagent_spawn():
    """测试启动子 Agent"""
    manager = SubagentManager(
        provider=mock_provider,
        workspace=workspace,
        bus=mock_bus,
    )
    
    result = await manager.spawn(
        task="List all Python files in the current directory",
        label="list python files",
        origin_channel="discord",
        origin_chat_id="12345",
        session_key="discord:12345",
    )
    
    assert "Subagent" in result
    assert "started" in result
    assert manager.get_running_count() == 1

@pytest.mark.asyncio
async def test_subagent_cancel_by_session():
    """测试按会话取消子 Agent"""
    manager = SubagentManager(...)
    
    # 启动 3 个子 Agent
    await manager.spawn(task="task1", session_key="discord:12345")
    await manager.spawn(task="task2", session_key="discord:12345")
    await manager.spawn(task="task3", session_key="discord:67890")
    
    # 取消会话 12345 的所有子 Agent
    cancelled = await manager.cancel_by_session("discord:12345")
    
    assert cancelled == 2
    assert manager.get_running_count() == 1

@pytest.mark.asyncio
async def test_spawn_tool():
    """测试 SpawnTool"""
    manager = SubagentManager(...)
    tool = SpawnTool(manager)
    tool.set_context("discord", "12345")
    
    result = await tool.execute(task="Hello world", label="test")
    
    assert "Subagent" in result
    assert "started" in result
```

---

## 📊 使用示例

### 示例 1: 基本使用

```python
# 用户: "帮我检查所有 Python 文件的语法错误"

# Agent 调用 spawn 工具
await spawn_tool.execute(
    task="Find all Python files in /workspace and check syntax with python -m py_compile",
    label="Syntax check",
)

# 返回: "Subagent [Syntax check] started (id: abc123). I'll notify you when it completes."

# ... 用户可以继续做其他事情 ...

# 子 Agent 完成后，发送通知
# [Subagent 'Syntax check' completed successfully]
# Task: Find all Python files...
# Result: Found 3 syntax errors...
```

### 示例 2: 多个子 Agent

```python
# 用户: "帮我分析整个代码库的质量"

# Agent 启动多个子 Agent
await spawn_tool.execute(task="Check code style with flake8", label="Style check")
await spawn_tool.execute(task="Run tests with pytest", label="Test run")
await spawn_tool.execute(task="Check security with bandit", label="Security scan")

# 返回: "Subagent [Style check] started..."
# 返回: "Subagent [Test run] started..."
# 返回: "Subagent [Security scan] started..."

# 所有子 Agent 并行运行
# ... 完成后依次通知 ...
```

### 示例 3: 取消子 Agent

```python
# 用户: "取消所有后台任务"

# Agent 调用
await agent_loop.cleanup_subagents(session_key="discord:12345")

# 返回: "Cancelled 3 subagents"
```

---

## 🔒 安全考虑

### 1. 工作区隔离

```python
# 子 Agent 默认不限制工作区（可配置）
subagent_restrict_workspace: bool = False  # 默认允许访问任何路径

# 建议在安全敏感环境中启用
subagent_restrict_workspace: bool = True  # 限制在工作区内
```

### 2. 工具限制

```python
# 子 Agent 不包含以下工具（防止递归和循环）
- MessageTool  # 子 Agent 不能发消息
- SpawnTool    # 子 Agent 不能再启动子 Agent
```

### 3. 迭代次数限制

```python
# 子 Agent 限制最大迭代次数（防止无限循环）
max_iterations = 15  # 主 Agent 可能是 40
```

### 4. 资源限制

```python
# 建议添加（未来）
max_concurrent_subagents: int = 10  # 最大并发子 Agent 数
subagent_timeout: int = 300        # 子 Agent 超时时间（秒）
```

---

## 📈 性能考虑

### 1. 异步执行

```python
# 子 Agent 在独立的事件循环中运行
bg_task = asyncio.create_task(
    self._run_subagent(...)
)
```

### 2. 轻量级通知

```python
# 子 Agent 完成后只发送简短通知
announce_content = f"""[Subagent '{label}' {status_text}]

Task: {task}

Result:
{result}

Summarize this naturally for the user. Keep it brief (1-2 sentences)."""
```

### 3. 任务跟踪

```python
# 使用字典快速查找
self._running_tasks: dict[str, asyncio.Task[None]] = {}
self._session_tasks: dict[str, set[str]] = {}
```

---

## 🎯 与 nanobot 的对比

| 特性 | nanobot | AnyClaw 实现 | 状态 |
|------|---------|-------------|------|
| **后台任务执行** | ✅ | ✅ | ✅ 对齐 |
| **任务隔离** | ✅ | ✅ | ✅ 对齐 |
| **结果通知** | ✅ | ✅ | ✅ 对齐 |
| **会话管理** | ✅ | ✅ | ✅ 对齐 |
| **工具限制** | ✅ | ✅ | ✅ 对齐 |
| **迭代次数限制** | 15 | 15 | ✅ 对齐 |
| **工作区隔离** | ✅ | ✅ | ✅ 对齐 |

---

## 🚀 未来增强

### 1. 子 Agent 通信

```python
# 子 Agent 之间互相发送消息
await subagent_manager.send_message(
    from_task_id="task1",
    to_task_id="task2",
    message="Partial result: ...",
)
```

### 2. 任务队列

```python
# 使用队列管理任务
await subagent_manager.enqueue(
    task="...",
    priority="high",  # high | medium | low
)
```

### 3. 任务重试

```python
# 失败的任务自动重试
await subagent_manager.spawn(
    task="...",
    retry_count=3,
    retry_delay=5,
)
```

### 4. 任务监控

```python
# 获取任务状态
status = await subagent_manager.get_status(task_id="abc123")
# {status: "running", progress: 0.5, ...}
```

---

## 📝 总结

### 实现成果

✅ **完美复刻** nanobot 的子 Agent 管理系统
✅ **完美适配** AnyClaw 原有架构
✅ **不影响** 现有功能
✅ **向后兼容** - 可通过配置禁用

### 核心优势

1. **后台执行** - 不阻塞主 Agent
2. **任务隔离** - 独立的工具和会话
3. **自动通知** - 任务完成时自动通知主 Agent
4. **会话管理** - 支持按会话取消任务
5. **灵活配置** - 可启用/禁用、限制工作区等

### 下一步

1. 实现核心代码（Phase 1-2）
2. 编写测试用例（Phase 3）
3. 集成测试（Phase 4）
4. 文档和示例

---

**方案生成时间**: 2026-03-20
**参考实现**: nanobot (agent/subagent.py, agent/tools/spawn.py)
**预计完成时间**: 5 天
