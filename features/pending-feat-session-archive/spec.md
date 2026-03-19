# 会话归档系统

## 背景

AnyClaw 当前使用纯内存的 `deque` 存储对话历史，存在以下问题：
- 会话结束后历史丢失
- 无法追溯历史对话
- 缺少 tool/skill 调用记录
- 无法按日期/项目查询历史
- 多 Channel 对话混在一起

## 需求

实现完整的会话归档系统，支持：
- 持久化存储对话记录
- 按项目隔离（Git root 或 cwd）
- 按日期归档
- 记录完整的 tool/skill 调用链
- 支持会话搜索和恢复

## 用户价值点

### VP1: 会话持久化存储

自动保存所有对话记录到本地文件，支持追加写入。

**Gherkin 场景**:

```gherkin
Feature: 会话持久化存储

  Scenario: 自动保存用户消息
    Given 用户发送消息 "帮我分析代码"
    When 消息被处理
    Then 消息自动追加到会话文件

  Scenario: 自动保存助手响应
    Given 助手响应 "我来分析..."
    When 响应完成
    Then 响应自动追加到会话文件

  Scenario: JSONL 格式存储
    Given 会话文件存在
    When 查看文件内容
    Then 每行是一个完整的 JSON 对象
    And 包含 type, uuid, timestamp 字段

  Scenario: 会话元信息
    Given 新会话开始
    When 创建会话文件
    Then 第一条记录是 session_start 类型
    And 包含 sessionId, projectId, cwd, gitBranch 等信息
```

### VP2: 项目隔离

按项目隔离会话存储，不同项目的对话互不干扰。

**Gherkin 场景**:

```gherkin
Feature: 项目隔离

  Scenario: Git 仓库项目隔离
    Given 在 /Users/ryan/mycode/AnyClaw 目录（Git 仓库）启动
    When 保存会话
    Then 存储路径为 ~/.anyclaw/sessions/cli/-Users-ryan-mycode-AnyClaw/

  Scenario: 子目录归属同一项目
    Given 在 /Users/ryan/mycode/AnyClaw/anyclaw 子目录启动
    When 保存会话
    Then 仍存储到 ~/.anyclaw/sessions/cli/-Users-ryan-mycode-AnyClaw/
    And 与根目录启动的会话在同一目录

  Scenario: 非 Git 项目使用 cwd
    Given 在 /tmp/test 目录（非 Git）启动
    When 保存会话
    Then 存储路径为 ~/.anyclaw/sessions/cli/-tmp-test/

  Scenario: Channel 隔离
    Given 从飞书 Channel chat_123 发起对话
    When 保存会话
    Then 存储路径为 ~/.anyclaw/sessions/channels/feishu/chat_123/

  Scenario: 项目元信息记录
    Given 首次在项目目录保存会话
    When 创建项目目录
    Then 生成 project.json 记录项目信息
    And 包含 name, path, git_url, created_at 等字段
```

### VP3: 按日期归档

每天一个目录，方便按时间查找和管理存储。

**Gherkin 场景**:

```gherkin
Feature: 按日期归档

  Scenario: 日期目录结构
    Given 当前日期为 2026-03-19
    When 保存会话
    Then 存储路径包含 /2026-03-19/

  Scenario: 跨日会话
    Given 会话开始于 2026-03-19 23:50
    And 持续到 2026-03-20 00:10
    When 保存消息
    Then 2026-03-19 的消息存到 2026-03-19 目录
    And 2026-03-20 的消息存到 2026-03-20 目录

  Scenario: 日期索引文件
    Given 某日期目录有会话文件
    When 查看目录
    Then 存在 index.json 索引文件
    And 包含该日期所有会话的摘要

  Scenario: 自动清理旧会话
    Given 配置 retention_days = 30
    And 存在 60 天前的会话
    When 执行清理
    Then 60 天前的会话被归档或删除
```

### VP4: Tool/Skill 调用记录

完整记录工具和技能的调用链。

**Gherkin 场景**:

