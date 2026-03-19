"""Session data models

完美复刻 nanobot 的 Session 数据结构，支持：
- JSONL 格式持久化
- 工具调用边界检测
- 会话元数据
- 媒体和图片支持
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


logger = logging.getLogger(__name__)


@dataclass
class SessionMessage:
    """
    单条会话消息

    与 nanobot 兼容的数据结构
    """
    role: str                              # "user" | "assistant" | "tool" | "system"
    content: str = ""                    # 消息内容（默认空字符串）
    timestamp: str = None             # ISO 格式时间戳
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)  # Tool 调用列表
    tool_call_id: str = None           # Tool 调用关联 ID
    name: str = None                   # Tool 名称（role="tool" 时）
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
            role=data.get("role", ""),
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
    - JSONL 格式持久化
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
        content: str = None,
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
            if message.role == "user":
                sliced = sliced[i:]
                break

        # 一些 provider 会拒绝孤立的 tool 结果
        # 检测 tool 结果是否有匹配的 assistant tool_call
        start = self._find_legal_start(sliced)

        if start:
            sliced = sliced[start:]

        # 转换为字典格式
        out: List[Dict[str, Any]] = []
        for message in sliced:
            entry: Dict[str, Any] = {"role": message.role, "content": message.content}

            # 添加工具调用信息
            if message.tool_calls:
                entry["tool_calls"] = message.tool_calls

            # 添加工具调用 ID
            if message.tool_call_id:
                entry["tool_call_id"] = message.tool_call_id

            # 添加工具名称（role="tool" 时）
            if message.name:
                entry["name"] = message.name

            # 添加时间戳
            if message.timestamp:
                entry["timestamp"] = message.timestamp

            # 添加媒体
            if message.media:
                entry["media"] = message.media

            # 添加图片
            if message.images:
                entry["images"] = message.images

            # 添加内部元数据
            for key, value in message._metadata.items():
                entry[key] = value

            out.append(entry)

        return out

    @staticmethod
    def _find_legal_start(messages: List[SessionMessage]) -> int:
        """
        找到第一个合法的 tool-call 边界

        确保不会在 tool 结果中间截断

        Args:
            messages: 消息列表

        Returns:
            第一个合法的起始索引
        """
        declared: set[str] = set()
        start = 0

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
                    return i + 1  # 返回合法的起始位置
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

        self.last_consolidated = len(self.messages)
        logger.debug(f"Session saved: {self.key} ({len(self.messages)} messages)")

    @staticmethod
    def load(path) -> "Session":
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
                key=metadata.get("key") or path.stem.replace("_", ":", 1),
                messages=messages,
                created_at=created_at or datetime.now(),
                updated_at=updated_at or datetime.now(),
                metadata=metadata,
                last_consolidated=last_consolidated
            )
        except Exception as e:
            logger.error(f"Failed to load session from {path}: {e}")
            return None
