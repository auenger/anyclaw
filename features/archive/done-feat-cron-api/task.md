# feat-cron-api 任务分解

## Phase 1: Schema 定义

### 1.1 创建路由文件
- [ ] 创建 `anyclaw/api/routes/cron.py`
- [ ] 导入必要的 FastAPI 和 Pydantic 组件

### 1.2 定义请求模型
- [ ] `ScheduleInput` - 调度配置输入
- [ ] `CreateJobRequest` - 创建任务请求
- [ ] `UpdateJobRequest` - 更新任务请求

### 1.3 定义响应模型
- [ ] `JobResponse` - 任务响应
- [ ] `RunLogResponse` - 执行日志响应
- [ ] `PruneResponse` - 清理响应

### 1.4 验证逻辑
- [ ] `validate_schedule()` 函数
- [ ] interval >= 60000ms
- [ ] cron expr 有效
- [ ] once time 在未来

---

## Phase 2: CRUD 端点

### 2.1 列出任务
- [ ] `GET /api/cron/jobs`
- [ ] 支持 `enabled` 过滤参数
- [ ] 调用 `cron_service.list_jobs()`

### 2.2 创建任务
- [ ] `POST /api/cron/jobs`
- [ ] 验证请求体
- [ ] 验证 schedule
- [ ] 调用 `cron_service.add_job()`
- [ ] 返回 201 Created

### 2.3 获取详情
- [ ] `GET /api/cron/jobs/{job_id}`
- [ ] 调用 `cron_service.get_job()`
- [ ] 404 处理

### 2.4 更新任务
- [ ] `PUT /api/cron/jobs/{job_id}`
- [ ] 部分更新支持
- [ ] 重新计算 next_run
- [ ] enabled=false 时清除 next_run

### 2.5 删除任务
- [ ] `DELETE /api/cron/jobs/{job_id}`
- [ ] 调用 `cron_service.remove_job()`
- [ ] 同时删除执行日志

---

## Phase 3: 高级操作

### 3.1 克隆任务
- [ ] `POST /api/cron/jobs/{job_id}/clone`
- [ ] 复制原任务配置
- [ ] 生成新 ID
- [ ] 名称添加 "(copy)" 后缀
- [ ] enabled = true
- [ ] consecutive_failures = 0

### 3.2 手动执行
- [ ] `POST /api/cron/jobs/{job_id}/run`
- [ ] 调用 `cron_service.run_job()`
- [ ] 不影响 consecutive_failures
- [ ] 返回执行结果

---

## Phase 4: 日志端点

### 4.1 执行日志
- [ ] `GET /api/cron/jobs/{job_id}/logs`
- [ ] 支持 `limit` 参数 (默认 50, 最大 200)
- [ ] 调用 `log_store.get_logs()`

### 4.2 清理日志
- [ ] `POST /api/cron/logs/prune`
- [ ] 支持 `days` 参数 (默认 30)
- [ ] 调用 `log_store.prune_old_logs()`
- [ ] 返回删除数量

---

## Phase 5: 集成与测试

### 5.1 注册路由
- [ ] 在 `server.py` 导入 cron router
- [ ] 传递 CronService 依赖
- [ ] 使用 dependency injection

### 5.2 API 测试
- [ ] 创建 `tests/test_api_cron.py`
- [ ] 测试所有 CRUD 端点
- [ ] 测试验证逻辑
- [ ] 测试错误响应

---

## 文件变更

```
anyclaw/
├── anyclaw/api/
│   ├── routes/
│   │   └── cron.py        # 新增
│   └── server.py          # 注册路由
└── tests/
    └── test_api_cron.py   # 新增
```

---

## 工作量估计

| Phase | 工作量 |
|-------|--------|
| Phase 1: Schema | 0.5 天 |
| Phase 2: CRUD | 0.5 天 |
| Phase 3: 高级操作 | 0.25 天 |
| Phase 4: 日志端点 | 0.25 天 |
| Phase 5: 集成测试 | 0.5 天 |
| **总计** | **2 天** |
