# feat-agents-api: 任务分解

## 阶段 1: 依赖注入改造

### Task 1.1: 修改 api/deps.py
- [ ] 添加 `_agent_manager` 全局变量
- [ ] 添加 `set_agent_manager()` 函数
- [ ] 添加 `get_agent_manager()` 函数

### Task 1.2: 修改 sidecar_cmd.py
- [ ] 导入 IdentityManager 和 AgentManager
- [ ] 创建 IdentityManager 实例
- [ ] 创建 AgentManager 实例
- [ ] 调用 `load_all_agents()`
- [ ] 调用 `set_agent_manager()` 注入

## 阶段 2: API 路由完善

### Task 2.1: 数据模型定义
- [ ] 创建 `AgentInfo` 响应模型（完善现有）
- [ ] 创建 `CreateAgentRequest` 请求模型
- [ ] 创建 `UpdateAgentRequest` 请求模型

### Task 2.2: GET /api/agents
- [ ] 从 AgentManager 获取 agent 列表
- [ ] 转换为 AgentInfo 格式
- [ ] 支持 include_disabled 查询参数

### Task 2.3: POST /api/agents
- [ ] 验证请求数据
- [ ] 调用 AgentManager.create_agent()
- [ ] 返回创建的 agent
- [ ] 处理重复名称错误

### Task 2.4: GET /api/agents/{id}
- [ ] 从 AgentManager 获取单个 agent
- [ ] 404 处理

### Task 2.5: PATCH /api/agents/{id}
- [ ] 获取现有 agent
- [ ] 更新 IdentityManager 中的 IDENTITY.md
- [ ] 返回更新后的数据

### Task 2.6: DELETE /api/agents/{id}
- [ ] 调用 AgentManager.delete_agent()
- [ ] 返回 204 No Content

### Task 2.7: POST /api/agents/{id}/activate
- [ ] 调用 AgentManager.switch_agent()
- [ ] 返回成功消息

### Task 2.8: POST /api/agents/{id}/deactivate
- [ ] 调用 AgentManager.enable_agent(id, False)
- [ ] 返回成功消息

## 阶段 3: 测试

### Task 3.1: 单元测试
- [ ] test_agents_api.py - API 端点测试
- [ ] Mock AgentManager 进行隔离测试

### Task 3.2: 集成测试
- [ ] 启动 sidecar 后测试完整流程
- [ ] 创建 -> 列表 -> 更新 -> 删除

## 预计工作量

- 阶段 1: 30 分钟
- 阶段 2: 1 小时
- 阶段 3: 30 分钟
- **总计**: 约 2 小时
