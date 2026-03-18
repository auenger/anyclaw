"""Token 计数器和限制器单元测试"""

import pytest

from anyclaw.agent.token_counter import (
    TokenCounter,
    get_token_counter,
    reset_token_counter,
    TIKTOKEN_AVAILABLE,
)
from anyclaw.agent.token_limiter import (
    TokenLimiter,
    TokenLimitStatus,
    get_token_limiter,
    reset_token_limiter,
)


class TestTokenCounter:
    """TokenCounter 测试"""

    def test_init_default(self):
        """测试默认初始化"""
        counter = TokenCounter()
        assert counter.model is None

    def test_init_with_model(self):
        """测试带模型初始化"""
        counter = TokenCounter("gpt-4")
        assert counter.model == "gpt-4"

    def test_count_empty_text(self):
        """测试空文本计数"""
        counter = TokenCounter()
        assert counter.count("") == 0

    def test_count_simple_text(self):
        """测试简单文本计数"""
        counter = TokenCounter()
        text = "Hello, world!"
        tokens = counter.count(text)
        assert tokens > 0
        assert tokens < len(text) * 2  # 合理范围

    def test_count_chinese_text(self):
        """测试中文文本计数"""
        counter = TokenCounter()
        text = "这是一个中文测试文本"
        tokens = counter.count(text)
        assert tokens > 0

    def test_count_messages_empty(self):
        """测试空消息列表"""
        counter = TokenCounter()
        result = counter.count_messages([])
        assert result["total"] == 0
        assert result["breakdown"] == {}

    def test_count_messages_single(self):
        """测试单条消息"""
        counter = TokenCounter()
        messages = [{"role": "user", "content": "Hello"}]
        result = counter.count_messages(messages)

        assert result["total"] > 0
        assert "user" in result["breakdown"]
        assert len(result["details"]) == 1

    def test_count_messages_multiple(self):
        """测试多条消息"""
        counter = TokenCounter()
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
        ]
        result = counter.count_messages(messages)

        assert result["total"] > 0
        assert "system" in result["breakdown"]
        assert "user" in result["breakdown"]
        assert "assistant" in result["breakdown"]

    def test_encoding_map(self):
        """测试编码器映射"""
        assert "gpt-4" in TokenCounter.ENCODING_MAP
        assert "gpt-4o" in TokenCounter.ENCODING_MAP
        assert "claude-3-opus" in TokenCounter.ENCODING_MAP

    def test_context_window(self):
        """测试上下文窗口"""
        counter = TokenCounter("gpt-4")
        window = counter.get_context_window()
        assert window == 8192

        counter = TokenCounter("gpt-4o")
        window = counter.get_context_window()
        assert window == 128000

    def test_context_window_unknown_model(self):
        """测试未知模型的上下文窗口"""
        counter = TokenCounter("unknown-model")
        window = counter.get_context_window()
        assert window == 128000  # 默认值

    def test_estimate_remaining(self):
        """测试剩余 token 估算"""
        counter = TokenCounter("gpt-4")
        messages = [{"role": "user", "content": "Hello"}]
        result = counter.estimate_remaining(messages)

        assert "used" in result
        assert "remaining" in result
        assert "context_window" in result
        assert "usage_percent" in result
        assert result["context_window"] == 8192

    def test_encoding_name(self):
        """测试编码器名称"""
        counter = TokenCounter("gpt-4o")
        assert counter.encoding_name == "o200k_base"

        counter = TokenCounter("gpt-4")
        assert counter.encoding_name == "cl100k_base"

    def test_tiktoken_available_property(self):
        """测试 tiktoken 可用性"""
        counter = TokenCounter()
        # 属性应该返回布尔值
        assert isinstance(counter.tiktoken_available, bool)


class TestTokenCounterGlobal:
    """全局计数器测试"""

    def test_get_token_counter(self):
        """测试获取全局计数器"""
        reset_token_counter()
        counter1 = get_token_counter()
        counter2 = get_token_counter()
        assert counter1 is counter2

    def test_get_token_counter_with_model(self):
        """测试带模型获取全局计数器"""
        reset_token_counter()
        counter = get_token_counter("gpt-4")
        assert counter.model == "gpt-4"

    def test_reset_token_counter(self):
        """测试重置全局计数器"""
        counter1 = get_token_counter()
        reset_token_counter()
        counter2 = get_token_counter()
        assert counter1 is not counter2


