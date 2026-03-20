# feat-session-manager

**状态**: ✅ 已完成
**完成时间**: 2026-03-20
**优先级**: 85
**大小**: M
**提交**: 9ba8bc4

## 描述

实现 SessionManager 会话管理器，提供会话持久化、工具调用边界检测、多会话管理等功能，与 nanobot 保持兼容。

## 价值点

1. **会话持久化**
   - JSONL 格式存储会话数据
   - 支持会话恢复和继续
   - 元数据追踪 (创建时间、更新时间、消息数)

2. **工具调用边界检测**
   - 检测 AI 何时需要调用工具
   - 检测工具调用何时完成
   - 支持多轮工具调用场景

3. **多会话管理**
   - 创建/获取/删除会话
   - 会话列表查询
   - 会话元数据管理

4. **向后兼容**
   - SessionManagerAdapter 适配 ConversationHistory
   - 无缝替换现有历史管理

## 实现文件

- `anyclaw/session/__init__.py` - 模块导出
- `anyclaw/session/manager.py` - SessionManager 核心实现
- `anyclaw/session/models.py` - 数据模型 (Session, SessionMetadata)

## 核心数据结构

```python
@dataclass
class Session:
    id: str
    messages: List[Message]
    metadata: SessionMetadata
    created_at: datetime
    updated_at: datetime

@dataclass
class SessionMetadata:
    channel: Optional[str]
    chat_id: Optional[str]
    message_count: int
    tool_calls: int
```

## 使用示例

```python
from anyclaw.session import SessionManager

# 创建会话管理器
manager = SessionManager(sessions_dir="~/.anyclaw/sessions")

# 创建新会话
session = manager.create_session(channel="cli", chat_id="user_123")

# 添加消息
session.add_message(role="user", content="Hello")
session.add_message(role="assistant", content="Hi there!")

# 保存会话
manager.save_session(session)

# 检测工具调用边界
if manager.has_pending_tool_call(session):
    # 等待工具执行
    pass
```

## 工具调用边界检测

```python
def has_pending_tool_call(session: Session) -> bool:
    """检查是否有待执行的工具调用"""
    last_message = session.messages[-1]
    return bool(last_message.tool_calls)

def is_tool_response_pending(session: Session) -> bool:
    """检查是否需要发送工具响应"""
    # 上一条是工具调用，但没有对应的工具响应
    pass
```

## 测试

```
tests/test_session_manager.py
```

## 与 nanobot 对比

| 特性 | nanobot | AnyClaw | 状态 |
|------|---------|---------|------|
| JSONL 持久化 | ✅ | ✅ | 完全兼容 |
| 工具调用边界 | ✅ | ✅ | 完全兼容 |
| 多会话管理 | ✅ | ✅ | 完全兼容 |
| 元数据追踪 | ✅ | ✅ | 完全兼容 |
