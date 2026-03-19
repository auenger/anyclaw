"""MCP Tool 测试

参考 nanobot/tests/test_mcp_tool.py 实现
"""

import asyncio
import sys
from contextlib import AsyncExitStack, asynccontextmanager
from types import ModuleType, SimpleNamespace
from typing import Any, Dict, Optional

import pytest

from anyclaw.tools.mcp.wrapper import MCPToolWrapper
from anyclaw.tools.mcp.client import connect_mcp_servers
from anyclaw.tools.mcp.config import MCPServerConfig
from anyclaw.tools.registry import ToolRegistry


class _FakeTextContent:
    """模拟 MCP TextContent"""
    def __init__(self, text: str) -> None:
        self.text = text


@pytest.fixture
def fake_mcp_runtime() -> Dict[str, Any]:
    """MCP 运行时状态"""
    return {"session": None}


@pytest.fixture(autouse=True)
def _fake_mcp_module(
    monkeypatch: pytest.MonkeyPatch,
    fake_mcp_runtime: Dict[str, Any]
) -> None:
    """模拟 MCP 模块"""
    mod = ModuleType("mcp")
    mod.types = SimpleNamespace(TextContent=_FakeTextContent)

    class _FakeStdioServerParameters:
        def __init__(self, command: str, args: list, env: Optional[dict] = None) -> None:
            self.command = command
            self.args = args
            self.env = env

    class _FakeClientSession:
        def __init__(self, _read: object, _write: object) -> None:
            self._session = fake_mcp_runtime["session"]

        async def __aenter__(self) -> object:
            return self._session

        async def __aexit__(self, exc_type, exc, tb) -> bool:
            return False

    @asynccontextmanager
    async def _fake_stdio_client(_params: object):
        yield object(), object()

    @asynccontextmanager
    async def _fake_sse_client(_url: str, httpx_client_factory=None):
        yield object(), object()

    @asynccontextmanager
    async def _fake_streamable_http_client(_url: str, http_client=None):
        yield object(), object(), object()

    mod.ClientSession = _FakeClientSession
    mod.StdioServerParameters = _FakeStdioServerParameters
    monkeypatch.setitem(sys.modules, "mcp", mod)

    client_mod = ModuleType("mcp.client")
    stdio_mod = ModuleType("mcp.client.stdio")
    stdio_mod.stdio_client = _fake_stdio_client
    sse_mod = ModuleType("mcp.client.sse")
    sse_mod.sse_client = _fake_sse_client
    streamable_http_mod = ModuleType("mcp.client.streamable_http")
    streamable_http_mod.streamable_http_client = _fake_streamable_http_client

    monkeypatch.setitem(sys.modules, "mcp.client", client_mod)
    monkeypatch.setitem(sys.modules, "mcp.client.stdio", stdio_mod)
    monkeypatch.setitem(sys.modules, "mcp.client.sse", sse_mod)
    monkeypatch.setitem(sys.modules, "mcp.client.streamable_http", streamable_http_mod)


def _make_wrapper(session: object, *, timeout: float = 0.1) -> MCPToolWrapper:
    """创建 MCPToolWrapper 测试实例"""
    tool_def = SimpleNamespace(
        name="demo",
        description="demo tool",
        inputSchema={"type": "object", "properties": {}},
    )
    return MCPToolWrapper(session, "test", tool_def, tool_timeout=timeout)


# ============ MCPToolWrapper 测试 ============

@pytest.mark.asyncio
async def test_execute_returns_text_blocks() -> None:
    """测试 execute 返回文本块"""
    async def call_tool(_name: str, arguments: dict) -> object:
        assert arguments == {"value": 1}
        return SimpleNamespace(content=[_FakeTextContent("hello"), 42])

    wrapper = _make_wrapper(SimpleNamespace(call_tool=call_tool))

    result = await wrapper.execute(value=1)

    assert result == "hello\n42"


@pytest.mark.asyncio
async def test_execute_returns_timeout_message() -> None:
    """测试超时处理"""
    async def call_tool(_name: str, arguments: dict) -> object:
        await asyncio.sleep(1)
        return SimpleNamespace(content=[])

    wrapper = _make_wrapper(SimpleNamespace(call_tool=call_tool), timeout=0.01)

    result = await wrapper.execute()

    assert result == "(MCP tool call timed out after 0.01s)"


@pytest.mark.asyncio
async def test_execute_handles_server_cancelled_error() -> None:
    """测试服务器取消错误处理"""
    async def call_tool(_name: str, arguments: dict) -> object:
        raise asyncio.CancelledError()

    wrapper = _make_wrapper(SimpleNamespace(call_tool=call_tool))

    result = await wrapper.execute()

    assert result == "(MCP tool call was cancelled)"


@pytest.mark.asyncio
async def test_execute_re_raises_external_cancellation() -> None:
    """测试外部取消重新抛出"""
    started = asyncio.Event()

    async def call_tool(_name: str, arguments: dict) -> object:
        started.set()
        await asyncio.sleep(60)
        return SimpleNamespace(content=[])

    wrapper = _make_wrapper(SimpleNamespace(call_tool=call_tool), timeout=10)
    task = asyncio.create_task(wrapper.execute())
    await started.wait()

    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_execute_handles_generic_exception() -> None:
    """测试通用异常处理"""
    async def call_tool(_name: str, arguments: dict) -> object:
        raise RuntimeError("boom")

    wrapper = _make_wrapper(SimpleNamespace(call_tool=call_tool))

    result = await wrapper.execute()

    assert result == "(MCP tool call failed: RuntimeError)"


