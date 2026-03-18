"""代码执行技能

执行 Python/JavaScript/Bash 代码片段。
"""

import asyncio
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional

from anyclaw.skills.base import Skill


class CodeExecSkill(Skill):
    """Execute code in various languages"""

    # 支持的语言及其执行器
    EXECUTORS = {
        "python": {
            "ext": ".py",
            "cmd": ["python3"],
            "check": "python3 --version",
        },
        "javascript": {
            "ext": ".js",
            "cmd": ["node"],
            "check": "node --version",
        },
        "bash": {
            "ext": ".sh",
            "cmd": ["bash"],
            "check": "bash --version",
        },
    }

    async def execute(
        self,
        language: str = "python",
        code: str = "",
        timeout: int = 30,
        **kwargs
    ) -> str:
        """Execute code in the specified language

        Args:
            language: Programming language (python, javascript, bash)
            code: Code to execute
            timeout: Execution timeout in seconds

        Returns:
            Execution result or error message
        """
        if not code:
            return "Error: No code provided"

        language = language.lower()
        if language not in self.EXECUTORS:
            available = ", ".join(self.EXECUTORS.keys())
            return f"Error: Unsupported language '{language}'. Available: {available}"

        executor = self.EXECUTORS[language]

        # 检查执行器是否可用
        if not await self._check_executor_available(executor["check"]):
            return f"Error: {language} executor not found. Please install {executor['cmd'][0]}"

        try:
            result = await self._execute_code(
                code=code,
                executor=executor,
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return f"Error: Execution timed out after {timeout} seconds"
        except Exception as e:
            return f"Error: {str(e)}"

    async def _check_executor_available(self, check_cmd: str) -> bool:
        """检查执行器是否可用"""
        try:
            proc = await asyncio.create_subprocess_shell(
                check_cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await proc.communicate()
            return proc.returncode == 0
        except Exception:
            return False

    async def _execute_code(
        self,
        code: str,
        executor: dict,
        timeout: int
    ) -> str:
        """执行代码并返回结果"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=executor["ext"],
            delete=False
        ) as f:
            f.write(code)
            temp_path = f.name

        try:
            # 构建命令
            cmd = executor["cmd"] + [temp_path]

            # 执行
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                raise

            # 解码输出
            stdout_str = stdout.decode('utf-8', errors='replace')
            stderr_str = stderr.decode('utf-8', errors='replace')

            # 构建结果
            result_parts = []
            if stdout_str:
                result_parts.append(stdout_str)
            if stderr_str:
                result_parts.append(f"[stderr]\n{stderr_str}")

            if not result_parts:
                if proc.returncode == 0:
                    return "Execution completed successfully (no output)"
                else:
                    return f"Execution failed with code {proc.returncode}"

            result = "\n".join(result_parts)
            if proc.returncode != 0:
                result = f"[Exit code: {proc.returncode}]\n{result}"

            return result

        finally:
            # 清理临时文件
            try:
                os.unlink(temp_path)
            except Exception:
                pass
