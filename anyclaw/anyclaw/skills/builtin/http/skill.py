"""HTTP 请求技能

执行 HTTP 请求并返回响应。
"""

import subprocess
from anyclaw.skills.base import Skill


class HttpSkill(Skill):
    """Execute HTTP requests"""

    async def execute(
        self,
        url: str = "",
        method: str = "GET",
        headers: str = "",
        data: str = "",
        **kwargs
    ) -> str:
        """Execute HTTP request using curl

        Args:
            url: URL to request
            method: HTTP method (GET, POST, PUT, DELETE)
            headers: Headers in format "Key: Value"
            data: Request body data

        Returns:
            HTTP response
        """
        if not url:
            return "Please provide a URL"

        # 检查 curl 是否可用
        try:
            subprocess.run(["curl", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "Error: curl command not available"

        # 构建 curl 命令
        cmd = ["curl", "-s", "-X", method.upper()]

        # 添加请求头
        if headers:
            for header in headers.split(","):
                header = header.strip()
                if header:
                    cmd.extend(["-H", header])

        # 添加请求体
        if data:
            cmd.extend(["-d", data])

        cmd.append(url)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return result.stdout[:5000]  # 限制输出长度
            else:
                return f"HTTP request failed: {result.stderr}"

        except subprocess.TimeoutExpired:
            return "HTTP request timed out"
        except Exception as e:
            return f"Error executing HTTP request: {str(e)}"
