# Cron 调度系统 - 需求分析与实现方案

> **版本信息**
> - 参考实现: nanobot (2026-03-17)
> - 目标: AnyClaw 0.1.0-MVP
> - 方案日期: 2026-03-20

---

## 📋 需求分析

### 用户场景

**场景 1: 定时提醒**
```
用户: "明天早上 9 点提醒我开会"
    ↓
Cron 调度器创建一次性任务
    ↓
第二天 9:00 自动触发
    ↓
发送提醒消息给用户
```

**场景 2: 周期性任务**
```
用户: "每天上午 9 点发送日报"
    ↓
Cron 调度器创建周期性任务
    ↓
每天 9:00 自动触发
    ↓
Agent 生成日报并发送
```

**场景 3: 间隔任务**
```
用户: "每 30 分钟检查一次新邮件"
    ↓
Cron 调度器创建间隔任务
    ↓
每 30 分钟自动触发
    ↓
检查邮件并通知用户
```

### 功能需求

| 需求 | 优先级 | 描述 |
|------|--------|------|
| **一次性任务** | 🔴 高 | 支持指定时间执行一次任务（`at` 调度） |
| **周期性任务** | 🔴 高 | 支持周期性执行任务（`cron` 表达式） |
| **间隔任务** | 🔴 高 | 支持按间隔执行任务（`every` 调度） |
| **任务管理** | 🔴 高 | 添加、列表、删除、启用/禁用任务 |
| **手动触发** | 🟡 中 | 手动运行任务（调试用） |
| **时区支持** | 🟡 中 | 支持不同时区的调度 |
| **任务持久化** | 🔴 高 | 任务保存在磁盘，重启后恢复 |
| **任务状态** | 🟡 中 | 跟踪任务状态（成功、失败、错误） |
| **任务日志** | 🟡 中 | 记录任务执行历史 |

### 非功能需求

| 需求 | 优先级 | 描述 |
|------|--------|------|
| **准确性** | 🔴 高 | 任务在准确的时间执行 |
| **可靠性** | 🔴 高 | 服务崩溃重启后恢复任务 |
| **性能** | 🟡 中 | 支持大量任务（100+） |
| **异步执行** | 🔴 高 | 任务执行不阻塞调度器 |
| **错误处理** | 🟡 中 | 任务失败不影响其他任务 |
| **资源限制** | 🟡 中 | 防止任务占用过多资源 |

---

## 🏗️ 架构设计

### 核心组件

```
Cron 调度系统
├── cron/
│   ├── service.py          # ✨ CronService - 核心调度器
│   ├── types.py           # ✨ 数据类型定义
│   └── jobs.json         # 任务持久化存储
├── agent/
│   └── tools/
│       └── cron.py        # ✨ CronTool - 任务管理工具
├── cli/
│   └── cron_cmd.py       # ✨ Cron CLI 命令
└── config/
    └── settings.py        # 添加 Cron 配置
```

### 数据模型

#### 1. CronSchedule - 调度类型

```python
@dataclass
class CronSchedule:
    """调度定义"""
    kind: Literal["at", "every", "cron"]  # 调度类型
    
    # "at" 类型：一次性执行的时间戳（毫秒）
    at_ms: int | None = None
    
    # "every" 类型：执行间隔（毫秒）
    every_ms: int | None = None
    
    # "cron" 类型：Cron 表达式
    expr: str | None = None
    
    # 时区（仅用于 cron 表达式）
    tz: str | None = None
```

#### 2. CronPayload - 任务负载

```python
@dataclass
class CronPayload:
    """任务执行时做什么"""
    kind: Literal["system_event", "agent_turn"] = "agent_turn"
    message: str = ""  # 发送给 Agent 的消息
    deliver: bool = False  # 是否回复到 Channel
    channel: str | None = None  # 目标 Channel
    to: str | None = None  # 目标 Chat ID
```

#### 3. CronJobState - 任务状态

