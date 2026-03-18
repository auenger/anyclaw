"""记忆自动化

自动识别需要记忆的信息并生成更新建议。
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import re

from anyclaw.memory.manager import MemoryManager


@dataclass
class MemorySuggestion:
    """记忆更新建议"""
    type: str  # preference, decision, note, context
    content: str
    section: str  # 对应 MEMORY.md 的部分
    original_message: str
    confidence: float  # 0.0 - 1.0


class MemoryAutomation:
    """记忆自动化处理

    自动识别对话中的重要信息并生成记忆更新建议。
    """

    # 重要信息模式
    IMPORTANT_PATTERNS = [
        # 偏好相关
        (r"我喜欢(.{1,50})", "preference", "偏好", 0.8),
        (r"我讨厌(.{1,50})", "preference", "偏好", 0.8),
        (r"我偏好(.{1,50})", "preference", "偏好", 0.9),
        (r"我的(?:首选|常用)的(.{1,30})是(.{1,30})", "preference", "偏好", 0.9),

        # 提醒相关
        (r"记住[：:]?(.{1,100})", "note", "重要笔记", 0.9),
        (r"别忘了[：:]?(.{1,100})", "note", "重要笔记", 0.9),
        (r"记得[：:]?(.{1,100})", "note", "重要笔记", 0.7),

        # 决策相关
        (r"决定[：:]?(.{1,100})", "decision", "重要笔记", 0.8),
        (r"确定[：:]?(.{1,100})", "decision", "重要笔记", 0.7),
        (r"我们(?:约定|说好)(.{1,100})", "decision", "重要笔记", 0.8),

        # 个人信息
        (r"我叫(.{1,20})", "info", "用户信息", 0.9),
        (r"我是(.{1,50})", "info", "用户信息", 0.7),
        (r"我的名字是(.{1,20})", "info", "用户信息", 0.9),

        # 项目上下文
        (r"我在做(.{1,100})", "context", "项目上下文", 0.7),
        (r"项目(?:名|叫)(.{1,50})", "context", "项目上下文", 0.8),
    ]

    # 否定模式（不应该记忆的）
    NEGATIVE_PATTERNS = [
        r"^不[，。]",
        r"^没[有关系的]",
        r"^算了",
        r"^算了[，。]",
    ]

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        """初始化记忆自动化

        Args:
            memory_manager: 记忆管理器实例
        """
        self.memory_manager = memory_manager

    def analyze_message(self, message: str) -> Optional[MemorySuggestion]:
        """分析消息是否包含重要信息

        Args:
            message: 用户消息

        Returns:
            记忆建议，如果不重要则返回 None
        """
        # 检查否定模式
        for pattern in self.NEGATIVE_PATTERNS:
            if re.match(pattern, message, re.IGNORECASE):
                return None

        # 检查重要模式
        for pattern, suggestion_type, section, confidence in self.IMPORTANT_PATTERNS:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                # 提取完整匹配内容
                content = match.group(0)

                # 如果有捕获组，使用捕获组内容
                if match.groups():
                    content = " ".join(g for g in match.groups() if g)

                return MemorySuggestion(
                    type=suggestion_type,
                    content=content.strip(),
                    section=section,
                    original_message=message,
                    confidence=confidence,
                )

        return None

    def analyze_conversation(self, messages: List[Dict[str, str]]) -> List[MemorySuggestion]:
        """分析整个对话

        Args:
            messages: 消息列表

        Returns:
            记忆建议列表
        """
        suggestions = []

        for msg in messages:
            # 只分析用户消息
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    suggestion = self.analyze_message(content)
                    if suggestion:
                        suggestions.append(suggestion)

        return suggestions

    def should_update_memory(self, context: Dict[str, Any]) -> bool:
        """判断是否应该更新记忆

        Args:
            context: 上下文信息

        Returns:
            是否应该更新
        """
        # 检查是否有高置信度的建议
        suggestions = context.get("suggestions", [])
        if not suggestions:
            return False

        # 检查是否有置信度超过阈值的建议
        threshold = context.get("confidence_threshold", 0.7)
        for suggestion in suggestions:
            if suggestion.confidence >= threshold:
                return True

        return False

    def suggest_memory_update(self, info: MemorySuggestion) -> str:
        """生成记忆更新建议文本

        Args:
            info: 记忆建议

        Returns:
            建议文本
        """
        type_names = {
            "preference": "偏好",
            "decision": "决策",
            "note": "笔记",
            "info": "信息",
            "context": "项目",
        }

        type_name = type_names.get(info.type, "信息")

        if info.confidence >= 0.9:
            return f"我注意到你说：「{info.content}」。这看起来很重要，要我把这添加到记忆的「{info.section}」部分吗？"
        else:
            return f"你说：「{info.content}」。这看起来是有用的{type_name}信息，需要我记录下来吗？"

    def generate_update_content(self, info: MemorySuggestion) -> str:
        """生成要添加到记忆的内容

        Args:
            info: 记忆建议

        Returns:
            格式化的内容
        """
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d")

        if info.type == "preference":
            return f"- {info.content} (记录于 {timestamp})"
        elif info.type == "decision":
            return f"- 决定: {info.content} ({timestamp})"
        elif info.type == "note":
            return f"- {info.content} ({timestamp})"
        elif info.type == "info":
            return f"- {info.content}"
        elif info.type == "context":
            return f"- {info.content} ({timestamp})"
        else:
            return f"- {info.content} ({timestamp})"


# 全局实例
_memory_automation: Optional[MemoryAutomation] = None


def get_memory_automation(memory_manager: Optional[MemoryManager] = None) -> MemoryAutomation:
    """获取全局记忆自动化实例

    Args:
        memory_manager: 记忆管理器

    Returns:
        MemoryAutomation 实例
    """
    global _memory_automation

    if _memory_automation is None:
        _memory_automation = MemoryAutomation(memory_manager=memory_manager)

    return _memory_automation


def reset_memory_automation() -> None:
    """重置全局记忆自动化实例"""
    global _memory_automation
    _memory_automation = None
