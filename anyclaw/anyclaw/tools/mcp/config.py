"""MCP Server 配置模型"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class MCPServerConfig(BaseModel):
    """MCP Server 配置

    支持三种传输类型：
    - stdio: 本地进程通信
    - sse: Server-Sent Events
    - streamableHttp: HTTP 流式传输
    """

    type: Optional[Literal["stdio", "sse", "streamableHttp"]] = Field(
        default=None,
        description="传输类型，如果不指定则根据 command/url 自动推断"
    )

    # stdio 传输配置
    command: str = Field(
        default="",
        description="stdio: 启动命令"
    )
    args: List[str] = Field(
        default_factory=list,
        description="stdio: 命令参数"
    )
    env: Optional[Dict[str, str]] = Field(
        default=None,
        description="stdio: 环境变量"
    )

    # HTTP/SSE 传输配置
    url: str = Field(
        default="",
        description="HTTP/SSE: 服务器 URL"
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="HTTP/SSE: 请求头"
    )

    # 工具配置
    tool_timeout: int = Field(
        default=30,
        ge=1,
        description="工具调用超时时间（秒）"
    )
    enabled_tools: List[str] = Field(
        default_factory=lambda: ["*"],
        description="启用的工具列表，'*' 表示全部"
    )

    model_config = {
        "extra": "allow",
    }

    def get_effective_type(self) -> Optional[str]:
        """获取有效的传输类型"""
        if self.type:
            return self.type
        if self.command:
            return "stdio"
        if self.url:
            # 约定：以 /sse 结尾的 URL 使用 SSE 传输
            return "sse" if self.url.rstrip("/").endswith("/sse") else "streamableHttp"
        return None
