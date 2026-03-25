# feat-cron-resilience

## 概述

为 Cron 系统添加执行日志持久化、失败退避机制和卡死检测，提升任务执行的可靠性和可观测性。

## 背景

当前 AnyClaw 的 cron 实现：
- 执行状态只在内存中，重启后丢失
- 失败后没有退避机制，可能频繁重试消耗资源
- 没有卡死检测，任务可能永远卡住

## 用户价值点

### VP2: 执行日志持久化

持久化任务执行历史，支持查询、统计和问题排查。

**Gherkin 场景:**

```gherkin
Feature: 执行日志持久化

  Scenario: 记录成功执行
    Given 定时任务执行成功
    When 执行完成
    Then 系统记录日志包含: job_id, run_at_ms, duration_ms, status=success, result

  Scenario: 记录失败执行
    Given 定时任务执行失败
    When 执行抛出异常
    Then 系统记录日志包含: job_id, run_at_ms, duration_ms, status=error, error

  Scenario: 查询执行历史
    Given 任务有执行历史
    When 调用 get_logs(job_id, limit=20)
    Then 返回最近 20 条执行记录，按时间倒序

  Scenario: 自动清理过期日志
    Given 执行日志超过 30 天
    When 调用 prune_old_logs(days=30)
    Then 过期日志被删除
    And 返回删除数量
```

### VP3: 失败退避机制

连续失败时采用指数退避策略，达到阈值自动暂停。

**Gherkin 场景:**

```gherkin
Feature: 失败退避机制

  Scenario Outline: 退避延迟计算
    Given 任务连续失败 <failures> 次
    When 计算下次运行时间
    Then 退避延迟为 <delay> 秒

    Examples:
      | failures | delay |
      | 1        | 30    |
      | 2        | 60    |
      | 3        | 300   |
      | 4        | 900   |
      | 5+       | 3600  |

  Scenario: 连续失败 5 次自动暂停
    Given 任务连续失败 4 次
    When 第 5 次执行失败
    Then 任务状态变为 "paused"
    And 记录 last_result = "ERROR: 5 consecutive failures, auto-paused"

  Scenario: 成功后重置退避
    Given 任务有 3 次连续失败
    When 执行成功
    Then consecutive_failures 重置为 0
    And 退避延迟清除
    And next_run 按正常调度计算

  Scenario: 恢复暂停任务重置计数
    Given 任务状态为 "paused" 且 consecutive_failures = 5
    When 用户将状态改为 "active"
    Then consecutive_failures 重置为 0
    And 立即重新计算 next_run
```

### VP4: 卡死检测与恢复

检测长时间运行的任务并自动恢复。

**Gherkin 场景:**

```gherkin
Feature: 卡死检测与恢复

  Scenario: 检测卡死任务
    Given 任务 running_since_ms 超过 5 分钟
    When 调度器执行 tick
    Then 任务被识别为卡死
    And 记录错误日志 "Task execution timed out (exceeded 300s)"
    And consecutive_failures += 1

  Scenario: 卡死任务恢复
    Given 任务被检测为卡死
    When 系统处理卡死任务
    Then running_since_ms 被清除
    And 按退避策略计算 next_run

  Scenario: 卡死任务达到暂停阈值
    Given 任务卡死且 consecutive_failures = 4
    When 系统处理卡死任务
    Then consecutive_failures = 5
    And 任务状态变为 "paused"

  Scenario: 执行开始时锁定
    Given 任务开始执行
    When 调用 _execute_job()
    Then running_since_ms 设置为当前时间

  Scenario: 执行完成时解锁
    Given 任务正在执行
    When 执行完成（成功或失败）
    Then running_since_ms 被清除
```

## 技术方案

### 数据模型扩展

```python
# anyclaw/cron/types.py

@dataclass
class CronJobState:
    next_run_at_ms: Optional[int] = None
    last_run_at_ms: Optional[int] = None
    last_status: Optional[Literal["ok", "error", "skipped"]] = None
    last_error: Optional[str] = None
    # 新增
    consecutive_failures: int = 0
    running_since_ms: Optional[int] = None

@dataclass
class CronRunLog:
    """执行日志记录"""
    id: int
    job_id: str
    run_at_ms: int
    duration_ms: int
    status: Literal["success", "error"]
    result: Optional[str] = None
    error: Optional[str] = None
```

### 退避配置

```python
# anyclaw/cron/service.py

# 退避延迟阶梯 (秒): 30s, 1m, 5m, 15m, 60m
BACKOFF_DELAYS = [30_000, 60_000, 300_000, 900_000, 3_600_000]

# 最大连续失败次数
MAX_CONSECUTIVE_FAILURES = 5

# 卡死检测阈值 (5分钟)
STUCK_THRESHOLD_MS = 5 * 60 * 1000

def calculate_backoff_delay(consecutive_failures: int) -> int:
    """计算退避延迟 (ms)"""
    if consecutive_failures <= 0:
        return 0
    idx = min(consecutive_failures - 1, len(BACKOFF_DELAYS) - 1)
    return BACKOFF_DELAYS[idx]
```

### 日志存储

