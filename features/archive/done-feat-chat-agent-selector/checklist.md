# Checklist: Chat Agent Selector

## Phase 1: 前端 Agent 列表加载

- [x] Chat.tsx 添加 agents state
- [x] Chat.tsx 从 `/api/agents` 获取 agents 列表
- [x] agents 列表排序（default 优先，然后按名称）
- [x] 从 localStorage 读取 `lastAgentId`
- [x] 传递 agents 和 initialAgentId 给 ChatProvider
- [x] agentId 变化时保存到 localStorage

## Phase 2: 后端消息路由

- [x] InboundMessage 添加 agent_id 字段
- [x] messages.py 传递 agent_id 到 InboundMessage
- [x] ServeManager 添加 AgentManager 依赖
- [x] _process_with_semaphore 根据 agent_id 获取 workspace
- [x] SessionAgentPool 支持不同 workspace 参数

## Phase 3: 测试验证

- [ ] 创建多个 Agent 测试
- [ ] Agent 选择器显示测试
- [ ] Agent 切换测试
- [ ] 消息路由测试
- [ ] localStorage 持久化测试
- [ ] 单元测试通过

## 完成标准

- [ ] 所有 Phase 1-3 任务完成
- [ ] 功能验收通过
- [ ] 无回归问题
- [ ] 代码已提交
