"""文件操作技能

执行基本的文件读写操作。
"""

import os
from pathlib import Path
from anyclaw.skills.base import Skill


class FileSkill(Skill):
    """File operations: read, write, list, delete"""

    async def execute(
        self,
        action: str = "",
        path: str = "",
        content: str = "",
        **kwargs
    ) -> str:
        """Execute file operation

        Args:
            action: Operation to perform (read, write, list, delete, exists)
            path: File or directory path
            content: Content to write (for write action)

        Returns:
            Operation result
        """
        if not action:
            return "Please specify an action: read, write, list, delete, exists"

        if not path and action != "list":
            return "Please provide a file path"

        try:
            path_obj = Path(path).expanduser().resolve()

            if action == "read":
                return self._read_file(path_obj)
            elif action == "write":
                return self._write_file(path_obj, content)
            elif action == "list":
                return self._list_dir(path_obj if path else Path.cwd())
            elif action == "delete":
                return self._delete_file(path_obj)
            elif action == "exists":
                return self._check_exists(path_obj)
            else:
                return f"Unknown action: {action}. Supported: read, write, list, delete, exists"

        except Exception as e:
            return f"Error: {str(e)}"

    def _read_file(self, path: Path) -> str:
        """Read file content"""
        if not path.exists():
            return f"File not found: {path}"
        if not path.is_file():
            return f"Not a file: {path}"

        try:
            content = path.read_text(encoding="utf-8")
            # 限制输出长度
            if len(content) > 10000:
                content = content[:10000] + "\n\n... [content truncated]"
            return f"Content of {path}:\n\n{content}"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def _write_file(self, path: Path, content: str) -> str:
        """Write content to file"""
        if not content:
            return "Please provide content to write"

        try:
            # 确保父目录存在
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return f"Successfully wrote {len(content)} characters to {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    def _list_dir(self, path: Path) -> str:
        """List directory contents"""
        if not path.exists():
            return f"Directory not found: {path}"
        if not path.is_dir():
            return f"Not a directory: {path}"

        try:
            items = list(path.iterdir())
            if not items:
                return f"Empty directory: {path}"

            result = [f"Contents of {path}:"]
            for item in sorted(items):
                if item.is_dir():
                    result.append(f"  📁 {item.name}/")
                else:
                    size = item.stat().st_size
                    result.append(f"  📄 {item.name} ({size} bytes)")

            return "\n".join(result)
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    def _delete_file(self, path: Path) -> str:
        """Delete file"""
        if not path.exists():
            return f"File not found: {path}"
        if path.is_dir():
            return f"Cannot delete directory: {path}. Use rm -r command instead."

        try:
            path.unlink()
            return f"Successfully deleted: {path}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"

    def _check_exists(self, path: Path) -> str:
        """Check if path exists"""
        if path.exists():
            if path.is_file():
                return f"✓ File exists: {path}"
            else:
                return f"✓ Directory exists: {path}"
        else:
            return f"✗ Path does not exist: {path}"
