# Checklist: MCP 客户端

## 开发前

- [x] 添加 `mcp >= 1.0.0` 依赖
- [x] 添加 `httpx >= 0.27.0` 依赖
- [ ] 运行 `poetry lock --no-update` (需要 Python 3.10+)
- [ ] 运行 `poetry install` (需要 Python 3.10+)

### 模块结构
- [x] 创建 `anyclaw/tools/mcp/` 目录
- [x] 创建 `__init__.py`
- [x] 创建 `config.py`, `wrapper.py`, `client.py`

## Phase 2: 配置模型

### config.py
- [x] `MCPServerConfig` Pydantic 模型
  - [x] type: Literal["stdio", "sse", "streamableHttp"] | None
  - [x] command: str
  - [x] args: list[str]
  - [x] env: dict[str, str]
  - [x] url: str
  - [x] headers: dict[str, str]
  - [x] tool_timeout: int = 30
  - [x] enabled_tools: list[str] = ["*"]
  - [x] get_effective_type() 方法

### settings.py
- [x] 添加 `mcp_servers: Dict[str, MCPServerConfig]`
- [x] 导入 MCPServerConfig

## Phase 3: Tool 包装器

### wrapper.py
- [x] `MCPToolWrapper(Tool)` 类
  - [x] `__init__(session, server_name, tool_def, tool_timeout)`
  - [x] `name` 属性：`mcp_{server}_{tool}`
  - [x] `description` 属性
  - [x] `parameters` 属性：映射 inputSchema
  - [x] `execute(**kwargs)` 方法
    - [x] 调用 `session.call_tool()`
    - [x] 使用 `asyncio.wait_for()` 超时
    - [x] 处理 TextContent 结果
    - [x] 处理超时返回 "(MCP tool call timed out)"
    - [x] 处理取消返回 "(MCP tool call was cancelled)"
    - [x] 处理异常返回 "(MCP tool call failed: ...)"
  - [x] `to_schema()` 方法（继承）

## Phase 4: 客户端连接

### client.py
- [x] `connect_mcp_servers(mcp_servers, registry, stack)` 异步函数
  - [x] 遍历 mcp_servers
  - [x] 自动检测传输类型 (get_effective_type)
    - [x] 有 command → stdio
    - [x] URL 以 /sse 结尾 → sse
    - [x] 其他 URL → streamableHttp
  - [x] stdio 传输
    - [x] StdioServerParameters
    - [x] stdio_client()
  - [x] SSE 传输
    - [x] sse_client(url, headers)
    - [x] httpx_client_factory
  - [x] streamableHttp 传输
    - [x] streamable_http_client(url)
    - [x] 自定义 httpx.AsyncClient (timeout=None)
  - [x] ClientSession 初始化
  - [x] 获取 `session.list_tools()`
  - [x] 根据 enabled_tools 过滤
  - [x] 创建 MCPToolWrapper
  - [x] registry.register(wrapper)
  - [x] 日志：connected, X tools registered
  - [x] 错误处理：failed to connect

- [x] 工具过滤逻辑（内联）
  - [x] "*" in enabled_tools → 注册所有
  - [x] tool_def.name in enabled_tools → 注册
  - [x] f"mcp_{server}_{tool_def.name}" in enabled_tools → 注册
  - [x] 未知工具名警告

## Phase 5: Agent 集成

### loop.py
- [x] 导入 `AsyncExitStack`
- [x] 添加 `_mcp_stack` 属性
- [x] `connect_mcp_servers()` 方法
- [x] `close_mcp_servers()` 方法
- [x] `__aenter__` / `__aexit__` 支持 async context manager

## Phase 6: CLI 支持

### mcp_cmd.py
- [x] `anyclaw mcp list` 命令
  - [x] 显示配置的 servers
  - [x] 显示类型、地址、超时、启用工具
- [x] `anyclaw mcp test <name>` 命令
  - [x] 测试连接
  - [x] 显示注册的工具
  - [x] 超时处理

### app.py
- [x] 注册 mcp 子命令

## Phase 7: 测试

### tests/test_mcp_tool.py
- [x] Fake MCP 模块 fixture
  - [x] FakeTextContent
  - [x] FakeClientSession
  - [x] Fake stdio_client
  - [x] Fake sse_client
  - [x] Fake streamable_http_client

- [x] MCPToolWrapper 测试
  - [x] test_execute_returns_text_blocks
  - [x] test_execute_returns_timeout_message
  - [x] test_execute_handles_server_cancelled_error
  - [x] test_execute_re_raises_external_cancellation
  - [x] test_execute_handles_generic_exception

- [x] connect_mcp_servers 测试
  - [x] test_connect_mcp_servers_enabled_tools_supports_raw_names
  - [x] test_connect_mcp_servers_enabled_tools_defaults_to_all
  - [x] test_connect_mcp_servers_enabled_tools_supports_wrapped_names
  - [x] test_connect_mcp_servers_enabled_tools_empty_list_registers_none
  - [x] test_connect_mcp_servers_enabled_tools_warns_on_unknown_entries

- [x] MCPServerConfig 测试
  - [x] test_mcp_server_config_stdio_type
  - [x] test_mcp_server_config_sse_type
  - [x] test_mcp_server_config_http_type
  - [x] test_mcp_server_config_explicit_type
  - [x] test_mcp_server_config_no_type

## 完成后
- [x] 提交代码
- [ ] 运行完整测试套件 (需要 Python 3.10+)
