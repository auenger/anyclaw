# Feature: MCP 客户端

## 概述

为 AnyClaw 添加完整的 MCP (Model Context Protocol) 客户端支持，允许连接任意 MCP Server 并将其工具作为 AnyClaw 的原生 Tool 使用。

**优先级**: 70 (中)
**大小**: L
**依赖**: 无

## 背景与动机

MCP (Model Context Protocol) 是 Anthropic 推出的开放协议，用于连接 AI 助手与外部数据源和工具：

- **Claude Code** 使用 MCP 提供工具能力
- **OpenClaw/Nanobot** 已实现 MCP 客户端
- **丰富的 MCP Server 生态**：文件系统、数据库、API 网关等

通过实现 MCP 客户端，AnyClaw 可以：
1. 直接使用 Claude Code 的 MCP skills
2. 接入任意 MCP Server（官方/社区）
3. 复用现有的 MCP 工具生态

## 用户价值点

### VP1: MCP Server 连接管理

支持多种传输协议连接 MCP Server。

```gherkin
Feature: MCP Server 连接

  Scenario: 通过 stdio 连接本地 MCP Server
    Given 配置了 MCP server "filesystem"
      | command | "npx" |
      | args    | ["-y", "@modelcontextprotocol/server-filesystem", "/path"] |
    When 启动 AnyClaw
    Then 成功连接 filesystem server
    And 日志显示 "MCP server 'filesystem': connected, X tools registered"

  Scenario: 通过 SSE 连接远程 MCP Server
    Given 配置了 MCP server "remote-api"
      | type | "sse" |
      | url  | "https://api.example.com/mcp/sse" |
    When 启动 AnyClaw
    Then 成功连接 remote-api server

  Scenario: 通过 HTTP 连接 MCP Server
    Given 配置了 MCP server "http-api"
      | type | "streamableHttp" |
      | url  | "https://api.example.com/mcp" |
    When 启动 AnyClaw
    Then 成功连接 http-api server

  Scenario: 连接失败时记录错误
    Given MCP server 配置无效
    When 启动 AnyClaw
    Then 日志显示连接错误
    And 不影响其他 MCP server 连接
```

### VP2: MCP Tool 包装

将 MCP Server 的工具包装为 AnyClaw Tool。

```gherkin
Feature: MCP Tool 包装

  Scenario: 工具名称转换
    Given MCP server "github" 提供 tool "create_issue"
    When 注册到 AnyClaw
    Then 工具名称为 "mcp_github_create_issue"

  Scenario: 工具 Schema 转换
    Given MCP tool 定义了 inputSchema
    When 包装为 AnyClaw Tool
    Then parameters 属性正确映射
    And to_schema() 返回正确的 OpenAI 格式

  Scenario: 工具执行
    Given MCP tool "mcp_github_create_issue" 已注册
    When 执行该工具，参数为 {"title": "Bug", "body": "Description"}
    Then 调用 MCP session.call_tool("create_issue", {...})
    And 返回结果文本

  Scenario: 执行超时处理
    Given MCP tool 执行超过 30 秒
    When 执行该工具
    Then 返回 "(MCP tool call timed out after 30s)"
    And 不阻塞其他操作
```

### VP3: 工具过滤配置

支持配置启用哪些 MCP 工具。

```gherkin
Feature: 工具过滤

  Scenario: 启用所有工具（默认）
    Given MCP server 配置 enabled_tools: ["*"]
    When 连接 server
    Then 注册所有可用工具

  Scenario: 启用指定工具
    Given MCP server 配置 enabled_tools: ["create_issue", "list_issues"]
    When 连接 server
    Then 只注册 mcp_github_create_issue 和 mcp_github_list_issues

  Scenario: 禁用所有工具
    Given MCP server 配置 enabled_tools: []
    When 连接 server
    Then 不注册任何工具

  Scenario: 警告未知工具名
    Given enabled_tools 包含 "unknown_tool"
    When 连接 server
    Then 日志警告 "enabledTools entries not found: unknown_tool"
    And 显示可用工具列表
```

### VP4: 配置集成

将 MCP 配置集成到 AnyClaw 配置系统。

