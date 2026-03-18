"""对话压缩器

将多轮旧对话压缩为简洁摘要，保留关键信息但大幅减少 token 消耗。
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import json

from anyclaw.agent.token_counter import TokenCounter, get_token_counter


@dataclass
class CompressionResult:
    """压缩结果"""
    original_messages: List[Dict[str, Any]]
    compressed_messages: List[Dict[str, Any]]
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    strategy: str

    @property
    def saved_tokens(self) -> int:
        """节省的 token 数"""
        return self.original_tokens - self.compressed_tokens

    @property
    def compression_ratio_display(self) -> str:
        """压缩率显示"""
        return f"{self.compression_ratio * 100:.1f}%"


class ConversationCompressor:
    """对话压缩器

    支持多种压缩策略：
    - summary: 使用 LLM 生成摘要（需要异步调用）
    - truncate: 简单截断旧消息
    - key_points: 提取关键点
    """

    DEFAULT_COMPRESS_THRESHOLD = 10
    DEFAULT_KEEP_RECENT = 5
    DEFAULT_MAX_SUMMARY_TOKENS = 500

    SUMMARY_PROMPT = """请将以下对话历史压缩为一个简洁的摘要。

要求：
1. 保留关键决策和结论
2. 保留重要的上下文信息
3. 保留待办事项或未完成任务
4. 摘要长度控制在 500 字符以内

对话历史：
{conversation}

