# feat-cron-api

## 概述

为 Cron 系统提供完整的 REST API，支持任务的 CRUD 操作、手动执行、克隆和日志查询。

## 背景

当前 AnyClaw 的 cron 只能通过 Agent Tool 调用管理，没有独立的 REST API，无法支持前端 UI。

## 用户价值点

### VP5: REST API

提供完整的任务管理 API。

**Gherkin 场景:**

```gherkin
Feature: REST API

  Scenario: 获取任务列表
    When 请求 GET /api/cron/jobs
    Then 返回所有任务列表 (200 OK)
    And 每个任务包含: id, name, enabled, schedule, state, created_at

  Scenario: 获取任务列表 (过滤)
    When 请求 GET /api/cron/jobs?enabled=true
    Then 只返回启用的任务

  Scenario: 创建任务 - interval
    When 请求 POST /api/cron/jobs
    And body 包含 {name, agent_id, chat_id, prompt, schedule: {type: "interval", value_ms: 300000}}
    Then 创建任务并返回 201 Created
    And 返回完整任务对象

  Scenario: 创建任务 - cron
    When 请求 POST /api/cron/jobs
    And body 包含 {name, agent_id, chat_id, prompt, schedule: {type: "cron", expr: "0 9 * * *", tz: "Asia/Shanghai"}}
    Then 创建任务并返回 201 Created
    And next_run_at_ms 已计算

  Scenario: 创建任务 - once
    When 请求 POST /api/cron/jobs
    And body 包含 {name, agent_id, chat_id, prompt, schedule: {type: "once", at_ms: 1735689600000}}
    Then 创建任务并返回 201 Created

  Scenario: 创建任务验证失败
    When 请求 POST /api/cron/jobs
    And body 缺少必填字段
    Then 返回 400 Bad Request
    And 错误信息指出缺失字段

  Scenario: 获取任务详情
    Given 任务存在
    When 请求 GET /api/cron/jobs/:id
    Then 返回任务详情 (200 OK)

  Scenario: 获取不存在的任务
    Given 任务不存在
    When 请求 GET /api/cron/jobs/:id
    Then 返回 404 Not Found

  Scenario: 更新任务
    Given 任务存在
    When 请求 PUT /api/cron/jobs/:id
    And body 包含 {prompt: "new prompt", schedule: {type: "interval", value_ms: 600000}}
    Then 更新任务属性
    And 重新计算 next_run_at_ms
    And 返回更新后的任务

  Scenario: 暂停/恢复任务
    Given 任务存在
    When 请求 PUT /api/cron/jobs/:id
    And body 包含 {enabled: false}
    Then 任务被暂停
    And next_run_at_ms = null

  Scenario: 删除任务
    Given 任务存在
    When 请求 DELETE /api/cron/jobs/:id
    Then 任务被删除 (200 OK)
    And 执行日志也被删除

  Scenario: 克隆任务
    Given 任务存在
    When 请求 POST /api/cron/jobs/:id/clone
    Then 创建新任务，复制原任务配置
    And 新任务 ID 不同
    And 新任务名称添加 "(copy)" 后缀
    And 新任务 enabled = true

  Scenario: 手动执行任务
    Given 任务存在
    When 请求 POST /api/cron/jobs/:id/run
    Then 立即执行任务
    And 返回执行结果
    And 不影响 consecutive_failures

  Scenario: 获取执行日志
    Given 任务有执行历史
    When 请求 GET /api/cron/jobs/:id/logs?limit=20
    Then 返回最近 20 条执行记录
    And 按时间倒序排列

  Scenario: 清理过期日志
    When 请求 POST /api/cron/logs/prune
    And body 包含 {days: 30}
    Then 删除 30 天前的日志
    And 返回删除数量
```

## 技术方案

### API 路由设计

