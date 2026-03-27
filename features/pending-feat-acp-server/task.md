# feat-acp-server 任务分解

## 任务列表

### T1: 协议类型定义 (protocol.py)
- [ ] 定义 ACPRequest / ACPResponse (JSON-RPC 2.0)
- [ ] 定义 ContentBlock (text/image/resource)
- [ ] 定义 SessionUpdateType 枚举
- [ ] 定义 InitializeRequest/Response
- [ ] 定义 NewSessionRequest/Response
- [ ] 定义 PromptRequest/Response
- [ ] 定义 SessionNotification
- [ ] 定义 ToolCallContent / ToolCallLocation
- [ ] 定义 AcpSession 数据模型

### T2: NDJSON stdio 服务器 (server.py)
- [ ] 实现 NDJSON 读取 (stdin → asyncio)
- [ ] 实现 NDJSON 写入 (stdout)
- [ ] 实现 JSON-RPC 请求路由
- [ ] 实现 JSON-RPC 错误响应
- [ ] 实现信号处理 (SIGINT/SIGTERM 优雅关闭)
- [ ] 实现并发请求处理

### T3: 协议翻译层 (translator.py)
- [ ] 实现 initialize 处理器
- [ ] 实现 newSession 处理器
- [ ] 实现 loadSession 处理器
- [ ] 实现 prompt 处理器 (文本提取 + InboundMessage 构建)
- [ ] 实现 cancel 处理器 (中断 AgentLoop)
- [ ] 实现 listSessions 处理器
- [ ] 实现图片附件提取
- [ ] 集成 AgentLoop.process() 调用

### T4: 会话管理 (session.py)
- [ ] 实现 AcpSession 数据模型
- [ ] 实现 AcpSessionManager (创建/查找/删除)
- [ ] 实现会话到 AnyClaw SessionManager 的映射
- [ ] 实现 LRU 驱逐 (MAX_SESSIONS = 5000)
- [ ] 实现 TTL 过期检查 (24h)
- [ ] 实现活跃运行管理 (abort_controller)

### T5: 流式事件映射 (event_mapper.py)
- [ ] 实现 message:outbound → agent_message_chunk
- [ ] 实现 tool:start → tool_call (status: running)
- [ ] 实现 tool:complete → tool_call_update
- [ ] 实现 agent:thinking → agent_message_chunk (thought)
- [ ] 实现 usage 统计 → usage_update
- [ ] 实现 AgentLoop 流式回调集成

### T6: 工具权限审批 (permissions.py)
- [ ] 定义 AUTO_APPROVE_TOOLS 列表
- [ ] 定义 MANUAL_APPROVE_TOOLS 列表
- [ ] 实现 requestPermission 发送
- [ ] 实现 IDE 审批结果处理
- [ ] 实现工具位置推断 (文件路径 → ToolCallLocation)

### T7: CLI 命令 (cli_cmd.py)
- [ ] 实现 `anyclaw acp serve` 命令
- [ ] 实现 --cwd 参数
- [ ] 实现 --session 参数
- [ ] 实现 --verbose 参数
- [ ] 集成到 Typer CLI 应用

### T8: 测试
- [ ] 协议类型定义测试
- [ ] NDJSON 解析测试
- [ ] 翻译层单元测试
- [ ] 会话管理测试 (LRU, TTL)
- [ ] 事件映射测试
- [ ] 权限审批测试
- [ ] 集成测试 (端到端 ACP 对话)
