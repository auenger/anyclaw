"""文件系统工具"""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Tool
from anyclaw.security.validators import PathValidator, ValidationError
from anyclaw.security.path import PathGuard, PathSecurityError


class ReadFileTool(Tool):
    """读取文件工具"""

    _MAX_SIZE = 100_000

    def __init__(
        self,
        workspace: Optional[Path] = None,
        allowed_dir: Optional[Path] = None,
        path_guard: Optional[PathGuard] = None,
    ):
        self.workspace = workspace or Path.cwd()
        self.allowed_dir = allowed_dir or self.workspace
        self.path_guard = path_guard

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
            # 路径安全验证（使用 PathGuard）
            if self.path_guard:
                try:
                    file_path = self.path_guard.resolve_and_validate(path)
                except PathSecurityError as e:
                    return f"错误: {e}"
            else:
                # 回退到旧的验证逻辑
                path = PathValidator.validate_path(path, self.workspace)
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
        """解析路径（向后兼容）"""
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
        path_guard: Optional[PathGuard] = None,
    ):
        self.workspace = workspace or Path.cwd()
        self.allowed_dir = allowed_dir or self.workspace
        self.restrict_to_workspace = restrict_to_workspace
        self.path_guard = path_guard

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
            # 路径安全验证（使用 PathGuard）
            if self.path_guard:
                try:
                    file_path = self.path_guard.resolve_and_validate(path, for_write=True)
                except PathSecurityError as e:
                    return f"错误: {e}"
            else:
                # 验证路径（旧逻辑）
                path = PathValidator.validate_path(path, self.workspace)
                file_path = self._resolve_path(path)

            # 验证内容非空
            if not content:
                return "错误: 内容不能为空"

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
        """解析路径并进行权限检查（向后兼容）"""
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
    """列出目录工具（带超时和限制）"""

    _DEFAULT_MAX = 200  # 默认最大条目数
    _IGNORE_DIRS = {  # 忽略常见噪声目录
        ".git", "node_modules", "__pycache__", ".venv", "venv",
        "dist", "build", ".tox", ".mypy_cache", ".pytest_cache",
        ".ruff_cache", ".coverage", "htmlcov",
    }

    def __init__(
        self,
        workspace: Optional[Path] = None,
        allowed_dir: Optional[Path] = None,
        timeout: int = 30,  # 添加超时参数（默认 30 秒）
        max_entries: int = 200,  # 添加最大条目数限制
        path_guard: Optional[PathGuard] = None,
    ):
        self.workspace = workspace or Path.cwd()
        self.allowed_dir = allowed_dir or self.workspace
        self.timeout = timeout
        self.max_entries = max_entries
        self.path_guard = path_guard

    @property
    def name(self) -> str:
        return "list_dir"

    @property
    def description(self) -> str:
        return "列出目录内容（支持递归和最大条目限制）"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "目录路径（默认为工作区）",
                },
                "max_entries": {
                    "type": "integer",
                    "description": "最大返回条目数（默认 200）",
                    "minimum": 1,
                    "default": self.max_entries,
                },
            },
            "required": [],
        }

    async def execute(self, path: str = ".", max_entries: int = None, **kwargs: Any) -> str:
        """使用 asyncio.wait_for 添加超时控制"""
        try:
            effective_max = max_entries or self.max_entries
            return await asyncio.wait_for(
                self._list_directory(path, effective_max),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            return f"错误: 列出目录超时（{self.timeout}秒）"

    async def _list_directory(self, path: str, max_entries: int) -> str:
        """异步列出目录内容（使用线程池）"""
        # 路径安全验证（使用 PathGuard）
        if self.path_guard:
            try:
                dir_path = self.path_guard.resolve_and_validate(path)
            except PathSecurityError as e:
                return f"错误: {e}"
        else:
            dir_path = self._resolve_path(path)

        if not dir_path.exists():
            return f"错误: 目录不存在: {path}"

        if not dir_path.is_dir():
            return f"错误: 不是目录: {path}"

        # 在线程池中执行，避免阻塞事件循环
        loop = asyncio.get_event_loop()
        items = await loop.run_in_executor(
            None,
            lambda: self._list_items(dir_path, max_entries)
        )

        if not items:
            return "(空目录)"

        result = "\n".join(items)
        if len(items) > max_entries:
            result += f"\n\n(已截断，显示前 {max_entries} 个，共 {self._total_count} 个)"

        return result

    def _list_items(self, dir_path: Path, max_entries: int) -> List[str]:
        """列出目录项（在线程中执行）"""
        items = []
        self._total_count = 0

        for item in sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            # 忽略噪声目录
            if item.name in self._IGNORE_DIRS:
                continue

            self._total_count += 1
            if len(items) >= max_entries:
                break

            item_type = "📁" if item.is_dir() else "📄"
            size = ""
            if item.is_file():
                try:
                    size = f" ({item.stat().st_size:,} bytes)"
                except:
                    pass
            items.append(f"{item_type} {item.name}{size}")

        return items

    def _resolve_path(self, path: str) -> Path:
        """解析路径（向后兼容）"""
        p = Path(path)
        if p.is_absolute():
            return p
        return self.workspace / p
