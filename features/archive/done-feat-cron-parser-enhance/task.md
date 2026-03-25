# feat-cron-parser-enhance 任务分解

## 任务列表

### 1. 添加依赖
- [ ] 在 `pyproject.toml` 添加 `croniter = "^3.0.0"`
- [ ] 运行 `poetry lock && poetry install`

### 2. 创建解析器模块
- [ ] 创建 `anyclaw/cron/parser.py`
- [ ] 实现 `CronParser` 类初始化
- [ ] 实现 `validate()` 静态方法
- [ ] 实现 `get_next()` 方法
- [ ] 实现 `get_next_n()` 方法
- [ ] 处理时区转换逻辑

### 3. 集成到 CronService
- [ ] 导入 `CronParser` 和 `validate_cron_expr`
- [ ] 重写 `_compute_next_run()` 函数
- [ ] 添加 `validate_cron_expr()` 辅助函数

### 4. 更新 CronTool
- [ ] 在 `_add_job()` 中添加 cron 表达式验证
- [ ] 返回友好的错误提示

### 5. 测试
- [ ] 创建 `tests/test_cron_parser.py`
- [ ] 测试: 标准表达式 (0 9 * * *)
- [ ] 测试: 间隔表达式 (*/5 * * * *)
- [ ] 测试: 列表表达式 (0 9,12,18 * * *)
- [ ] 测试: 范围表达式 (0 9-17 * * 1-5)
- [ ] 测试: 无效表达式拒绝
- [ ] 测试: 时区支持
- [ ] 测试: get_next_n 返回多个时间

## 文件变更

```
anyclaw/
├── pyproject.toml          # +1 依赖
├── anyclaw/cron/
│   ├── parser.py           # 新增
│   ├── service.py          # 修改 _compute_next_run
│   └── tool.py             # 添加验证
└── tests/
    └── test_cron_parser.py # 新增
```
