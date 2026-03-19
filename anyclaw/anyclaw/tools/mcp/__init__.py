"""MCP 客户端模块

提供 MCP (Model Context Protocol) 客户端支持，连接任意 MCP Server 并将其工具作为 AnyClaw 原生 Tool 使用。
"""

from anyclaw.tools.mcp.client import connect_mcp_servers
from anyclaw.tools.mcp.config import MCPServerConfig
from anyclaw.tools.mcp.wrapper import MCPToolWrapper

__all__ = [
    "MCPServerConfig",
    "MCPToolWrapper",
    "connect_mcp_servers",
]
