# Feature Spec: Agent 引擎核心

## 元数据
- **ID**: feat-mvp-agent
- **名称**: Agent 引擎核心
- **优先级**: 95
- **尺寸**: L
- **状态**: completed
- **创建日期**: 2026-03-18
- **完成日期**: 2026-03-18
- **依赖**: feat-mvp-init

## 描述
实现 AnyClaw 的核心 Agent 引擎，包括对话理解、对话记忆和 LLM 集成。

## 用户价值点

### 价值点 1: 智能对话理解
Agent 能够理解用户输入并生成智能响应。

**Gherkin 场景**:
```gherkin
Scenario: 用户发送消息并获得响应
  Given Agent 已初始化
  When 用户输入 "Hello, who are you?"
  Then Agent 应该返回包含其名称的响应
```

### 价值点 2: 对话历史记忆
Agent 能够记住之前的对话内容。

**Gherkin 场景**:
```gherkin
Scenario: Agent 记住对话历史
  Given 用户之前说了 "My name is Alice"
  When 用户问 "What's my name?"
  Then Agent 应该能够引用 "Alice"
```

## 技术栈
- litellm (LLM 统一接口)
- asyncio (异步处理)

## 实现文件
- `anyclaw/anyclaw/agent/loop.py` - AgentLoop 主处理循环
- `anyclaw/anyclaw/agent/history.py` - ConversationHistory 对话历史
- `anyclaw/anyclaw/agent/context.py` - ContextBuilder 上下文构建
- `anyclaw/tests/test_agent.py` - Agent 测试

## 验收标准
- [x] AgentLoop 可以处理用户输入
- [x] 对话历史可以存储和检索
- [x] 可以调用 LLM 生成响应
- [x] 支持异步处理

## 完成说明
Agent 核心引擎已完成，包括：
- AgentLoop: 主处理循环，集成 LLM 调用
- ConversationHistory: 使用 deque 管理对话历史，支持最大长度限制
- ContextBuilder: 构建包含系统提示词和历史对话的完整上下文
- 异步处理支持
