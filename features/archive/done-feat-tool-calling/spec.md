# feat-tool-calling: Tool Calling 核心框架

## 概述

实现 Function Calling / Tool Use 能力，让 Agent 能自动识别和调用技能执行实际操作。支持 OpenClaw SKILL.md 格式兼容，通过 litellm 实现跨 LLM Provider 的 tool calling 支持。

## 依赖

- `feat-mvp-skills` (已完成) - 基础技能系统

## 用户价值点

### VP1: SKILL.md 解析器

**价值**: 能够加载和解析 OpenClaw 兼容的 SKILL.md 文件，复用 OpenClaw 生态的 50+ skills。

**Gherkin 场景**:

```gherkin
Feature: SKILL.md 解析

  Scenario: 解析基础 SKILL.md
    Given 存在 SKILL.md 文件，包含 YAML frontmatter 和 Markdown 内容
    When 加载该 skill
    Then 应解析出 name, description, metadata 字段
    And 应保留 Markdown 内容作为指令

  Scenario: 解析带依赖的 SKILL.md
    Given SKILL.md 包含 metadata.openclaw.requires 字段
    When 加载该 skill
    Then 应验证 bins 依赖（检查命令是否存在）
    And 应验证 env 依赖（检查环境变量）
    And 依赖不满足时应标记为不可用

  Scenario: 处理无效 SKILL.md
    Given SKILL.md 格式错误或缺少必要字段
    When 尝试加载
    Then 应记录错误日志
    And 不应中断其他 skills 加载

  Scenario: 加载多个 skill 目录
    Given 存在多个 skill 目录（bundled, managed, workspace）
    When 加载所有 skills
    Then 应按优先级合并同名 skills
    And workspace > managed > bundled
```

### VP2: Tool Definition 生成

**价值**: 将 skills 转换为 litellm 兼容的 tools JSON Schema，让 LLM 能识别和选择合适的工具。

**Gherkin 场景**:

```gherkin
Feature: Tool Definition 生成

  Scenario: 生成单个 tool definition
    Given 存在一个有效的 skill
    When 生成 tool definition
    Then 应生成符合 OpenAI tools schema 的 JSON
    And name 应来自 skill.name
    And description 应来自 skill.description
    And parameters 应基于 skill 的参数定义

  Scenario: 批量生成 tools
    Given 存在多个可用 skills
    When 生成 tools 列表
    Then 应生成完整的 tools 数组
    And 不可用的 skills 应被过滤

  Scenario: 处理无参数 skill
    Given skill 没有定义参数
    When 生成 tool definition
    Then parameters 应为空对象 schema
    And tool definition 应有效

  Scenario: 处理复杂参数类型
    Given skill 定义了复杂参数（嵌套对象、数组）
    When 生成 tool definition
    Then 应正确转换为 JSON Schema
    And 必填字段应标记 required
```

### VP3: Tool Calling 执行

**价值**: 处理 LLM 返回的 tool_calls，执行对应的 shell 命令，并将结果返回给 Agent 继续对话。

**Gherkin 场景**:

```gherkin
Feature: Tool Calling 执行

  Scenario: 执行单个 tool call
    Given LLM 返回一个 tool_call
    When Agent 处理该调用
    Then 应找到对应的 skill
    And 应执行 skill 定义的命令
    And 应捕获命令输出
    And 应将结果作为 tool message 返回

  Scenario: 并行执行多个 tool calls
    Given LLM 返回多个独立的 tool_calls
    When Agent 处理这些调用
    Then 应并行执行无依赖的调用
    And 应按顺序返回所有结果

  Scenario: 处理 tool 执行错误
    Given tool 执行失败（命令不存在、权限错误等）
    When Agent 处理错误
    Then 应捕获错误信息
    And 应返回有意义的错误消息给 LLM
    And LLM 可以尝试其他方案

  Scenario: 处理超时
    Given tool 执行超过配置的超时时间
    When Agent 检测到超时
    Then 应终止命令执行
    And 应返回超时错误消息

  Scenario: 集成到 Agent 主循环
    Given Agent 收到用户消息
    When 调用 LLM 并收到 tool_calls
    Then 应执行 tools
    And 应将结果添加到对话历史
    And 应继续调用 LLM 直到获得最终响应

  Scenario: 无 tool calling 的正常对话
    Given 用户消息不需要调用工具
    When Agent 处理消息
    Then 应正常返回 LLM 响应
    And 不应尝试执行任何工具
```

## 技术设计

### 核心组件

```
anyclaw/
├── skills/
│   ├── parser.py          # SKILL.md 解析器
│   ├── converter.py       # Skill -> Tool Definition 转换
│   ├── executor.py        # Tool 执行器
│   └── builtin/
│       └── openclaw/      # OpenClaw 兼容 skills
└── agent/
    └── tool_loop.py       # Tool Calling 主循环
```

### 数据流

```
用户消息
    ↓
AgentLoop.process()
    ↓
构建 messages + tools ─────────────────┐
    ↓                                   │
litellm.acompletion(tools=tools)       │
    ↓                                   │
LLM 返回 response                       │
    ↓                                   │
有 tool_calls?                          │
    ├─ Yes → ToolExecutor.execute() ────┘
    │         ↓
    │    添加 tool results 到 history
    │         ↓
    │    重新调用 LLM
    │
    └─ No → 返回最终响应
```

### SKILL.md 格式

```markdown
---
name: weather
description: "Get current weather via wttr.in"
metadata:
  {
    "openclaw":
      {
        "emoji": "☔",
        "requires": { "bins": ["curl"] }
      }
  }
---

# Weather Skill

Get current weather conditions and forecasts.

## Commands

\`\`\`bash
curl "wttr.in/{location}?format=3"
\`\`\`
```

### Tool Definition Schema

```json
{
  "type": "function",
  "function": {
    "name": "weather",
    "description": "Get current weather via wttr.in",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "City name or location"
        }
      },
      "required": ["location"]
    }
  }
}
```

## 验收标准

- [ ] 能成功解析 OpenClaw SKILL.md 格式
- [ ] 生成的 tool definitions 被 litellm 接受
- [ ] Tool calling 在 OpenAI/GPT 模型上正常工作
- [ ] Tool calling 在 Anthropic/Claude 模型上正常工作（如支持）
- [ ] 错误处理健壮，不会崩溃
- [ ] 测试覆盖率 > 80%
- [ ] 有完整的文档和示例

## 参考

- OpenClaw Skills: `reference/openclaw/skills/`
- OpenClaw Skills Doc: `reference/openclaw/docs/tools/skills.md`
- litellm Tool Calling: https://docs.litellm.ai/docs/completion/function_call
- OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling
