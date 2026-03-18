"""Token 计数器

使用 tiktoken 进行精确的 token 计数，支持多种模型编码器。
"""

import os
from typing import Optional

# tiktoken 是可选依赖
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    tiktoken = None
    TIKTOKEN_AVAILABLE = False


class TokenCounter:
    """Token 计数器

    支持多种模型的 token 计数，包括精确计数和估算方法。
    """

    # 模型到编码器的映射
    ENCODING_MAP = {
        # OpenAI GPT-4 系列
        "gpt-4": "cl100k_base",
        "gpt-4-turbo": "cl100k_base",
        "gpt-4-turbo-preview": "cl100k_base",
        "gpt-4o": "o200k_base",
        "gpt-4o-mini": "o200k_base",
        "gpt-4-32k": "cl100k_base",

        # OpenAI GPT-3.5 系列
        "gpt-3.5-turbo": "cl100k_base",
        "gpt-3.5-turbo-16k": "cl100k_base",

        # OpenAI o1 系列
        "o1-preview": "o200k_base",
        "o1-mini": "o200k_base",

        # Claude 系列（使用 cl100k 近似）
        "claude-3-opus": "cl100k_base",
        "claude-3-sonnet": "cl100k_base",
        "claude-3-haiku": "cl100k_base",
        "claude-3-5-sonnet": "cl100k_base",
        "claude-3-5-haiku": "cl100k_base",

        # ZAI/GLM 系列（使用 cl100k 近似）
        "zai/glm-4": "cl100k_base",
        "zai/glm-4-flash": "cl100k_base",
        "zai/glm-5": "cl100k_base",
    }

    # 默认编码器
    DEFAULT_ENCODING = "cl100k_base"

    # 模型上下文窗口大小
    CONTEXT_WINDOWS = {
        "gpt-4": 8192,
        "gpt-4-turbo": 128000,
        "gpt-4-turbo-preview": 128000,
        "gpt-4o": 128000,
        "gpt-4o-mini": 128000,
        "gpt-4-32k": 32768,
        "gpt-3.5-turbo": 16385,
        "gpt-3.5-turbo-16k": 16385,
        "o1-preview": 128000,
        "o1-mini": 128000,
        "claude-3-opus": 200000,
        "claude-3-sonnet": 200000,
        "claude-3-haiku": 200000,
        "claude-3-5-sonnet": 200000,
        "claude-3-5-haiku": 200000,
        "zai/glm-4": 128000,
        "zai/glm-4-flash": 128000,
        "zai/glm-5": 128000,
    }

    def __init__(self, model: Optional[str] = None):
        """初始化 Token 计数器

        Args:
            model: 模型名称，用于选择编码器
        """
        self.model = model
        self._encoding = None
        self._encoding_name = None

        if model:
            self._init_encoding(model)

    def _init_encoding(self, model: str) -> None:
        """初始化编码器"""
        # 获取编码器名称
        self._encoding_name = self._get_encoding_name(model)

        # 尝试加载编码器
        if TIKTOKEN_AVAILABLE:
            try:
                self._encoding = tiktoken.get_encoding(self._encoding_name)
            except Exception:
                # 编码器不存在，使用默认
                try:
                    self._encoding = tiktoken.get_encoding(self.DEFAULT_ENCODING)
                except Exception:
                    self._encoding = None

    def _get_encoding_name(self, model: str) -> str:
        """获取模型对应的编码器名称"""
        # 精确匹配
        if model in self.ENCODING_MAP:
            return self.ENCODING_MAP[model]

        # 前缀匹配
        model_lower = model.lower()
        for key, encoding in self.ENCODING_MAP.items():
            if model_lower.startswith(key.lower()):
                return encoding

        # 默认编码器
        return self.DEFAULT_ENCODING

    def get_context_window(self, model: Optional[str] = None) -> int:
        """获取模型的上下文窗口大小

        Args:
            model: 模型名称（可选，默认使用初始化时的模型）

        Returns:
            上下文窗口大小
        """
        model = model or self.model
        if not model:
            return 128000  # 默认值

        # 精确匹配
        if model in self.CONTEXT_WINDOWS:
            return self.CONTEXT_WINDOWS[model]

        # 前缀匹配
        model_lower = model.lower()
        for key, window in self.CONTEXT_WINDOWS.items():
            if model_lower.startswith(key.lower()):
                return window

        return 128000  # 默认值

    def count(self, text: str) -> int:
        """计算文本的 token 数

        Args:
            text: 要计算的文本

        Returns:
            token 数量
        """
        if not text:
            return 0

        # 使用 tiktoken 精确计数
        if self._encoding:
            try:
                return len(self._encoding.encode(text))
            except Exception:
                pass

        # 估算方法：平均 4 字符 = 1 token
        # 中文字符通常占用更多 token
        char_count = len(text)

        # 检测中文字符比例
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        chinese_ratio = chinese_chars / char_count if char_count > 0 else 0

        # 中文平均 2 字符 = 1 token，英文平均 4 字符 = 1 token
        if chinese_ratio > 0.5:
            return int(char_count / 2)
        else:
            return int(char_count / 4)

    def count_messages(self, messages: list) -> dict:
        """计算消息列表的 token 分布

        Args:
            messages: 消息列表，每条消息包含 role 和 content

        Returns:
            包含总数和分布的字典
        """
        result = {
            "total": 0,
            "breakdown": {},
            "details": [],
        }

        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # 计算内容的 token 数
            content_tokens = self.count(content) if isinstance(content, str) else 0

            # 消息格式开销（role, separators 等）
            # 通常每条消息有 4-10 个 token 的开销
            overhead = 4

            msg_tokens = content_tokens + overhead

            result["total"] += msg_tokens
            result["breakdown"][role] = result["breakdown"].get(role, 0) + msg_tokens
            result["details"].append({
                "role": role,
                "tokens": msg_tokens,
                "content_tokens": content_tokens,
            })

        return result

    def estimate_remaining(self, messages: list, model: Optional[str] = None) -> dict:
        """估算剩余可用 token

        Args:
            messages: 当前消息列表
            model: 模型名称

        Returns:
            包含使用情况和剩余量的字典
        """
        stats = self.count_messages(messages)
        context_window = self.get_context_window(model)
        used = stats["total"]
        remaining = max(0, context_window - used)

        return {
            "used": used,
            "remaining": remaining,
            "context_window": context_window,
            "usage_percent": (used / context_window * 100) if context_window > 0 else 0,
            "breakdown": stats["breakdown"],
        }

    @property
    def encoding_name(self) -> str:
        """当前使用的编码器名称"""
        return self._encoding_name or self.DEFAULT_ENCODING

    @property
    def tiktoken_available(self) -> bool:
        """tiktoken 是否可用"""
        return TIKTOKEN_AVAILABLE and self._encoding is not None

    def __repr__(self) -> str:
        return f"TokenCounter(model={self.model}, encoding={self.encoding_name})"


# 全局计数器实例（延迟初始化）
_token_counter: Optional[TokenCounter] = None


def get_token_counter(model: Optional[str] = None) -> TokenCounter:
    """获取全局 Token 计数器实例

    Args:
        model: 模型名称

    Returns:
        TokenCounter 实例
    """
    global _token_counter

    if _token_counter is None or (model and _token_counter.model != model):
        _token_counter = TokenCounter(model)

    return _token_counter


def reset_token_counter() -> None:
    """重置全局 Token 计数器"""
    global _token_counter
    _token_counter = None
