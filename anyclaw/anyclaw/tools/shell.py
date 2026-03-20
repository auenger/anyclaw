"""Shell 执行工具"""

import asyncio
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Tool
from .guards import CommandGuard
from anyclaw.security.validators import Validator, ValidationError
from anyclaw.security.sanitizers import ContentSanitizer


class ExecTool(Tool):
    """Shell 命令执行工具

    安全机制：
    - 输入验证：命令非空检查、超时范围验证
    - 核心保护层：硬编码的危险命令拦截（不可绕过）
    - 用户保护层：可配置的 deny/allow patterns
    """

    _MAX_TIMEOUT = 600  # 从 300 增加到 600（与 nanobot 一致）
    _MAX_OUTPUT = 10_000
    # 超时处理时间（渐进式 kill 策略）
    _GRACEFUL_WAIT = 10  # SIGTERM 等待时间（优雅退出）
    _FORCE_WAIT = 3     # SIGKILL 等待时间（强制终止）

    def __init__(
        self,
        timeout: int = 60,
        working_dir: Optional[str] = None,
        deny_patterns: Optional[List[str]] = None,
        allow_patterns: Optional[List[str]] = None,
        path_append: str = "",
    ):
        self.timeout = timeout
        self.working_dir = working_dir
        self.path_append = path_append

        # 用户自定义 deny/allow patterns（保留向后兼容）
        self.user_deny_patterns = deny_patterns or []
        self.user_allow_patterns = allow_patterns or []

        # 初始化命令保护器
        self.guard = CommandGuard(
            user_deny_patterns=self.user_deny_patterns,
            user_allow_patterns=self.user_allow_patterns,
        )

        # 向后兼容：保留 deny_patterns 属性
        self.deny_patterns = self.user_deny_patterns

    @property
    def name(self) -> str:
        return "exec"

    @property
    def description(self) -> str:
        return "执行 shell 命令并返回输出。谨慎使用."

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
        # === 输入验证 ===
        try:
            # 验证命令非空
            command = ContentSanitizer.sanitize_command(command)
        except ValueError as e:
            return f"错误: {e}"

        # 验证 timeout 范围
        if timeout is not None:
            try:
                timeout = Validator.in_range(timeout, 1, self._MAX_TIMEOUT, "timeout")
            except ValidationError as e:
                return f"错误: {e.message}"

        cwd = working_dir or self.working_dir or os.getcwd()

        # 安全检查（传递 cwd）
        guard_error = self._guard_command(command, cwd)
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
                # 超时处理（改进版 - 渐进式 kill 策略）
                # 1. 首先尝试 SIGTERM（优雅退出）
                try:
                    process.terminate()
                    # 等待进程退出（最多 10 秒）
                    try:
                        await asyncio.wait_for(
                            process.wait(),
                            timeout=10.0  # 给进程 10 秒时间优雅退出
                        )
                        return f"错误: 命令在 {effective_timeout} 秒后超时，已终止"
                    except asyncio.TimeoutError:
                        # 2. 如果 SIGTERM 失败，尝试 SIGKILL（强制终止）
                        import signal
                        try:
                            process.kill()
                            # 再等待 3 秒
                            try:
                                await asyncio.wait_for(
                                    process.wait(),
                                    timeout=3.0
                                )
                                return f"错误: 命令在 {effective_timeout} 秒后超时，已强制终止"
                            except asyncio.TimeoutError:
                                # 3. 如果还是没退出，杀死进程组
                                try:
                                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                                except (ProcessLookupError, PermissionError):
                                    pass
                                return f"错误: 命令在 {effective_timeout} 秒后超时，进程组已强制终止"
                        except (ProcessLookupError, PermissionError):
                            pass
                except (ProcessLookupError, PermissionError):
                    # 进程可能已经退出
                    pass
                except Exception as e:
                    return f"错误: 超时后终止进程失败: {str(e)}"

            output_parts = []

            if stdout:
                output_parts.append(stdout.decode("utf-8", errors="replace"))

            if stderr:
                stderr_text = stderr.decode("utf-8", errors="replace")
                if stderr_text.strip():
                    output_parts.append(f"[stderr]\n{stderr_text}")  # 与 nanobot 一致

            if process.returncode is not None:  # 检查退出码是否存在
                output_parts.append(f"\nExit code: {process.returncode}")

            result = "\n".join(output_parts) if output_parts else "(no output)"

            # 保留头部和尾部（与 nanobot 一致）
            if len(result) > self._MAX_OUTPUT:
                half = self._MAX_OUTPUT // 2
                result = (
                    result[:half]
                    + f"\n\n... ({len(result) - self._MAX_OUTPUT:,} chars truncated) ...\n\n"
                    + result[-half:]
                )

            return result

        except Exception as e:
            # 确保进程被清理
            if process and process.returncode is None:
                try:
                    process.kill()
                    await asyncio.wait_for(process.wait(), timeout=2.0)
                except:
                    pass

            return f"执行命令时出错: {str(e)}"

    def _guard_command(self, command: str, cwd: str) -> Optional[str]:
        """安全检查（使用混合保护模式）

        检查优先级：
        1. 检查 allow_all_access（跳过所有检查）
        2. 核心保护（不可绕过）
        3. 用户 deny_patterns
        4. 用户 allow_patterns（如果启用）
        5. 路径遍历检查
        6. 内部 URL 检查（SSRF）
        7. 路径限制检查
        """
        from anyclaw.config.settings import settings

        # 检查是否开放所有权限
        allow_all = getattr(settings, 'allow_all_access', False)
        exec_unrestricted = getattr(settings, 'exec_unrestricted', False)

        # 如果开放所有权限或执行不限制，跳过安全检查
        if allow_all or exec_unrestricted:
            return None

        blocked, reason = self.guard.check(command)
        if blocked:
            return f"错误: 命令被安全策略阻止 - {reason}"

        cmd = command.strip()
        lower = cmd.lower()

        # 路径遍历检查
        if "..\\" in cmd or "../" in cmd:
            return "错误: 命令被安全策略阻止 - 检测到路径遍历"

        # 内部 URL 检查（SSRF 防护）
        ssrf_enabled = getattr(settings, 'ssrf_enabled', True)
        if ssrf_enabled:
            _URL_RE = re.compile(r'https?://[^\s\"\'`;|<>]+', re.IGNORECASE)
            for m in _URL_RE.finditer(cmd):
                url = m.group(0)
                from anyclaw.security.network import SSRFGuard
                ssrf_guard = SSRFGuard(enabled=True)
                if not ssrf_guard.is_safe_url(url):
                    return "错误: 命令被安全策略阻止 - 检测到内部/私有 URL"

        # Workspace 限制
        if settings.restrict_to_workspace:
            cwd_path = Path(cwd).resolve()
            for raw in self._extract_absolute_paths(cmd):
                try:
                    expanded = os.path.expandvars(raw.strip())
                    p = Path(expanded).expanduser().resolve()
                except Exception:
                    continue
                if p.is_absolute() and cwd_path not in p.parents and p != cwd_path:
                    return f"错误: 命令被安全策略阻止 - 路径超出工作目录"

        return None

    @staticmethod
    def _extract_absolute_paths(command: str) -> List[str]:
        """提取命令中的绝对路径（Windows + POSIX + home）"""
        # Windows 路径
        win_paths = re.findall(r"[A-Za-z]:\\[^\s\"'|><;]+", command)
        # POSIX 绝对路径
        posix_paths = re.findall(r"(?:^|[\s|>'\"])(/[^\s\"'>;|<]+)", command)
        # Home 快捷方式
        home_paths = re.findall(r"(?:^|[\s|>'\"])(~[^\s\"'>;|<]*)", command)
        return win_paths + posix_paths + home_paths
