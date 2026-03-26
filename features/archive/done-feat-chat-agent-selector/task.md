# Task: Chat Agent Selector

## 任务分解

### Phase 1: 前端 Agent 列表加载 (30min)

- [ ] **T1.1** 修改 `Chat.tsx`
  - 添加 `agents` state 和 `useEffect` 从 `/api/agents` 获取列表
  - 实现排序逻辑（default 优先）
  - 将 agents 传递给 `ChatProvider`

- [ ] **T1.2** 添加 localStorage 持久化
  - 在 `Chat.tsx` 中读取 `lastAgentId`
  - 传递 `initialAgentId` 给 `ChatProvider`
  - 在 `chatCtx.tsx` 中保存 `agentId` 到 localStorage

### Phase 2: 后端消息路由 (1h)

- [ ] **T2.1** 修改 `bus/events.py`
  - `InboundMessage` 添加 `agent_id: Optional[str] = None` 字段

- [ ] **T2.2** 修改 `api/routes/messages.py`
  - 将 `request.agent_id` 传递到 `InboundMessage.agent_id`

- [ ] **T2.3** 修改 `core/serve.py`
  - `ServeManager.__init__` 添加 `agent_manager` 参数
  - `_process_with_semaphore` 根据 `msg.agent_id` 获取 agent workspace
  - 如果 agent 不存在，fallback 到默认 workspace

- [ ] **T2.4** 修改 `core/session_pool.py`
  - `SessionAgentPool` 添加 `get_or_create(session_key, workspace=None)` 参数
  - 支持为不同 workspace 创建 AgentLoop

### Phase 3: 测试与验证 (30min)

- [ ] **T3.1** 手动测试
  - 创建多个 Agent
  - 在 Chat 页面切换 Agent
  - 发送消息验证路由正确

- [ ] **T3.2** 单元测试
  - `test_session_pool.py` 添加 workspace 参数测试
  - `test_serve.py` 添加 agent 路由测试

## 文件清单

### 修改文件

| 文件 | 修改内容 |
|------|----------|
| `tauri-app/src/pages/Chat.tsx` | 添加 agents 加载和 localStorage 持久化 |
| `tauri-app/src/hooks/chatCtx.tsx` | 添加 agentId 持久化逻辑 |
| `anyclaw/bus/events.py` | InboundMessage 添加 agent_id |
| `anyclaw/api/routes/messages.py` | 传递 agent_id |
| `anyclaw/core/serve.py` | Agent 路由逻辑 |
| `anyclaw/core/session_pool.py` | 支持不同 workspace |

## 验收标准

1. Chat 页面显示 Agent 选择器（多 Agent 时）
2. 切换 Agent 后消息路由正确
3. 刷新页面后保持 Agent 选择
4. 不同 Agent 使用独立的 workspace 和记忆
