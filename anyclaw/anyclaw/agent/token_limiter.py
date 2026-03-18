"""Token 限制器

管理 token 使用限制，提供警告和阻止功能。
"""

from typing import Optional
from dataclasses import dataclass

from anyclaw.agent.token_counter import TokenCounter, get_token_counter


@dataclass
class TokenLimitStatus:
    """Token 限制状态"""
    used: int
    soft_limit: int
    hard_limit: int
    usage_ratio: float
    should_warn: bool
    is_over_soft: bool
    is_over_hard: bool
    remaining: int
    context_window: int

    @property
    def is_ok(self) -> bool:
        """是否在正常范围内"""
        return not self.is_over_soft

    @property
    def usage_percent(self) -> float:
        """使用百分比（相对于软限制）"""
        return self.usage_ratio * 100


class TokenLimiter:
    """Token 限制器

    管理 token 使用限制，在接近或超过限制时发出警告或阻止操作。
    """

    DEFAULT_SOFT_LIMIT = 100000
    DEFAULT_HARD_LIMIT = 200000
    DEFAULT_WARNING_THRESHOLD = 0.8

    def __init__(
        self,
        counter: Optional[TokenCounter] = None,
        soft_limit: int = DEFAULT_SOFT_LIMIT,
        hard_limit: int = DEFAULT_HARD_LIMIT,
        warning_threshold: float = DEFAULT_WARNING_THRESHOLD,
        warning_enabled: bool = True,
    ):
        """初始化 Token 限制器

        Args:
            counter: Token 计数器实例
            soft_limit: 软限制（触发警告）
            hard_limit: 硬限制（阻止输入）
            warning_threshold: 警告阈值（相对于软限制的比例）
            warning_enabled: 是否启用警告
        """
        self.counter = counter or get_token_counter()
        self.soft_limit = soft_limit
        self.hard_limit = hard_limit
        self.warning_threshold = warning_threshold
        self.warning_enabled = warning_enabled

    def check(self, messages: list, model: Optional[str] = None) -> TokenLimitStatus:
        """检查 token 使用情况

        Args:
            messages: 消息列表
            model: 模型名称

        Returns:
            TokenLimitStatus 状态对象
        """
        stats = self.counter.count_messages(messages)
        used = stats["total"]
        context_window = self.counter.get_context_window(model)

        # 计算使用比例（相对于软限制）
        usage_ratio = used / self.soft_limit if self.soft_limit > 0 else 0

        # 计算剩余量
        remaining = max(0, self.soft_limit - used)

        return TokenLimitStatus(
            used=used,
            soft_limit=self.soft_limit,
            hard_limit=self.hard_limit,
            usage_ratio=usage_ratio,
            should_warn=self._should_warn(usage_ratio),
            is_over_soft=used >= self.soft_limit,
            is_over_hard=used >= self.hard_limit,
            remaining=remaining,
            context_window=context_window,
        )

    def _should_warn(self, usage_ratio: float) -> bool:
        """判断是否需要发出警告"""
        if not self.warning_enabled:
            return False
        return usage_ratio >= self.warning_threshold

    def should_warn(self, messages: list) -> bool:
        """检查是否应该发出警告

        Args:
            messages: 消息列表

        Returns:
            是否需要警告
        """
        status = self.check(messages)
        return status.should_warn

    def is_over_limit(self, messages: list, hard: bool = False) -> bool:
        """检查是否超过限制

        Args:
            messages: 消息列表
            hard: 是否检查硬限制

        Returns:
            是否超过限制
        """
        status = self.check(messages)
        return status.is_over_hard if hard else status.is_over_soft

    def get_warning_message(self, status: TokenLimitStatus) -> Optional[str]:
        """获取警告消息

        Args:
            status: Token 限制状态

        Returns:
            警告消息，如果不需要警告则返回 None
        """
        if not status.should_warn and not status.is_over_soft:
            return None

        if status.is_over_hard:
            return (
                f"⚠️ Token 硬限制已达到！\n"
                f"  已使用: {status.used:,} / {status.hard_limit:,}\n"
                f"  请压缩对话或开始新会话。"
            )
        elif status.is_over_soft:
            return (
                f"⚠️ Token 软限制已超过！\n"
                f"  已使用: {status.used:,} / {status.soft_limit:,} ({status.usage_percent:.1f}%)\n"
                f"  建议压缩对话或开始新会话。"
            )
        elif status.should_warn:
            return (
                f"💡 Token 使用提醒: {status.used:,} / {status.soft_limit:,} ({status.usage_percent:.1f}%)\n"
                f"   剩余: {status.remaining:,} tokens"
            )

        return None

    def update_limits(
        self,
        soft_limit: Optional[int] = None,
        hard_limit: Optional[int] = None,
        warning_threshold: Optional[float] = None,
        warning_enabled: Optional[bool] = None,
    ) -> None:
        """更新限制设置

        Args:
            soft_limit: 新的软限制
            hard_limit: 新的硬限制
            warning_threshold: 新的警告阈值
            warning_enabled: 是否启用警告
        """
        if soft_limit is not None:
            self.soft_limit = soft_limit
        if hard_limit is not None:
            self.hard_limit = hard_limit
        if warning_threshold is not None:
            self.warning_threshold = warning_threshold
        if warning_enabled is not None:
            self.warning_enabled = warning_enabled

    def __repr__(self) -> str:
        return (
            f"TokenLimiter(soft={self.soft_limit}, hard={self.hard_limit}, "
            f"threshold={self.warning_threshold}, enabled={self.warning_enabled})"
        )


# 全局限制器实例（延迟初始化）
_token_limiter: Optional[TokenLimiter] = None


def get_token_limiter(
    soft_limit: Optional[int] = None,
    hard_limit: Optional[int] = None,
    warning_threshold: Optional[float] = None,
    warning_enabled: Optional[bool] = None,
) -> TokenLimiter:
    """获取全局 Token 限制器实例

    Args:
        soft_limit: 软限制
        hard_limit: 硬限制
        warning_threshold: 警告阈值
        warning_enabled: 是否启用警告

    Returns:
        TokenLimiter 实例
    """
    global _token_limiter

    if _token_limiter is None:
        _token_limiter = TokenLimiter(
            soft_limit=soft_limit or TokenLimiter.DEFAULT_SOFT_LIMIT,
            hard_limit=hard_limit or TokenLimiter.DEFAULT_HARD_LIMIT,
            warning_threshold=warning_threshold or TokenLimiter.DEFAULT_WARNING_THRESHOLD,
            warning_enabled=warning_enabled if warning_enabled is not None else True,
        )
    elif any([
        soft_limit is not None,
        hard_limit is not None,
        warning_threshold is not None,
        warning_enabled is not None,
    ]):
        _token_limiter.update_limits(
            soft_limit=soft_limit,
            hard_limit=hard_limit,
            warning_threshold=warning_threshold,
            warning_enabled=warning_enabled,
        )

    return _token_limiter


def reset_token_limiter() -> None:
    """重置全局 Token 限制器"""
    global _token_limiter
    _token_limiter = None