```gherkin
Feature: Tool/Skill 调用记录

  Scenario: 记录 Tool 调用
    Given 助手调用 read_file 工具
    When 工具执行
    Then 记录 tool_call 类型：{name: "read_file", input: {...}}
    And 记录 tool_result 类型：{output: "...", duration_ms: 150}

  Scenario: 记录 Skill 调用
    Given 助手调用 /commit 技能
    When 技能执行
    Then 记录 skill_call 类型：{skill: "commit", args: "..."}
    And 记录 skill_result 类型：{output: "...", success: true}

  Scenario: 调用链追踪
    Given 消息 A 触发工具调用 B
    And 工具调用 B 触发技能调用 C
    When 查看记录
    Then 可通过 parentUuid 追溯完整调用链

  Scenario: 记录错误信息
    Given 工具执行失败
    When 记录结果
    Then 记录 error 类型：{message: "...", traceback: "..."}
```

### VP5: 会话查询

支持多维度查询历史会话。

**Gherkin 场景**:

```gherkin
Feature: 会话查询

  Scenario: 按日期查询
    Given 执行 "anyclaw session list --date 2026-03-19"
    When 查询执行
    Then 返回该日期所有会话列表

  Scenario: 按关键词搜索
    Given 执行 "anyclaw session search 'MCP 集成'"
    When 搜索执行
    Then 返回包含该关键词的会话片段
    And 高亮显示匹配位置

  Scenario: 按工具过滤
    Given 执行 "anyclaw session list --tool read_file"
    When 查询执行
    Then 返回使用了 read_file 工具的会话

  Scenario: 查看会话详情
    Given 执行 "anyclaw session show {session-id}"
    When 命令执行
    Then 显示完整会话内容
    And 包含消息树结构
```

## 技术方案

### 1. 目录结构

```
~/.anyclaw/sessions/
├── cli/
│   ├── -Users-ryan-mycode-AnyClaw/        # Git 项目
│   │   ├── project.json                   # 项目元信息
│   │   ├── 2026-03-19/
│   │   │   ├── {session-uuid}.jsonl       # 会话文件
│   │   │   └── index.json                 # 日期索引
│   │   └── 2026-03-18/
│   └── -tmp-test/                         # 非 Git 项目
│       └── ...
├── channels/
│   ├── feishu/
│   │   └── {chat-id}/
│   │       └── 2026-03-19/
│   └── discord/
│       └── {channel-id}/
│           └── ...
└── index.db                               # SQLite 索引（可选）
```

### 2. 记录类型定义

```python
# anyclaw/session/records.py

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Optional
import uuid

@dataclass
class SessionRecord:
    """会话记录基类"""
    type: str
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_json(self) -> str:
        import json
        return json.dumps(asdict(self), ensure_ascii=False)

@dataclass
class SessionStart(SessionRecord):
    """会话开始"""
    type: str = "session_start"
    session_id: str = ""
    project_id: str = ""
    cwd: str = ""
    git_branch: Optional[str] = None
    version: str = ""
    channel: str = "cli"  # cli, feishu, discord

@dataclass
class SessionEnd(SessionRecord):
    """会话结束"""
    type: str = "session_end"
    session_id: str = ""
    message_count: int = 0
    tool_call_count: int = 0
    duration_seconds: float = 0

@dataclass
class UserMessage(SessionRecord):
    """用户消息"""
    type: str = "user_message"
    parent_uuid: Optional[str] = None
    content: str = ""

@dataclass
class AssistantMessage(SessionRecord):
    """助手消息"""
    type: str = "assistant_message"
    parent_uuid: Optional[str] = None
    content: str = ""
    model: Optional[str] = None
    stop_reason: Optional[str] = None

@dataclass
class ToolCall(SessionRecord):
    """工具调用"""
    type: str = "tool_call"
    parent_uuid: Optional[str] = None
    tool_call_id: str = ""
    tool_name: str = ""
    tool_input: dict = field(default_factory=dict)

@dataclass
class ToolResult(SessionRecord):
    """工具结果"""
    type: str = "tool_result"
    tool_call_id: str = ""
    output: str = ""
    duration_ms: int = 0
    success: bool = True

@dataclass
class SkillCall(SessionRecord):
    """技能调用"""
    type: str = "skill_call"
    parent_uuid: Optional[str] = None
    skill_call_id: str = ""
    skill_name: str = ""
    skill_args: str = ""

@dataclass
class SkillResult(SessionRecord):
    """技能结果"""
    type: str = "skill_result"
    skill_call_id: str = ""
    output: str = ""
    success: bool = True

@dataclass
class Thinking(SessionRecord):
    """思考过程"""
    type: str = "thinking"
    parent_uuid: Optional[str] = None
    content: str = ""

@dataclass
class ErrorRecord(SessionRecord):
    """错误记录"""
    type: str = "error"
    parent_uuid: Optional[str] = None
    error_type: str = ""
    message: str = ""
    traceback: Optional[str] = None
```

