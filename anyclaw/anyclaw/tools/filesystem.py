"""文件系统工具"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Tool


class ReadFileTool(Tool):
    """读取文件工具"""

    _MAX_SIZE = 100_000

    def __init__(self, workspace: Optional[Path] = None, allowed_dir: Optional[Path] = None):
        self.workspace = workspace or Path.cwd()
        self.allowed_dir = allowed_dir or self.workspace

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "读取文件内容"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径（相对或绝对）",
                },
                "offset": {
                    "type": "integer",
                    "description": "起始行号（可选，从 0 开始）",
                    "minimum": 0,
                },
                "limit": {
                    "type": "integer",
                    "description": "读取行数（可选）",
                    "minimum": 1,
                },
            },
            "required": ["path"],
        }

    async def execute(self, path: str, offset: int = 0, limit: Optional[int] = None, **kwargs: Any) -> str:
        try:
            file_path = self._resolve_path(path)

            if not file_path.exists():
                return f"错误: 文件不存在: {path}"

            if not file_path.is_file():
                return f"错误: 不是文件: {path}"

            # 检查文件大小
            size = file_path.stat().st_size
            if size > self._MAX_SIZE:
                return f"错误: 文件太大 ({size:,} 字节)，最大允许 {self._MAX_SIZE:,} 字节"

            # 读取文件
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            # 应用偏移和限制
            start = offset
            end = offset + limit if limit else len(lines)
            selected_lines = lines[start:end]

            # 添加行号
            result_lines = []
            for i, line in enumerate(selected_lines, start=offset):
                result_lines.append(f"{i:6d}\t{line.rstrip()}")

            result = "\n".join(result_lines)

            if not result:
                return "(空文件)"

            return result

        except Exception as e:
            return f"读取文件时出错: {str(e)}"

    def _resolve_path(self, path: str) -> Path:
        """解析路径"""
        p = Path(path)
        if p.is_absolute():
            return p
        return self.workspace / p


class WriteFileTool(Tool):
    """写入文件工具"""

    def __init__(
        self,
        workspace: Optional[Path] = None,
        allowed_dir: Optional[Path] = None,
        restrict_to_workspace: bool = True,
    ):
        self.workspace = workspace or Path.cwd()
        self.allowed_dir = allowed_dir or self.workspace
        self.restrict_to_workspace = restrict_to_workspace

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "写入内容到文件（会覆盖现有文件）"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "文件路径",
                },
                "content": {
                    "type": "string",
                    "description": "要写入的内容",
                },
            },
            "required": ["path", "content"],
        }

    async def execute(self, path: str, content: str, **kwargs: Any) -> str:
        try:
            file_path = self._resolve_path(path)

            # 创建父目录
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 写入文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            return f"成功写入 {len(content):,} 字符到 {path}"

        except PermissionError as e:
            return str(e)
        except Exception as e:
            return f"写入文件时出错: {str(e)}"

    def _resolve_path(self, path: str) -> Path:
        """解析路径并进行权限检查"""
        p = Path(path)
        if p.is_absolute():
            resolved = p.resolve()
        else:
            resolved = (self.workspace / p).resolve()

        # 如果启用了 workspace 限制，检查路径是否在允许范围内
        if self.restrict_to_workspace:
            allowed_resolved = self.allowed_dir.resolve()
            try:
                # 检查解析后的路径是否在允许的目录内
                resolved.relative_to(allowed_resolved)
            except ValueError:
                raise PermissionError(
                    f"权限错误: 路径 {path} 超出 workspace 范围\n"
                    f"允许的目录: {allowed_resolved}\n"
                    f"提示: 设置 restrict_to_workspace=false 可禁用此限制"
                )

        return resolved


class ListDirTool(Tool):
    """列出目录工具"""

    def __init__(self, workspace: Optional[Path] = None, allowed_dir: Optional[Path] = None):
        self.workspace = workspace or Path.cwd()
        self.allowed_dir = allowed_dir or self.workspace

    @property
    def name(self) -> str:
        return "list_dir"

    @property
    def description(self) -> str:
        return "列出目录内容"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "目录路径（默认为工作区）",
                },
            },
            "required": [],
        }

    async def execute(self, path: str = ".", **kwargs: Any) -> str:
        try:
            dir_path = self._resolve_path(path)

            if not dir_path.exists():
                return f"错误: 目录不存在: {path}"

            if not dir_path.is_dir():
                return f"错误: 不是目录: {path}"

            # 列出内容
            items = []
            for item in sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                item_type = "📁" if item.is_dir() else "📄"
                size = ""
                if item.is_file():
                    try:
                        size = f" ({item.stat().st_size:,} bytes)"
                    except:
                        pass
                items.append(f"{item_type} {item.name}{size}")

            if not items:
                return "(空目录)"

            return "\n".join(items)

        except Exception as e:
            return f"列出目录时出错: {str(e)}"

    def _resolve_path(self, path: str) -> Path:
        """解析路径"""
        p = Path(path)
        if p.is_absolute():
            return p
        return self.workspace / p
