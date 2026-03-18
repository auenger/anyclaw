"""Workspace Manager - 工作区管理器"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List

from anyclaw.workspace.templates import sync_workspace_templates, GITIGNORE_TEMPLATE


class WorkspaceManager:
    """工作区管理器

    管理智能体工作区目录，支持多 Profile 和自定义路径。
    """

    DEFAULT_BASE_DIR = ".anyclaw"
    DEFAULT_WORKSPACE_NAME = "workspace"

    def __init__(
        self,
        workspace_path: Optional[str] = None,
        profile: Optional[str] = None,
    ):
        """初始化工作区管理器

        Args:
            workspace_path: 自定义工作区路径（优先级最高）
            profile: Profile 名称，用于多工作区隔离
        """
        self._profile = profile or os.environ.get("ANYCLAW_PROFILE", "default")
        self._custom_path = workspace_path

        # 解析实际路径
        self._path = self._resolve_path()

    def _resolve_path(self) -> Path:
        """解析工作区路径

        优先级：
        1. 自定义路径 (workspace_path)
        2. Profile 路径 (~/.anyclaw/workspace-{profile})
        3. 默认路径 (~/.anyclaw/workspace)
        """
        if self._custom_path:
            return Path(self._custom_path).expanduser().resolve()

        base_dir = Path.home() / self.DEFAULT_BASE_DIR

        if self._profile and self._profile.lower() != "default":
            return base_dir / f"{self.DEFAULT_WORKSPACE_NAME}-{self._profile}"
        else:
            return base_dir / self.DEFAULT_WORKSPACE_NAME

    @property
    def path(self) -> Path:
        """工作区路径"""
        return self._path

    @property
    def profile(self) -> str:
        """当前 Profile"""
        return self._profile

    @property
    def state_dir(self) -> Path:
        """状态目录 (~/.anyclaw/)

        用于存储配置和凭证，与工作区分离。
        """
        return Path.home() / self.DEFAULT_BASE_DIR

    def exists(self) -> bool:
        """检查工作区是否存在"""
        return self._path.exists()

    def is_git_repo(self) -> bool:
        """检查是否是 git 仓库"""
        return (self._path / ".git").exists()

    def create(self, init_git: bool = True, force: bool = False, silent: bool = False) -> List[str]:
        """创建工作区

        Args:
            init_git: 是否初始化 git 仓库
            force: 是否强制重新创建（删除已存在的）
            silent: 是否静默模式

        Returns:
            创建的文件列表
        """
        try:
            # 强制模式下删除已存在的目录
            if force and self._path.exists():
                shutil.rmtree(self._path)

            # 创建目录
            self._path.mkdir(parents=True, exist_ok=True)

            # 初始化 git
            if init_git and not self.is_git_repo():
                self._init_git()

            # 创建 .gitignore
            gitignore_path = self._path / ".gitignore"
            if not gitignore_path.exists():
                gitignore_path.write_text(GITIGNORE_TEMPLATE, encoding="utf-8")

            # 同步模板文件
            added = sync_workspace_templates(self._path, silent=silent)

            return added

        except Exception as e:
            raise RuntimeError(f"创建工作区失败: {e}") from e

    def _init_git(self) -> bool:
        """初始化 git 仓库

        Returns:
            是否成功初始化
        """
        try:
            # 检查 git 是否可用
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return False

            # 初始化仓库
            result = subprocess.run(
                ["git", "init"],
                cwd=self._path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def ensure_exists(self, silent: bool = False) -> List[str]:
        """确保工作区存在

        如果不存在则创建。

        Args:
            silent: 是否静默模式

        Returns:
            创建的文件列表
        """
        if self.exists():
            # 同步模板文件（只创建缺失的）
            return sync_workspace_templates(self._path, silent=silent)
        else:
            return self.create(silent=silent)

    def get_files(self) -> List[dict]:
        """获取工作区文件列表

        Returns:
            文件信息列表
        """
        if not self.exists():
            return []

        files = []
        for item in sorted(self._path.iterdir()):
            if item.is_file() and not item.name.startswith("."):
                stat = item.stat()
                files.append({
                    "name": item.name,
                    "path": str(item),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                })

        return files

    def get_status(self) -> dict:
        """获取工作区状态

        Returns:
            状态信息字典
        """
        status = {
            "exists": self.exists(),
            "path": str(self._path),
            "profile": self._profile,
            "is_git_repo": False,
            "files": [],
        }

        if self.exists():
            status["is_git_repo"] = self.is_git_repo()
            status["files"] = self.get_files()

        return status

    def read_file(self, filename: str) -> Optional[str]:
        """读取工作区文件

        Args:
            filename: 文件名

        Returns:
            文件内容，不存在返回 None
        """
        filepath = self._path / filename
        if filepath.exists():
            return filepath.read_text(encoding="utf-8")
        return None

    def write_file(self, filename: str, content: str) -> bool:
        """写入工作区文件

        Args:
            filename: 文件名
            content: 文件内容

        Returns:
            是否成功
        """
        try:
            filepath = self._path / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content, encoding="utf-8")
            return True
        except Exception:
            return False

    def get_bootstrap_files(self) -> List[dict]:
        """获取引导文件列表

        Returns:
            引导文件信息列表
        """
        bootstrap_files = []
        filenames = ["BOOTSTRAP.md"]

        for filename in filenames:
            filepath = self._path / filename
            if filepath.exists():
                bootstrap_files.append({
                    "name": filename,
                    "path": str(filepath),
                    "content": filepath.read_text(encoding="utf-8"),
                    "size": filepath.stat().st_size,
                })

        return bootstrap_files

    def delete_bootstrap(self) -> bool:
        """删除引导文件（完成仪式后）

        Returns:
            是否成功删除
        """
        bootstrap_path = self._path / "BOOTSTRAP.md"
        if bootstrap_path.exists():
            bootstrap_path.unlink()
            return True
        return False

    def __repr__(self) -> str:
        return f"WorkspaceManager(path={self._path}, profile={self._profile})"
