"""Session record types

完整的会话记录类型定义，支持：
- 会话生命周期记录（SessionStart/SessionEnd）
- 消息记录（UserMessage/AssistantMessage）
- 工具调用记录（ToolCall/ToolResult）
- 技能调用记录（SkillCall/SkillResult）
- 思考过程记录（Thinking）
- 错误记录（ErrorRecord）

所有记录类型支持 JSON 序列化，用于 JSONL 持久化。
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class SessionRecord:
    """会话记录基类

    所有记录类型共享的基础字段：
    - type: 记录类型标识
    - uuid: 唯一标识符
    - timestamp: ISO 格式时间戳
    """

    type: str
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于 JSON 序列化）"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionRecord":
        """从字典创建记录对象（由子类实现）"""
        raise NotImplementedError


@dataclass
class SessionStart(SessionRecord):
    """会话开始记录

    记录会话启动时的元信息：
    - session_id: 会话唯一标识
    - project_id: 项目标识符（Git root 或 cwd）
    - cwd: 当前工作目录
    - git_branch: Git 分支名（如有）
    - channel: 来源渠道（cli/feishu/discord）
    - version: AnyClaw 版本
    """

    type: str = "session_start"
    session_id: str = ""
    project_id: str = ""
    cwd: str = ""
    git_branch: Optional[str] = None
    channel: str = "cli"  # cli, feishu, discord
    version: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionStart":
        return cls(
            type=data.get("type", "session_start"),
            uuid=data.get("uuid", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            session_id=data.get("session_id", ""),
            project_id=data.get("project_id", ""),
            cwd=data.get("cwd", ""),
            git_branch=data.get("git_branch"),
            channel=data.get("channel", "cli"),
            version=data.get("version", ""),
        )


@dataclass
class SessionEnd(SessionRecord):
    """会话结束记录

    记录会话结束时的统计信息：
    - session_id: 会话唯一标识
    - message_count: 消息总数
    - tool_call_count: 工具调用总数
    - skill_call_count: 技能调用总数
    - duration_seconds: 会话持续时间
    """

    type: str = "session_end"
    session_id: str = ""
    message_count: int = 0
    tool_call_count: int = 0
    skill_call_count: int = 0
    duration_seconds: float = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionEnd":
        return cls(
            type=data.get("type", "session_end"),
            uuid=data.get("uuid", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            session_id=data.get("session_id", ""),
            message_count=data.get("message_count", 0),
            tool_call_count=data.get("tool_call_count", 0),
            skill_call_count=data.get("skill_call_count", 0),
            duration_seconds=data.get("duration_seconds", 0),
        )


@dataclass
class UserMessage(SessionRecord):
    """用户消息记录

    记录用户发送的消息：
    - parent_uuid: 父记录 UUID（用于调用链追踪）
    - content: 消息内容
    - media: 媒体文件路径列表
    - images: 图片数据列表
    """

    type: str = "user_message"
    parent_uuid: Optional[str] = None
    content: str = ""
    media: list = field(default_factory=list)
    images: list = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserMessage":
        return cls(
            type=data.get("type", "user_message"),
            uuid=data.get("uuid", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            parent_uuid=data.get("parent_uuid"),
            content=data.get("content", ""),
            media=data.get("media", []),
            images=data.get("images", []),
        )


@dataclass
class AssistantMessage(SessionRecord):
    """助手消息记录

    记录助手的响应：
    - parent_uuid: 父记录 UUID
    - content: 响应内容
    - model: 使用的模型名称
    - stop_reason: 停止原因（end_turn/tool_use等）
    """

    type: str = "assistant_message"
    parent_uuid: Optional[str] = None
    content: str = ""
    model: Optional[str] = None
    stop_reason: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssistantMessage":
        return cls(
            type=data.get("type", "assistant_message"),
            uuid=data.get("uuid", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            parent_uuid=data.get("parent_uuid"),
            content=data.get("content", ""),
            model=data.get("model"),
            stop_reason=data.get("stop_reason"),
        )


@dataclass
class ToolCall(SessionRecord):
    """工具调用记录

    记录工具调用的请求：
    - parent_uuid: 父记录 UUID
    - tool_call_id: 工具调用唯一标识
    - tool_name: 工具名称
    - tool_input: 工具输入参数
    """

    type: str = "tool_call"
    parent_uuid: Optional[str] = None
    tool_call_id: str = ""
    tool_name: str = ""
    tool_input: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolCall":
        return cls(
            type=data.get("type", "tool_call"),
            uuid=data.get("uuid", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            parent_uuid=data.get("parent_uuid"),
            tool_call_id=data.get("tool_call_id", ""),
            tool_name=data.get("tool_name", ""),
            tool_input=data.get("tool_input", {}),
        )


@dataclass
class ToolResult(SessionRecord):
    """工具结果记录

    记录工具调用的结果：
    - tool_call_id: 对应的工具调用 ID
    - output: 工具输出
    - duration_ms: 执行耗时（毫秒）
    - success: 是否成功
    """

    type: str = "tool_result"
    tool_call_id: str = ""
    output: str = ""
    duration_ms: int = 0
    success: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolResult":
        return cls(
            type=data.get("type", "tool_result"),
            uuid=data.get("uuid", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            tool_call_id=data.get("tool_call_id", ""),
            output=data.get("output", ""),
            duration_ms=data.get("duration_ms", 0),
            success=data.get("success", True),
        )


@dataclass
class SkillCall(SessionRecord):
    """技能调用记录

    记录技能调用的请求：
    - parent_uuid: 父记录 UUID
    - skill_call_id: 技能调用唯一标识
    - skill_name: 技能名称
    - skill_args: 技能参数
    """

    type: str = "skill_call"
    parent_uuid: Optional[str] = None
    skill_call_id: str = ""
    skill_name: str = ""
    skill_args: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillCall":
        return cls(
            type=data.get("type", "skill_call"),
            uuid=data.get("uuid", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            parent_uuid=data.get("parent_uuid"),
            skill_call_id=data.get("skill_call_id", ""),
            skill_name=data.get("skill_name", ""),
            skill_args=data.get("skill_args", ""),
        )


@dataclass
class SkillResult(SessionRecord):
    """技能结果记录

    记录技能调用的结果：
    - skill_call_id: 对应的技能调用 ID
    - output: 技能输出
    - success: 是否成功
    """

    type: str = "skill_result"
    skill_call_id: str = ""
    output: str = ""
    success: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillResult":
        return cls(
            type=data.get("type", "skill_result"),
            uuid=data.get("uuid", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            skill_call_id=data.get("skill_call_id", ""),
            output=data.get("output", ""),
            success=data.get("success", True),
        )


@dataclass
class Thinking(SessionRecord):
    """思考过程记录

    记录助手的思考过程（扩展 thinking）：
    - parent_uuid: 父记录 UUID
    - content: 思考内容
    """

    type: str = "thinking"
    parent_uuid: Optional[str] = None
    content: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Thinking":
        return cls(
            type=data.get("type", "thinking"),
            uuid=data.get("uuid", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            parent_uuid=data.get("parent_uuid"),
            content=data.get("content", ""),
        )


@dataclass
class ErrorRecord(SessionRecord):
    """错误记录

    记录执行过程中的错误：
    - parent_uuid: 父记录 UUID
    - error_type: 错误类型
    - message: 错误消息
    - traceback: 堆栈追踪（可选）
    """

    type: str = "error"
    parent_uuid: Optional[str] = None
    error_type: str = ""
    message: str = ""
    traceback: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ErrorRecord":
        return cls(
            type=data.get("type", "error"),
            uuid=data.get("uuid", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            parent_uuid=data.get("parent_uuid"),
            error_type=data.get("error_type", ""),
            message=data.get("message", ""),
            traceback=data.get("traceback"),
        )


# 记录类型映射（用于反序列化）
RECORD_TYPES = {
    "session_start": SessionStart,
    "session_end": SessionEnd,
    "user_message": UserMessage,
    "assistant_message": AssistantMessage,
    "tool_call": ToolCall,
    "tool_result": ToolResult,
    "skill_call": SkillCall,
    "skill_result": SkillResult,
    "thinking": Thinking,
    "error": ErrorRecord,
}


def parse_record(data: Dict[str, Any]) -> Optional[SessionRecord]:
    """从字典解析记录对象

    Args:
        data: 记录数据字典

    Returns:
        对应类型的 SessionRecord 对象，如果类型未知则返回 None
    """
    record_type = data.get("type")
    record_cls = RECORD_TYPES.get(record_type)

    if record_cls:
        return record_cls.from_dict(data)

    return None


def parse_record_from_json(json_str: str) -> Optional[SessionRecord]:
    """从 JSON 字符串解析记录对象

    Args:
        json_str: JSON 格式的记录字符串

    Returns:
        对应类型的 SessionRecord 对象
    """
    try:
        data = json.loads(json_str)
        return parse_record(data)
    except json.JSONDecodeError:
        return None