请输出摘要（不要添加任何额外说明）："""

    def __init__(
        self,
        counter: Optional[TokenCounter] = None,
        compress_threshold: int = DEFAULT_COMPRESS_THRESHOLD,
        keep_recent: int = DEFAULT_KEEP_RECENT,
        max_summary_tokens: int = DEFAULT_MAX_SUMMARY_TOKENS,
    ):
        """初始化压缩器

        Args:
            counter: Token 计数器
            compress_threshold: 触发压缩的消息数阈值
            keep_recent: 保留最近的 N 轮对话
            max_summary_tokens: 摘要最大 token 数
        """
        self.counter = counter or get_token_counter()
        self.compress_threshold = compress_threshold
        self.keep_recent = keep_recent
        self.max_summary_tokens = max_summary_tokens

    def needs_compression(self, messages: List[Dict[str, Any]]) -> bool:
        """检查是否需要压缩

        Args:
            messages: 消息列表

        Returns:
            是否需要压缩
        """
        return len(messages) > self.compress_threshold

    def _separate_messages(
        self,
        messages: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """分离要压缩和保留的消息

        Args:
            messages: 消息列表

        Returns:
            (要压缩的消息, 保留的消息)
        """
        if len(messages) <= self.keep_recent:
            return [], messages

        # 保护系统消息
        system_messages = [m for m in messages if m.get("role") == "system"]
        non_system = [m for m in messages if m.get("role") != "system"]

        # 分离
        to_compress = non_system[:-self.keep_recent]
        to_keep = non_system[-self.keep_recent:]

        return to_compress, system_messages + to_keep

    def _format_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """格式化对话为文本

        Args:
            messages: 消息列表

        Returns:
            格式化的对话文本
        """
        lines = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if isinstance(content, list):
                content = " ".join(str(c) for c in content)
            lines.append(f"[{role}]: {content}")

        return "\n".join(lines)

    async def compress(
        self,
        messages: List[Dict[str, Any]],
        strategy: str = "truncate",
        llm_call: Optional[callable] = None,
    ) -> CompressionResult:
        """压缩对话历史

        Args:
            messages: 消息列表
            strategy: 压缩策略 (summary/truncate/key_points)
            llm_call: LLM 调用函数（summary 策略需要）

        Returns:
            CompressionResult 压缩结果
        """
        if not self.needs_compression(messages):
            return CompressionResult(
                original_messages=messages,
                compressed_messages=messages,
                original_tokens=self._count_tokens(messages),
                compressed_tokens=self._count_tokens(messages),
                compression_ratio=1.0,
                strategy="none",
            )

        to_compress, to_keep = self._separate_messages(messages)
        original_tokens = self._count_tokens(messages)

        if not to_compress:
            return CompressionResult(
                original_messages=messages,
                compressed_messages=messages,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                compression_ratio=1.0,
                strategy="none",
            )

        # 根据策略压缩
        if strategy == "summary" and llm_call:
            compressed = await self._summarize(to_compress, llm_call)
        elif strategy == "key_points":
            compressed = self._extract_key_points(to_compress)
        else:
            compressed = self._truncate(to_compress)

        # 合并结果
        result_messages = self._merge_messages(compressed, to_keep)
        compressed_tokens = self._count_tokens(result_messages)

        return CompressionResult(
            original_messages=messages,
            compressed_messages=result_messages,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 1.0,
            strategy=strategy,
        )

    async def _summarize(
        self,
        messages: List[Dict[str, Any]],
        llm_call: callable,
    ) -> List[Dict[str, Any]]:
        """使用 LLM 生成摘要

        Args:
            messages: 要压缩的消息
            llm_call: LLM 调用函数

        Returns:
            包含摘要的消息列表
        """
        try:
            conversation = self._format_conversation(messages)
            prompt = self.SUMMARY_PROMPT.format(conversation=conversation)

            # 调用 LLM
            summary = await llm_call(prompt)

            # 限制摘要长度
            if self.counter.count(summary) > self.max_summary_tokens:
                summary = summary[:self.max_summary_tokens * 4]  # 粗略估计

            return [{
                "role": "system",
                "content": f"[对话摘要]\n{summary}",
                "metadata": {"compressed": True, "original_count": len(messages)}
            }]

        except Exception as e:
            # 失败时回退到截断
            return self._truncate(messages)

    def _truncate(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """简单截断策略

        Args:
            messages: 要压缩的消息

        Returns:
            截断后的消息列表
        """
        # 保留最后 3 条消息
        kept = messages[-3:] if len(messages) > 3 else messages

        # 添加截断标记
        if len(messages) > 3:
            return [{
                "role": "system",
                "content": f"[已截断 {len(messages) - 3} 条旧消息]",
                "metadata": {"compressed": True, "strategy": "truncate"}
            }] + kept

        return kept

    def _extract_key_points(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取关键点（简化版）

        Args:
            messages: 消息列表

        Returns:
            包含关键点的消息列表
        """
        key_points = []

        # 简单的关键词检测
        important_keywords = [
            "决定", "decision", "重要", "important",
            "结论", "conclusion", "待办", "todo",
            "注意", "note", "记住", "remember",
        ]

        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, list):
                content = " ".join(str(c) for c in content)

            # 检测重要消息
            if any(kw in content.lower() for kw in important_keywords):
                key_points.append(f"- {content[:200]}")

        if key_points:
            return [{
                "role": "system",
                "content": "[关键点摘要]\n" + "\n".join(key_points[:10]),
                "metadata": {"compressed": True, "strategy": "key_points"}
            }]

        # 没有关键点时使用截断
        return self._truncate(messages)

    def _merge_messages(
        self,
        compressed: List[Dict[str, Any]],
        to_keep: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """合并压缩后的消息和保留的消息

        Args:
            compressed: 压缩后的消息
            to_keep: 保留的消息

        Returns:
            合并后的消息列表
        """
        # 确保系统消息在最前面
        system_messages = [m for m in to_keep if m.get("role") == "system"]
        other_keep = [m for m in to_keep if m.get("role") != "system"]

        # 压缩后的消息通常是系统消息
        compressed_system = [m for m in compressed if m.get("role") == "system"]

        # 合并系统消息
        merged_system = system_messages + compressed_system

        return merged_system + other_keep

    def _count_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """计算消息列表的 token 数

        Args:
            messages: 消息列表

        Returns:
            token 数
        """
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, list):
                content = " ".join(str(c) for c in content)
            total += self.counter.count(content) + 4  # 消息格式开销

        return total

    def get_compression_stats(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取压缩统计信息

        Args:
            messages: 消息列表

        Returns:
            统计信息
        """
        return {
            "total_messages": len(messages),
            "total_tokens": self._count_tokens(messages),
            "needs_compression": self.needs_compression(messages),
            "threshold": self.compress_threshold,
            "keep_recent": self.keep_recent,
        }


# 全局压缩器实例
_compressor: Optional[ConversationCompressor] = None


def get_compressor(
    compress_threshold: Optional[int] = None,
    keep_recent: Optional[int] = None,
) -> ConversationCompressor:
    """获取全局压缩器实例

    Args:
        compress_threshold: 压缩阈值
        keep_recent: 保留最近消息数

    Returns:
        ConversationCompressor 实例
    """
    global _compressor

    if _compressor is None:
        _compressor = ConversationCompressor(
            compress_threshold=compress_threshold or ConversationCompressor.DEFAULT_COMPRESS_THRESHOLD,
            keep_recent=keep_recent or ConversationCompressor.DEFAULT_KEEP_RECENT,
        )

    return _compressor


def reset_compressor() -> None:
    """重置全局压缩器"""
    global _compressor
    _compressor = None
