# feat-cron-api 检查清单

## Schema 定义

- [x] ScheduleInput 模型
- [x] CreateJobRequest 模型
- [x] UpdateJobRequest 模型
- [x] JobResponse 模型
- [x] RunLogResponse 模型
- [x] validate_schedule() 函数

## CRUD 端点

- [x] GET /api/cron/jobs - 列表
- [x] GET /api/cron/jobs?enabled=true - 过滤
- [x] POST /api/cron/jobs - 创建
- [x] GET /api/cron/jobs/:id - 详情
- [x] PUT /api/cron/jobs/:id - 更新
- [x] DELETE /api/cron/jobs/:id - 删除

## 高级操作

- [x] POST /api/cron/jobs/:id/clone - 克隆
- [x] POST /api/cron/jobs/:id/run - 手动执行

## 日志端点

- [x] GET /api/cron/jobs/:id/logs - 执行日志
- [x] POST /api/cron/logs/prune - 清理日志

## 验证

- [x] interval >= 60000ms
- [x] cron expr 有效性
- [x] once time 在未来
- [x] 必填字段验证

## 错误处理

- [x] 400 Bad Request - 验证失败
- [x] 404 Not Found - 任务不存在
- [x] 统一错误格式

## 集成

- [x] 注册路由到 FastAPI
- [x] CronService 依赖注入
- [x] API 文档生成

## 测试

- [x] 测试所有 CRUD 操作
- [x] 测试验证逻辑
- [x] 测试错误响应
- [x] 测试过滤参数
