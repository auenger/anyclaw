# feat-token-counter: Token 计数与限制

## 概述

为 AnyClaw 添加 Token 计数和限制功能，支持实时统计对话 token 使用量，并在超过限制时发出警告或自动处理。使用 tiktoken 库进行精确的 token 计数。

## 依赖

- `feat-mvp-agent` (已完成) - Agent 引擎核心

## 用户价值点

### VP1: Token 计数器

**价值**: 实时统计和显示对话的 token 使用量，帮助用户了解上下文消耗情况。

**Gherkin 场景**:

```gherkin
Feature: Token 计数器

  Scenario: 统计单条消息的 token 数
    Given 使用 tiktoken 库
    When 计算一条消息的 token 数
    Then 应返回准确的 token 数量
    And 应支持多种模型编码器（cl100k, o200k 等）

  Scenario: 统计完整对话的 token 数
    Given 存在多轮对话历史
    When 计算对话总 token 数
    Then 应返回总 token 数
    And 应返回各部分的 token 分布（系统提示、历史消息、用户输入）

  Scenario: 显示 token 使用统计
    Given 用户请求查看 token 统计
    When 运行统计命令
    Then 应显示当前对话 token 数
    And 显示相对于模型上下文窗口的百分比
    And 显示剩余可用 token 数

  Scenario: 支持不同模型的编码器
    Given 使用不同模型（GPT-4, Claude, GLM）
    When 计算 token
    Then 应自动选择对应的编码器
    And 无编码器时应使用估算方法
```

### VP2: Token 限制与警告

**价值**: 当对话接近 token 限制时，自动发出警告，帮助用户管理上下文。

**Gherkin 场景**:

```gherkin
Feature: Token 限制与警告

  Scenario: 设置 token 限制
    Given 配置了 token 软限制
    When 对话 token 数接近限制（80%）
    Then 应发出警告信息
    And 显示当前使用量和限制值

  Scenario: 超过软限制
    Given 配置 token 软限制为 100000
    And 当前对话已使用 85000 tokens
    When 用户继续输入
    Then 应显示警告
    And 建议用户压缩或清空对话

  Scenario: 达到硬限制
    Given 配置 token 硬限制为 200000
    And 当前对话已使用 200000 tokens
    When 用户继续输入
    Then 应阻止新输入
    And 强制要求压缩或清空对话

  Scenario: 自定义警告阈值
    Given 配置警告阈值为 70%
    And 配置限制为 100000 tokens
    When 对话达到 70000 tokens
    Then 应发出首次警告
    And 显示剩余 token 数

  Scenario: 禁用警告
    Given 用户禁用了 token 警告
    When 对话 token 超过限制
    Then 不应显示警告
    And 正常处理对话
```

## 技术设计

### 核心组件

```
anyclaw/
├── agent/
│   ├── token_counter.py    # Token 计数器
│   └── token_limiter.py    # Token 限制器
└── config/
    └── settings.py          # 添加 token 相关配置
```

### Token 计数器设计

```python
# agent/token_counter.py
import tiktoken
from typing import Optional

class TokenCounter:
    """Token 计数器"""

    # 模型到编码器的映射
    ENCODING_MAP = {
        "gpt-4": "cl100k_base",
        "gpt-4o": "o200k_base",
        "gpt-3.5-turbo": "cl100k_base",
        "claude": "cl100k_base",  # 近似
        "zai/glm-5": "cl100k_base",  # 近似
    }

    def __init__(self, model: str):
        self.model = model
        self.encoding = self._get_encoding(model)

    def count(self, text: str) -> int:
        """计算文本的 token 数"""
        if self.encoding:
            return len(self.encoding.encode(text))
        # 估算：平均 4 字符 = 1 token
        return len(text) // 4

    def count_messages(self, messages: list) -> dict:
        """计算消息列表的 token 分布"""
        result = {"total": 0, "breakdown": {}}
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            count = self.count(content)
            result["breakdown"][role] = result["breakdown"].get(role, 0) + count
            result["total"] += count
        return result
```

### Token 限制器设计

```python
# agent/token_limiter.py
from typing import Optional
from .token_counter import TokenCounter

class TokenLimiter:
    """Token 限制器"""

    def __init__(
        self,
        counter: TokenCounter,
        soft_limit: int = 100000,
        hard_limit: int = 200000,
        warning_threshold: float = 0.8,
    ):
        self.counter = counter
        self.soft_limit = soft_limit
        self.hard_limit = hard_limit
        self.warning_threshold = warning_threshold

    def check(self, messages: list) -> dict:
        """检查 token 使用情况"""
        stats = self.counter.count_messages(messages)
        usage_ratio = stats["total"] / self.soft_limit

        return {
            "total": stats["total"],
            "soft_limit": self.soft_limit,
            "hard_limit": self.hard_limit,
            "usage_ratio": usage_ratio,
            "should_warn": usage_ratio >= self.warning_threshold,
            "is_over_soft": stats["total"] >= self.soft_limit,
            "is_over_hard": stats["total"] >= self.hard_limit,
        }
```

### 配置扩展

```python
# config/settings.py 新增字段
class Settings(BaseSettings):
    # Token 管理配置
    token_soft_limit: int = Field(
        default=100000,
        description="Token 软限制（触发警告）"
    )
    token_hard_limit: int = Field(
        default=200000,
        description="Token 硬限制（阻止输入）"
    )
    token_warning_threshold: float = Field(
        default=0.8,
        ge=0.5,
        le=1.0,
        description="Token 警告阈值（相对于软限制）"
    )
    token_warning_enabled: bool = Field(
        default=True,
        description="是否启用 token 警告"
    )
```

### CLI 命令

```bash
# 显示 token 统计
anyclaw token stats

# 设置 token 限制
anyclaw token limit --soft 100000 --hard 200000

# 临时禁用警告
anyclaw token warn off
```

## 数据流

```
用户输入
    ↓
ConversationHistory.add_message()
    ↓
TokenCounter.count(new_message)
    ↓
TokenLimiter.check(all_messages)
    ├─ 正常 (< 80%) → 继续处理
    ├─ 警告 (80%-100%) → 显示警告，继续处理
    └─ 阻止 (> 100%) → 拒绝输入，提示压缩
```

## 验收标准

- [ ] tiktoken 集成正常工作
- [ ] 支持多种模型编码器
- [ ] Token 统计准确（误差 < 5%）
- [ ] 警告在正确时机触发
- [ ] 硬限制正确阻止输入
- [ ] CLI 命令正常工作
- [ ] 测试覆盖率 > 80%

## 依赖

```toml
[project.dependencies]
tiktoken = ">=0.5.0"
```

## 参考

- tiktoken: https://github.com/openai/tiktoken
- OpenAI Tokenizer: https://platform.openai.com/tokenizer
- Anthropic Counting: https://docs.anthropic.com/claude/docs/tokens
