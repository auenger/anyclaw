# LLM 响应韧性增强

## 概述

解决 LLM（特别是 GLM-4.7）在工具调用后返回空响应的问题，增强 LLM 调用的稳定性和可观测性。

## 背景问题

从日志分析发现：
```
[00:44:13] exec 执行成功（10秒内完成）
[00:44:43] LiteLLM 重试请求（30秒后）
[00:44:57] CONVERSATION [ASSISTANT] (glm-4.7) (empty)
```

问题根因：
1. LLM API 不稳定导致第一次请求失败
2. LiteLLM 内部重试后返回空 content
3. 没有对空响应进行兜底处理

## 用户价值点

### VP1: 空响应检测与自动恢复

当 LLM 返回空响应时，自动检测并触发重新生成，而不是直接返回空字符串。

**验收场景**：

```gherkin
Feature: 空响应检测与恢复

Scenario: 检测到空响应时自动重试
  Given AgentLoop 正在处理工具调用结果
  When LLM 返回 message.content 为 None 或空字符串
  And 没有 tool_calls
  Then 系统应记录警告日志 "LLM returned empty content"
  And 自动追加提示消息 "请继续完成任务"
  And 重新调用 LLM 获取响应

Scenario: 空响应重试次数限制
  Given 空响应重试功能已启用
  When 连续遇到 3 次空响应
  Then 系统应返回友好的错误提示
  And 不再继续重试

Scenario: 空响应统计与告警
  Given 会话正在进行
  When 累计空响应次数超过阈值（如 5 次/会话）
  Then 系统应记录 ERROR 级别日志
  And 可选发送系统事件通知
```

### VP2: LiteLLM 重试配置优化

配置合理的 LiteLLM 重试策略，减少不必要的超时等待。

**验收场景**：

```gherkin
Feature: LiteLLM 重试配置

Scenario: 配置重试参数
  Given 系统配置文件
  When 设置 llm_retry 配置项
  Then 应支持以下参数：
    | 参数 | 默认值 | 说明 |
    | max_retries | 3 | 最大重试次数 |
    | retry_delay | 1 | 重试延迟（秒）|
    | retry_on_timeout | true | 超时时是否重试 |
    | retry_on_rate_limit | true | 限流时是否重试 |

Scenario: 重试日志透明化
  Given LiteLLM 正在重试请求
  When 重试发生时
  Then 应记录 INFO 级别日志
  And 日志应包含重试原因、重试次数、下次重试时间
```

### VP3: 增强的 LLM 响应诊断日志

记录 LLM 响应的详细信息，便于排查问题。

**验收场景**：

```gherkin
Feature: LLM 响应诊断日志

Scenario: 记录 LLM 响应详情
  Given AgentLogger 已初始化
  When LLM 返回响应时
  Then 应记录以下信息（DEBUG 级别）：
    | 字段 | 说明 |
    | model | 实际使用的模型 |
    | has_content | 是否有 content |
    | has_tool_calls | 是否有 tool_calls |
    | tool_calls_count | tool_calls 数量 |
    | usage | token 使用量（如有）|
    | response_time_ms | 响应时间 |

Scenario: 空响应详情记录
  Given 检测到空响应
  When 记录日志时
  Then 应记录完整的响应对象（DEBUG 级别）
  And 包括 finish_reason、response 对象摘要
```

## 技术方案

### 1. 空响应处理（loop.py）

```python
# _run_with_tools 方法中
if not hasattr(message, 'tool_calls') or not message.tool_calls:
    content = message.content or ""
    if not content:
        # 空响应检测与恢复
        logger.warning("LLM returned empty content without tool_calls")
        if self._empty_response_retry < MAX_EMPTY_RETRIES:
            self._empty_response_retry += 1
            # 追加提示消息，重新请求
            messages.append({
                "role": "user",
                "content": "请继续完成任务。"
            })
            continue  # 继续循环，重新调用 LLM
        else:
            return "抱歉，模型响应异常，请重试。"
    return content
```

### 2. LiteLLM 配置（loop.py 开头）

```python
import litellm
litellm.drop_params = True
litellm.set_verbose = False
litellm.suppress_debug_info = True
# 新增重试配置
litellm.num_retries = settings.llm_max_retries  # 默认 3
litellm.retry_delay = settings.llm_retry_delay  # 默认 1
```

### 3. 诊断日志（logger.py）

```python
def log_llm_response_detail(
    self,
    model: str,
    has_content: bool,
    has_tool_calls: bool,
    tool_calls_count: int = 0,
    usage: Dict[str, int] = None,
    response_time_ms: float = None,
    finish_reason: str = None,
):
    """记录 LLM 响应详情（DEBUG 级别）"""
    self.logger.debug(
        f"[LLM] Response detail: model={model}, "
        f"content={has_content}, tool_calls={has_tool_calls}({tool_calls_count}), "
        f"usage={usage}, time={response_time_ms}ms, finish={finish_reason}"
    )
```

## 配置项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `llm_empty_response_retry` | int | 2 | 空响应最大重试次数 |
| `llm_max_retries` | int | 3 | LiteLLM 最大重试次数 |
| `llm_retry_delay` | float | 1.0 | LiteLLM 重试延迟（秒）|
| `llm_log_response_detail` | bool | false | 是否记录详细响应日志 |

## 影响范围

- `anyclaw/agent/loop.py` - 空响应处理逻辑
- `anyclaw/agent/logger.py` - 新增诊断日志方法
- `anyclaw/config/settings.py` - 新增配置项
- `anyclaw/providers/zai.py` - 可能需要调整超时处理

## 参考资料

- OpenClaw 超时处理方案：`/Users/ryan/mycode/openclaw/openclaw/src/agents/bash-tools.exec-runtime.ts`
- LiteLLM 重试文档：https://docs.litellm.ai/docs/completion/retry_policy
