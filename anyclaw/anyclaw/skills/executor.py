"""Tool 执行器 - 执行 shell 命令并返回结果"""
import asyncio
import subprocess
import re
from typing import Dict, Any, Optional, List
from pathlib import Path

from .models import SkillDefinition


class ToolExecutionError(Exception):
    """Tool 执行错误"""
    pass


class ToolExecutor:
    """Tool 执行器"""

    def __init__(
        self,
        timeout: int = 60,
        max_output_size: int = 10000,
        cwd: Optional[str] = None
    ):
        """
        初始化执行器

        Args:
            timeout: 命令执行超时时间（秒）
            max_output_size: 最大输出大小（字符）
            cwd: 工作目录
        """
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.cwd = cwd or str(Path.cwd())

    async def execute(
        self,
        skill: SkillDefinition,
        arguments: Dict[str, Any]
    ) -> str:
        """
        执行 Skill 命令

        Args:
            skill: Skill 定义
            arguments: 参数字典

        Returns:
            命令输出
        """
        # 获取命令模板
        commands = skill.get_commands()
        if not commands:
            return f"Error: No commands defined for skill '{skill.name}'"

        # 使用第一个命令作为主命令
        command_template = commands[0]

        # 替换参数
        command = self._substitute_args(command_template, arguments)

        # 执行命令
        return await self._execute_command(command)

    async def _execute_command(self, command: str) -> str:
        """
        执行 shell 命令

        Args:
            command: 要执行的命令

        Returns:
            命令输出
        """
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.cwd
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return f"Error: Command timed out after {self.timeout} seconds"

            # 解码输出
            stdout_str = stdout.decode('utf-8', errors='replace')
            stderr_str = stderr.decode('utf-8', errors='replace')

            # 截断过长输出
            if len(stdout_str) > self.max_output_size:
                stdout_str = stdout_str[:self.max_output_size] + "\n... (output truncated)"
            if len(stderr_str) > self.max_output_size:
                stderr_str = stderr_str[:self.max_output_size] + "\n... (output truncated)"

            # 组合输出
            result = ""
            if stdout_str.strip():
                result += stdout_str.strip()
            if stderr_str.strip():
                if result:
                    result += "\n"
                result += f"[stderr] {stderr_str.strip()}"

            if process.returncode != 0:
                result = f"Error (exit code {process.returncode}): {result}"

            return result or "Command completed with no output"

        except FileNotFoundError as e:
            return f"Error: Command not found - {e}"
        except PermissionError as e:
            return f"Error: Permission denied - {e}"
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"

    def _substitute_args(
        self,
        template: str,
        arguments: Dict[str, Any]
    ) -> str:
        """
        替换命令模板中的参数

        Args:
            template: 命令模板
            arguments: 参数字典

        Returns:
            替换后的命令
        """
        result = template

        for key, value in arguments.items():
            # 安全转义值（防止命令注入）
            safe_value = self._escape_shell_arg(str(value))
            result = result.replace(f"{{{key}}}", safe_value)

        return result

    def _escape_shell_arg(self, arg: str) -> str:
        """
        转义 shell 参数

        Args:
            arg: 原始参数

        Returns:
            转义后的参数
        """
        # 如果参数包含特殊字符，用单引号包裹
        # 单引号内的内容会被原样保留
        if re.search(r'[^\w@%+=:,./-]', arg):
            # 替换单引号为 '\'' (结束引号，转义单引号，重新开始引号)
            arg = "'" + arg.replace("'", "'\\''") + "'"
        return arg

    async def execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        skills: Dict[str, SkillDefinition]
    ) -> str:
        """
        根据 tool call 执行对应的 skill

        Args:
            tool_name: 工具名称
            arguments: 参数
            skills: 可用 skills 字典

        Returns:
            执行结果
        """
        skill = skills.get(tool_name)
        if not skill:
            return f"Error: Tool '{tool_name}' not found"

        if not skill.eligible:
            reasons = ", ".join(skill.eligibility_reasons)
            return f"Error: Tool '{tool_name}' is not available. Reasons: {reasons}"

        return await self.execute(skill, arguments)
