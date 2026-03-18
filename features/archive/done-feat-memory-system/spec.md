# feat-memory-system: 记忆系统

## 概述

为 AnyClaw 创建智能体记忆系统，包含长期记忆（MEMORY.md）和每日记忆日志（memory/YYYY-MM-DD.md）。记忆系统允许智能体跨会话保留重要信息，持续学习用户偏好和项目上下文。

## 依赖

- `feat-mvp-agent` (已完成) - Agent 引擎核心
- `feat-workspace-init` (pending) - Workspace 初始化
- `feat-agent-persona` (pending) - 智能体人设系统

## 用户价值点

### VP1: 长期记忆

**价值**: 存储跨会话持久化的重要信息，如用户偏好、项目上下文和关键决策。

**Gherkin 场景**:

```gherkin
Feature: 长期记忆

  Scenario: 加载长期记忆
    Given 工作区包含 MEMORY.md
    And 是私密会话
    When 会话开始
    Then 应加载 MEMORY.md 内容
    And 智能体应记住存储的信息

  Scenario: 更新长期记忆
    Given 智能体了解到重要信息
    When 信息需要长期保留
    Then 应更新 MEMORY.md
    And 更新应持久化

  Scenario: 私密会话隔离
    Given 是群组会话
    When 会话开始
    Then 不应加载 MEMORY.md
    And 长期记忆保持私密

  Scenario: 记忆大小限制
    Given MEMORY.md 超过大小限制
    When 加载到上下文
    Then 应截断或压缩
    And 保留关键信息

  Scenario: 手动记忆管理
    Given 用户想管理记忆
    When 运行 "anyclaw memory edit"
    Then 应打开编辑器
    And 用户可编辑 MEMORY.md
```

### VP2: 每日记忆日志

**价值**: 按日期记录每日会话的关键信息，方便回顾和检索。

**Gherkin 场景**:

```gherkin
Feature: 每日记忆日志

  Scenario: 创建今日日志
    Given 今日没有日志文件
    When 会话开始
    Then 应创建 memory/YYYY-MM-DD.md
    And 包含日期标题

  Scenario: 写入日志
    Given 会话中有重要事件
    When 需要记录
    Then 应追加到今日日志
    And 包含时间戳和摘要

  Scenario: 加载最近日志
    Given 会话开始
    When 加载记忆
    Then 应加载今天和昨天的日志
    And 提供上下文连续性

  Scenario: 搜索日志
    Given 用户想查找历史记录
    When 运行 "anyclaw memory search <keyword>"
    Then 应搜索所有日志文件
    And 显示匹配结果

  Scenario: 日志导出
    Given 用户想导出日志
    When 运行 "anyclaw memory export"
    Then 应生成包含所有日志的文件
    And 支持 Markdown/JSON 格式
```

### VP3: 记忆自动化

**价值**: 智能体自动识别需要记忆的信息并更新记忆文件。

**Gherkin 场景**:

```gherkin
Feature: 记忆自动化

  Scenario: 自动识别重要信息
    Given 会话中提到用户偏好
    When 智能体识别到重要信息
    Then 应建议添加到记忆
    And 用户确认后更新

  Scenario: 定期记忆刷新
    Given 长时间会话
    When 积累足够新信息
    Then 应更新长期记忆
    And 更新今日日志

  Scenario: 记忆冲突处理
    Given 新信息与旧记忆冲突
    When 智能体检测到冲突
    Then 应询问用户确认
    And 更新或保留旧记忆

  Scenario: 记忆清理
    Given 记忆文件过大
    When 用户请求清理
    Then 应识别过时信息
    And 建议删除
```

## 技术设计

### 核心组件

```
anyclaw/
├── memory/
│   ├── __init__.py
│   ├── manager.py       # MemoryManager 类
│   ├── long_term.py     # 长期记忆
│   ├── daily.py         # 每日日志
│   └── templates.py     # 记忆模板
└── cli/
    └── memory.py        # memory 命令
```

### 目录结构

```
~/.anyclaw/workspace/
├── MEMORY.md               # 长期记忆（精选）
└── memory/                 # 每日日志目录
    ├── 2026-03-18.md
    ├── 2026-03-17.md
    └── ...
```

### MemoryManager 设计

