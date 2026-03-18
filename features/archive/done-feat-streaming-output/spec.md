# 流式输出支持

## 概述

为 AnyClaw 添加 LLM 响应流式输出能力，实现逐 token/chunk 实时显示，提升用户体验和感知响应速度。

## 背景

当前实现使用 `litellm.acompletion` 等待完整响应后返回，用户需要等待较长时间才能看到任何输出。流式输出可以让用户实时看到 AI 的响应过程，提供更好的交互体验。

## 用户价值点

### 价值点 1：Agent 流式响应

AgentLoop 支持流式返回响应，使用 async generator 逐块产出内容。

**验收场景**：
```gherkin
Feature: Agent 流式响应

Scenario: 流式返回简单响应
  Given 用户发送消息 "你好"
  When AgentLoop.process_stream() 被调用
  Then 应该逐块返回响应内容
  And 每个块都是字符串片段

Scenario: 流式响应包含完整内容
  Given 用户发送消息 "写一首诗"
  When 收集所有流式块并拼接
  Then 结果与完整响应一致

Scenario: 流式中断处理
  Given 流式响应正在进行
  When 用户中断（Ctrl+C）
  Then 流式输出停止
  And 不影响后续对话
```

### 价值点 2：CLI 实时显示

CLI 频道支持流式显示，实时打印接收到的内容块。

**验收场景**：
```gherkin
Feature: CLI 实时显示

Scenario: 实时打印流式响应
  Given CLI 正在运行
  When 用户输入消息
  Then 响应内容实时逐字显示
  And 不等待完整响应

Scenario: 流式显示带颜色
  Given 流式响应正在显示
  Then 使用配置的颜色显示
  And 显示完成后换行

Scenario: 打字机效果
  Given 流式响应正在显示
  Then 内容平滑出现
  And 无明显卡顿
```

### 价值点 3：流式配置控制

支持通过配置启用/禁用流式输出。

**验收场景**：
```gherkin
Feature: 流式配置控制

Scenario: 启用流式输出
  Given 配置 stream_enabled = true
  When 用户发送消息
  Then 使用流式输出

Scenario: 禁用流式输出
  Given 配置 stream_enabled = false
  When 用户发送消息
  Then 等待完整响应后显示

Scenario: 模型兼容性检查
  Given 某些模型不支持流式输出
  When 调用流式 API
  Then 自动回退到非流式模式
```

### 价值点 4：Tool Calling 流式支持

Tool Calling 场景下的流式处理。

**验收场景**：
```gherkin
Feature: Tool Calling 流式支持

Scenario: 工具调用前流式显示思考
  Given Agent 需要调用工具
  When 工具调用前的思考内容
  Then 实时显示思考过程

Scenario: 工具执行时显示状态
  Given 工具正在执行
  Then 显示执行状态指示器
  And 执行完成后继续流式输出

Scenario: 多次工具调用
  Given 需要多次调用工具
  When 完成一次工具调用
  Then 流式显示中间结果
```

## 技术设计

### 架构变更

```
┌─────────────────────────────────────────────────────────────┐
│                    流式输出架构                              │
└─────────────────────────────────────────────────────────────┘

用户输入 → CLIChannel
              │
              ▼
         AgentLoop.process_stream()  ← async generator
              │
              ▼
         ContextBuilder.build()
              │
              ▼
         litellm.acompletion(stream=True)
              │
              ▼ (逐块返回)
         yield chunk  ─────────────────→ CLI 实时打印
              │
              ▼
         完成后保存到历史
```

### 文件变更

1. **anyclaw/agent/loop.py**
   - 添加 `process_stream()` 方法（async generator）
   - 添加 `_stream_llm()` 私有方法

2. **anyclaw/channels/cli.py**
   - 添加 `print_stream()` 方法
   - 修改 `run()` 支持流式处理函数

3. **anyclaw/config/settings.py**
   - 添加 `stream_enabled: bool = True`
   - 添加 `stream_buffer_size: int = 10` (缓冲块数)

4. **anyclaw/agent/tool_loop.py**
   - 添加 `process_with_tools_stream()` 方法

### litellm 流式调用

```python
async def _stream_llm(self, messages: list):
    """流式调用 LLM"""
    response = await acompletion(
        model=settings.llm_model,
        messages=messages,
        stream=True,  # 启用流式
        **kwargs
    )

    async for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

### CLI 流式显示

```python
async def print_stream(self, stream_func):
    """打印流式响应"""
    self.console.print(f"\n[bold green]{settings.agent_name}:[/bold green] ", end="")

    async for chunk in stream_func:
        self.console.print(chunk, end="")

    self.console.print()  # 完成后换行
```

## 优先级

76 - 较高优先级，直接影响用户体验

## 依赖

- 无前置依赖
- 与 feat-builtin-skills-v2 可并行开发

## 大小评估

**M** - 4 个价值点，涉及多个核心模块修改，但流式逻辑相对清晰

## 风险

1. **Tool Calling 复杂性**：流式 + Tool Calling 组合较复杂，需要仔细处理
2. **模型兼容性**：部分模型可能不支持流式，需要回退机制
3. **中断处理**：Ctrl+C 中断流式输出需要正确清理状态
