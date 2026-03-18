"""对话历史管理"""
from collections import deque
from typing import List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """消息数据类"""
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ConversationHistory:
    """对话历史管理器"""

    def __init__(self, max_length: int = 10):
        self.messages: deque[Message] = deque(maxlen=max_length)

    def add_message(self, role: str, content: str) -> None:
        """添加消息"""
        self.messages.append(Message(role=role, content=content))

    def add_user_message(self, content: str) -> None:
        """添加用户消息"""
        self.add_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        """添加助手消息"""
        self.add_message("assistant", content)

    def get_history(self) -> List[dict]:
        """获取历史记录（LLM 格式）"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]

    def clear(self) -> None:
        """清空历史"""
        self.messages.clear()

    def __len__(self) -> int:
        return len(self.messages)