```python
# memory/manager.py
from pathlib import Path
from datetime import datetime, date
from typing import Optional
import re

class MemoryManager:
    """记忆管理器"""

    LONG_TERM_FILE = "MEMORY.md"
    DAILY_DIR = "memory"

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.memory_dir = workspace_path / self.DAILY_DIR

    def load_long_term(self) -> Optional[str]:
        """加载长期记忆"""
        filepath = self.workspace_path / self.LONG_TERM_FILE
        if filepath.exists():
            return filepath.read_text()
        return None

    def save_long_term(self, content: str) -> None:
        """保存长期记忆"""
        filepath = self.workspace_path / self.LONG_TERM_FILE
        filepath.write_text(content)

    def update_long_term(self, section: str, content: str) -> None:
        """更新长期记忆的特定部分"""
        current = self.load_long_term() or self._get_default_long_term()
        # 更新特定部分
        updated = self._update_section(current, section, content)
        self.save_long_term(updated)

    def get_today_log_path(self) -> Path:
        """获取今日日志路径"""
        today = date.today().isoformat()
        return self.memory_dir / f"{today}.md"

    def load_daily(self, days: int = 2) -> list[dict]:
        """加载最近 N 天的日志"""
        logs = []
        for i in range(days):
            log_date = date.today() - __import__('datetime').timedelta(days=i)
            log_path = self.memory_dir / f"{log_date.isoformat()}.md"
            if log_path.exists():
                logs.append({
                    "date": log_date.isoformat(),
                    "content": log_path.read_text(),
                })
        return logs

    def append_to_today(self, entry: str) -> None:
        """追加到今日日志"""
        self.memory_dir.mkdir(exist_ok=True)
        log_path = self.get_today_log_path()

        if not log_path.exists():
            log_path.write_text(self._get_daily_header())

        with open(log_path, "a") as f:
            timestamp = datetime.now().strftime("%H:%M")
            f.write(f"\n### {timestamp}\n\n{entry}\n")

    def search(self, keyword: str) -> list[dict]:
        """搜索所有日志"""
        results = []
        pattern = re.compile(keyword, re.IGNORECASE)

        # 搜索长期记忆
        long_term = self.load_long_term()
        if long_term and pattern.search(long_term):
            results.append({
                "source": "MEMORY.md",
                "matches": self._extract_matches(long_term, pattern),
            })

        # 搜索每日日志
        for log_file in sorted(self.memory_dir.glob("*.md"), reverse=True):
            content = log_file.read_text()
            if pattern.search(content):
                results.append({
                    "source": log_file.stem,
                    "matches": self._extract_matches(content, pattern),
                })

        return results

    def export(self, format: str = "markdown") -> str:
        """导出所有记忆"""
        if format == "markdown":
            return self._export_markdown()
        elif format == "json":
            return self._export_json()
        raise ValueError(f"Unsupported format: {format}")

    def _get_default_long_term(self) -> str:
        return """# 长期记忆

此文件存储跨会话持久化的重要信息。

## 用户信息

（关于用户的重要信息）

## 偏好

（用户偏好学习）

## 项目上下文

（正在进行的项目的相关信息）

## 重要笔记

（需要记住的事情）

---

*此文件由 AnyClaw 自动更新，当有重要信息时应被记住。*
"""

    def _get_daily_header(self) -> str:
        today = date.today()
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][today.weekday()]
        return f"# {today.isoformat()} ({weekday})\n\n"
```

### 记忆自动化

```python
# memory/automation.py
from typing import Optional
import re

class MemoryAutomation:
    """记忆自动化处理"""

    # 重要信息模式
    IMPORTANT_PATTERNS = [
        r"我喜欢(.+)",
        r"我讨厌(.+)",
        r"我偏好(.+)",
        r"记住(.+)",
        r"别忘了(.+)",
        r"我的(.+)是(.+)",
    ]

    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager

    def analyze_message(self, message: str) -> Optional[dict]:
        """分析消息是否包含重要信息"""
        for pattern in self.IMPORTANT_PATTERNS:
            match = re.search(pattern, message)
            if match:
                return {
                    "type": "preference",
                    "content": match.group(0),
                    "should_remember": True,
                }
        return None

    def should_update_memory(self, context: dict) -> bool:
        """判断是否应该更新记忆"""
        # 检查是否有足够的新信息
        # 检查是否有冲突
        # 检查用户确认
        return False  # 默认不自动更新，需要用户确认

    def suggest_memory_update(self, info: dict) -> str:
        """生成记忆更新建议"""
        return f"我注意到你说：{info['content']}。要我把这添加到长期记忆吗？"
```

### CLI 命令

```bash
# 记忆管理
anyclaw memory show                    # 显示长期记忆
anyclaw memory edit                    # 编辑长期记忆
anyclaw memory today                   # 显示今日日志
anyclaw memory log                     # 追加到今日日志
anyclaw memory search <keyword>        # 搜索记忆
anyclaw memory export [--format json]  # 导出记忆
anyclaw memory clean                   # 清理过时记忆
```

### AgentLoop 集成

```python
# agent/loop.py (修改)
from memory.manager import MemoryManager

class AgentLoop:
    def __init__(self, ...):
        self.memory_manager = MemoryManager(workspace_path)

    async def _build_context(self, user_input: str) -> list:
        """构建对话上下文"""
        messages = []

        # 加载人设
        system_prompt = self.persona_loader.build_system_prompt(
            is_private=self._is_private_session()
        )

        # 加载记忆（仅私密会话）
        if self._is_private_session():
            memory_context = self._build_memory_context()
            if memory_context:
                system_prompt += f"\n\n## 记忆\n\n{memory_context}"

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # ... 其他上下文

        return messages

    def _build_memory_context(self) -> str:
        """构建记忆上下文"""
        parts = []

        # 加载长期记忆
        long_term = self.memory_manager.load_long_term()
        if long_term:
            parts.append(f"### 长期记忆\n{long_term}")

        # 加载最近日志
        daily_logs = self.memory_manager.load_daily(days=2)
        for log in daily_logs:
            parts.append(f"### {log['date']}\n{log['content']}")

        return "\n\n".join(parts)
```

## 配置扩展

```python
# config/settings.py 新增
class Settings(BaseSettings):
    # 记忆配置
    memory_enabled: bool = Field(default=True)
    memory_max_chars: int = Field(default=10000)
    memory_daily_load_days: int = Field(default=2)  # 加载最近几天日志
    memory_auto_update: bool = Field(default=False)  # 自动更新记忆
```

## 验收标准

- [ ] 长期记忆正确加载和保存
- [ ] 每日日志正确创建和追加
- [ ] 搜索功能正常
- [ ] 导出功能正常
- [ ] 仅私密会话加载记忆
- [ ] CLI 命令正常工作
- [ ] 测试覆盖率 > 80%

## 优先级

| 功能 | 优先级 | 理由 |
|------|--------|------|
| 长期记忆 | P0 | 核心能力 |
| 每日日志 | P0 | 上下文连续性 |
| 搜索 | P1 | 高级功能 |
| 自动化 | P2 | 优化体验 |

## 参考

- OpenClaw `docs/zh-CN/concepts/agent-workspace.md` (memory section)
- Nanobot `nanobot/templates/memory/MEMORY.md`
