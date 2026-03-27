# feat-acp-server 完成检查清单

## 代码实现
- [ ] `anyclaw/acp/__init__.py` 模块导出
- [ ] `anyclaw/acp/protocol.py` 协议类型定义 (Pydantic)
- [ ] `anyclaw/acp/server.py` NDJSON stdio 服务器
- [ ] `anyclaw/acp/translator.py` 协议翻译层
- [ ] `anyclaw/acp/session.py` 会话管理
- [ ] `anyclaw/acp/event_mapper.py` 流式事件映射
- [ ] `anyclaw/acp/permissions.py` 工具权限审批
- [ ] `anyclaw/acp/cli_cmd.py` CLI 命令入口

## 功能验证
- [ ] `anyclaw acp serve` 能正常启动
- [ ] initialize 请求返回正确响应
- [ ] newSession 创建会话并映射到 AnyClaw Session
- [ ] prompt 消息能触发 AgentLoop 处理
- [ ] 流式事件 (message_chunk, tool_call) 正确推送
- [ ] cancel 能中止正在执行的操作
- [ ] loadSession 能恢复会话历史
- [ ] listSessions 返回活跃会话列表
- [ ] 权限审批流 (自动审批 + 手动审批) 正常工作
- [ ] 工具位置推断正确

## 测试
- [ ] 协议类型单元测试
- [ ] NDJSON 解析单元测试
- [ ] 翻译层单元测试
- [ ] 会话管理单元测试 (LRU, TTL)
- [ ] 事件映射单元测试
- [ ] 权限审批单元测试
- [ ] 集成测试 (端到端 ACP 对话)
- [ ] 所有测试通过
- [ ] 覆盖率 >= 80%

## 文档
- [ ] CLAUDE.md 更新 (ACP 命令)
- [ ] 模块 docstring 完整

## 兼容性
- [ ] 不影响现有 Channel 功能
- [ ] 不影响现有 Sidecar 模式
- [ ] 不影响现有 CLI 聊天功能
