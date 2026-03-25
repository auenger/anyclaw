# feat-agents-api: 完成检查清单

## 代码实现

- [x] `api/deps.py` 添加 AgentManager 依赖注入
- [x] `sidecar_cmd.py` 初始化并注入 AgentManager
- [x] `api/routes/agents.py` GET /api/agents 返回真实数据
- [x] `api/routes/agents.py` POST /api/agents 创建功能
- [x] `api/routes/agents.py` GET /api/agents/{id} 获取单个
- [x] `api/routes/agents.py` PATCH /api/agents/{id} 更新功能
- [x] `api/routes/agents.py` DELETE /api/agents/{id} 删除功能
- [x] `api/routes/agents.py` POST /api/agents/{id}/activate 激活
- [x] `api/routes/agents.py` POST /api/agents/{id}/deactivate 禁用

## 数据模型

- [x] AgentInfo 模型完善（添加 emoji, avatar, workspace 字段）
- [x] CreateAgentRequest 模型
- [x] UpdateAgentRequest 模型

## 测试

- [x] 单元测试 test_agents_api.py
- [x] 所有测试通过 (18/18)

## 文档

- [x] API 端点在代码中有完整 docstring

## 验收

- [x] GET /api/agents 返回真实 agent 列表
- [x] 可以通过 API 创建新 agent
- [x] 可以更新 agent 配置
- [x] 可以删除 agent
- [x] 可以切换默认 agent (activate)
- [x] 可以启用/禁用 agent (deactivate)

## 附加改进

- [x] 修复 cron/parser.py 的 TYPE_CHECKING 类型注解问题
- [x] 添加 IdentityManager.update_identity() 方法
