"""Persona 人设加载器

加载和管理智能体人设文件，包括 SOUL.md、USER.md、IDENTITY.md、TOOLS.md。
"""

import os
from pathlib import Path
from typing import Optional

from anyclaw.workspace.manager import WorkspaceManager
from anyclaw.workspace.templates import (
    SOUL_TEMPLATE,
    USER_TEMPLATE,
    IDENTITY_TEMPLATE,
    TOOLS_TEMPLATE,
)


class PersonaLoader:
    """人设加载器

    负责加载和管理智能体的人设文件，构建系统提示。
    """

    SOUL_FILE = "SOUL.md"
    USER_FILE = "USER.md"
    IDENTITY_FILE = "IDENTITY.md"
    TOOLS_FILE = "TOOLS.md"

    DEFAULT_MAX_CHARS = 10000

    def __init__(
        self,
        workspace: Optional[WorkspaceManager] = None,
        max_chars: Optional[int] = None,
    ):
        """初始化人设加载器

        Args:
            workspace: 工作区管理器
            max_chars: 每个文件的最大字符数
        """
        self.workspace = workspace or WorkspaceManager()
        self.max_chars = max_chars or int(
            os.environ.get("ANYCLAW_PERSONA_MAX_CHARS", self.DEFAULT_MAX_CHARS)
        )
        self._cache: dict = {}

    def _load_file(self, filename: str) -> Optional[str]:
        """加载单个文件

        Args:
            filename: 文件名

        Returns:
            文件内容，如果不存在则返回 None
        """
        filepath = self.workspace.path / filename

        if not filepath.exists():
            return None

        try:
            content = filepath.read_text(encoding="utf-8")

            # 截断过长的内容
            if len(content) > self.max_chars:
                content = content[:self.max_chars]
                content += f"\n\n... [文件已截断，原大小: {len(filepath.read_text())} 字符]"

            return content.strip()

        except Exception:
            return None

    def load_all(self, is_private: bool = True, use_cache: bool = True) -> dict:
        """加载所有人设文件

        Args:
            is_private: 是否为私密会话（影响 USER.md 是否加载）
            use_cache: 是否使用缓存

        Returns:
            包含所有人设内容的字典
        """
        cache_key = f"persona_{is_private}"

        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        persona = {
            "soul": self._load_file(self.SOUL_FILE),
            "identity": self._load_file(self.IDENTITY_FILE),
            "tools": self._load_file(self.TOOLS_FILE),
        }

        # 仅私密会话加载用户档案
        if is_private:
            persona["user"] = self._load_file(self.USER_FILE)

        if use_cache:
            self._cache[cache_key] = persona

        return persona

    def build_system_prompt(self, is_private: bool = True) -> str:
        """构建系统提示

        Args:
            is_private: 是否为私密会话

        Returns:
            格式化的系统提示字符串
        """
        persona = self.load_all(is_private)
        parts = []

        if persona.get("soul"):
            parts.append(f"## 人设\n\n{persona['soul']}")

        if persona.get("identity"):
            parts.append(f"## 身份\n\n{persona['identity']}")

        if is_private and persona.get("user"):
            parts.append(f"## 用户信息\n\n{persona['user']}")

        if persona.get("tools"):
            parts.append(f"## 工具说明\n\n{persona['tools']}")

        return "\n\n".join(parts)

    def create_default_files(self) -> list[str]:
        """创建默认人设文件

        Returns:
            创建的文件名列表
        """
        created = []

        files_to_create = [
            (self.SOUL_FILE, SOUL_TEMPLATE),
            (self.USER_FILE, USER_TEMPLATE),
            (self.IDENTITY_FILE, IDENTITY_TEMPLATE),
            (self.TOOLS_FILE, TOOLS_TEMPLATE),
        ]

        for filename, content in files_to_create:
            if self._create_if_missing(filename, content):
                created.append(filename)

        return created

    def _create_if_missing(self, filename: str, content: str) -> bool:
        """如果文件不存在则创建

        Args:
            filename: 文件名
            content: 文件内容

        Returns:
            是否创建了文件
        """
        filepath = self.workspace.path / filename

        if filepath.exists():
            return False

        try:
            filepath.write_text(content, encoding="utf-8")
            return True
        except Exception:
            return False

    def reset_file(self, filename: str) -> bool:
        """重置文件为默认模板

        Args:
            filename: 文件名

        Returns:
            是否重置成功
        """
        templates = {
            self.SOUL_FILE: SOUL_TEMPLATE,
            self.USER_FILE: USER_TEMPLATE,
            self.IDENTITY_FILE: IDENTITY_TEMPLATE,
            self.TOOLS_FILE: TOOLS_TEMPLATE,
        }

        if filename not in templates:
            return False

        filepath = self.workspace.path / filename

        try:
            filepath.write_text(templates[filename], encoding="utf-8")
            # 清除缓存
            self._cache.clear()
            return True
        except Exception:
            return False

    def get_file_path(self, filename: str) -> Optional[Path]:
        """获取文件路径

        Args:
            filename: 文件名

        Returns:
            文件路径，如果文件名无效则返回 None
        """
        valid_files = [
            self.SOUL_FILE,
            self.USER_FILE,
            self.IDENTITY_FILE,
            self.TOOLS_FILE,
        ]

        if filename not in valid_files:
            return None

        return self.workspace.path / filename

    def file_exists(self, filename: str) -> bool:
        """检查文件是否存在

        Args:
            filename: 文件名

        Returns:
            文件是否存在
        """
        path = self.get_file_path(filename)
        return path is not None and path.exists()

    def get_status(self) -> dict:
        """获取人设状态

        Returns:
            状态信息字典
        """
        files_status = {}

        for filename in [self.SOUL_FILE, self.USER_FILE, self.IDENTITY_FILE, self.TOOLS_FILE]:
            path = self.workspace.path / filename
            if path.exists():
                stat = path.stat()
                files_status[filename] = {
                    "exists": True,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                }
            else:
                files_status[filename] = {"exists": False}

        return {
            "workspace_path": str(self.workspace.path),
            "max_chars": self.max_chars,
            "files": files_status,
        }

    def clear_cache(self) -> None:
        """清除缓存"""
        self._cache.clear()

    def __repr__(self) -> str:
        return f"PersonaLoader(workspace={self.workspace.path})"


# 全局加载器实例
_persona_loader: Optional[PersonaLoader] = None


def get_persona_loader(
    workspace: Optional[WorkspaceManager] = None,
    max_chars: Optional[int] = None,
) -> PersonaLoader:
    """获取全局人设加载器实例

    Args:
        workspace: 工作区管理器
        max_chars: 每个文件的最大字符数

    Returns:
        PersonaLoader 实例
    """
    global _persona_loader

    if _persona_loader is None:
        _persona_loader = PersonaLoader(workspace=workspace, max_chars=max_chars)
    elif workspace is not None:
        # 更新工作区
        _persona_loader.workspace = workspace
        _persona_loader.clear_cache()

    return _persona_loader


def reset_persona_loader() -> None:
    """重置全局人设加载器"""
    global _persona_loader
    _persona_loader = None
