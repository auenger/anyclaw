"""搜索启发式规则引擎

根据文件类型和用户习惯，智能确定搜索优先级。
"""

import os
from pathlib import Path
from typing import Dict, List, Optional


class SearchHeuristics:
    """搜索启发式规则引擎

    根据文件类型和默认优先级确定搜索顺序。

    Usage:
        heuristics = SearchHeuristics()
        paths = heuristics.get_search_paths("*.xlsx")
        # 优先搜索 Downloads，然后是 Desktop 等
    """

    # 默认搜索优先级目录
    DEFAULT_PRIORITY_DIRS = [
        "Downloads",     # 下载文件默认位置
        "Desktop",       # 桌面临时文件
        "Documents",     # 文档目录
        "projects",      # 项目目录
        "",              # 用户主目录
    ]

    # 文件类型 → 目录关联
    FILE_TYPE_DIRS: Dict[str, str] = {
        # 下载文件
        ".xlsx": "Downloads",
        ".xls": "Downloads",
        ".dmg": "Downloads",
        ".zip": "Downloads",
        ".tar": "Downloads",
        ".gz": "Downloads",
        ".exe": "Downloads",
        ".msi": "Downloads",
        ".deb": "Downloads",
        ".rpm": "Downloads",
        ".iso": "Downloads",

        # 文档文件
        ".pdf": "Documents",
        ".doc": "Documents",
        ".docx": "Documents",
        ".ppt": "Documents",
        ".pptx": "Documents",

        # 代码文件
        ".py": "projects",
        ".js": "projects",
        ".ts": "projects",
        ".go": "projects",
        ".rs": "projects",
        ".java": "projects",

        # 图片文件
        ".png": "Pictures",
        ".jpg": "Pictures",
        ".jpeg": "Pictures",
        ".gif": "Pictures",
        ".svg": "Pictures",

        # 音频文件
        ".mp3": "Music",
        ".wav": "Music",
        ".flac": "Music",

        # 视频文件
        ".mp4": "Movies",
        ".mov": "Movies",
        ".avi": "Movies",
        ".mkv": "Movies",
    }

    # 排除的目录
    EXCLUDE_DIRS = {
        ".git",
        ".svn",
        ".hg",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "Library",
        ".Trash",
        ".cache",
    }

    def __init__(
        self,
        home_dir: Optional[Path] = None,
        project_dir: Optional[Path] = None,
        priority_dirs: Optional[List[str]] = None,
        file_type_dirs: Optional[Dict[str, str]] = None,
    ):
        """初始化搜索启发式引擎

        Args:
            home_dir: 用户主目录（默认自动检测）
            project_dir: 当前项目目录
            priority_dirs: 自定义优先级目录列表
            file_type_dirs: 自定义文件类型映射
        """
        self.home_dir = Path(home_dir) if home_dir else Path.home()
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.priority_dirs = priority_dirs or self.DEFAULT_PRIORITY_DIRS.copy()
        self.file_type_dirs = {**self.FILE_TYPE_DIRS, **(file_type_dirs or {})}

    def get_search_paths(
        self,
        file_pattern: str,
        context_paths: Optional[List[Path]] = None,
    ) -> List[Path]:
        """获取搜索路径优先级列表

        Args:
            file_pattern: 文件名模式（支持通配符）
            context_paths: 对话上下文中提到的路径（高优先级）

        Returns:
            按优先级排序的搜索路径列表
        """
        paths = []

        # 1. 上下文路径最高优先级
        if context_paths:
            for cp in context_paths:
                if cp.exists() and cp not in paths:
                    paths.append(cp)

        # 2. 根据文件类型确定首选目录
        file_ext = self._get_extension(file_pattern)
        if file_ext and file_ext in self.file_type_dirs:
            preferred_dir = self.file_type_dirs[file_ext]
            dir_path = self.home_dir / preferred_dir
            if dir_path.exists() and dir_path not in paths:
                paths.append(dir_path)

        # 3. 添加默认优先级目录
        for dir_name in self.priority_dirs:
            if dir_name:
                dir_path = self.home_dir / dir_name
            else:
                dir_path = self.home_dir

            if dir_path.exists() and dir_path not in paths:
                paths.append(dir_path)

        # 4. 添加项目目录
        if self.project_dir.exists() and self.project_dir not in paths:
            paths.append(self.project_dir)

        return paths

    def get_file_type_directory(self, file_pattern: str) -> Optional[Path]:
        """根据文件类型获取推荐目录

        Args:
            file_pattern: 文件名模式

        Returns:
            推荐的搜索目录
        """
        file_ext = self._get_extension(file_pattern)
        if file_ext and file_ext in self.file_type_dirs:
            dir_name = self.file_type_dirs[file_ext]
            return self.home_dir / dir_name
        return None

    def should_exclude_dir(self, dir_name: str) -> bool:
        """检查目录是否应该被排除

        Args:
            dir_name: 目录名

        Returns:
            是否应该排除
        """
        return dir_name in self.EXCLUDE_DIRS

    def _get_extension(self, file_pattern: str) -> Optional[str]:
        """从文件模式中提取扩展名

        Args:
            file_pattern: 文件名模式（如 "*.xlsx", "report.pdf"）

        Returns:
            文件扩展名（如 ".xlsx", ".pdf"）
        """
        # 处理通配符
        pattern = file_pattern.lstrip("*")

        # 提取扩展名
        if "." in pattern:
            ext = "." + pattern.rsplit(".", 1)[-1]
            return ext.lower()
        return None

    def get_default_search_paths(self) -> List[Path]:
        """获取默认搜索路径列表（不考虑文件类型）

        Returns:
            默认搜索路径列表
        """
        paths = []
        for dir_name in self.priority_dirs:
            if dir_name:
                dir_path = self.home_dir / dir_name
            else:
                dir_path = self.home_dir

            if dir_path.exists():
                paths.append(dir_path)

        return paths
