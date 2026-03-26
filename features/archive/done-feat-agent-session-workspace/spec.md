# Agent Session 存储位置修复

## 问题描述

当用户选择特定 Agent 进行对话时，对话产生的 session 记录保存到了主工作空间的 `sessions/` 目录，而不是 Agent 对应的 workspace 的 `sessions/` 目录。

## 问题分析

### 当前行为
- `ServeManager.initialize()` 创建了一个 `shared_session_manager`，使用主工作空间路径
- `SessionAgentPool` 把这个共享的 SessionManager 传给所有 AgentLoop
- 所以即使 AgentLoop 使用了 agent 的 workspace，session 仍然保存到主工作空间

### 期望行为
- 默认 Agent 的 session 保存到 `/workspace/sessions/`
- Agent "dandan" 的 session 应该保存到 `/workspace/agents/dandan/sessions/`

## 验收场景

### 场景 1: 默认 Agent Session 存储
```gherkin
Given 用户使用默认 Agent 进行对话
When 对话产生 session 记录
Then session 应该保存到 /workspace/sessions/ 目录
```

### 场景 2: 自定义 Agent Session 存储
```gherkin
Given 用户选择 Agent "dandan" 进行对话
When 对话产生 session 记录
Then session 应该保存到 /workspace/agents/dandan/sessions/ 目录
```

### 场景 3: Agent 模板文件加载
```gherkin
Given 用户选择 Agent "dandan" 进行对话
When Agent 处理消息时
Then ContextBuilder 应该从 /workspace/agents/dandan/ 加载 SOUL.md, USER.md, AGENTS.md 等模板
```

## 解决方案

修改 `SessionAgentPool.get_or_create()` 方法：
- 当 `workspace` 参数与默认 workspace 不同时，不使用共享的 SessionManager
- 让 AgentLoop 根据传入的 workspace 创建自己的 SessionManager

## 影响范围

- `anyclaw/core/session_pool.py` - 修改 get_or_create 逻辑
- `anyclaw/core/serve.py` - 检查调用逻辑是否需要调整
