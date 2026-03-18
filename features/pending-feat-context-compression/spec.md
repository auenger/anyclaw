# feat-context-compression: 智能上下文压缩

## 概述

为 AnyClaw 添加智能上下文压缩功能，当对话历史过长时，自动压缩旧消息以节省 token，同时保留关键信息。支持摘要压缩、滑动窗口、优先级保留等多种策略。

## 依赖

- `feat-mvp-agent` (已完成) - Agent 引擎核心
- `feat-token-counter` (pending) - Token 计数功能

## 用户价值点

### VP1: 对话摘要压缩

**价值**: 将多轮旧对话压缩为简洁摘要，保留关键信息但大幅减少 token 消耗。

**Gherkin 场景**:

```gherkin
Feature: 对话摘要压缩

  Scenario: 自动压缩旧对话
    Given 对话历史超过 10 轮
    And 启用了自动压缩
    When 达到压缩阈值
    Then 应将最早 5 轮对话压缩为摘要
    And 摘要应保留关键决策和信息
    And 压缩后 token 数应减少 60% 以上

  Scenario: 保留关键对话
    Given 对话历史包含重要决策
    When 执行压缩
    Then 应识别并保留包含决策的对话
    And 只压缩普通对话
    And 关键对话不应被压缩

  Scenario: 压缩摘要质量
    Given 存在 5 轮对话
    When 压缩为摘要
    Then 摘要应包含主要话题
    And 摘要应包含关键结论
    And 摘要应包含待办事项（如有）
    And 摘要长度应 < 原文 30%

  Scenario: 手动触发压缩
    Given 用户想手动压缩对话
    When 运行 "anyclaw compress"
    Then 应显示压缩预览
    And 应询问用户确认
    And 用户确认后执行压缩

  Scenario: 压缩失败回退
    Given LLM 压缩请求失败
    When 执行压缩
    Then 应使用简单截断作为回退
    And 不应丢失最近对话
```

### VP2: 滑动窗口策略

**价值**: 使用滑动窗口保留最近的 N 条消息，自动丢弃更早的消息。

**Gherkin 场景**:

```gherkin
Feature: 滑动窗口策略

  Scenario: 基本滑动窗口
    Given 配置窗口大小为 10 条消息
    And 当前有 15 条消息
    When 应用滑动窗口
    Then 应保留最近 10 条消息
    And 丢弃最早 5 条消息

  Scenario: 保护系统消息
    Given 对话包含系统消息
    When 应用滑动窗口
    Then 系统消息应始终保留
    And 系统消息不计入窗口大小

  Scenario: 保护重要消息
    Given 部分消息标记为重要
    When 应用滑动窗口
    Then 重要消息应优先保留
    And 普通消息优先丢弃

  Scenario: 自定义窗口大小
    Given 配置窗口大小为 20
    When 用户设置新窗口大小为 30
    Then 下次窗口应用时应使用 30
    And 配置应持久化

  Scenario: 结合 token 限制
    Given 配置 token 限制为 50000
    And 窗口大小为 20
    When 消息 token 数超过限制
    Then 应动态缩小窗口
    And 直到 token 数低于限制
```

### VP3: 长对话处理

**价值**: 提供完整的长对话处理方案，结合压缩和窗口策略，确保对话可以无限延续。

**Gherkin 场景**:

```gherkin
Feature: 长对话处理

  Scenario: 自动长对话管理
    Given 启用了自动管理
    And 配置了 token 限制
    When 对话接近限制
    Then 应自动触发压缩
    And 如压缩后仍超限，应用滑动窗口
    And 用户应收到通知

  Scenario: 分段处理超长输入
    Given 用户提供超长文本（超过上下文窗口）
    When Agent 处理输入
    Then 应自动分段处理
    And 每段独立处理
    And 最后合并结果

  Scenario: 对话检查点
    Given 用户创建检查点
    When 运行 "anyclaw checkpoint create"
    Then 应保存当前对话状态
    And 可以后续恢复
    And 检查点包含完整上下文

  Scenario: 从检查点恢复
    Given 存在保存的检查点
    When 运行 "anyclaw checkpoint restore <name>"
    Then 应恢复对话状态
    And 恢复压缩后的摘要
    And 继续对话

  Scenario: 导出对话摘要
    Given 存在长对话历史
    When 用户请求导出
    Then 应生成完整摘要
    And 包含所有关键决策
    And 支持多种格式（Markdown, JSON）
```

## 技术设计

### 核心组件