### 3. 会话管理器

```python
# anyclaw/session/manager.py

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import subprocess

from .records import (
    SessionRecord, SessionStart, SessionEnd,
    UserMessage, AssistantMessage, ToolCall, ToolResult,
    SkillCall, SkillResult, Thinking, ErrorRecord
)

class SessionManager:
    """会话管理器"""

    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.home() / ".anyclaw" / "sessions"
        self.current_session_id: Optional[str] = None
        self.current_project_id: Optional[str] = None
        self.session_start_time: Optional[datetime] = None
        self._message_count = 0
        self._tool_call_count = 0

    def start_session(
        self,
        cwd: Path,
        channel: str = "cli",
        channel_id: Optional[str] = None
    ) -> str:
        """开始新会话"""
        import uuid
        self.current_session_id = str(uuid.uuid4())
        self.session_start_time = datetime.now()
        self._message_count = 0
        self._tool_call_count = 0

        # 确定项目标识
        if channel == "cli":
            self.current_project_id = self._get_project_id(cwd)
        else:
            self.current_project_id = f"{channel}_{channel_id}"

        # 写入 session_start
        start_record = SessionStart(
            session_id=self.current_session_id,
            project_id=self.current_project_id,
            cwd=str(cwd),
            git_branch=self._get_git_branch(cwd),
            channel=channel,
        )
        self._append_record(start_record)

        return self.current_session_id

    def end_session(self) -> None:
        """结束会话"""
        if not self.current_session_id:
            return

        duration = (datetime.now() - self.session_start_time).total_seconds()
        end_record = SessionEnd(
            session_id=self.current_session_id,
            message_count=self._message_count,
            tool_call_count=self._tool_call_count,
            duration_seconds=duration,
        )
        self._append_record(end_record)

    def record_user_message(self, content: str, parent_uuid: str = None) -> str:
        """记录用户消息"""
        record = UserMessage(content=content, parent_uuid=parent_uuid)
        self._append_record(record)
        self._message_count += 1
        return record.uuid

    def record_assistant_message(
        self, content: str, parent_uuid: str = None, model: str = None
    ) -> str:
        """记录助手消息"""
        record = AssistantMessage(
            content=content, parent_uuid=parent_uuid, model=model
        )
        self._append_record(record)
        self._message_count += 1
        return record.uuid

    def record_tool_call(
        self, tool_name: str, tool_input: dict, parent_uuid: str = None
    ) -> str:
        """记录工具调用"""
        import uuid
        record = ToolCall(
            parent_uuid=parent_uuid,
            tool_call_id=f"call_{uuid.uuid4().hex[:8]}",
            tool_name=tool_name,
            tool_input=tool_input,
        )
        self._append_record(record)
        self._tool_call_count += 1
        return record.tool_call_id

    def record_tool_result(
        self, tool_call_id: str, output: str, duration_ms: int, success: bool = True
    ) -> None:
        """记录工具结果"""
        record = ToolResult(
            tool_call_id=tool_call_id,
            output=output,
            duration_ms=duration_ms,
            success=success,
        )
        self._append_record(record)

    def record_skill_call(
        self, skill_name: str, skill_args: str, parent_uuid: str = None
    ) -> str:
        """记录技能调用"""
        import uuid
        record = SkillCall(
            parent_uuid=parent_uuid,
            skill_call_id=f"skill_{uuid.uuid4().hex[:8]}",
            skill_name=skill_name,
            skill_args=skill_args,
        )
        self._append_record(record)
        return record.skill_call_id

    def record_skill_result(
        self, skill_call_id: str, output: str, success: bool = True
    ) -> None:
        """记录技能结果"""
        record = SkillResult(
            skill_call_id=skill_call_id,
            output=output,
            success=success,
        )
        self._append_record(record)

    def _get_project_id(self, cwd: Path) -> str:
        """获取项目标识符（Git root 或 cwd）"""
        git_root = self._find_git_root(cwd)
        path = git_root or cwd
        return self._make_safe_dirname(str(path.resolve()))

    def _find_git_root(self, path: Path) -> Optional[Path]:
        """查找 Git 仓库根目录"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=path, capture_output=True, text=True
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except Exception:
            pass
        return None

    def _get_git_branch(self, path: Path) -> Optional[str]:
        """获取当前 Git 分支"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=path, capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def _make_safe_dirname(self, path: str) -> str:
        """生成安全的目录名"""
        return path.replace("/", "-").replace("\\", "-").lstrip("-")

    def _get_session_file_path(self) -> Path:
        """获取当前会话文件路径"""
        date_dir = datetime.now().strftime("%Y-%m-%d")

        if self.current_project_id.startswith("feishu_") or \
           self.current_project_id.startswith("discord_"):
            # Channel 类型
            parts = self.current_project_id.split("_", 1)
            channel_type, channel_id = parts[0], parts[1]
            return (
                self.base_dir / "channels" / channel_type / channel_id /
                date_dir / f"{self.current_session_id}.jsonl"
            )
        else:
            # CLI 类型
            return (
                self.base_dir / "cli" / self.current_project_id /
                date_dir / f"{self.current_session_id}.jsonl"
            )

    def _append_record(self, record: SessionRecord) -> None:
        """追加记录到会话文件"""
        file_path = self._get_session_file_path()
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(record.to_json() + "\n")

        # 更新日期索引
        self._update_date_index(file_path.parent)

    def _update_date_index(self, date_dir: Path) -> None:
        """更新日期索引文件"""
        index_path = date_dir / "index.json"
        # 简化实现：每天更新一次
        # 完整实现可以增量更新
        pass
```

