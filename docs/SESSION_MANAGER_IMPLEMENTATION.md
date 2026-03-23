# AnyClaw SessionManager 完整实现方案

## 📋 设计目标

1. **完美复刻 nanobot 的 SessionManager 核心逻辑**
2. **保持向后兼容** - 不影响现有的 history.py 功能
3. **平滑集成** - 与 AgentLoop 无缝配合
4. **可测试性** - 提供完整的测试覆盖

---

## 🏗️ 架构设计

### 文件结构

```
anyclaw/
├── session/
│   ├── __init__.py          # 模块导出
│   ├── manager.py          # SessionManager 主类
│   └── models.py          # Session 数据模型
├── agent/
│   ├── history.py          # ConversationHistory（保持不变）
│   └── loop.py            # AgentLoop（集成 SessionManager）
└── config/
    └── settings.py         # 添加会话配置项
```

### 组件关系

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentLoop                      │
│                       │                            │
│            ┌──────────────────────────┐            │
│            │   SessionManager        │            │
│            │                        │            │
│  ┌────────┴──────┐     ┌─────────────────┴──┐
│  │ Session         │     │ ContextBuilder      │
│  │ (model)        │     │                     │
│  └───────┬────────┘     └─────────────────────┘
│         │
│    ┌────┴──────┐
│    │  History    │
│    │ (legacy)   │
│    └─────────────┘
└─────────────────────────────────────────────────────┘
```

---

## 📦 核心实现

### 1. `session/models.py` - 数据模型

```python
"""Session 数据模型"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class SessionMessage:
    """
    单条会话消息

    与 nanobot 兼容的数据结构
    """
    role: str                              # "user" | "assistant" | "tool" | "system"
    content: str | None = None             # 消息内容
    timestamp: str | None = None           # ISO 格式时间戳
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)  # Tool 调用列表
    tool_call_id: str | None = None       # Tool 调用关联 ID
    name: str | None = None               # Tool 名称（role="tool" 时）
    _metadata: Dict[str, Any] = field(default_factory=dict)  # 内部元数据
    media: List[str] = field(default_factory=list)  # 媒体文件路径
    images: List[Dict[str, Any]] = field(default_factory=list)  # 图片数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于 JSON 序列化）"""
        result: Dict[str, Any] = {
            "role": self.role,
            "content": self.content,
        }

        if self.timestamp:
            result["timestamp"] = self.timestamp

        if self.tool_calls:
            result["tool_calls"] = self.tool_calls

        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id

        if self.name:
            result["name"] = self.name

        if self.media:
            result["media"] = self.media

        if self.images:
            result["images"] = self.images

        for key, value in self._metadata.items():
            result[key] = value

        return result

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SessionMessage":
        """从字典创建消息对象"""
        return SessionMessage(
            role=data.get("role"),
            content=data.get("content"),
            timestamp=data.get("timestamp"),
            tool_calls=data.get("tool_calls", []),
            tool_call_id=data.get("tool_call_id"),
            name=data.get("name"),
            media=data.get("media", []),
            images=data.get("images", []),
            _metadata={k: v for k, v in data.items()
                      if k not in {"role", "content", "timestamp", "tool_calls",
                                "tool_call_id", "name", "media", "images"}}
        )