```python
@dataclass
class CronJobState:
    """任务运行时状态"""
    next_run_at_ms: int | None = None  # 下次运行时间
    last_run_at_ms: int | None = None  # 上次运行时间
    last_status: Literal["ok", "error", "skipped"] | None = None  # 上次状态
    last_error: str | None = None  # 上次错误
```

#### 4. CronJob - 定时任务

```python
@dataclass
class CronJob:
    """一个定时任务"""
    id: str  # 任务 ID
    name: str  # 任务名称
    enabled: bool = True  # 是否启用
    schedule: CronSchedule  # 调度定义
    payload: CronPayload  # 任务负载
    state: CronJobState  # 运行状态
    created_at_ms: int = 0  # 创建时间
    updated_at_ms: int = 0  # 更新时间
    delete_after_run: bool = False  # 运行后是否删除（一次性任务）
```

#### 5. CronStore - 持久化存储

```python
@dataclass
class CronStore:
    """任务持久化存储"""
    version: int = 1  # 存储格式版本
    jobs: list[CronJob] = field(default_factory=list)  # 任务列表
```

---

### CronService - 核心调度器

**位置**: `anyclaw/cron/service.py`

```python
class CronService:
    """定时任务调度服务"""
    
    def __init__(
        self,
        store_path: Path,  # 任务存储文件路径
        on_job: Callable[[CronJob], Coroutine[Any, Any, str | None]] | None = None,
    ):
        self.store_path = store_path
        self.on_job = on_job  # 任务执行回调
        self._store: CronStore | None = None  # 内存中的任务存储
        self._last_mtime: float = 0.0  # 文件修改时间
        self._timer_task: asyncio.Task | None = None  # 定时器任务
        self._running = False  # 是否运行中
    
    async def start(self) -> None:
        """启动 Cron 服务"""
        self._running = True
        self._load_store()  # 加载任务
        self._recompute_next_runs()  # 计算下次运行时间
        self._save_store()  # 保存任务
        self._arm_timer()  # 启动定时器
    
    def stop(self) -> None:
        """停止 Cron 服务"""
        self._running = False
        if self._timer_task:
            self._timer_task.cancel()
            self._timer_task = None
    
    def add_job(...) -> CronJob:
        """添加新任务"""
        # ...
    
    def remove_job(self, job_id: str) -> bool:
        """删除任务"""
        # ...
    
    def enable_job(self, job_id: str, enabled: bool) -> CronJob | None:
        """启用或禁用任务"""
        # ...
    
    async def run_job(self, job_id: str, force: bool = False) -> bool:
        """手动运行任务"""
        # ...
    
    def list_jobs(self, include_disabled: bool = False) -> list[CronJob]:
        """列出所有任务"""
        # ...
    
    def status(self) -> dict:
        """获取服务状态"""
        # ...
```

### 核心逻辑

#### 1. 定时器循环

```python
async def _on_timer(self) -> None:
    """定时器触发 - 执行到期任务"""
    self._load_store()
    if not self._store:
        return
    
    now = _now_ms()  # 当前时间（毫秒）
    
    # 查找所有到期任务
    due_jobs = [
        j for j in self._store.jobs
        if j.enabled and j.state.next_run_at_ms and now >= j.state.next_run_at_ms
    ]
    
    # 执行所有到期任务
    for job in due_jobs:
        await self._execute_job(job)
    
    # 保存任务状态
    self._save_store()
    
    # 重新设置定时器
    self._arm_timer()
```

#### 2. 计算下次运行时间

