# feat-cron-resilience 任务分解

## Phase 1: 数据模型扩展

### 1.1 更新 types.py
- [ ] 添加 `CronJobState.consecutive_failures: int = 0`
- [ ] 添加 `CronJobState.running_since_ms: Optional[int] = None`
- [ ] 创建 `CronRunLog` dataclass
- [ ] 更新 `CronJob` 的 JSON 序列化

### 1.2 测试
- [ ] 测试数据模型序列化/反序列化

---

## Phase 2: 日志存储

### 2.1 创建 logs.py
- [ ] 创建 `anyclaw/cron/logs.py`
- [ ] 实现 `CronLogStore.__init__(log_path)`
- [ ] 实现 `_next_id()` 自增 ID 生成
- [ ] 实现 `append(log: CronRunLog)` 异步追加
- [ ] 实现 `get_logs(job_id, limit)` 查询
- [ ] 实现 `prune_old_logs(days)` 清理

### 2.2 存储格式
- [ ] 使用 JSONL 格式 (每行一个 JSON)
- [ ] 文件路径: `{store_dir}/cron_logs.jsonl`
- [ ] 按时间戳顺序追加

### 2.3 集成到 CronService
- [ ] 构造函数添加 `log_store: CronLogStore` 参数
- [ ] 在 `_execute_job()` 成功时记录日志
- [ ] 在 `_execute_job()` 失败时记录日志

### 2.4 测试
- [ ] 测试日志写入
- [ ] 测试日志查询 (按 job_id)
- [ ] 测试日志清理 (按天数)
- [ ] 测试并发写入安全

---

## Phase 3: 退避机制

### 3.1 定义常量
- [ ] `BACKOFF_DELAYS = [30_000, 60_000, 300_000, 900_000, 3_600_000]`
- [ ] `MAX_CONSECUTIVE_FAILURES = 5`

### 3.2 实现退避函数
- [ ] 实现 `calculate_backoff_delay(failures: int) -> int`
- [ ] failures=0 返回 0
- [ ] failures=1-5 返回对应延迟
- [ ] failures>5 返回最大延迟

### 3.3 更新执行逻辑
- [ ] 失败时 `consecutive_failures += 1`
- [ ] 失败时计算 `next_run_at_ms = now + backoff`
- [ ] 达到阈值时 `enabled = False`
- [ ] 成功时 `consecutive_failures = 0`

### 3.4 更新恢复逻辑
- [ ] `enable_job()` 时重置 `consecutive_failures = 0`
- [ ] 重新计算 `next_run_at_ms`

### 3.5 测试
- [ ] 测试退避延迟计算
- [ ] 测试连续失败升级
- [ ] 测试达到阈值自动暂停
- [ ] 测试成功后重置
- [ ] 测试恢复时重置

---

## Phase 4: 卡死检测

### 4.1 定义常量
- [ ] `STUCK_THRESHOLD_MS = 5 * 60 * 1000`

### 4.2 实现检测方法
- [ ] 实现 `_recover_stuck_tasks()` 方法
- [ ] 遍历所有任务
- [ ] 检查 `running_since_ms < now - STUCK_THRESHOLD`
- [ ] 记录超时错误日志
- [ ] 增加 `consecutive_failures`
- [ ] 清除 `running_since_ms`
- [ ] 应用退避策略

### 4.3 更新 tick 逻辑
- [ ] 在 `_tick()` 开头调用 `_recover_stuck_tasks()`
- [ ] 在执行任务前设置 `running_since_ms`
- [ ] 在执行完成后清除 `running_since_ms`

### 4.4 测试
- [ ] 测试卡死检测
- [ ] 测试卡死恢复
- [ ] 测试卡死达到暂停阈值
- [ ] 测试正常执行不触发卡死

---

## 文件变更

```
anyclaw/
├── anyclaw/cron/
│   ├── types.py          # 扩展 CronJobState, 添加 CronRunLog
│   ├── logs.py           # 新增: CronLogStore
│   └── service.py        # 添加退避、卡死、日志记录
└── tests/
    ├── test_cron_logs.py        # 新增
    ├── test_cron_backoff.py     # 新增
    └── test_cron_stuck.py       # 新增
```

---

## 工作量估计

| Phase | 工作量 |
|-------|--------|
| Phase 1: 数据模型 | 0.5 天 |
| Phase 2: 日志存储 | 1 天 |
| Phase 3: 退避机制 | 0.5 天 |
| Phase 4: 卡死检测 | 0.5 天 |
| **总计** | **2.5 天** |
