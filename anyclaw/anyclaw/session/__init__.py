"""Session module

提供会话管理功能，支持：
- 会话持久化存储（JSONL 格式）
- 按项目和日期归档
- 完整的记录类型（消息、工具调用、技能调用等）
- 会话查询和导出
"""

from .models import Session, SessionMessage
from .records import (
    SessionRecord,
    SessionStart,
    SessionEnd,
    UserMessage,
    AssistantMessage,
    ToolCall,
    ToolResult,
    SkillCall,
    SkillResult,
    Thinking,
    ErrorRecord,
    RECORD_TYPES,
    parse_record,
    parse_record_from_json,
)
from .project import (
    find_git_root,
    get_git_branch,
    get_project_identifier,
    make_safe_dirname,
)
from .manager import SessionManager, SessionManagerConfig
from .archive import SessionArchiveManager, ArchiveConfig

__all__ = [
    # 模型
    "Session",
    "SessionMessage",
    # 记录类型
    "SessionRecord",
    "SessionStart",
    "SessionEnd",
    "UserMessage",
    "AssistantMessage",
    "ToolCall",
    "ToolResult",
    "SkillCall",
    "SkillResult",
    "Thinking",
    "ErrorRecord",
    "RECORD_TYPES",
    "parse_record",
    "parse_record_from_json",
    # 项目识别
    "find_git_root",
    "get_git_branch",
    "get_project_identifier",
    "make_safe_dirname",
    # 管理器
    "SessionManager",
    "SessionManagerConfig",
    "SessionArchiveManager",
    "ArchiveConfig",
]