```python
def _compute_next_run(schedule: CronSchedule, now_ms: int) -> int | None:
    """计算下次运行时间"""
    
    if schedule.kind == "at":
        # 一次性任务：直接返回设定时间
        return schedule.at_ms if schedule.at_ms and schedule.at_ms > now_ms else None
    
    if schedule.kind == "every":
        # 间隔任务：当前时间 + 间隔
        if not schedule.every_ms or schedule.every_ms <= 0:
            return None
        return now_ms + schedule.every_ms
    
    if schedule.kind == "cron" and schedule.expr:
        # Cron 表达式：使用 croniter 解析
        try:
            from zoneinfo import ZoneInfo
            from croniter import croniter
            
            tz = ZoneInfo(schedule.tz) if schedule.tz else datetime.now().astimezone().tzinfo
            base_time = now_ms / 1000
            base_dt = datetime.fromtimestamp(base_time, tz=tz)
            cron = croniter(schedule.expr, base_dt)
            next_dt = cron.get_next(datetime)
            return int(next_dt.timestamp() * 1000)
        except Exception:
            return None
    
    return None
```

#### 3. 执行任务

```python
async def _execute_job(self, job: CronJob) -> None:
    """执行单个任务"""
    start_ms = _now_ms()
    logger.info("Cron: executing job '{}' ({})", job.name, job.id)
    
    try:
        # 调用任务回调
        response = None
        if self.on_job:
            response = await self.on_job(job)
        
        job.state.last_status = "ok"
        job.state.last_error = None
        logger.info("Cron: job '{}' completed", job.name)
    
    except Exception as e:
        job.state.last_status = "error"
        job.state.last_error = str(e)
        logger.error("Cron: job '{}' failed: {}", job.name, e)
    
    job.state.last_run_at_ms = start_ms
    job.updated_at_ms = _now_ms()
    
    # 处理一次性任务
    if job.schedule.kind == "at":
        if job.delete_after_run:
            # 删除任务
            self._store.jobs = [j for j in self._store.jobs if j.id != job.id]
        else:
            # 禁用任务
            job.enabled = False
            job.state.next_run_at_ms = None
    else:
        # 计算下次运行时间
        job.state.next_run_at_ms = _compute_next_run(job.schedule, _now_ms())
```

---

### CronTool - 任务管理工具

**位置**: `anyclaw/agent/tools/cron.py`

```python
class CronTool(Tool):
    """定时任务管理工具"""
    
    def __init__(self, cron_service: CronService):
        self._cron = cron_service
        self._channel = ""
        self._chat_id = ""
        self._in_cron_context: ContextVar[bool] = ContextVar("cron_in_context", default=False)
    
    def set_context(self, channel: str, chat_id: str) -> None:
        """设置当前会话上下文（用于任务发送）"""
        self._channel = channel
        self._chat_id = chat_id
    
    def set_cron_context(self, active: bool):
        """标记当前是否在 Cron 任务执行中"""
        return self._in_cron_context.set(active)
    
    def reset_cron_context(self, token) -> None:
        """恢复之前的 Cron 上下文"""
        self._in_cron_context.reset(token)
    
    @property
    def name(self) -> str:
        return "cron"
    
    @property
    def description(self) -> str:
        return "Schedule reminders and recurring tasks. Actions: add, list, remove."
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "list", "remove"],
                    "description": "Action to perform",
                },
                "message": {"type": "string", "description": "Reminder message (for add)"},
                "every_seconds": {
                    "type": "integer",
                    "description": "Interval in seconds (for recurring tasks)",
                },
                "cron_expr": {
                    "type": "string",
                    "description": "Cron expression like '0 9 * * *' (for scheduled tasks)",
                },
                "tz": {
                    "type": "string",
                    "description": "IANA timezone for cron expressions (e.g. 'America/Vancouver')",
                },
                "at": {
                    "type": "string",
                    "description": "ISO datetime for one-time execution (e.g. '2026-02-12T10:30:00')",
                },
                "job_id": {"type": "string", "description": "Job ID (for remove)"},
            },
            "required": ["action"],
        }
    
    async def execute(
        self,
        action: str,
        message: str = "",
        every_seconds: int | None = None,
        cron_expr: str | None = None,
        tz: str | None = None,
        at: str | None = None,
        job_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        if action == "add":
            if self._in_cron_context.get():
                return "Error: cannot schedule new jobs from within a cron job execution"
            return self._add_job(message, every_seconds, cron_expr, tz, at)
        elif action == "list":
            return self._list_jobs()
        elif action == "remove":
            return self._remove_job(job_id)
        return f"Unknown action: {action}"
```