```
anyclaw/
├── agent/
│   ├── compressor.py       # 对话压缩器
│   ├── sliding_window.py   # 滑动窗口
│   └── checkpoint.py       # 检查点管理
└── cli/
    └── compress.py          # 压缩相关命令
```

### 压缩器设计

```python
# agent/compressor.py
from typing import Optional
from .token_counter import TokenCounter

class ConversationCompressor:
    """对话压缩器"""

    def __init__(
        self,
        counter: TokenCounter,
        compress_threshold: int = 10,  # 超过 10 轮触发
        keep_recent: int = 5,  # 保留最近 5 轮
    ):
        self.counter = counter
        self.compress_threshold = compress_threshold
        self.keep_recent = keep_recent

    async def compress(
        self,
        messages: list,
        strategy: str = "summary"
    ) -> list:
        """压缩对话历史"""
        if len(messages) <= self.compress_threshold:
            return messages

        # 分离要压缩和保留的消息
        to_compress = messages[:-self.keep_recent]
        to_keep = messages[-self.keep_recent:]

        if strategy == "summary":
            compressed = await self._summarize(to_compress)
        elif strategy == "truncate":
            compressed = self._truncate(to_compress)
        else:
            compressed = to_compress

        return compressed + to_keep

    async def _summarize(self, messages: list) -> list:
        """使用 LLM 生成摘要"""
        # 调用 LLM 生成摘要
        summary = await self._generate_summary(messages)
        return [{
            "role": "system",
            "content": f"[对话摘要] {summary}"
        }]

    def _truncate(self, messages: list) -> list:
        """简单截断"""
        return messages[-3:]  # 只保留最后 3 条
```

### 滑动窗口设计

```python
# agent/sliding_window.py
from typing import Optional

class SlidingWindow:
    """滑动窗口管理器"""

    def __init__(
        self,
        window_size: int = 20,
        protect_system: bool = True,
        protect_tagged: bool = True,
    ):
        self.window_size = window_size
        self.protect_system = protect_system
        self.protect_tagged = protect_tagged

    def apply(self, messages: list) -> list:
        """应用滑动窗口"""
        if len(messages) <= self.window_size:
            return messages

        # 分离受保护的消息
        protected = []
        regular = []
        for msg in messages:
            if self._is_protected(msg):
                protected.append(msg)
            else:
                regular.append(msg)

        # 对普通消息应用窗口
        kept_regular = regular[-self.window_size:]

        return protected + kept_regular

    def _is_protected(self, message: dict) -> bool:
        """检查消息是否受保护"""
        if self.protect_system and message.get("role") == "system":
            return True
        if self.protect_tagged and message.get("metadata", {}).get("important"):
            return True
        return False
```

### 配置扩展

```python
# config/settings.py 新增
class Settings(BaseSettings):
    # 压缩配置
    compress_enabled: bool = Field(default=True)
    compress_threshold: int = Field(default=10)
    compress_keep_recent: int = Field(default=5)
    compress_strategy: str = Field(default="summary")  # summary/truncate

    # 滑动窗口配置
    window_enabled: bool = Field(default=True)
    window_size: int = Field(default=20)

    # 检查点配置
    checkpoint_dir: str = Field(default="checkpoints")
```

### CLI 命令

```bash
# 压缩对话
anyclaw compress [--preview] [--strategy summary|truncate]

# 滑动窗口
anyclaw window set 20
anyclaw window apply

# 检查点
anyclaw checkpoint create <name>
anyclaw checkpoint list
anyclaw checkpoint restore <name>
anyclaw checkpoint delete <name>
```

## 数据流

```
新消息到达
    ↓
检查对话长度
    ↓
超过阈值？
    ├─ No → 正常处理
    └─ Yes ↓
        检查 token 数
            ↓
        超过限制？
            ├─ No → 警告，继续
            └─ Yes ↓
                执行压缩策略
                    ├─ 摘要压缩
                    └─ 滑动窗口
                        ↓
                更新对话历史
                        ↓
                继续处理
```

## 验收标准

- [ ] 摘要压缩能减少 60%+ token
- [ ] 滑动窗口正确保留重要消息
- [ ] 长对话可以无限延续
- [ ] CLI 命令正常工作
- [ ] 测试覆盖率 > 80%
- [ ] 文档完整

## 优先级

| 功能 | 优先级 | 理由 |
|------|--------|------|
| 摘要压缩 | P0 | 核心能力 |
| 滑动窗口 | P1 | 基础能力 |
| 检查点 | P2 | 高级功能 |

## 参考

- LangChain ConversationSummaryMemory
- AutoGen 压缩策略
- OpenAI Best Practices for Long Context
