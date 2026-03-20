# feat-cron

**状态**: ✅ 已完成
**完成时间**: 2026-03-20
**优先级**: 70
**大小**: M
**提交**: 9ba8bc4, b8c5e27

## 描述

实现 Cron 定时任务系统，支持 at (一次性)、every (间隔)、cron (标准 cron 表达式) 三种调度模式，与 nanobot 的 CronService 保持兼容。

## 价值点

1. **三种调度模式**
   - `at` - 一次性定时任务 (指定时间执行一次)
   - `every` - 间隔重复任务 (每 N 秒/分/时执行)
   - `cron` - 标准 cron 表达式 (灵活时间调度)

2. **任务持久化**
   - JSONL 格式存储任务
   - 重启后自动恢复
   - 文件修改检测自动重载

3. **任务管理**
   - 添加/列出/删除/启用/禁用任务
   - 手动触发执行
   - 任务状态追踪

4. **Channel 集成**
   - ChannelManager 集成
   - 任务执行结果通过 MessageBus 通知

## 实现文件

- `anyclaw/cron/types.py` - 数据类型 (CronJob, JobType)
- `anyclaw/cron/service.py` - CronService 核心实现
- `anyclaw/cron/tool.py` - CronTool 工具定义
- `anyclaw/channels/manager.py` - ChannelManager 集成
- `anyclaw/config/settings.py` - 配置项

## 配置项

```json
{
  "enable_cron": true,
  "cron_jobs_file": "~/.anyclaw/cron_jobs.jsonl",
  "cron_max_jobs": 100
}
```

## 使用示例

### 通过 CronTool

```python
from anyclaw.cron.tool import CronTool

cron_tool = CronTool(cron_service)

# 添加一次性任务 (at)
result = await cron_tool.execute(
    action="add",
    type="at",
    prompt="提醒我开会",
    time="2026-03-21T10:00:00"
)

# 添加间隔任务 (every)
result = await cron_tool.execute(
    action="add",
    type="every",
    prompt="检查系统状态",
    interval=300  # 每 5 分钟
)

# 添加 cron 任务
result = await cron_tool.execute(
    action="add",
    type="cron",
    prompt="每日报告",
    cron="0 9 * * *"  # 每天 9:00
)

# 列出所有任务
result = await cron_tool.execute(action="list")

# 删除任务
result = await cron_tool.execute(action="remove", job_id="job_abc123")
```

### 直接使用 CronService

```python
from anyclaw.cron.service import CronService

service = CronService(jobs_file="~/.anyclaw/cron_jobs.jsonl")
await service.start()

# 添加任务
job = await service.add_job(
    type=JobType.EVERY,
    prompt="定期任务",
    interval=60,
    channel="discord",
    chat_id="123456"
)

# 等待执行...
# 任务触发时调用 callback

await service.stop()
```

## CronTool 接口

```python
class CronTool(BaseTool):
    name = "cron"
    description = "管理定时任务"

    async def execute(
        self,
        action: str,      # "add" | "list" | "remove" | "enable" | "disable" | "run"
        type: str = None, # "at" | "every" | "cron"
        prompt: str = None,
        time: str = None,    # ISO 时间 (at)
        interval: int = None, # 秒数 (every)
        cron: str = None,     # cron 表达式
        job_id: str = None
    ) -> Dict[str, Any]:
        pass
```

## 数据结构

```python
@dataclass
class CronJob:
    id: str
    type: JobType  # AT | EVERY | CRON
    prompt: str
    channel: Optional[str]
    chat_id: Optional[str]
    created_at: datetime
    next_run: Optional[datetime]
    last_run: Optional[datetime]
    enabled: bool = True

    # AT 特有
    scheduled_time: Optional[datetime] = None

    # EVERY 特有
    interval_seconds: Optional[int] = None

    # CRON 特有
    cron_expression: Optional[str] = None
```

## 架构流程

```
CronTool.execute(action="add", type="every", ...)
    ↓
CronService.add_job()
    ↓
保存到 JSONL 文件
    ↓
CronService._on_timer() 定期检查
    ↓
任务到期 → ChannelManager.cron_job_callback()
    ↓
MessageBus.publish_inbound()
    ↓
AgentLoop 处理 prompt
    ↓
结果发送到 channel/chat_id
```

## 测试

```
tests/test_cron.py
```

## 与 nanobot 对比

| 特性 | nanobot | AnyClaw | 状态 |
|------|---------|---------|------|
| at (一次性) | ✅ | ✅ | 完全兼容 |
| every (间隔) | ✅ | ✅ | 完全兼容 |
| cron 表达式 | ✅ | ✅ | 完全兼容 |
| JSONL 持久化 | ✅ | ✅ | 完全兼容 |
| Channel 集成 | ✅ | ✅ | 完全兼容 |
