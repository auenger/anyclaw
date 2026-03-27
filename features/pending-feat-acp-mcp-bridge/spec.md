# ACP-MCP 桥接

> ID: feat-acp-mcp-bridge
> 父特性: feat-acp-integration
> 优先级: 70
> 大小: S
> 依赖: []

## 概述

集成 `acp-mcp` 适配器，使 AnyClaw 通过现有的 MCP Client 调用外部 ACP Agent（Claude Code、Gemini CLI 等）作为工具。这是零代码集成方案，主要通过配置实现，同时添加便捷的配置管理命令。

## 参考文档

- `docs/ACP_PROTOCOL_ANALYSIS.md` — 第七节 7.3 路径 1
- [acp-mcp GitHub](https://github.com/i-am-bee/acp-mcp)

## 用户价值点

### VP1: acp-mcp 适配器配置集成

提供便捷的方式配置 acp-mcp 适配器，使 AnyClaw Agent 能调用外部 ACP Agent 作为工具。

**验收场景:**
```gherkin
Feature: acp-mcp 配置

  Scenario: 通过配置添加 ACP Agent 作为 MCP 工具
    Given 用户在配置文件中添加 acp-mcp 服务器
    When AnyClaw 启动并连接 MCP 服务器
    Then acp-mcp 服务器作为 MCP Server 注册
      And AnyClaw Agent 可调用 ACP Agent 的工具

  Scenario: 便捷 CLI 命令
    When 运行 `anyclaw acp add claude-code`
    Then 自动配置 acp-mcp 适配器
      And 添加到 MCP 服务器列表
      And 配置可验证

  Scenario: 列出已配置的 ACP Agent
    When 运行 `anyclaw acp list`
    Then 显示所有通过 acp-mcp 配置的外部 Agent
      And 包含名称、状态、MCP 服务器名称

  Scenario: 移除 ACP Agent 配置
    When 运行 `anyclaw acp remove claude-code`
    Then 从 MCP 服务器列表中移除对应配置
```

### VP2: Agent 编排模式文档与示例

提供使用文档，说明如何通过 AnyClaw 编排多个 ACP Agent。

**验收场景:**
```gherkin
Feature: 编排文档

  Scenario: 使用文档完整
    Given docs/ 目录下有 ACP 集成指南
    When 用户阅读文档
    Then 文档包含:
      | acp-mcp 安装和配置步骤       |
      | Claude Code 集成示例        |
      | Gemini CLI 集成示例         |
      | 多 Agent 编排使用场景       |
      | 与 ACP Server/Client 的区别 |
```

## 技术设计

### 配置格式

```toml
# acp-mcp 适配器配置 (作为 MCP Server)
[mcp_servers.claude-code]
command = "npx"
args = ["@i-am-bee/acp-mcp", "--agent", "claude-code"]
env = {}

[mcp_servers.gemini-cli]
command = "npx"
args = ["@i-am-bee/acp-mcp", "--agent", "gemini"]
env = {}
```

### CLI 命令

```bash
# 添加 ACP Agent
anyclaw acp add <agent-name> [--command <cmd>] [--args <args>]

# 列出已配置的 ACP Agent
anyclaw acp list

# 移除 ACP Agent
anyclaw acp remove <agent-name>

# 测试 ACP Agent 连接
anyclaw acp test <agent-name>
```

### 与其他特性的关系

```
feat-acp-mcp-bridge (配置级，零代码)
    │
    │ 复用现有 MCP Client
    ▼
AnyClaw AgentLoop
    │
    │ 调用 mcp_<server>_<tool>
    ▼
acp-mcp 适配器 (外部进程)
    │
    │ ACP 协议
    ▼
Claude Code / Gemini CLI 等
```

这是最轻量的集成方式，利用 AnyClaw 已有的 MCP Client，无需新增 Python 代码（除 CLI 便捷命令）。
