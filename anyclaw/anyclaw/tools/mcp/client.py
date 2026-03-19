"""MCP 客户端连接管理"""

import logging
from contextlib import AsyncExitStack
from typing import Dict, Set

import httpx

from anyclaw.tools.mcp.config import MCPServerConfig
from anyclaw.tools.mcp.wrapper import MCPToolWrapper
from anyclaw.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


async def connect_mcp_servers(
    mcp_servers: Dict[str, MCPServerConfig],
    registry: ToolRegistry,
    stack: AsyncExitStack
) -> None:
    """连接配置的 MCP Server 并注册其工具

    Args:
        mcp_servers: MCP Server 配置字典
        registry: Tool 注册表
        stack: AsyncExitStack 用于管理连接生命周期
    """
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.sse import sse_client
    from mcp.client.stdio import stdio_client
    from mcp.client.streamable_http import streamable_http_client

    for name, cfg in mcp_servers.items():
        try:
            transport_type = cfg.get_effective_type()

            if not transport_type:
                logger.warning(
                    "MCP server '%s': no command or url configured, skipping",
                    name
                )
                continue

            # 根据传输类型建立连接
            if transport_type == "stdio":
                params = StdioServerParameters(
                    command=cfg.command,
                    args=cfg.args,
                    env=cfg.env or None
                )
                read, write = await stack.enter_async_context(stdio_client(params))

            elif transport_type == "sse":
                def httpx_client_factory(
                    headers: dict | None = None,
                    timeout: httpx.Timeout | None = None,
                    auth: httpx.Auth | None = None,
                ) -> httpx.AsyncClient:
                    merged_headers = {**(cfg.headers or {}), **(headers or {})}
                    return httpx.AsyncClient(
                        headers=merged_headers or None,
                        follow_redirects=True,
                        timeout=timeout,
                        auth=auth,
                    )

                read, write = await stack.enter_async_context(
                    sse_client(cfg.url, httpx_client_factory=httpx_client_factory)
                )

            elif transport_type == "streamableHttp":
                # 始终提供显式的 httpx 客户端，以便 MCP HTTP 传输
                # 不会继承 httpx 的默认 5 秒超时，从而使用更高层级的工具超时
                http_client = await stack.enter_async_context(
                    httpx.AsyncClient(
                        headers=cfg.headers or None,
                        follow_redirects=True,
                        timeout=None,
                    )
                )
                read, write, _ = await stack.enter_async_context(
                    streamable_http_client(cfg.url, http_client=http_client)
                )

            else:
                logger.warning(
                    "MCP server '%s': unknown transport type '%s'",
                    name, transport_type
                )
                continue

            # 创建 session 并初始化
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()

            # 获取工具列表
            tools = await session.list_tools()

            # 处理 enabled_tools 过滤
            enabled_tools: Set[str] = set(cfg.enabled_tools)
            allow_all_tools = "*" in enabled_tools
            registered_count = 0
            matched_enabled_tools: Set[str] = set()

            available_raw_names = [tool_def.name for tool_def in tools.tools]
            available_wrapped_names = [
                f"mcp_{name}_{tool_def.name}" for tool_def in tools.tools
            ]

            for tool_def in tools.tools:
                wrapped_name = f"mcp_{name}_{tool_def.name}"

                # 检查是否应该注册此工具
                if (
                    not allow_all_tools
                    and tool_def.name not in enabled_tools
                    and wrapped_name not in enabled_tools
                ):
                    logger.debug(
                        "MCP: skipping tool '%s' from server '%s' (not in enabledTools)",
                        wrapped_name, name
                    )
                    continue

                # 创建并注册包装器
                wrapper = MCPToolWrapper(
                    session, name, tool_def, tool_timeout=cfg.tool_timeout
                )
                registry.register(wrapper)
                logger.debug(
                    "MCP: registered tool '%s' from server '%s'",
                    wrapper.name, name
                )
                registered_count += 1

                # 追踪匹配的工具
                if enabled_tools:
                    if tool_def.name in enabled_tools:
                        matched_enabled_tools.add(tool_def.name)
                    if wrapped_name in enabled_tools:
                        matched_enabled_tools.add(wrapped_name)

            # 警告未匹配的 enabled_tools 条目
            if enabled_tools and not allow_all_tools:
                unmatched_enabled_tools = sorted(enabled_tools - matched_enabled_tools)
                if unmatched_enabled_tools:
                    logger.warning(
                        "MCP server '%s': enabledTools entries not found: %s. "
                        "Available raw names: %s. Available wrapped names: %s",
                        name,
                        ", ".join(unmatched_enabled_tools),
                        ", ".join(available_raw_names) or "(none)",
                        ", ".join(available_wrapped_names) or "(none)",
                    )

            logger.info(
                "MCP server '%s': connected, %d tools registered",
                name, registered_count
            )

        except Exception as e:
            logger.error(
                "MCP server '%s': failed to connect: %s",
                name, e
            )