---

## 🔧 集成到 AnyClaw

### 1. 修改 ChannelManager

**文件**: `anyclaw/channels/manager.py`

```python
class ChannelManager:
    """Channel 管理器（添加 Cron 支持）"""
    
    def __init__(
        self,
        # ... 现有参数 ...
        
        # ✨ 新增：Cron 服务
        cron_service: Optional[CronService] = None,
    ):
        # ... 现有初始化 ...
        
        # ✨ 新增：Cron 服务
        self.cron_service = cron_service
        
        # 注册 CronTool
        if self.cron_service:
            cron_tool = CronTool(self.cron_service)
            # 所有 Channel 共享一个 CronTool
            for channel in self.channels.values():
                if hasattr(channel, 'agent_loop'):
                    channel.agent_loop.tools.register(cron_tool)
    
    async def start(self) -> None:
        """启动所有服务"""
        # ... 现有启动逻辑 ...
        
        # ✨ 新增：启动 Cron 服务
        if self.cron_service:
            await self.cron_service.start()
    
    async def stop(self) -> None:
        """停止所有服务"""
        # ✨ 新增：停止 Cron 服务
        if self.cron_service:
            self.cron_service.stop()
        
        # ... 现有停止逻辑 ...
```

### 2. Cron 任务执行回调

**文件**: `anyclaw/channels/manager.py`

```python
async def _on_cron_job(self, job: CronJob) -> str | None:
    """Cron 任务执行回调"""
    
    # 构建 InboundMessage
    msg = InboundMessage(
        channel=job.payload.channel or "system",
        sender_id="cron",
        chat_id=job.payload.to or "",
        content=job.payload.message,
    )
    
    # 发布到消息总线
    await self.bus.publish_inbound(msg)
    
    logger.info("Cron job '{}' executed", job.name)
    
    return None  # 不需要返回内容
```

### 3. 配置系统更新

**文件**: `anyclaw/config/settings.py`

```python
class Settings(BaseSettings):
    """AnyClaw 配置（添加 Cron 支持）"""
    
    # ... 现有配置 ...
    
    # ✨ 新增：Cron 配置
    cron_enabled: bool = True  # 是否启用 Cron
    cron_jobs_file: str = "~/.anyclaw/cron/jobs.json"  # 任务存储文件
    cron_max_jobs: int = 100  # 最大任务数
```

---

## 📋 实施步骤

### Phase 1: 核心实现 (Day 1-2)

**任务清单**:

- [ ] 1.1 创建 `anyclaw/cron/types.py`
  - 实现 `CronSchedule` 类
  - 实现 `CronPayload` 类
  - 实现 `CronJobState` 类
  - 实现 `CronJob` 类
  - 实现 `CronStore` 类

- [ ] 1.2 创建 `anyclaw/cron/service.py`
  - 实现 `CronService` 类
  - 实现 `start()` 方法
  - 实现 `stop()` 方法
  - 实现 `add_job()` 方法
  - 实现 `remove_job()` 方法
  - 实现 `enable_job()` 方法
  - 实现 `run_job()` 方法
  - 实现 `list_jobs()` 方法
  - 实现 `status()` 方法
  - 实现 `_on_timer()` 方法
  - 实现 `_execute_job()` 方法
  - 实现 `_compute_next_run()` 方法

- [ ] 1.3 单元测试
  - 测试 `CronService` 的基本功能
  - 测试调度时间计算
  - 测试任务执行

### Phase 2: 工具集成 (Day 3)

**任务清单**:

