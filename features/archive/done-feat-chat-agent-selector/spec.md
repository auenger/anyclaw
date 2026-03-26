# Feature: Chat Agent Selector

## 概述

在 Chat 页面添加 Agent 切换功能，允许用户选择不同的 Agent 进行对话。参考 youclaw 的实现，实现前端 Agent 选择器和后端消息路由。

## 背景与动机

当前系统已支持多 Agent 和多工作区，但 Chat 页面只能使用默认 Agent。需要让用户能够在聊天时选择不同的 Agent，每个 Agent 有自己的配置、记忆和技能。

## 用户价值点

### 价值点 1: 前端 Agent 选择器

**用户故事**: 作为用户，我希望在聊天时能看到并选择不同的 Agent，以便使用不同配置的 AI 助手。

**验收场景**:

```gherkin
Feature: Agent 选择器显示

  Scenario: 有多个 Agent 时显示选择器
    Given 系统中存在多个 Agent（至少 2 个）
    When 用户打开 Chat 页面
    Then 聊天输入框下方显示 Agent 选择器
    And 选择器中列出所有可用的 Agent
    And 默认 Agent 排在第一位

  Scenario: 只有一个 Agent 时不显示选择器
    Given 系统中只有 1 个 Agent
    When 用户打开 Chat 页面
    Then 不显示 Agent 选择器
    And 使用默认 Agent 进行对话

  Scenario: 切换 Agent
    Given Agent 选择器已显示
    And 当前选中的是 "Default Agent"
    When 用户点击选择器并选择 "Research Assistant"
    Then 选中状态变为 "Research Assistant"
    And 后续发送的消息使用 "Research Assistant" 处理
```

### 价值点 2: Agent 选择持久化

**用户故事**: 作为用户，我希望系统记住我上次选择的 Agent，这样下次打开时不需要重新选择。

**验收场景**:

```gherkin
Feature: Agent 选择持久化

  Scenario: 保存 Agent 选择
    Given 用户选择了 "Research Assistant"
    When 用户发送消息或刷新页面
    Then "Research Assistant" 仍保持选中状态

  Scenario: 恢复上次选择
    Given 用户上次选择了 "Research Assistant"
    When 用户重新打开 Chat 页面
    Then 自动选中 "Research Assistant"
```

### 价值点 3: 后端 Agent 路由

**用户故事**: 作为系统，我需要将用户消息路由到正确的 Agent workspace，以便使用对应的配置、记忆和技能。

**验收场景**:

```gherkin
Feature: 消息路由到指定 Agent

  Scenario: 消息使用指定 Agent 的 workspace
    Given 用户选择了 "Research Assistant"
    And "Research Assistant" 的 workspace 为 "/path/to/research"
    When 用户发送消息 "帮我分析这篇论文"
    Then 消息被路由到 "Research Assistant"
    And 使用 /path/to/research 下的 SOUL.md、记忆、技能
    And 响应基于 "Research Assistant" 的人设生成

  Scenario: 不同 Agent 独立记忆
    Given 用户在 "Default Agent" 对话中讨论了项目 A
    And 用户切换到 "Research Assistant"
    When 用户发送消息
    Then "Research Assistant" 不知道项目 A 的内容
    And 使用自己独立的记忆和上下文
```

## 技术设计

### 前端修改

1. **Chat.tsx**:
   - 添加 `useEffect` 从 `/api/agents` 获取 agents 列表
   - 将 agents 传递给 `ChatProvider`
   - 从 localStorage 读取/保存 `lastAgentId`

2. **chatCtx.tsx**:
   - 已有 `agentId`, `setAgentId`, `agents` 支持
   - 添加 localStorage 持久化逻辑

3. **ChatInput.tsx**:
   - 已支持 `agents`, `selectedAgentId`, `onAgentChange` 属性
   - 已有 Agent 选择器 UI（`agents.length > 1` 时显示）
   - 无需修改

### 后端修改

1. **bus/events.py**:
   - `InboundMessage` 添加 `agent_id: Optional[str]` 字段

2. **api/routes/messages.py**:
   - 将 `agent_id` 传递到 `InboundMessage`

3. **core/serve.py**:
   - `ServeManager` 添加 `AgentManager` 依赖
   - 根据 `agent_id` 获取对应 agent 的 workspace
   - 修改 `SessionAgentPool` 支持不同的 workspace

4. **core/session_pool.py**:
   - 添加 `get_or_create_with_workspace(session_key, workspace)` 方法
   - 或修改 `get_or_create` 接受 workspace 参数

## 依赖

- `feat-agents-api` (已完成 AgentManager 和 API)
- `feat-agents-ui` (可选，用于 Agent 管理)

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Agent workspace 切换导致上下文丢失 | 中 | 每个 Agent 独立管理 session |
| 性能：多个 AgentLoop 实例 | 低 | 使用 pool 管理，按需创建 |

## 预估大小

**M** (3 个价值点)
