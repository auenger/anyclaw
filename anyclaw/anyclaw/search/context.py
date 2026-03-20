"""对话上下文路径提取器

从对话历史中提取路径信息，用于优化搜索优先级。
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class ContextPath:
    """对话上下文中提取的路径"""

    path: Path
    mention_turn: int = 0       # 提到的对话轮次（越小越新鲜）
    mention_count: int = 1      # 提到次数

    def __hash__(self) -> int:
        return hash(self.path)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ContextPath):
            return self.path == other.path
        return False


class ContextPathExtractor:
    """从对话历史中提取路径信息

    Usage:
        extractor = ContextPathExtractor()
        paths = extractor.extract_from_history(messages)
        priority_paths = extractor.get_priority_paths(messages)
    """

    # 路径匹配模式
    PATH_PATTERNS = [
        # Unix 绝对路径
        r'/(?:[\w.-]+/)*[\w.-]+',
        # 用户目录
        r'~/[\w/.-]+',
        # Windows 路径
        r'[A-Z]:\\(?:[\w.-]+\\)*[\w.-]+',
        # 相对路径（以 ./ 开头）
        r'\./[\w/.-]+',
    ]

    # 排除的路径模式（避免误匹配）
    EXCLUDE_PATTERNS = [
        r'^/dev/',           # 设备文件
        r'^/proc/',          # 进程文件
        r'^/sys/',           # 系统文件
        r'^/tmp/',           # 临时文件
        r'\.\.$',            # 父目录引用
        r'^\.$',             # 当前目录
    ]

    def __init__(self, max_context_turns: int = 10, home_dir: Optional[Path] = None):
        """初始化上下文路径提取器

        Args:
            max_context_turns: 上下文过期轮次（超过此轮次的路径降权）
            home_dir: 用户主目录
        """
        self.max_context_turns = max_context_turns
        self.home_dir = Path(home_dir) if home_dir else Path.home()

        # 编译正则表达式
        self._path_regex = re.compile(
            '|'.join(self.PATH_PATTERNS),
            re.IGNORECASE
        )
        self._exclude_regex = re.compile(
            '|'.join(self.EXCLUDE_PATTERNS),
            re.IGNORECASE
        )

    def extract_from_history(self, messages: List[dict]) -> List[ContextPath]:
        """从对话历史提取路径

        Args:
            messages: 对话消息列表，每条消息包含 'role' 和 'content'

        Returns:
            提取的上下文路径列表（按新鲜度排序）
        """
        path_map: dict[Path, ContextPath] = {}
        total_turns = len(messages)

        for turn_index, message in enumerate(messages):
            content = message.get("content", "")
            if not isinstance(content, str):
                continue

            # 提取路径
            extracted = self._extract_paths_from_text(content)

            for path_str in extracted:
                try:
                    path = self._normalize_path(path_str)

                    # 跳过不存在的路径
                    if not path.exists():
                        continue

                    if path in path_map:
                        # 更新已存在的路径
                        path_map[path].mention_count += 1
                        # 更新为更近的轮次
                        path_map[path].mention_turn = turn_index
                    else:
                        # 添加新路径
                        path_map[path] = ContextPath(
                            path=path,
                            mention_turn=turn_index,
                            mention_count=1,
                        )
                except (OSError, ValueError):
                    continue

        # 按新鲜度和提到次数排序
        sorted_paths = sorted(
            path_map.values(),
            key=lambda p: (
                -p.mention_turn,      # 最近提到优先
                -p.mention_count,     # 提到次数多优先
            )
        )

        return sorted_paths

    def get_priority_paths(
        self,
        messages: List[dict],
        current_turn: Optional[int] = None,
    ) -> List[Path]:
        """获取优先搜索路径列表

        Args:
            messages: 对话消息列表
            current_turn: 当前轮次（用于计算过期）

        Returns:
            优先搜索路径列表
        """
        context_paths = self.extract_from_history(messages)

        if current_turn is None:
            current_turn = len(messages)

        priority_paths = []

        for cp in context_paths:
            # 计算路径年龄
            age = current_turn - cp.mention_turn

            # 过期路径降权（但仍然包含）
            if age <= self.max_context_turns:
                priority_paths.append(cp.path)

        # 添加父目录（去重）
        all_dirs = set()
        for p in priority_paths:
            all_dirs.add(p)
            if p.is_file():
                all_dirs.add(p.parent)

        return list(all_dirs)

    def _extract_paths_from_text(self, text: str) -> List[str]:
        """从文本中提取路径字符串

        Args:
            text: 输入文本

        Returns:
            提取的路径字符串列表
        """
        matches = self._path_regex.findall(text)

        # 过滤排除模式
        filtered = []
        for match in matches:
            if isinstance(match, tuple):
                # 正则分组结果
                match = match[0] if match[0] else match[1] if len(match) > 1 else ""

            if match and not self._exclude_regex.search(match):
                # 清理路径
                cleaned = match.strip('.,;:!?\'"()[]{}')
                if cleaned:
                    filtered.append(cleaned)

        return filtered

    def _normalize_path(self, path_str: str) -> Path:
        """规范化路径

        Args:
            path_str: 路径字符串

        Returns:
            规范化后的 Path 对象
        """
        path = Path(path_str)

        # 展开 ~ 为用户目录
        if path_str.startswith("~"):
            path = self.home_dir / path_str[2:]

        # 相对路径转换为绝对路径
        if not path.is_absolute():
            path = Path.cwd() / path

        # 解析符号链接
        try:
            path = path.resolve()
        except OSError:
            pass

        return path