```python
# anyclaw/api/routes/cron.py

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Literal

router = APIRouter(prefix="/api/cron", tags=["cron"])

# ========== Schemas ==========

class ScheduleInput(BaseModel):
    type: Literal["interval", "cron", "once"]
    value_ms: Optional[int] = None  # for interval
    expr: Optional[str] = None      # for cron
    tz: Optional[str] = None        # for cron
    at_ms: Optional[int] = None     # for once

class CreateJobRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    agent_id: str
    chat_id: str
    prompt: str = Field(..., min_length=1)
    schedule: ScheduleInput
    deliver: bool = False
    delivery_channel: Optional[str] = None
    delivery_target: Optional[str] = None

class UpdateJobRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    prompt: Optional[str] = Field(None, min_length=1)
    schedule: Optional[ScheduleInput] = None
    enabled: Optional[bool] = None
    deliver: Optional[bool] = None
    delivery_channel: Optional[str] = None
    delivery_target: Optional[str] = None

class JobResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    agent_id: str
    chat_id: str
    prompt: str
    enabled: bool
    schedule: dict
    state: dict
    created_at_ms: int
    updated_at_ms: int

class RunLogResponse(BaseModel):
    id: int
    job_id: str
    run_at_ms: int
    duration_ms: int
    status: Literal["success", "error"]
    result: Optional[str]
    error: Optional[str]

# ========== Routes ==========

@router.get("/jobs")
async def list_jobs(enabled: Optional[bool] = None) -> list[JobResponse]:
    """列出所有任务"""
    ...

@router.post("/jobs", status_code=201)
async def create_job(req: CreateJobRequest) -> JobResponse:
    """创建任务"""
    ...

@router.get("/jobs/{job_id}")
async def get_job(job_id: str) -> JobResponse:
    """获取任务详情"""
    ...

@router.put("/jobs/{job_id}")
async def update_job(job_id: str, req: UpdateJobRequest) -> JobResponse:
    """更新任务"""
    ...

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str) -> dict:
    """删除任务"""
    ...

@router.post("/jobs/{job_id}/clone", status_code=201)
async def clone_job(job_id: str) -> JobResponse:
    """克隆任务"""
    ...

@router.post("/jobs/{job_id}/run")
async def run_job(job_id: str) -> dict:
    """手动执行任务"""
    ...

@router.get("/jobs/{job_id}/logs")
async def get_job_logs(
    job_id: str,
    limit: int = Query(default=50, le=200)
) -> list[RunLogResponse]:
    """获取执行日志"""
    ...

@router.post("/logs/prune")
async def prune_logs(days: int = 30) -> dict:
    """清理过期日志"""
    ...
```

### 注册路由

```python
# anyclaw/api/server.py

from anyclaw.api.routes.cron import router as cron_router
from anyclaw.cron.service import CronService

def create_app(cron_service: CronService) -> FastAPI:
    app = FastAPI()
    # ... 其他路由
    app.include_router(cron_router)
    return app
```

### 验证逻辑

```python
def validate_schedule(schedule: ScheduleInput) -> None:
    """验证调度配置"""
    if schedule.type == "interval":
        if not schedule.value_ms or schedule.value_ms < 60_000:
            raise HTTPException(400, "interval must be >= 60000ms")

    elif schedule.type == "cron":
        if not schedule.expr:
            raise HTTPException(400, "cron expr is required")
        if not validate_cron_expr(schedule.expr):
            raise HTTPException(400, "Invalid cron expression")

    elif schedule.type == "once":
        if not schedule.at_ms or schedule.at_ms <= int(time.time() * 1000):
            raise HTTPException(400, "once time must be in the future")
```

## 任务分解

### Phase 1: Schema 定义 (0.5 天)
- [ ] 创建 `anyclaw/api/routes/cron.py`
- [ ] 定义 Pydantic 请求/响应模型
- [ ] 定义验证逻辑

### Phase 2: CRUD 端点 (0.5 天)
- [ ] `GET /api/cron/jobs` - 列表
- [ ] `POST /api/cron/jobs` - 创建
- [ ] `GET /api/cron/jobs/:id` - 详情
- [ ] `PUT /api/cron/jobs/:id` - 更新
- [ ] `DELETE /api/cron/jobs/:id` - 删除

### Phase 3: 高级操作 (0.25 天)
- [ ] `POST /api/cron/jobs/:id/clone` - 克隆
- [ ] `POST /api/cron/jobs/:id/run` - 手动执行

### Phase 4: 日志端点 (0.25 天)
- [ ] `GET /api/cron/jobs/:id/logs` - 执行日志
- [ ] `POST /api/cron/logs/prune` - 清理日志

### Phase 5: 集成与测试 (0.5 天)
- [ ] 注册路由到 FastAPI app
- [ ] 传递 CronService 依赖
- [ ] 编写 API 测试

## 验收标准

- [ ] 所有 Gherkin 场景通过
- [ ] API 与 YouClaw 兼容
- [ ] Pydantic 验证正确
- [ ] 错误响应格式统一

## 预计工作量

1.5 天

## 依赖

- feat-cron-resilience (需要日志存储)

## 父特性

feat-tasks-alignment