@dataclass
class Session:
    """
    会话对象（对应 nanobot 的 Session）

    特性：
    - 只追加消息，不修改历史（LLM 缓存优化）
    - JSONL 格式持久化（每行一个 JSON）
    - 工具调用边界检测
    - 支持会话元数据
    """
    key: str                               # 会话唯一标识（channel:chat_id 或 session_key）
    messages: List[SessionMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_consolidated: int = 0              # 已整合到 MEMORY.md 的消息数

    def add_message(
        self,
        role: str,
        content: str | None = None,
        **kwargs
    ) -> None:
        """添加消息到会话（只追加，不修改历史）"""
        msg = SessionMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            **kwargs
        )
        self.messages.append(msg)
        self.updated_at = datetime.now()

    def get_history(self, max_messages: int = 500) -> List[Dict[str, Any]]:
        """
        获取历史记录（智能截断）

        关键特性：工具调用边界检测
        确保不会在 tool 结果中间截断

        Args:
            max_messages: 最大返回消息数

        Returns:
            对齐后的消息列表（dict 格式）
        """
        unconsolidated = self.messages[self.last_consolidated:]
        sliced = unconsolidated[-max_messages:]

        # 删除前导非用户消息（避免从中间开始）
        for i, message in enumerate(sliced):
            if message.get("role") == "user":
                sliced = sliced[i:]
                break

        # 一些 provider 会拒绝孤立的 tool 结果
        # 检测 tool 结果是否有匹配的 assistant tool_call
        start = self._find_legal_start(sliced)

        if start:
            sliced = sliced[start:]

        # 转换为字典格式
        return [msg.to_dict() for msg in sliced]

    @staticmethod
    def _find_legal_start(messages: List["SessionMessage"]) -> int:
        """
        找到第一个合法的 tool-call 边界

        确保不会在 tool 结果中间截断

        Args:
            messages: 消息列表

        Returns:
            第一个合法的起始索引
        """
        declared: set[str] = set()

        for i, msg in enumerate(messages):
            role = msg.role

            if role == "assistant":
                # 记录所有声明的 tool_call id
                for tc in msg.tool_calls:
                    if isinstance(tc, dict) and tc.get("id"):
                        declared.add(str(tc["id"]))

            elif role == "tool":
                # 如果遇到 tool 结果，但其 id 未在前面声明过
                # 说明这是孤立的 tool 结果，需要从这里开始
                tid = msg.tool_call_id
                if tid and str(tid) not in declared:
                    return i + 1
                    declared.clear()  # 重置，开始新的检查

        return 0

    def clear(self) -> None:
        """清空会话"""
        self.messages = []
        self.last_consolidated = 0
        self.updated_at = datetime.now()

    def save(self, path) -> None:
        """保存会话到 JSONL 文件"""
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            # 写入元数据行
            metadata_line = {
                "_type": "metadata",
                "key": self.key,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "metadata": self.metadata,
                "last_consolidated": self.last_consolidated
            }
            f.write(json.dumps(metadata_line, ensure_ascii=False) + "\n")

            # 写入消息行
            for msg in self.messages:
                f.write(json.dumps(msg.to_dict(), ensure_ascii=False) + "\n")

    @staticmethod
    def load(path) -> "Session | None":
        """从 JSONL 文件加载会话"""
        if not path.exists():
            return None

        try:
            messages = []
            metadata = {}
            created_at = None
            updated_at = None
            last_consolidated = 0

            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    data = json.loads(line)

                    if data.get("_type") == "metadata":
                        metadata = data.get("metadata", {})
                        created_at = datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
                        updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
                        last_consolidated = data.get("last_consolidated", 0)
                    else:
                        messages.append(SessionMessage.from_dict(data))

            return Session(
                key=metadata.get("key", path.stem.replace("_", ":", 1)),
                messages=messages,
                created_at=created_at or datetime.now(),
                updated_at=updated_at or datetime.now(),
                metadata=metadata,
                last_consolidated=last_consolidated
            )
        except Exception as e:
            print(f"Failed to load session from {path}: {e}")
            return None
```

---

### 2. `session/manager.py` - SessionManager 类

```python
"""Session Manager - 会话管理系统

完美复刻 nanobot 的 SessionManager 实现，同时保持向后兼容。
"""

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from .models import Session


@dataclass
class SessionManagerConfig:
    """SessionManager 配置"""
    workspace: Path
    sessions_dir: Path = field(init=False)
    max_history_messages: int = 500
    enable_persistence: bool = True
    enable_memory_cache: bool = True


