# 移除 litellm 依赖

## 背景

**安全事件**: 2026年3月24日，litellm PyPI 包被供应链攻击投毒（攻击者 TeamPCP）。

- **受影响版本**: 1.82.7 和 1.82.8
- **恶意行为**: 多阶段凭证窃取器（SSH keys、云凭证、Kubernetes secrets、API keys）
- **当前状态**: 已锁定到安全版本 1.82.4

## 目标

移除 litellm 依赖，创建自有 LLM 抽象层，直接使用各 provider 的原生 SDK。

## 用户价值点

### VP1: 统一 LLM 抽象层
创建 `anyclaw/llm/` 模块，提供统一的 LLM 调用接口，屏蔽不同 provider 的 API 差异。

**验收场景**:
```gherkin
Scenario: 通过抽象层调用 OpenAI
  Given 配置了 OpenAI provider
  When 调用 LLMClient.chat() 方法
  Then 应该使用 openai SDK 发送请求
  And 返回统一格式的响应

Scenario: 通过抽象层调用 Anthropic
  Given 配置了 Anthropic provider
  When 调用 LLMClient.chat() 方法
  Then 应该使用 anthropic SDK 发送请求
  And 返回统一格式的响应

Scenario: 通过抽象层调用 ZAI (OpenAI 兼容)
  Given 配置了 ZAI provider
  When 调用 LLMClient.chat() 方法
  Then 应该使用 openai SDK 发送请求到 ZAI endpoint
  And 返回统一格式的响应
```

### VP2: Provider Adapter 实现
为每个支持的 provider 实现适配器，处理认证、请求格式、响应格式转换。

**验收场景**:
```gherkin
Scenario: OpenAI adapter 处理 tool calling
  Given 使用 OpenAI provider
  When LLM 返回包含 tool_calls 的响应
  Then adapter 应正确解析 tool_calls
  And 返回统一格式

Scenario: Anthropic adapter 处理 tool calling
  Given 使用 Anthropic provider
  When LLM 返回包含 tool_use 的响应
  Then adapter 应转换为统一格式
  And 与 OpenAI 格式一致

Scenario: ZAI adapter 使用自定义 endpoint
  Given 配置了 ZAI_API_KEY 和 ZAI_API_BASE
  When 调用 ZAI adapter
  Then 应使用自定义 endpoint
  And 正确传递 API key
```

### VP3: 重试与容错机制
实现内置重试机制，替代 litellm 的重试功能。

**验收场景**:
```gherkin
Scenario: 网络错误自动重试
  Given 配置 max_retries=3
  When 第一次请求因网络错误失败
  Then 应自动重试
  And 最多重试 3 次

Scenario: 空响应检测与恢复
  Given LLM 返回空响应
  When 检测到空响应
  Then 应追加提示消息重新请求
  And 达到最大重试次数时返回友好错误

Scenario: 超时处理
  Given 配置 timeout=60
  When 请求超过 60 秒未响应
  Then 应抛出 TimeoutError
```

### VP4: 调用点迁移
将所有使用 litellm 的代码迁移到新抽象层。

**涉及文件**:
- `anyclaw/agent/loop.py` - 主处理循环
- `anyclaw/agent/tool_loop.py` - 工具调用循环
- `anyclaw/agent/summary.py` - 迭代摘要生成
- `anyclaw/core/serve.py` - 聊天标题生成

**验收场景**:
```gherkin
Scenario: AgentLoop 使用新抽象层
  Given AgentLoop 初始化
  When 调用 _call_llm 或 _call_llm_with_tools
  Then 应使用 LLMClient 而非 litellm.acompletion

Scenario: 流式响应正常工作
  Given 启用流式响应
  When 调用流式接口
  Then 应正确返回 AsyncGenerator
  And chunk 格式与 litellm 兼容

Scenario: 移除 litellm 全局配置
  Given 迁移完成
  When 检查代码
  Then 不应存在 litellm.drop_params 等全局配置
```

### VP5: 依赖清理
从 pyproject.toml 移除 litellm 依赖，更新相关文档。

**验收场景**:
```gherkin
Scenario: pyproject.toml 不含 litellm
  Given 迁移完成
  When 检查 pyproject.toml
  Then dependencies 中不应有 litellm

Scenario: 所有测试通过
  Given 迁移完成
  When 运行 pytest tests/
  Then 所有测试应通过

Scenario: 文档更新
  Given 迁移完成
  When 检查 CLAUDE.md
  Then 依赖列表应更新
```

## 技术设计

### 目录结构
```
anyclaw/llm/
├── __init__.py          # 导出 LLMClient
├── client.py            # 统一客户端
├── base.py              # 抽象基类
├── adapters/
│   ├── __init__.py
│   ├── openai.py        # OpenAI adapter
│   ├── anthropic.py     # Anthropic adapter
│   └── zai.py           # ZAI adapter (OpenAI 兼容)
├── retry.py             # 重试装饰器
└── types.py             # 统一类型定义
```

### 核心接口
```python
class LLMClient:
    async def chat(
        self,
        messages: List[Dict],
        model: str,
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        **kwargs
    ) -> ChatResponse:
        ...

    async def stream(
        self,
        messages: List[Dict],
        model: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        ...
```

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| API 格式差异导致兼容问题 | 高 | 完整的单元测试覆盖 |
| 流式响应处理复杂 | 中 | 参考现有实现，保持接口兼容 |
| 遗漏某些 litellm 功能 | 中 | 代码审查 + 集成测试 |

## 建议拆分

此特性有 5 个价值点，建议拆分为：

1. **feat-llm-abstraction** - 统一抽象层 + 重试机制 (VP1, VP3)
2. **feat-llm-adapters** - Provider adapters 实现 (VP2)
3. **feat-llm-migration** - 调用点迁移 + 依赖清理 (VP4, VP5)

## 优先级

**55** - 中等优先级

当前版本 (1.82.4) 是安全的，已锁定版本防止意外升级。此特性可后续实施。
