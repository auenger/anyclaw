# Task: MCP 客户端

## 任务分解

### Phase 1: 基础设施

#### Task 1.1: 添加 MCP 依赖
**文件**: `anyclaw/pyproject.toml`
**内容**:
- [ ] 添加 `mcp >= 1.0.0` 依赖
- [ ] 添加 `httpx >= 0.27.0` 依赖
- [ ] 运行 `poetry lock --no-update`

#### Task 1.2: 创建 MCP 模块目录
**文件**: `anyclaw/anyclaw/tools/mcp/__init__.py`
**内容**:
- [ ] 创建 `tools/mcp/` 目录
- [ ] 导出主要类和函数

### Phase 2: 配置模型

#### Task 2.1: MCP 配置 Schema
**文件**: `anyclaw/anyclaw/tools/mcp/config.py`
**内容**:
- [ ] `MCPServerConfig` 类
  - [ ] type: stdio/sse/streamableHttp
  - [ ] command/args/env (stdio)
  - [ ] url/headers (HTTP/SSE)
  - [ ] tool_timeout: int
  - [ ] enabled_tools: list[str]

#### Task 2.2: 集成到主配置
**文件**: `anyclaw/anyclaw/config/settings.py`
**内容**:
- [ ] 添加 `mcp_servers: dict[str, MCPServerConfig]`
- [ ] 默认空字典
- [ ] 配置验证

### Phase 3: Tool 包装器

#### Task 3.1: MCPToolWrapper 实现
**文件**: `anyclaw/anyclaw/tools/mcp/wrapper.py`
**内容**:
- [ ] 继承 `Tool` 基类
- [ ] `name` 属性：`mcp_{server}_{tool}`
- [ ] `description` 属性
- [ ] `parameters` 属性：从 inputSchema 映射
- [ ] `execute()` 方法：
  - [ ] 调用 session.call_tool()
  - [ ] 超时处理 (asyncio.wait_for)
  - [ ] 结果格式化
  - [ ] 异常处理

### Phase 4: 客户端连接

#### Task 4.1: MCP 客户端实现
**文件**: `anyclaw/anyclaw/tools/mcp/client.py`
**内容**:
- [ ] `connect_mcp_servers()` 函数
  - [ ] 遍历配置的 servers
  - [ ] 根据类型选择传输
  - [ ] stdio: StdioServerParameters + stdio_client
  - [ ] sse: sse_client with headers
  - [ ] streamableHttp: streamable_http_client
  - [ ] 创建 ClientSession
  - [ ] 初始化 session
  - [ ] 获取工具列表
  - [ ] 根据 enabled_tools 过滤
  - [ ] 创建 wrapper 并注册到 registry
  - [ ] 日志记录

#### Task 4.2: 工具过滤逻辑
**文件**: `anyclaw/anyclaw/tools/mcp/client.py`
**内容**:
- [ ] `should_register_tool()` 函数
- [ ] 支持 "*" 通配符
- [ ] 支持原始名称匹配
- [ ] 支持 wrapped 名称匹配
- [ ] 警告未知工具名

### Phase 5: Agent 集成

#### Task 5.1: AgentLoop 集成
**文件**: `anyclaw/anyclaw/agent/loop.py`
**内容**:
- [ ] 在初始化时连接 MCP servers
- [ ] 使用 AsyncExitStack 管理连接生命周期
- [ ] 传递 ToolRegistry 给 connect_mcp_servers

### Phase 6: CLI 支持

#### Task 6.1: MCP 配置命令
**文件**: `anyclaw/anyclaw/cli/app.py`
**内容**:
- [ ] `anyclaw mcp list` - 列出配置的 servers
- [ ] `anyclaw mcp test <name>` - 测试连接

### Phase 7: 测试

#### Task 7.1: 单元测试
**文件**: `tests/test_mcp_tool.py`
**内容**:
- [ ] MCPToolWrapper 测试
  - [ ] execute 返回文本
  - [ ] 超时处理
  - [ ] 取消处理
  - [ ] 异常处理
- [ ] connect_mcp_servers 测试
  - [ ] enabled_tools 过滤
  - [ ] 默认注册所有工具
  - [ ] 空列表注册无工具
  - [ ] 未知工具警告

## 执行顺序

1. Task 1.1 + 1.2 - 基础设施
2. Task 2.1 + 2.2 - 配置模型
3. Task 3.1 - Tool 包装器
4. Task 4.1 + 4.2 - 客户端连接
5. Task 5.1 - Agent 集成
6. Task 6.1 - CLI 支持
7. Task 7.1 - 测试

## 依赖关系

```
依赖安装 ──> 配置模型 ──> Tool 包装器
                │              │
                └──────────────┴──> 客户端连接 ──> Agent 集成
                                                              │
                                         CLI 支持 <────────────┘
                                                              │
                                         测试 <────────────────┘
```

## 预计工作量

| 阶段 | 预计时间 |
|------|----------|
| Phase 1 | 0.5h |
| Phase 2 | 1h |
| Phase 3 | 1.5h |
| Phase 4 | 2h |
| Phase 5 | 1h |
| Phase 6 | 1h |
| Phase 7 | 1.5h |
| **总计** | **8.5h** |