class SessionManager:
    """
    会话管理器

    特性：
    - JSONL 格式持久化（与 nanobot 兼容）
    - 内存缓存（避免重复磁盘 IO）
    - 多会话支持
    - 会话清理和迁移
    - 工具调用边界检测

    与现有 History 系统的关系：
    - SessionManager 负责持久化和多会话管理
    - ConversationHistory 保持向后兼容，用于简单场景
    - AgentLoop 可以选择使用任一个
    """

    def __init__(self, config: SessionManagerConfig):
        self.config = config
        self.workspace = config.workspace

        # 会话目录
        self.sessions_dir = config.sessions_dir
        if not self.sessions_dir.is_dir():
            self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # 内存缓存
        self._cache: Dict[str, Session] = {}

        logger.info(f"SessionManager initialized with workspace: {self.workspace}")

    def _get_session_path(self, key: str) -> Path:
        """获取会话文件路径"""
        # 将 channel:chat_id 转换为安全的文件名
        safe_key = key.replace(":", "_")
        return self.sessions_dir / f"{safe_key}.jsonl"

    def get_or_create(self, key: str) -> Session:
        """
        获取或创建会话

        Args:
            key: 会话键（通常为 "channel:chat_id" 或 session_key）

        Returns:
            Session 对象
        """
        # 1. 检查内存缓存
        if key in self._cache:
            logger.debug(f"Session cache hit: {key}")
            return self._cache[key]

        # 2. 尝试从磁盘加载
        path = self._get_session_path(key)
        if path.exists():
            session = Session.load(path)
            if session:
                self._cache[key] = session
                logger.debug(f"Session loaded from disk: {key}")
                return session

        # 3. 创建新会话
        logger.info(f"Creating new session: {key}")
        session = Session(key=key)
        self._cache[key] = session
        return session

    def save(self, session: Session) -> None:
        """保存会话到磁盘"""
        if not self.config.enable_persistence:
            return

        path = self._get_session_path(session.key)
        session.save(path)
        self._cache[session.key] = session
        logger.debug(f"Session saved: {session.key}")

    def invalidate(self, key: str) -> None:
        """从内存缓存移除会话"""
        self._cache.pop(key, None)
        logger.debug(f"Session invalidated: {key}")

    def add_message(
        self,
        key: str,
        role: str,
        content: str | None = None,
        **kwargs
    ) -> None:
        """添加消息到会话（快捷方法）"""
        session = self.get_or_create(key)
        session.add_message(role, content, **kwargs)
        self.save(session)

    def get_history(
        self,
        key: str,
        max_messages: int = None
    ) -> List[Dict[str, Any]]:
        """获取会话历史（快捷方法）"""
        session = self.get_or_create(key)
        max_messages = max_messages or self.config.max_history_messages
        return session.get_history(max_messages)

    def clear_session(self, key: str) -> None:
        """清空会话"""
        session = self.get_or_create(key)
        session.clear()
        self.save(session)
        logger.info(f"Session cleared: {key}")

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        列出所有会话

        Returns:
            会话信息列表
        """
        sessions = []

        for path in self.sessions_dir.glob("*.jsonl"):
            try:
                # 只读取元数据行
                with open(path, encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    if first_line:
                        data = json.loads(first_line)
                        if data.get("_type") == "metadata":
                            key = data.get("key") or path.stem.replace("_", ":", 1)
                            sessions.append({
                                "key": key,
                                "created_at": data.get("created_at"),
                                "updated_at": data.get("updated_at"),
                                "path": str(path),
                                "message_count": self._count_messages(path)
                            })
            except Exception:
                continue

        return sorted(sessions, key=lambda x: x.get("updated_at", ""), reverse=True)

    @staticmethod
    def _count_messages(path: Path) -> int:
        """统计会话文件中的消息数"""
        count = 0
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not json.loads(line).get("_type") == "metadata":
                    count += 1
        return count

    def delete_session(self, key: str) -> None:
        """删除会话"""
        path = self._get_session_path(key)
        if path.exists():
            path.unlink()
            logger.info(f"Session deleted: {key}")

        self.invalidate(key)

    def migrate_from_legacy(self, legacy_dir: Path) -> int:
        """
        从旧格式迁移会话

        Args:
            legacy_dir: 旧的会话目录

        Returns:
            迁移的会话数量
        """
        if not legacy_dir.exists():
            return 0

        migrated = 0

        for old_path in legacy_dir.glob("*.jsonl"):
            try:
                session = Session.load(old_path)
                if session:
                    new_path = self._get_session_path(session.key)
                    session.save(new_path)
                    old_path.unlink()
                    migrated += 1
                    logger.info(f"Migrated session: {session.key}")
            except Exception as e:
                logger.warning(f"Failed to migrate session from {old_path}: {e}")
                continue

        return migrated

    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return {
            "workspace": str(self.workspace),
            "sessions_dir": str(self.sessions_dir),
            "max_history_messages": self.config.max_history_messages,
            "enable_persistence": self.config.enable_persistence,
            "enable_memory_cache": self.config.enable_memory_cache,
            "cached_sessions": len(self._cache),
        }
```

---

### 3. `agent/loop.py` - 集成 SessionManager

```python
# 在 AgentLoop.__init__() 中添加

from anyclaw.session.manager import SessionManager, SessionManagerConfig

class AgentLoop:
    def __init__(
        self,
        enable_tools: bool = True,
        workspace: Optional[Path] = None,
        # 新增参数：是否启用 SessionManager
        enable_session_manager: bool = True,
    ):
        self.history = ConversationHistory(max_length=10)
        self.skills: Dict[str, SkillDefinition] = {}
        self.enable_tools = enable_tools
        self.workspace = workspace or Path.cwd()

        # 初始化 SessionManager（可选）
        self.session_manager: Optional[SessionManager] = None
        if enable_session_manager:
            session_config = SessionManagerConfig(
                workspace=self.workspace,
                sessions_dir=self.workspace / "sessions",
                max_history_messages=500,
                enable_persistence=True,
                enable_memory_cache=True
            )
            self.session_manager = SessionManager(session_config)
            logger.info("SessionManager enabled")

        # MCP 连接管理
        self._mcp_stack: Optional[AsyncExitStack] = None

        # 初始化 Tool Registry
        self.tools = ToolRegistry()
        if enable_tools:
            self._register_default_tools()

    # 修改其他方法以支持 SessionManager
    def get_session(self, key: str):
        """获取会话（优先使用 SessionManager）"""
        if self.session_manager:
            return self.session_manager.get_or_create(key)
        # 向后兼容：使用 history
        return self.history

    def add_message(self, key: str, role: str, content: str, **kwargs):
        """添加消息到会话"""
        if self.session_manager:
            return self.session_manager.add_message(key, role, content, **kwargs)
        # 向后兼容
        return self.history.add(role, content)

    def get_conversation_history(self, key: str, max_messages: int = None):
        """获取会话历史"""
        if self.session_manager:
            return self.session_manager.get_history(key, max_messages)
        # 向后兼容
        return self.history.get_messages(max_messages)
```

---

### 4. `config/settings.py` - 添加配置项

```python
# 在 Settings 类中添加

class Settings(BaseSettings):
    # ... 现有配置 ...

    # SessionManager 配置
    session_enabled: bool = Field(
        default=True,
        description="是否启用 SessionManager（默认启用）"
    )

    sessions_dir: str = Field(
        default="sessions",
        description="会话存储目录（相对于 workspace）"
    )

    max_history_messages: int = Field(
        default=500,
        ge=1,
        le=10000,
        description="会话历史最大消息数"
    )

    enable_session_persistence: bool = Field(
        default=True,
        description="是否启用会话持久化（JSONL 文件）"
    )

    enable_session_cache: bool = Field(
        default=True,
        description="是否启用会话内存缓存"
    )
```

---

## 🔧 向后兼容策略

### 1. 保留现有 History 系统

```python
# ConversationHistory 保持不变
# 用户可以选择使用：
# - agent.history.add() - 简单场景
# - session_manager.add_message() - 需要多会话/持久化的场景
```

### 2. 渐进式迁移

```python
# 通过配置控制是否启用 SessionManager
enable_session_manager = settings.session_enabled  # 默认 True

if enable_session_manager:
    # 使用新的 SessionManager
    pass
else:
    # 使用旧的 History 系统
    pass
```

### 3. API 兼容

```python
# 提供统一的接口
loop.add_message(key, role, content)          # 适配器模式
loop.get_conversation_history(key, max)   # 适配器模式
```

---

## 🧪 测试计划

### 单元测试

```python
# tests/test_session_manager.py

import pytest
from pathlib import Path
from anyclaw.session.manager import SessionManager, SessionManagerConfig
from anyclaw.session.models import Session

def test_create_session():
    """测试创建会话"""
    config = SessionManagerConfig(workspace=Path("/tmp/test_workspace"))
    manager = SessionManager(config)

    session = manager.get_or_create("test:123")

    assert session is not None
    assert session.key == "test:123"
    assert len(session.messages) == 0

def test_add_message():
    """测试添加消息"""
    config = SessionManagerConfig(workspace=Path("/tmp/test_workspace"))
    manager = SessionManager(config)

    session = manager.get_or_create("test:123")
    session.add_message(role="user", content="Hello")

    assert len(session.messages) == 1
    assert session.messages[0].role == "user"
    assert session.messages[0].content == "Hello"

def test_get_history():
    """测试获取历史"""
    config = SessionManagerConfig(workspace=Path("/tmp/test_workspace"))
    manager = SessionManager(config)

    session = manager.get_or_create("test:123")
    session.add_message(role="user", content="Hello")
    session.add_message(role="assistant", content="Hi there!")
    session.add_message(role="tool", name="echo", tool_calls=[], tool_call_id="123", content="echoed: Hi there!")

    history = session.get_history(max_messages=100)

    assert len(history) == 3  # 不应该包含孤立的 tool 结果
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"

def test_tool_call_boundary_detection():
    """测试工具调用边界检测"""
    config = SessionManagerConfig(workspace=Path("/tmp/test_workspace"))
    manager = SessionManager(config)

    session = manager.get_or_create("test:123")

    # 添加完整的 tool call
    session.add_message(role="assistant", content="...", tool_calls=[{"id": "tc1"}])
    session.add_message(role="tool", tool_call_id="tc1", name="echo", content="result")

    # 添加孤立的 tool result
    session.add_message(role="tool", tool_call_id="tc999", name="unknown", content="orphaned")

    history = session.get_history(max_messages=100)

    # 应该从 tc1 开始，跳过 tc999
    assert len(history) >= 2
    assert history[0]["role"] == "assistant"
    assert history[1]["role"] == "tool"

def test_persistence():
    """测试持久化"""
    import tempfile
    import shutil

    with tempfile.TemporaryDirectory() as tmpdir:
        config = SessionManagerConfig(workspace=Path(tmpdir))
        manager = SessionManager(config)

        session = manager.get_or_create("test:persist")
        session.add_message(role="user", content="Test message")

        # 保存会话
        manager.save(session)

        # 重新加载
        reloaded = manager.get_or_create("test:persist")

        assert len(reloaded.messages) == 1
        assert reloaded.messages[0].content == "Test message"
```

### 集成测试

```python
# tests/integration/test_session_integration.py

from pathlib import Path
from anyclaw.agent.loop import AgentLoop
from anyclaw.config.settings import Settings

def test_agent_loop_with_session_manager():
    """测试 AgentLoop 集成 SessionManager"""
    workspace = Path("/tmp/test_integration")

    # 启用 SessionManager
    settings = Settings(workspace=str(workspace), session_enabled=True)

    loop = AgentLoop(enable_tools=False, workspace=workspace, enable_session_manager=True)

    # 测试会话操作
    loop.add_message("test:123", "user", "Hello")
    history = loop.get_conversation_history("test:123")

    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
```

---

## 📋 实施步骤

### Phase 1: 创建数据模型（1-2 天）
- [ ] 创建 `session/models.py` - Session 和 SessionMessage 类
- [ ] 实现 to_dict() 和 from_dict() 方法
- [ ] 实现 add_message() 方法
- [ ] 实现 get_history() 方法
- [ ] 实现 _find_legal_start() 方法

### Phase 2: 创建 SessionManager（2-3 天）
- [ ] 创建 `session/manager.py` - SessionManager 类
- [ ] 实现 get_or_create() 方法
- [ ] 实现 save() 方法
- [ ] 实现 invalidate() 方法
- [ ] 实现 list_sessions() 方法
- [ ] 实现 delete_session() 方法
- [ ] 实现内存缓存
- [ ] 添加日志记录

### Phase 3: 集成到 AgentLoop（2-3 天）
- [ ] 更新 AgentLoop.__init__() 添加 SessionManager 支持
- [ ] 添加 session_manager 参数
- [ ] 实现适配器方法（get_session, add_message 等）
- [ ] 保持向后兼容（不启用 SessionManager 时）

### Phase 4: 添加配置项（1 天）
- [ ] 在 settings.py 中添加 SessionManager 配置项
- [ ] 添加默认值
- [ ] 添加验证规则

### Phase 5: 编写测试（2-3 天）
- [ ] 编写单元测试（test_session_manager.py）
- [ ] 编写集成测试（test_session_integration.py）
- [ ] 确保测试覆盖率达到 90%+

### Phase 6: 文档和示例（1 天）
- [ ] 更新 README.md 添加 SessionManager 说明
- [ ] 添加使用示例
- [ ] 更新 COMPARISON_WITH_NANOBOT.md

---

## 🎯 关键特性清单

### ✅ 核心功能

| 功能 | nanobot | AnyClaw 实现 | 优先级 |
|------|---------|---------------|--------|
| JSONL 持久化 | ✅ | ✅ | 🔴 **高** |
| 工具调用边界检测 | ✅ | ✅ | 🔴 **高** |
| 内存缓存 | ✅ | ✅ | 🟢 **中** |
| 多会话支持 | ✅ | ✅ | 🔴 **高** |
| 会话元数据 | ✅ | ✅ | 🟢 **中** |
| 只追加消息 | ✅ | ✅ | 🔴 **高** |
| 向后兼容 History | ❌ | ✅ | 🟢 **中** |

### 🔄 向后兼容策略

| 场景 | 解决方案 |
|------|---------|
| 简单对话（无需持久化） | 保持使用 ConversationHistory |
| 需要多会话/持久化 | 使用 SessionManager |
| 不启用 SessionManager | 自动降级到 History |
| 从 History 迁移 | 提供 migrate_from_legacy() 方法 |

---

## 📊 预期效果

### 对用户的影响

1. **完全兼容** - 现有功能不受影响
2. **可选启用** - 通过配置控制是否使用 SessionManager
3. **平滑升级** - 可以渐进式从 History 迁移到 SessionManager

### 对开发的影响

1. **清晰的架构** - 分离的会话管理逻辑
2. **易于测试** - 独立的组件和测试
3. **可扩展性** - 为未来的增强奠定基础

### 对 nanobot 的对比

| 特性 | nanobot | AnyClaw 实现 |
|------|---------|---------------|
| **JSONL 格式** | ✅ | ✅ 完全一致 |
| **工具调用边界检测** | ✅ | ✅ 完全一致 |
| **内存缓存** | ✅ | ✅ 完全一致 |
| **向后兼容** | ❌ 不需要 | ✅ 提供平滑迁移路径 |

---

## 🎁 额外优化建议

### 1. 性能优化

```python
# 批量保存（减少磁盘 IO）
def save_batch(self, sessions: List[Session]) -> None:
    """批量保存多个会话"""
    for session in sessions:
        self.save(session)
```

### 2. 内存优化

```python
# LRU 缓存（限制内存使用）
from functools import lru_cache

@lru_cache(maxsize=100)
def _load_from_disk_cached(key: str) -> Optional[Session]:
    """缓存的磁盘加载"""
    return Session.load(path)
```

### 3. 监控和诊断

```python
# 添加指标收集
class SessionMetrics:
    """会话指标收集"""
    cache_hits: int = 0
    cache_misses: int = 0
    disk_reads: int = 0
    disk_writes: int = 0
```

---

## 📝 文档示例

### 使用示例

```python
# 基础使用
from anyclaw.session.manager import SessionManager, SessionManagerConfig
from pathlib import Path

# 创建 SessionManager
config = SessionManagerConfig(
    workspace=Path("~/myproject"),
    sessions_dir="sessions",
    max_history_messages=500
)
manager = SessionManager(config)

# 获取或创建会话
session = manager.get_or_create("cli:default")

# 添加消息
session.add_message(role="user", content="Hello")
session.add_message(role="assistant", content="Hi!")

# 获取历史
history = session.get_history(max_messages=100)
for msg in history:
    print(f"{msg['role']}: {msg['content']}")

# 保存会话
manager.save(session)

# 列出所有会话
sessions = manager.list_sessions()
for session_info in sessions:
    print(f"{session_info['key']}: {session_info['message_count']} messages")
```

### AgentLoop 集成示例

```python
# 在 AgentLoop 中使用
loop = AgentLoop(
    enable_tools=True,
    workspace=workspace,
    enable_session_manager=True  # 启用 SessionManager
)

# 添加消息
loop.add_message("discord:123:456", "user", "Test message")

# 获取历史
history = loop.get_conversation_history("discord:123:456")
```

---

## 🚀 总结

### 核心目标

1. ✅ **完美复刻 nanobot SessionManager 核心逻辑**
2. ✅ **保持向后兼容** - 不影响现有功能
3. ✅ **平滑集成** - 与 AgentLoop 无缝配合
4. ✅ **完整测试** - 单元测试 + 集成测试

### 关键优势

1. **JSONL 持久化** - 与 nanobot 完全一致
2. **工具调用边界检测** - 避免 provider 拒绝
3. **内存缓存** - 提高性能
4. **多会话支持** - 同时管理多个对话
5. **向后兼容** - 现有系统不受影响
6. **可配置** - 通过配置控制是否启用

### 预期效果

- 🎯 **100% 功能对齐** - 与 nanobot SessionManager 特性完全一致
- 🔄 **零破坏升级** - 现有功能完全兼容
- 📈 **性能提升** - 内存缓存 + JSONL 高效持久化
- 🧪 **可测试** - 完整的单元测试和集成测试
- 📚 **易于维护** - 清晰的架构和文档

---

**方案创建时间**: 2026-03-20
**参考**: nanobot (2026-03-17) SessionManager 实现
**作者**: Yilia
**状态**: 🎉 完整实现方案，等待实施