### 4. CLI 命令

```python
# anyclaw/cli/session.py

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="session", help="会话管理")
console = Console()

@app.command("list")
def list_sessions(
    date: str = typer.Option(None, "--date", "-d", help="指定日期 (YYYY-MM-DD)"),
    project: str = typer.Option(None, "--project", "-p", help="指定项目"),
    limit: int = typer.Option(20, "--limit", "-l", help="限制数量"),
):
    """列出会话"""
    # 实现查询逻辑
    pass

@app.command("show")
def show_session(
    session_id: str = typer.Argument(..., help="会话 ID"),
    format: str = typer.Option("tree", "--format", "-f", help="输出格式 (tree/json/markdown)"),
):
    """显示会话详情"""
    pass

@app.command("search")
def search_sessions(
    query: str = typer.Argument(..., help="搜索关键词"),
    tool: str = typer.Option(None, "--tool", "-t", help="按工具过滤"),
):
    """搜索会话内容"""
    pass

@app.command("export")
def export_session(
    session_id: str = typer.Argument(..., help="会话 ID"),
    output: str = typer.Option(None, "--output", "-o", help="输出文件"),
    format: str = typer.Option("markdown", "--format", "-f", help="格式 (json/markdown)"),
):
    """导出会话"""
    pass

@app.command("clean")
def clean_sessions(
    days: int = typer.Option(30, "--days", "-d", help="保留天数"),
    dry_run: bool = typer.Option(False, "--dry-run", help="仅显示将删除的内容"),
):
    """清理旧会话"""
    pass
```

## 影响范围

- `anyclaw/session/__init__.py` - 新建会话模块
- `anyclaw/session/records.py` - 记录类型定义
- `anyclaw/session/manager.py` - 会话管理器
- `anyclaw/session/project.py` - 项目识别逻辑
- `anyclaw/agent/history.py` - 集成会话管理
- `anyclaw/agent/loop.py` - 集成记录逻辑
- `anyclaw/cli/session.py` - CLI 命令
- `tests/test_session.py` - 测试文件

## 验收标准

- [ ] 会话自动持久化到 JSONL 文件
- [ ] Git 项目按 root 目录隔离
- [ ] 非 Git 项目按 cwd 隔离
- [ ] Channel 按类型和 ID 隔离
- [ ] 按日期归档（YYYY-MM-DD 目录）
- [ ] 记录 user/assistant 消息
- [ ] 记录 tool_call/tool_result
- [ ] 记录 skill_call/skill_result
- [ ] CLI 支持列出/查看/搜索会话
- [ ] 支持导出为 Markdown
- [ ] 测试覆盖率 > 80%