# ============ connect_mcp_servers 测试 ============

def _make_tool_def(name: str) -> SimpleNamespace:
    """创建工具定义"""
    return SimpleNamespace(
        name=name,
        description=f"{name} tool",
        inputSchema={"type": "object", "properties": {}},
    )


def _make_fake_session(tool_names: list) -> SimpleNamespace:
    """创建模拟 session"""
    async def initialize() -> None:
        return None

    async def list_tools() -> SimpleNamespace:
        return SimpleNamespace(tools=[_make_tool_def(name) for name in tool_names])

    return SimpleNamespace(initialize=initialize, list_tools=list_tools)


@pytest.mark.asyncio
async def test_connect_mcp_servers_enabled_tools_supports_raw_names(
    fake_mcp_runtime: Dict[str, Any],
) -> None:
    """测试 enabled_tools 支持原始名称"""
    fake_mcp_runtime["session"] = _make_fake_session(["demo", "other"])
    registry = ToolRegistry()
    stack = AsyncExitStack()
    await stack.__aenter__()
    try:
        await connect_mcp_servers(
            {"test": MCPServerConfig(command="fake", enabled_tools=["demo"])},
            registry,
            stack,
        )
    finally:
        await stack.aclose()

    assert registry.tool_names == ["mcp_test_demo"]


@pytest.mark.asyncio
async def test_connect_mcp_servers_enabled_tools_defaults_to_all(
    fake_mcp_runtime: Dict[str, Any],
) -> None:
    """测试默认启用所有工具"""
    fake_mcp_runtime["session"] = _make_fake_session(["demo", "other"])
    registry = ToolRegistry()
    stack = AsyncExitStack()
    await stack.__aenter__()
    try:
        await connect_mcp_servers(
            {"test": MCPServerConfig(command="fake")},
            registry,
            stack,
        )
    finally:
        await stack.aclose()

    assert registry.tool_names == ["mcp_test_demo", "mcp_test_other"]


@pytest.mark.asyncio
async def test_connect_mcp_servers_enabled_tools_supports_wrapped_names(
    fake_mcp_runtime: Dict[str, Any],
) -> None:
    """测试 enabled_tools 支持 wrapped 名称"""
    fake_mcp_runtime["session"] = _make_fake_session(["demo", "other"])
    registry = ToolRegistry()
    stack = AsyncExitStack()
    await stack.__aenter__()
    try:
        await connect_mcp_servers(
            {"test": MCPServerConfig(command="fake", enabled_tools=["mcp_test_demo"])},
            registry,
            stack,
        )
    finally:
        await stack.aclose()

    assert registry.tool_names == ["mcp_test_demo"]


@pytest.mark.asyncio
async def test_connect_mcp_servers_enabled_tools_empty_list_registers_none(
    fake_mcp_runtime: Dict[str, Any],
) -> None:
    """测试空列表不注册任何工具"""
    fake_mcp_runtime["session"] = _make_fake_session(["demo", "other"])
    registry = ToolRegistry()
    stack = AsyncExitStack()
    await stack.__aenter__()
    try:
        await connect_mcp_servers(
            {"test": MCPServerConfig(command="fake", enabled_tools=[])},
            registry,
            stack,
        )
    finally:
        await stack.aclose()

    assert registry.tool_names == []


@pytest.mark.asyncio
async def test_connect_mcp_servers_enabled_tools_warns_on_unknown_entries(
    fake_mcp_runtime: Dict[str, Any],
    monkeypatch: pytest.MonkeyPatch
) -> None:
    """测试未知工具名警告"""
    import logging

    fake_mcp_runtime["session"] = _make_fake_session(["demo"])
    registry = ToolRegistry()
    warnings: list[str] = []

    # 捕获 warning 日志
    class WarningHandler(logging.Handler):
        def emit(self, record):
            if record.levelno == logging.WARNING:
                warnings.append(record.getMessage())

    handler = WarningHandler()
    logging.getLogger("anyclaw.tools.mcp.client").addHandler(handler)

    stack = AsyncExitStack()
    await stack.__aenter__()
    try:
        await connect_mcp_servers(
            {"test": MCPServerConfig(command="fake", enabled_tools=["unknown"])},
            registry,
            stack,
        )
    finally:
        await stack.aclose()

    assert registry.tool_names == []
    assert warnings
    # 检查警告消息包含预期内容
    warning_text = warnings[-1]
    assert "enabledTools entries not found: unknown" in warning_text
    assert "Available raw names: demo" in warning_text
    assert "Available wrapped names: mcp_test_demo" in warning_text


# ============ MCPServerConfig 测试 ============

def test_mcp_server_config_stdio_type():
    """测试 stdio 配置"""
    cfg = MCPServerConfig(command="npx", args=["-y", "@anthropic/mcp-server"])
    assert cfg.get_effective_type() == "stdio"


def test_mcp_server_config_sse_type():
    """测试 SSE 配置"""
    cfg = MCPServerConfig(url="https://api.example.com/mcp/sse")
    assert cfg.get_effective_type() == "sse"


def test_mcp_server_config_http_type():
    """测试 HTTP 配置"""
    cfg = MCPServerConfig(url="https://api.example.com/mcp")
    assert cfg.get_effective_type() == "streamableHttp"


def test_mcp_server_config_explicit_type():
    """测试显式指定类型"""
    cfg = MCPServerConfig(type="sse", url="https://api.example.com/mcp")
    assert cfg.get_effective_type() == "sse"


def test_mcp_server_config_no_type():
    """测试无类型配置"""
    cfg = MCPServerConfig()
    assert cfg.get_effective_type() is None
