"""滑动窗口管理器

使用滑动窗口保留最近的 N 条消息，自动丢弃更早的消息。
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class WindowResult:
    """滑动窗口结果"""
    original_messages: List[Dict[str, Any]]
    windowed_messages: List[Dict[str, Any]]
    protected_count: int
    removed_count: int
    window_size: int


class SlidingWindow:
    """滑动窗口管理器

    保留最近的 N 条消息，支持：
    - 保护系统消息
    - 保护标记为重要的消息
    - 动态调整窗口大小
    """

    DEFAULT_WINDOW_SIZE = 20

    def __init__(
        self,
        window_size: int = DEFAULT_WINDOW_SIZE,
        protect_system: bool = True,
        protect_tagged: bool = True,
        protect_tag: str = "important",
    ):
        """初始化滑动窗口

        Args:
            window_size: 窗口大小（保留的消息数）
            protect_system: 是否保护系统消息
            protect_tagged: 是否保护标记消息
            protect_tag: 保护标记的键名
        """
        self.window_size = window_size
        self._protect_system = protect_system
        self._protect_tagged = protect_tagged
        self._protect_tag = protect_tag

    @property
    def protect_tagged(self) -> bool:
        """是否保护标记消息"""
        return self._protect_tagged

    @property
    def protect_system(self) -> bool:
        """是否保护系统消息"""
        return self._protect_system

    def apply(
        self,
        messages: List[Dict[str, Any]],
        dynamic_token_limit: Optional[int] = None,
    ) -> WindowResult:
        """应用滑动窗口

        Args:
            messages: 消息列表
            dynamic_token_limit: 动态 token 限制（可选）

        Returns:
            WindowResult 结果
        """
        if len(messages) <= self.window_size:
            return WindowResult(
                original_messages=messages,
                windowed_messages=messages,
                protected_count=0,
                removed_count=0,
                window_size=self.window_size,
            )

        # 分离受保护和普通消息
        protected = []
        regular = []

        for msg in messages:
            if self._is_protected(msg):
                protected.append(msg)
            else:
                regular.append(msg)

        # 计算可用窗口大小
        available_size = max(0, self.window_size - len(protected))

        # 保留最近的普通消息
        kept_regular = regular[-available_size:] if available_size > 0 else []

        # 合并结果（保持原始顺序）
        result = self._merge_preserving_order(messages, protected, kept_regular)

        return WindowResult(
            original_messages=messages,
            windowed_messages=result,
            protected_count=len(protected),
            removed_count=len(regular) - len(kept_regular),
            window_size=self.window_size,
        )

    def _is_protected(self, message: Dict[str, Any]) -> bool:
        """检查消息是否受保护

        Args:
            message: 消息

        Returns:
            是否受保护
        """
        # 保护系统消息
        if self._protect_system and message.get("role") == "system":
            return True

        # 保护标记消息
        if self._protect_tagged:
            metadata = message.get("metadata", {})
            if metadata.get(self._protect_tag):
                return True
            # 也检查消息内容中的标记
            content = message.get("content", "")
            if isinstance(content, str) and f"[{self._protect_tag}]" in content.lower():
                return True

        return False

    def _merge_preserving_order(
        self,
        original: List[Dict[str, Any]],
        protected: List[Dict[str, Any]],
        kept_regular: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """保持原始顺序合并消息

        Args:
            original: 原始消息列表
            protected: 受保护的消息
            kept_regular: 保留的普通消息

        Returns:
            合并后的消息列表
        """
        protected_set = {id(m) for m in protected}
        kept_set = {id(m) for m in kept_regular}

        return [m for m in original if id(m) in protected_set or id(m) in kept_set]

    def set_window_size(self, size: int) -> None:
        """设置窗口大小

        Args:
            size: 新的窗口大小
        """
        self.window_size = max(1, size)

    def get_stats(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取窗口统计信息

        Args:
            messages: 消息列表

        Returns:
            统计信息
        """
        protected = [m for m in messages if self._is_protected(m)]
        regular = [m for m in messages if not self._is_protected(m)]

        return {
            "total_messages": len(messages),
            "protected_messages": len(protected),
            "regular_messages": len(regular),
            "window_size": self.window_size,
            "would_remove": max(0, len(regular) - (self.window_size - len(protected))),
        }


# 全局窗口实例
_sliding_window: Optional[SlidingWindow] = None


def get_sliding_window(
    window_size: Optional[int] = None,
    protect_system: bool = True,
    protect_tagged: bool = True,
) -> SlidingWindow:
    """获取全局滑动窗口实例"""
    global _sliding_window

    if _sliding_window is None:
        _sliding_window = SlidingWindow(
            window_size=window_size or SlidingWindow.DEFAULT_WINDOW_SIZE,
            protect_system=protect_system,
            protect_tagged=protect_tagged,
        )

    return _sliding_window


def reset_sliding_window() -> None:
    """重置全局滑动窗口"""
    global _sliding_window
    _sliding_window = None