class TestTokenLimiter:
    """TokenLimiter 测试"""

    def test_init_default(self):
        """测试默认初始化"""
        limiter = TokenLimiter()
        assert limiter.soft_limit == TokenLimiter.DEFAULT_SOFT_LIMIT
        assert limiter.hard_limit == TokenLimiter.DEFAULT_HARD_LIMIT
        assert limiter.warning_threshold == TokenLimiter.DEFAULT_WARNING_THRESHOLD

    def test_init_custom(self):
        """测试自定义初始化"""
        limiter = TokenLimiter(
            soft_limit=50000,
            hard_limit=100000,
            warning_threshold=0.7,
        )
        assert limiter.soft_limit == 50000
        assert limiter.hard_limit == 100000
        assert limiter.warning_threshold == 0.7

    def test_check_empty_messages(self):
        """测试空消息列表检查"""
        limiter = TokenLimiter(soft_limit=1000)
        status = limiter.check([])

        assert isinstance(status, TokenLimitStatus)
        assert status.used == 0
        assert status.is_ok is True
        assert status.is_over_soft is False

    def test_check_normal_usage(self):
        """测试正常使用"""
        limiter = TokenLimiter(soft_limit=10000)
        messages = [{"role": "user", "content": "Hello"}]
        status = limiter.check(messages)

        assert status.used > 0
        assert status.used < limiter.soft_limit
        assert status.is_ok is True

    def test_check_over_soft_limit(self):
        """测试超过软限制"""
        limiter = TokenLimiter(soft_limit=10, hard_limit=100)
        # 创建大量消息以超过限制
        messages = [{"role": "user", "content": "This is a test message " * 100}]

        status = limiter.check(messages)
        assert status.is_over_soft is True

    def test_check_over_hard_limit(self):
        """测试超过硬限制"""
        limiter = TokenLimiter(soft_limit=10, hard_limit=20)
        messages = [{"role": "user", "content": "This is a very long test message " * 100}]

        status = limiter.check(messages)
        assert status.is_over_hard is True

    def test_should_warn(self):
        """测试警告判断"""
        limiter = TokenLimiter(soft_limit=100, warning_threshold=0.8)
        messages = [{"role": "user", "content": "Short"}]

        # 低于阈值不应警告
        assert limiter.should_warn(messages) is False

    def test_should_warn_disabled(self):
        """测试禁用警告"""
        limiter = TokenLimiter(soft_limit=10, warning_enabled=False)
        messages = [{"role": "user", "content": "This is a test message"}]

        assert limiter.should_warn(messages) is False

    def test_is_over_limit_soft(self):
        """测试软限制检查"""
        limiter = TokenLimiter(soft_limit=5, hard_limit=100)
        # 创建足够长的消息以超过软限制
        messages = [{"role": "user", "content": "This is a test message that should be long enough to exceed the soft limit"}]

        assert limiter.is_over_limit(messages, hard=False) is True

    def test_is_over_limit_hard(self):
        """测试硬限制检查"""
        limiter = TokenLimiter(soft_limit=5, hard_limit=500)
        # 创建足够长的消息
        messages = [{"role": "user", "content": "This is a test message that should be long enough to exceed the soft limit"}]

        # 软限制应该超过
        assert limiter.is_over_limit(messages, hard=False) is True
        # 硬限制不应超过
        assert limiter.is_over_limit(messages, hard=True) is False

    def test_get_warning_message_none(self):
        """测试无警告消息"""
        limiter = TokenLimiter(soft_limit=10000)
        messages = [{"role": "user", "content": "Hello"}]
        status = limiter.check(messages)

        warning = limiter.get_warning_message(status)
        assert warning is None

    def test_get_warning_message_soft(self):
        """测试软限制警告消息"""
        limiter = TokenLimiter(soft_limit=5, hard_limit=100)
        # 创建足够长的消息以超过软限制
        messages = [{"role": "user", "content": "This is a test message that should be long enough to exceed the soft limit"}]
        status = limiter.check(messages)

        warning = limiter.get_warning_message(status)
        assert warning is not None
        assert "软限制" in warning

    def test_get_warning_message_hard(self):
        """测试硬限制警告消息"""
        limiter = TokenLimiter(soft_limit=5, hard_limit=10)
        messages = [{"role": "user", "content": "This is a very long test message" * 10}]
        status = limiter.check(messages)

        warning = limiter.get_warning_message(status)
        assert warning is not None
        assert "硬限制" in warning

    def test_update_limits(self):
        """测试更新限制"""
        limiter = TokenLimiter()

        limiter.update_limits(soft_limit=50000, hard_limit=100000)
        assert limiter.soft_limit == 50000
        assert limiter.hard_limit == 100000

        limiter.update_limits(warning_threshold=0.9, warning_enabled=False)
        assert limiter.warning_threshold == 0.9
        assert limiter.warning_enabled is False


class TestTokenLimitStatus:
    """TokenLimitStatus 测试"""

    def test_is_ok(self):
        """测试 is_ok 属性"""
        status = TokenLimitStatus(
            used=1000,
            soft_limit=10000,
            hard_limit=20000,
            usage_ratio=0.1,
            should_warn=False,
            is_over_soft=False,
            is_over_hard=False,
            remaining=9000,
            context_window=128000,
        )
        assert status.is_ok is True

    def test_usage_percent(self):
        """测试 usage_percent 属性"""
        status = TokenLimitStatus(
            used=8000,
            soft_limit=10000,
            hard_limit=20000,
            usage_ratio=0.8,
            should_warn=True,
            is_over_soft=False,
            is_over_hard=False,
            remaining=2000,
            context_window=128000,
        )
        assert status.usage_percent == 80.0


class TestTokenLimiterGlobal:
    """全局限制器测试"""

    def test_get_token_limiter(self):
        """测试获取全局限制器"""
        reset_token_limiter()
        limiter1 = get_token_limiter()
        limiter2 = get_token_limiter()
        assert limiter1 is limiter2

    def test_get_token_limiter_with_config(self):
        """测试带配置获取全局限制器"""
        reset_token_limiter()
        limiter = get_token_limiter(soft_limit=50000, hard_limit=100000)
        assert limiter.soft_limit == 50000
        assert limiter.hard_limit == 100000

    def test_reset_token_limiter(self):
        """测试重置全局限制器"""
        limiter1 = get_token_limiter()
        reset_token_limiter()
        limiter2 = get_token_limiter()
        assert limiter1 is not limiter2