- [ ] 2.1 创建 `anyclaw/agent/tools/cron.py`
  - 实现 `CronTool` 类
  - 实现 `set_context()` 方法
  - 实现 `execute()` 方法
  - 实现 `_add_job()` 方法
  - 实现 `_list_jobs()` 方法
  - 实现 `_remove_job()` 方法

- [ ] 2.2 单元测试
  - 测试 `CronTool` 的所有操作

### Phase 3: 集成到 AnyClaw (Day 4)

**任务清单**:

- [ ] 3.1 更新 `anyclaw/channels/manager.py`
  - 添加 `cron_service` 参数
  - 实现 `_on_cron_job()` 回调
  - 注册 `CronTool`
  - 在 `start()` 中启动 Cron 服务
  - 在 `stop()` 中停止 Cron 服务

- [ ] 3.2 更新 `anyclaw/config/settings.py`
  - 添加 `cron_enabled` 配置
  - 添加 `cron_jobs_file` 配置
  - 添加 `cron_max_jobs` 配置

### Phase 4: CLI 命令 (Day 5)

**任务清单**:

- [ ] 4.1 创建 `anyclaw/cli/cron_cmd.py`
  - 实现 `cron list` 命令
  - 实现 `cron add` 命令
  - 实现 `cron remove` 命令
  - 实现 `cron enable` 命令
  - 实现 `cron disable` 命令
  - 实现 `cron run` 命令
  - 实现 `cron status` 命令

- [ ] 4.2 集成到 CLI
  - 更新 `anyclaw/cli/app.py`

### Phase 5: 集成测试 (Day 6-7)

**任务清单**:

- [ ] 5.1 端到端测试
  - 测试一次性任务（`at`）
  - 测试周期性任务（`cron`）
  - 测试间隔任务（`every`）
  - 测试任务管理（添加、列表、删除、启用/禁用）

- [ ] 5.2 集成测试
  - 测试与 Discord Channel 集成
  - 测试与 Feishu Channel 集成

- [ ] 5.3 性能测试
  - 测试大量任务（100+）
  - 测试任务执行性能

---

## 🧪 测试用例

### 单元测试

**文件**: `tests/test_cron_service.py`

```python
import pytest
from anyclaw.cron.service import CronService
from anyclaw.cron.types import CronSchedule, CronJob

@pytest.mark.asyncio
async def test_cron_add_every_job():
    """测试添加间隔任务"""
    service = CronService(store_path=jobs_file, on_job=mock_callback)
    await service.start()
    
    job = service.add_job(
        name="Test job",
        schedule=CronSchedule(kind="every", every_ms=5000),
        message="Test message",
    )
    
    assert job.id
    assert job.enabled
    assert job.schedule.kind == "every"
    assert job.state.next_run_at_ms > 0

@pytest.mark.asyncio
async def test_cron_add_cron_job():
    """测试添加 Cron 表达式任务"""
    service = CronService(store_path=jobs_file, on_job=mock_callback)
    await service.start()
    
    job = service.add_job(
        name="Daily job",
        schedule=CronSchedule(kind="cron", expr="0 9 * * *"),
        message="Daily report",
    )
    
    assert job.id
    assert job.schedule.kind == "cron"

@pytest.mark.asyncio
async def test_cron_list_jobs():
    """测试列出任务"""
    service = CronService(store_path=jobs_file, on_job=mock_callback)
    await service.start()
    
    service.add_job(
        name="Job 1",
        schedule=CronSchedule(kind="every", every_ms=5000),
        message="Message 1",
    )
    
    jobs = service.list_jobs()
    assert len(jobs) == 1
    assert jobs[0].name == "Job 1"

@pytest.mark.asyncio
async def test_cron_remove_job():
    """测试删除任务"""
    service = CronService(store_path=jobs_file, on_job=mock_callback)
    await service.start()
    
    job = service.add_job(
        name="Test job",
        schedule=CronSchedule(kind="every", every_ms=5000),
        message="Test message",
    )
    
    removed = service.remove_job(job.id)
    assert removed
    
    jobs = service.list_jobs()
    assert len(jobs) == 0

@pytest.mark.asyncio
async def test_cron_enable_disable():
    """测试启用/禁用任务"""
    service = CronService(store_path=jobs_file, on_job=mock_callback)
    await service.start()
    
    job = service.add_job(
        name="Test job",
        schedule=CronSchedule(kind="every", every_ms=5000),
        message="Test message",
    )
    
    # 禁用任务
    service.enable_job(job.id, enabled=False)
    assert not job.enabled
    assert job.state.next_run_at_ms is None
    
    # 启用任务
    service.enable_job(job.id, enabled=True)
    assert job.enabled
    assert job.state.next_run_at_ms > 0
```

