# feat-acp-client 任务分解

## 任务列表

### T1: ACP Client 核心模块 (client.py)
- [ ] 实现 ACPClient 类 (管理 ACP Agent 子进程)
- [ ] 实现 spawn 子进程 (asyncio.create_subprocess_exec)
- [ ] 实现 NDJSON 读取 (stdin 写入 + stdout 读取)
- [ ] 实现 initialize 握手
- [ ] 实现 newSession / prompt / cancel 调用
- [ ] 实现 sessionUpdate 事件接收和回调
- [ ] 实现 requestPermission 请求转发
- [ ] 实现进程退出检测和清理
- [ ] 实现可选的自动重连

### T2: Agent Registry (agent_registry.py)
- [ ] 定义 AcpAgentConfig 模型 (name, command, args, description, icon)
- [ ] 实现 AgentRegistry 类 (加载/查询/健康检查)
- [ ] 实现从配置文件加载 Agent 列表
- [ ] 实现 Agent 可用性检测 (命令是否存在)
- [ ] 实现 get_available_agents() 方法

### T3: Client 端会话管理 (client_session.py)
- [ ] 实现 AcpClientSession 模型
- [ ] 实现 AcpClientSessionManager (创建/恢复/销毁会话)
- [ ] 实现跨 Agent 会话切换
- [ ] 实现会话历史保存到 AnyClaw SessionManager
- [ ] 实现会话取消 (cancel)

### T4: API 端点
- [ ] GET /api/acp/agents — 列出可用 ACP Agent
- [ ] POST /api/acp/agents/{name}/connect — 连接 Agent
- [ ] POST /api/acp/agents/{name}/disconnect — 断开 Agent
- [ ] GET /api/acp/agents/{name}/status — Agent 状态
- [ ] POST /api/acp/sessions/{id}/cancel — 取消会话
- [ ] POST /api/acp/sessions/{id}/permission — 权限审批响应

### T5: SSE 事件转发
- [ ] ACP sessionUpdate 事件转发到 SSE
- [ ] requestPermission 事件转发到 SSE
- [ ] Agent 连接/断开状态事件

### T6: 配置集成
- [ ] Settings 添加 acp 配置模型
- [ ] Config loader 支持 acp 配置节
- [ ] 配置模板更新

### T7: Tauri 前端集成
- [ ] Agent 选择器 UI (显示 ACP Agent 列表)
- [ ] ACP Agent 对话界面 (消息流)
- [ ] 工具调用卡片组件
- [ ] 权限审批对话框组件
- [ ] Agent 状态指示器 (连接中/已连接/断开)
- [ ] i18n 翻译 (中英文)

### T8: 测试
- [ ] ACP Client 单元测试 (mock 子进程)
- [ ] Agent Registry 单元测试
- [ ] Client Session 管理测试
- [ ] API 端点测试
- [ ] 集成测试 (实际连接 ACP Agent, 可选)
