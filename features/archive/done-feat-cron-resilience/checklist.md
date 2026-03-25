# feat-cron-resilience 检查清单

## Phase 1: 数据模型

- [x] CronJobState.consecutive_failures 字段
- [x] CronJobState.running_since_ms 字段
- [x] CronRunLog dataclass 创建
- [x] JSON 序列化/反序列化更新
- [x] 数据模型测试通过

## Phase 2: 日志存储

- [x] CronLogStore 类创建
- [x] append() 方法实现
- [x] get_logs() 方法实现
- [x] prune_old_logs() 方法实现
- [x] JSONL 文件格式正确
- [x] 并发写入安全
- [x] 集成到 CronService
- [x] 成功执行记录日志
- [x] 失败执行记录日志
- [x] 日志测试通过

## Phase 3: 退避机制

- [x] BACKOFF_DELAYS 常量定义
- [x] MAX_CONSECUTIVE_FAILURES 常量定义
- [x] calculate_backoff_delay() 函数
- [x] 失败时增加计数
- [x] 失败时应用退避
- [x] 达到阈值自动暂停
- [x] 成功时重置计数
- [x] enable_job() 时重置计数
- [x] 退避测试通过

## Phase 4: 卡死检测

- [x] STUCK_THRESHOLD_MS 常量定义
- [x] _recover_stuck_tasks() 方法
- [x] tick() 开头调用检测
- [x] 执行开始设置 running_since_ms
- [x] 执行完成清除 running_since_ms
- [x] 卡死时记录日志
- [x] 卡死时应用退避
- [x] 卡死测试通过

## 代码质量

- [x] 所有新代码有类型注解
- [x] 测试覆盖率 ≥ 80%
- [x] 无 Ruff 检查错误
- [x] 无类型检查错误

## 集成测试

- [x] 完整执行流程测试
- [x] 多任务并发测试
- [x] 重启后状态恢复测试