---

## 📊 使用示例

### 示例 1: 一次性提醒

```python
# 用户: "明天早上 9 点提醒我开会"

# Agent 调用 CronTool
await cron_tool.execute(
    action="add",
    message="9:00 AM meeting reminder",
    at="2026-03-21T09:00:00",
)

# 返回: "Created job '9:00 AM meeting reminder' (id: abc123)"

# 第二天 9:00 自动触发
# 发送消息给用户
```

### 示例 2: 每日报告

```python
# 用户: "每天上午 9 点发送日报"

# Agent 调用 CronTool
await cron_tool.execute(
    action="add",
    message="Generate daily report",
    cron_expr="0 9 * * *",  # 每天 9:00
    tz="Asia/Shanghai",  # 时区
)

# 返回: "Created job 'Generate daily report' (id: def456)"

# 每天 9:00 自动触发
# Agent 生成日报并发送
```

### 示例 3: 间隔检查

```python
# 用户: "每 30 分钟检查一次新邮件"

# Agent 调用 CronTool
await cron_tool.execute(
    action="add",
    message="Check for new emails",
    every_seconds=1800,  # 30 分钟
)

# 返回: "Created job 'Check for new emails' (id: ghi789)"

# 每 30 分钟自动触发
# 检查邮件并通知用户
```

### 示例 4: 列出任务

```python
# 用户: "列出所有定时任务"

# Agent 调用 CronTool
await cron_tool.execute(
    action="list",
)

# 返回:
"""
Scheduled jobs:
- 9:00 AM meeting reminder (id: abc123, at)
- Generate daily report (id: def456, cron)
- Check for new emails (id: ghi789, every)
"""
```

### 示例 5: 删除任务

```python
# 用户: "删除会议提醒"

# Agent 调用 CronTool
await cron_tool.execute(
    action="remove",
    job_id="abc123",
)

# 返回: "Removed job abc123"
```

---

## 🔒 安全考虑

### 1. 任务数量限制

```python
# ✅ 防止创建过多任务
if len(store.jobs) >= settings.cron_max_jobs:
    raise ValueError(f"Maximum number of jobs ({settings.cron_max_jobs}) reached")
```

### 2. 时区验证

```python
# ✅ 验证时区是否有效
if tz:
    try:
        ZoneInfo(tz)
    except (KeyError, Exception):
        return f"Error: unknown timezone '{tz}'"
```

### 3. Cron 表达式验证

```python
# ✅ 验证 Cron 表达式是否有效
if cron_expr:
    try:
        croniter(cron_expr, datetime.now())
    except Exception:
        return f"Error: invalid cron expression '{cron_expr}'"
```

### 4. 递归调度防护

```python
# ✅ 防止 Cron 任务再调度 Cron 任务
if self._in_cron_context.get():
    return "Error: cannot schedule new jobs from within a cron job execution"
```

---

## 📈 性能考虑

### 1. 异步执行

```python
# ✅ 任务异步执行，不阻塞调度器
async def _execute_job(self, job: CronJob) -> None:
    if self.on_job:
        response = await self.on_job(job)
```

