# feat-cron-parser-enhance

## 概述

升级 Cron 表达式解析器，从简化版升级为完整支持标准 5 字段 cron 语法。

## 背景

当前 AnyClaw 的 cron 解析 (`anyclaw/cron/service.py`) 只支持简单的 `minute hour * * *` 格式，不支持 `*/5`, `1,15`, `Mon-Fri` 等常见语法。

## 用户价值点

### VP1: 完整 Cron 解析器

支持标准 5 字段 cron 表达式的所有语法。

**Gherkin 场景:**

```gherkin
Feature: 完整 Cron 解析器

  Scenario: 解析标准 cron 表达式
    Given 用户创建定时任务
    When 用户输入 cron 表达式 "0 9 * * *"
    Then 系统正确计算下次运行时间为明天 9:00

  Scenario: 解析间隔表达式
    Given 用户创建定时任务
    When 用户输入 cron 表达式 "*/5 * * * *"
    Then 系统正确计算下次运行时间为当前时间后下一个 5 分钟倍数点

  Scenario: 解析列表表达式
    Given 用户创建定时任务
    When 用户输入 cron 表达式 "0 9,12,18 * * *"
    Then 系统识别每天 9:00、12:00、18:00 执行

  Scenario: 解析范围表达式
    Given 用户创建定时任务
    When 用户输入 cron 表达式 "0 9-17 * * 1-5"
    Then 系统识别工作日 9:00-17:00 每小时执行

  Scenario: 无效 cron 表达式拒绝
    Given 用户创建定时任务
    When 用户输入无效的 cron 表达式 "invalid"
    Then 系统返回验证错误 "Invalid cron expression"

  Scenario: 时区支持
    Given 用户创建定时任务
    When 用户指定 timezone "Asia/Shanghai" 和 cron "0 9 * * *"
    Then 系统按上海时区计算下次运行时间
    And 返回 UTC 时间戳

  Scenario: 获取下次多个执行时间
    Given 有效的 cron 表达式 "0 9 * * *"
    When 请求获取接下来 5 次执行时间
    Then 返回 5 个递增的 ISO 时间戳
```

## 技术方案

### 依赖库

```toml
# pyproject.toml
croniter = "^3.0.0"
```

### 新增模块

```python
# anyclaw/cron/parser.py

from croniter import croniter
from typing import Optional, List
from datetime import datetime, timezone

class CronParser:
    """完整 cron 表达式解析器"""

    def __init__(self, expr: str, tz: Optional[str] = None):
        self.expr = expr
        self.tz = tz
        self._cron: Optional[croniter] = None

    @staticmethod
    def validate(expr: str) -> bool:
        """验证 cron 表达式有效性"""
        try:
            croniter(expr)
            return True
        except:
            return False

    def get_next(self, base: Optional[datetime] = None) -> Optional[datetime]:
        """获取下次执行时间"""
        ...

    def get_next_n(self, n: int, base: Optional[datetime] = None) -> List[datetime]:
        """获取接下来 N 次执行时间"""
        ...
```

### 修改文件

1. **anyclaw/cron/service.py**
   - 替换 `_compute_next_run()` 函数，使用 `CronParser`
   - 添加 `validate_cron_expr()` 辅助函数

2. **anyclaw/cron/tool.py**
   - `add_job` 时调用 `validate_cron_expr()` 验证

### 接口保持不变

现有 `CronSchedule` 数据结构保持兼容：

```python
@dataclass
class CronSchedule:
    kind: Literal["at", "every", "cron"]
    at_ms: Optional[int] = None      # for "at"
    every_ms: Optional[int] = None   # for "every"
    expr: Optional[str] = None       # for "cron" - 现在支持完整语法
    tz: Optional[str] = None         # IANA timezone
```

## 任务分解

- [ ] 添加 `croniter>=3.0.0` 依赖
- [ ] 创建 `anyclaw/cron/parser.py`
- [ ] 实现 `CronParser.validate()`
- [ ] 实现 `CronParser.get_next()`
- [ ] 实现 `CronParser.get_next_n()`
- [ ] 更新 `_compute_next_run()` 使用 CronParser
- [ ] 添加 `validate_cron_expr()` 函数
- [ ] 更新 CronTool 添加验证
- [ ] 编写单元测试

## 验收标准

- [ ] 所有 Gherkin 场景通过
- [ ] 测试覆盖率 ≥ 90%
- [ ] 现有 cron 任务数据兼容
- [ ] 无破坏性变更

## 预计工作量

0.5 天

## 依赖

无

## 父特性

feat-tasks-alignment
