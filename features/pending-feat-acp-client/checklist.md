# feat-acp-client 完成检查清单

## 代码实现
- [ ] `anyclaw/acp/client.py` ACP Client 核心模块
- [ ] `anyclaw/acp/client_session.py` Client 端会话管理
- [ ] `anyclaw/acp/agent_registry.py` Agent 注册管理
- [ ] API 端点 (agents CRUD + session 管理)
- [ ] SSE 事件转发
- [ ] 配置集成

## 功能验证
- [ ] 能启动并连接 Claude Code ACP Agent
- [ ] initialize 握手成功
- [ ] 能创建会话并发送 prompt
- [ ] 能接收流式 sessionUpdate 事件
- [ ] 能发送 cancel 中止操作
- [ ] 权限审批流正常工作
- [ ] Agent 进程异常退出能检测
- [ ] 跨 Agent 会话切换正常
- [ ] 会话历史能保存和恢复

## UI 验证
- [ ] Agent 选择器显示外部 ACP Agent
- [ ] 选择 ACP Agent 后能直接对话
- [ ] 工具调用卡片正确显示
- [ ] 权限审批弹窗正常弹出
- [ ] Agent 状态指示器正确

## 测试
- [ ] ACP Client 单元测试
- [ ] Agent Registry 单元测试
- [ ] Client Session 管理测试
- [ ] API 端点测试
- [ ] 所有测试通过
- [ ] 覆盖率 >= 80%

## 文档
- [ ] CLAUDE.md 更新 (ACP Client 配置说明)
- [ ] 配置模板更新 (acp 配置节)

## 兼容性
- [ ] 不影响 ACP Server 功能
- [ ] 不影响现有 Channel 功能
- [ ] Agent 不可用时优雅降级