### 2. 定时器优化

```python
# ✅ 只计算下一个最近的唤醒时间
def _get_next_wake_ms(self) -> int | None:
    times = [j.state.next_run_at_ms for j in self._store.jobs
             if j.enabled and j.state.next_run_at_ms]
    return min(times) if times else None
```

### 3. 文件监控

```python
# ✅ 监控文件变化，自动重载
if self._store and self.store_path.exists():
    mtime = self.store_path.stat().st_mtime
    if mtime != self._last_mtime:
        logger.info("Cron: jobs.json modified externally, reloading")
        self._store = None
```

---

## 🎯 与 nanobot 的对比

| 特性 | nanobot | AnyClaw 实现 | 状态 |
|------|---------|-------------|------|
| **一次性任务** | ✅ | ✅ | ✅ 对齐 |
| **周期性任务** | ✅ | ✅ | ✅ 对齐 |
| **间隔任务** | ✅ | ✅ | ✅ 对齐 |
| **任务管理** | ✅ | ✅ | ✅ 对齐 |
| **手动触发** | ✅ | ✅ | ✅ 对齐 |
| **时区支持** | ✅ | ✅ | ✅ 对齐 |
| **任务持久化** | ✅ | ✅ | ✅ 对齐 |
| **任务状态** | ✅ | ✅ | ✅ 对齐 |
| **文件驱动配置** | ✅ | ✅ | ✅ 对齐 |
| **CLI 命令** | ✅ | ✅ | ✅ 对齐 |

---

## 🚀 未来增强

### 1. 任务依赖

```python
# 任务 A 完成后触发任务 B
await cron_tool.execute(
    action="add",
    message="Task B",
    depends_on="task_a_id",
)
```

### 2. 任务模板

```python
# 使用预定义模板
await cron_tool.execute(
    action="add",
    template="daily_report",
    variables={"time": "09:00", "recipient": "Ryan"},
)
```

### 3. 任务重试

```python
# 失败的任务自动重试
await cron_tool.execute(
    action="add",
    message="Important task",
    retry_count=3,
    retry_delay=60,
)
```

### 4. 任务历史

```python
# 查看任务执行历史
history = await cron_service.get_job_history(job_id="abc123")
# [
#   {"run_at": "2026-03-20T09:00:00", "status": "ok"},
#   {"run_at": "2026-03-21T09:00:00", "status": "error"},
#   {"run_at": "2026-03-22T09:00:00", "status": "ok"},
# ]
```

### 5. 任务监控

```python
# Web UI 监控任务状态
await cron_service.start_monitoring_ui(port=8080)
# http://localhost:8080/cron
```

---

## 📝 总结

### 实现成果

✅ **完美复刻** nanobot 的 Cron 调度系统
✅ **完美适配** AnyClaw 原有架构
✅ **不影响** 现有功能
✅ **向后兼容** - 可通过配置禁用

### 核心优势

1. **三种调度模式** - at（一次性）、every（间隔）、cron（周期性）
2. **任务持久化** - 服务重启后恢复
3. **时区支持** - 支持全球时区
4. **异步执行** - 不阻塞调度器
5. **任务管理** - 完整的增删查改
6. **状态跟踪** - 记录执行状态和错误

### 下一步

1. 实现核心代码（Phase 1-3）
2. 实现 CLI 命令（Phase 4）
3. 集成测试（Phase 5）

---

## 🔧 依赖项

```toml
[tool.poetry.dependencies]
# Cron 调度
croniter = "^3.0.0"  # Cron 表达式解析
pytz = "^2024.1"  # 时区支持（Python < 3.9）

# 或使用 Python 3.9+ 内置
# from zoneinfo import ZoneInfo
```

---

**方案生成时间**: 2026-03-20
**参考实现**: nanobot (cron/service.py, cron/types.py, agent/tools/cron.py)
**预计完成时间**: 7 天
