"""系统信息技能

获取系统信息和执行系统操作。
"""

import os
import platform
import shutil
from typing import Optional

from anyclaw.skills.base import Skill


class SystemSkill(Skill):
    """System information and operations"""

    # 敏感环境变量（不显示值）
    SENSITIVE_ENV_PATTERNS = [
        'KEY', 'SECRET', 'PASSWORD', 'TOKEN', 'API', 'CREDENTIAL',
        'AUTH', 'PRIVATE', 'CERT', 'SIGN',
    ]

    async def execute(
        self,
        action: str = "info",
        command: str = "",
        **kwargs
    ) -> str:
        """Execute system action

        Args:
            action: Operation to perform (info, env, which)
            command: Command to check (for which action)

        Returns:
            Operation result
        """
        action = action.lower().strip()

        if action == "info":
            return self._get_system_info()
        elif action == "env":
            return self._get_env(command)
        elif action == "which":
            return self._which(command)
        else:
            return f"Unknown action: {action}. Available: info, env, which"

    def _get_system_info(self) -> str:
        """获取系统信息"""
        lines = ["System Information:", ""]

        # 基本信息
        lines.append(f"  OS: {platform.system()} {platform.release()}")
        lines.append(f"  Platform: {platform.platform()}")
        lines.append(f"  Architecture: {platform.machine()}")
        lines.append(f"  Python: {platform.python_version()}")

        # CPU 信息（如果可用）
        try:
            import multiprocessing
            lines.append(f"  CPU Cores: {multiprocessing.cpu_count()}")
        except Exception:
            pass

        # 内存信息（如果可用）
        try:
            import psutil
            mem = psutil.virtual_memory()
            lines.append(f"  Memory: {self._format_bytes(mem.total)} "
                        f"(Available: {self._format_bytes(mem.available)})")
            lines.append(f"  Memory Usage: {mem.percent}%")
        except ImportError:
            pass

        # 磁盘信息（如果可用）
        try:
            import psutil
            disk = psutil.disk_usage('/')
            lines.append(f"  Disk: {self._format_bytes(disk.total)} "
                        f"(Free: {self._format_bytes(disk.free)})")
            lines.append(f"  Disk Usage: {disk.percent}%")
        except Exception:
            pass

        # 主机名
        lines.append(f"  Hostname: {platform.node()}")

        # 用户
        try:
            import getpass
            lines.append(f"  User: {getpass.getuser()}")
        except Exception:
            pass

        return "\n".join(lines)

    def _get_env(self, name: Optional[str] = None) -> str:
        """获取环境变量"""
        if name:
            # 获取特定环境变量
            value = os.environ.get(name)
            if value is None:
                return f"Environment variable '{name}' not set"
            if self._is_sensitive(name):
                return f"{name}=***HIDDEN***"
            return f"{name}={value}"

        # 列出所有环境变量
        lines = ["Environment Variables:", ""]

        env_items = []
        for key, value in sorted(os.environ.items()):
            if self._is_sensitive(key):
                env_items.append(f"  {key}=***HIDDEN***")
            else:
                # 截断过长的值
                display_value = value if len(value) <= 100 else value[:97] + "..."
                env_items.append(f"  {key}={display_value}")

        lines.extend(env_items)
        lines.append(f"\nTotal: {len(os.environ)} variables")

        return "\n".join(lines)

    def _which(self, command: str) -> str:
        """检查命令可用性"""
        if not command:
            return "Error: No command specified"

        # 使用 shutil.which 查找
        path = shutil.which(command)

        if path:
            return f"Found: {path}"
        else:
            # 检查是否是内置命令
            builtins = ['cd', 'echo', 'exit', 'export', 'source', 'alias', 'unalias']
            if command in builtins:
                return f"'{command}' is a shell builtin"

            return f"Command '{command}' not found"

    def _is_sensitive(self, name: str) -> bool:
        """检查是否是敏感环境变量"""
        name_upper = name.upper()
        for pattern in self.SENSITIVE_ENV_PATTERNS:
            if pattern in name_upper:
                return True
        return False

    def _format_bytes(self, size: int) -> str:
        """格式化字节大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