```python
# anyclaw/cron/logs.py

class CronLogStore:
    """执行日志持久化存储 (JSONL 格式)"""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._lock = asyncio.Lock()
        self._counter = 0

    async def append(self, log: CronRunLog) -> None:
        """追加日志记录"""
        ...

    async def get_logs(self, job_id: str, limit: int = 50) -> list[CronRunLog]:
        """获取任务执行日志"""
        ...

    async def prune_old_logs(self, days: int = 30) -> int:
        """清理过期日志"""
        ...
```

### 执行流程改造

```python
# anyclaw/cron/service.py

class CronService:
    def __init__(self, store_path: Path, log_store: CronLogStore, ...):
        self.log_store = log_store
        ...

    async def _tick(self) -> None:
        # 1. 检测卡死任务
        await self._recover_stuck_tasks()

        # 2. 执行到期任务
        due_jobs = self._get_due_jobs()
        for job in due_jobs:
            # 同步锁定防止并发
            self._lock_job(job)
            # 异步执行
            asyncio.create_task(self._execute_job(job))

    async def _recover_stuck_tasks(self) -> None:
        """检测并恢复卡死任务"""
        now = _now_ms()
        cutoff = now - STUCK_THRESHOLD_MS

        for job in self._store.jobs:
            if job.state.running_since_ms and job.state.running_since_ms < cutoff:
                # 记录日志
                await self.log_store.append(CronRunLog(
                    id=self._next_log_id(),
                    job_id=job.id,
                    run_at_ms=job.state.running_since_ms,
                    duration_ms=now - job.state.running_since_ms,
                    status="error",
                    error=f"Task execution timed out (exceeded {STUCK_THRESHOLD_MS // 1000}s)",
                ))

                # 增加失败计数
                job.state.consecutive_failures += 1
                job.state.running_since_ms = None

                # 检查是否需要暂停
                if job.state.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    job.enabled = False
                    job.state.last_error = f"{job.state.consecutive_failures} consecutive failures, auto-paused"
                else:
                    # 应用退避
                    backoff = calculate_backoff_delay(job.state.consecutive_failures)
                    job.state.next_run_at_ms = now + backoff

    async def _execute_job(self, job: CronJob) -> None:
        start_ms = _now_ms()
        job.state.running_since_ms = start_ms

        try:
            result = await self.on_job(job)
            duration_ms = _now_ms() - start_ms

            # 记录成功日志
            await self.log_store.append(CronRunLog(
                id=self._next_log_id(),
                job_id=job.id,
                run_at_ms=start_ms,
                duration_ms=duration_ms,
                status="success",
                result=result[:500] if result else None,
            ))

            # 重置失败计数
            job.state.consecutive_failures = 0
            job.state.last_status = "ok"
            job.state.last_error = None

        except Exception as e:
            duration_ms = _now_ms() - start_ms

            # 记录失败日志
            await self.log_store.append(CronRunLog(
                id=self._next_log_id(),
                job_id=job.id,
                run_at_ms=start_ms,
                duration_ms=duration_ms,
                status="error",
                error=str(e),
            ))

            # 增加失败计数
            job.state.consecutive_failures += 1

            # 检查是否需要暂停
            if job.state.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                job.enabled = False
                job.state.last_status = "error"
                job.state.last_error = f"{job.state.consecutive_failures} consecutive failures, auto-paused"
            else:
                # 应用退避
                backoff = calculate_backoff_delay(job.state.consecutive_failures)
                job.state.next_run_at_ms = _now_ms() + backoff
                job.state.last_status = "error"
                job.state.last_error = str(e)

        finally:
            job.state.running_since_ms = None
            self._save_store()
```

## 任务分解

### Phase 1: 数据模型 (0.5 天)
- [ ] 扩展 `CronJobState` 添加新字段
- [ ] 创建 `CronRunLog` 数据类
- [ ] 更新 JSON 序列化/反序列化

### Phase 2: 日志存储 (1 天)
- [ ] 创建 `anyclaw/cron/logs.py`
- [ ] 实现 `CronLogStore.append()`
- [ ] 实现 `CronLogStore.get_logs()`
- [ ] 实现 `CronLogStore.prune_old_logs()`
- [ ] 集成到 `CronService`

### Phase 3: 退避机制 (0.5 天)
- [ ] 定义 `BACKOFF_DELAYS` 常量
- [ ] 实现 `calculate_backoff_delay()` 函数
- [ ] 更新 `_execute_job()` 失败处理
- [ ] 更新 `enable_job()` 重置计数

### Phase 4: 卡死检测 (0.5 天)
- [ ] 定义 `STUCK_THRESHOLD_MS` 常量
- [ ] 实现 `_recover_stuck_tasks()` 方法
- [ ] 在 `tick()` 开头调用
- [ ] 执行时设置/清除 `running_since_ms`

### Phase 5: 测试 (1 天)
- [ ] 测试日志写入和查询
- [ ] 测试日志清理
- [ ] 测试退避计算
- [ ] 测试自动暂停
- [ ] 测试成功重置
- [ ] 测试卡死检测
- [ ] 测试卡死恢复

## 验收标准

- [ ] 所有 Gherkin 场景通过
- [ ] 测试覆盖率 ≥ 80%
- [ ] 日志文件格式正确 (JSONL)
- [ ] 退避逻辑正确
- [ ] 卡死检测有效

## 预计工作量

2.5 天

## 依赖

- feat-cron-parser-enhance (VP1)

## 父特性

feat-tasks-alignment
