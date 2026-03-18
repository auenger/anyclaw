"""Shell 执行工具"""

import asyncio
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Tool


class ExecTool(Tool):
    """Shell 命令执行工具"""

    _MAX_TIMEOUT = 300
    _MAX_OUTPUT = 10_000

    def __init__(
        self,
        timeout: int = 60,
        working_dir: Optional[str] = None,
        deny_patterns: Optional[List[str]] = None,
        path_append: str = "",
    ):
        self.timeout = timeout
        self.working_dir = working_dir
        self.path_append = path_append
        self.deny_patterns = deny_patterns or [
            r"\brm\s+-[rf]{1,2}\b",
            r"\b(shutdown|reboot|poweroff)\b",
            r">\s*/dev/sd",
        ]

    @property
    def name(self) -> str:
        return "exec"

    @property
    def description(self) -> str:
        return "执行 shell 命令并返回输出。谨慎使用。"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "要执行的 shell 命令",
                },
                "working_dir": {
                    "type": "string",
                    "description": "工作目录（可选）",
                },
                "timeout": {
                    "type": "integer",
                    "description": "超时时间（秒），默认 60，最大 300",
                    "minimum": 1,
                    "maximum": 300,
                },
            },
            "required": ["command"],
        }

    async def execute(
        self,
        command: str,
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> str:
        cwd = working_dir or self.working_dir or os.getcwd()

        # 安全检查
        guard_error = self._guard_command(command)
        if guard_error:
            return guard_error

        effective_timeout = min(timeout or self.timeout, self._MAX_TIMEOUT)

        env = os.environ.copy()
        if self.path_append:
            env["PATH"] = env.get("PATH", "") + os.pathsep + self.path_append

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=effective_timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    pass
                return f"错误: 命令在 {effective_timeout} 秒后超时"

            output_parts = []

            if stdout:
                output_parts.append(stdout.decode("utf-8", errors="replace"))

            if stderr:
                stderr_text = stderr.decode("utf-8", errors="replace")
                if stderr_text.strip():
                    output_parts.append(f"[stderr]\n{stderr_text}")

            output_parts.append(f"\n退出码: {process.returncode}")

            result = "\n".join(output_parts) if output_parts else "(无输出)"

            # 截断过长输出
            if len(result) > self._MAX_OUTPUT:
                half = self._MAX_OUTPUT // 2
                result = (
                    result[:half]
                    + f"\n\n... ({len(result) - self._MAX_OUTPUT:,} 字符已截断) ...\n\n"
                    + result[-half:]
                )

            return result

        except Exception as e:
            return f"执行命令时出错: {str(e)}"

    def _guard_command(self, command: str) -> Optional[str]:
        """安全检查"""
        cmd = command.strip().lower()

        for pattern in self.deny_patterns:
            if re.search(pattern, cmd):
                return "错误: 命令被安全策略阻止（检测到危险模式）"

        return None
