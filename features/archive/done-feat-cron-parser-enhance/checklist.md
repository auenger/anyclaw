# feat-cron-parser-enhance 检查清单

## 依赖
- [x] 添加 croniter 依赖到 pyproject.toml
- [x] poetry install 成功

## 解析器实现
- [x] CronParser 类创建
- [x] validate() 静态方法
- [x] get_next() 方法
- [x] get_next_n() 方法
- [x] 时区处理正确

## 集成
- [x] _compute_next_run() 使用 CronParser
- [x] validate_cron_expr() 函数
- [x] CronTool 添加验证

## 测试
- [x] 标准表达式解析测试
- [x] 间隔表达式解析测试
- [x] 列表表达式解析测试
- [x] 范围表达式解析测试
- [x] 无效表达式拒绝测试
- [x] 时区支持测试
- [x] 多次执行时间测试

## 质量
- [x] 测试覆盖率 ≥ 90%
- [x] 无 Ruff 错误
- [x] 无类型检查错误
- [x] 现有测试全部通过