```gherkin
Feature: 配置集成

  Scenario: 配置文件格式
    Given anyclaw.json 包含 mcp_servers 配置
    ```json
    {
      "mcp_servers": {
        "filesystem": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-filesystem", "~"]
        },
        "github": {
          "type": "streamableHttp",
          "url": "https://api.github.com/mcp",
          "headers": {"Authorization": "Bearer ${GITHUB_TOKEN}"},
          "enabled_tools": ["create_issue", "list_issues"],
          "tool_timeout": 60
        }
      }
    }
    ```
    When 加载配置
    Then MCP servers 正确解析
    And 环境变量 ${GITHUB_TOKEN} 被展开

  Scenario: CLI 查看配置
    Given 已配置 MCP servers
    When 执行 "anyclaw config show --mcp"
    Then 显示所有 MCP server 配置
    And 显示连接状态
```

## 技术设计

### 目录结构

```
anyclaw/anyclaw/
├── tools/
│   ├── mcp/                    # 新增：MCP 模块
│   │   ├── __init__.py
│   │   ├── client.py           # MCP 客户端连接
│   │   ├── wrapper.py          # Tool 包装器
│   │   └── config.py           # MCP 配置模型
│   └── ...
├── config/
│   └── settings.py             # 添加 mcp_servers 配置
└── cli/
    └── app.py                  # 添加 mcp 相关命令
```

### 核心类设计

```python
# anyclaw/tools/mcp/wrapper.py

class MCPToolWrapper(Tool):
    """将 MCP Server Tool 包装为 AnyClaw Tool"""

    def __init__(self, session, server_name: str, tool_def, tool_timeout: int = 30):
        self._session = session
        self._server_name = server_name
        self._original_name = tool_def.name
        self._tool_timeout = tool_timeout

    @property
    def name(self) -> str:
        return f"mcp_{self._server_name}_{self._original_name}"

    @property
    def description(self) -> str:
        return tool_def.description or tool_def.name

    @property
    def parameters(self) -> dict:
        return tool_def.inputSchema or {"type": "object", "properties": {}}

    async def execute(self, **kwargs) -> str:
        result = await asyncio.wait_for(
            self._session.call_tool(self._original_name, arguments=kwargs),
            timeout=self._tool_timeout
        )
        return self._format_result(result)
```

```python
# anyclaw/tools/mcp/client.py

async def connect_mcp_servers(
    mcp_servers: dict[str, MCPServerConfig],
    registry: ToolRegistry,
    stack: AsyncExitStack
) -> None:
    """连接所有配置的 MCP Server 并注册工具"""

    for name, cfg in mcp_servers.items():
        # 根据配置选择传输类型
        if cfg.type == "stdio":
            read, write = await stdio_client(params)
        elif cfg.type == "sse":
            read, write = await sse_client(cfg.url, headers=cfg.headers)
        elif cfg.type == "streamableHttp":
            read, write, _ = await streamable_http_client(cfg.url)

        # 创建 session
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()

        # 获取并注册工具
        tools = await session.list_tools()
        for tool_def in tools.tools:
            if should_register(tool_def, cfg.enabled_tools):
                wrapper = MCPToolWrapper(session, name, tool_def, cfg.tool_timeout)
                registry.register(wrapper)
```

### 配置 Schema

```python
# anyclaw/tools/mcp/config.py

class MCPServerConfig(BaseModel):
    """MCP Server 配置"""

    type: Literal["stdio", "sse", "streamableHttp"] | None = None
    command: str = ""              # stdio: 命令
    args: list[str] = []           # stdio: 参数
    env: dict[str, str] = {}       # stdio: 环境变量
    url: str = ""                  # HTTP/SSE: URL
    headers: dict[str, str] = {}   # HTTP/SSE: 请求头
    tool_timeout: int = 30         # 工具调用超时
    enabled_tools: list[str] = ["*"]  # 启用的工具列表
```

### 依赖

```toml
# pyproject.toml 新增依赖
mcp = ">=1.0.0"  # MCP Python SDK
httpx = ">=0.27.0"  # HTTP 客户端
```

## 实现参考

完全参考 Nanobot 的实现：
- `reference/nanobot/nanobot/agent/tools/mcp.py`
- `reference/nanobot/tests/test_mcp_tool.py`

## 验收标准

- [ ] 支持 stdio 传输连接本地 MCP Server
- [ ] 支持 SSE 传输连接远程 MCP Server
- [ ] 支持 streamableHttp 传输
- [ ] MCP 工具正确包装为 AnyClaw Tool
- [ ] 工具名称格式为 `mcp_{server}_{tool}`
- [ ] 支持 enabled_tools 过滤
- [ ] 超时和错误处理
- [ ] 配置文件集成
- [ ] 有完整的单元测试
