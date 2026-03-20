"""搜索请求分析器

分析用户搜索请求，判断信息是否充足，生成询问建议。
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set


@dataclass
class SearchQuery:
    """解析后的搜索请求"""

    pattern: Optional[str] = None          # 文件名模式
    directory: Optional[Path] = None       # 指定目录
    file_type: Optional[str] = None        # 文件类型
    is_specific: bool = False              # 是否足够具体
    raw_request: str = ""                  # 原始请求


@dataclass
class QuerySuggestion:
    """询问建议"""

    questions: List[str] = field(default_factory=list)     # 需要询问的问题
    suggested_dirs: List[Path] = field(default_factory=list)  # 建议的目录选项
    reason: str = ""                                        # 询问原因


class SearchQueryAnalyzer:
    """分析搜索请求，判断信息是否充足

    Usage:
        analyzer = SearchQueryAnalyzer()
        query = analyzer.analyze("帮我找 report.xlsx", context_paths)
        suggestion = analyzer.needs_more_info(query)
        if suggestion:
            # 显示询问建议
    """

    # 模糊请求关键词
    VAGUE_KEYWORDS = {
        "文件", "file", "document", "文档",
        "找", "find", "search", "查找", "搜索",
        "一下", "看看", "帮我",
    }

    # 宽泛文件模式
    BROAD_PATTERNS = {
        "*.py", "*.js", "*.ts", "*.go", "*.java",
        "*.txt", "*.md", "*.json", "*.yaml", "*.yml",
        "*.html", "*.css", "*.xml",
    }

    # 文件扩展名 → 文件类型描述
    FILE_TYPE_NAMES = {
        ".xlsx": "Excel 表格",
        ".xls": "Excel 表格",
        ".pdf": "PDF 文档",
        ".doc": "Word 文档",
        ".docx": "Word 文档",
        ".py": "Python 代码",
        ".js": "JavaScript 代码",
        ".ts": "TypeScript 代码",
        ".png": "图片",
        ".jpg": "图片",
        ".jpeg": "图片",
    }

    def __init__(
        self,
        broad_search_threshold: int = 1000,
        max_suggested_dirs: int = 3,
    ):
        """初始化搜索请求分析器

        Args:
            broad_search_threshold: 宽泛搜索阈值（估计文件数超过此值视为宽泛）
            max_suggested_dirs: 最大建议目录数
        """
        self.broad_search_threshold = broad_search_threshold
        self.max_suggested_dirs = max_suggested_dirs

        # 编译正则
        self._file_pattern_regex = re.compile(
            r'\*?\.\w+|\b\w+\.\w+\b',  # *.ext 或 filename.ext
            re.IGNORECASE
        )
        self._path_regex = re.compile(
            r'(?:/|~/|[A-Z]:\\)[\w/.-]+',
            re.IGNORECASE
        )

    def analyze(
        self,
        user_request: str,
        context_paths: Optional[List[Path]] = None,
    ) -> SearchQuery:
        """分析用户请求

        Args:
            user_request: 用户请求文本
            context_paths: 对话上下文中的路径

        Returns:
            解析后的 SearchQuery 对象
        """
        query = SearchQuery(raw_request=user_request)

        # 1. 提取文件名模式
        patterns = self._extract_file_patterns(user_request)
        if patterns:
            query.pattern = patterns[0]  # 取第一个
            query.file_type = self._get_file_type(query.pattern)

        # 2. 提取目录
        directories = self._extract_directories(user_request)
        if directories:
            query.directory = directories[0]

        # 3. 检查上下文路径
        if context_paths and not query.directory:
            # 如果没有明确指定目录，使用第一个上下文目录
            for cp in context_paths:
                if cp.is_dir():
                    query.directory = cp
                    break

        # 4. 判断是否足够具体
        query.is_specific = self._is_specific(query, user_request)

        return query

    def needs_more_info(
        self,
        query: SearchQuery,
        suggested_dirs: Optional[List[Path]] = None,
    ) -> Optional[QuerySuggestion]:
        """判断是否需要更多信息

        Args:
            query: 解析后的搜索请求
            suggested_dirs: 建议的目录列表

        Returns:
            如果需要更多信息，返回 QuerySuggestion；否则返回 None
        """
        # 情况 1: 没有文件名模式
        if not query.pattern:
            return QuerySuggestion(
                questions=[
                    "文件名是什么？（支持通配符，如 *.xlsx）",
                    "大概在哪个目录？",
                    "文件类型是什么？（文档 / 图片 / 代码）",
                ],
                suggested_dirs=suggested_dirs or [],
                reason="缺少文件名或路径信息",
            )

        # 情况 2: 模式太宽泛且没有目录限制
        if self._is_broad_pattern(query.pattern) and not query.directory:
            file_type_desc = self.FILE_TYPE_NAMES.get(
                self._get_extension(query.pattern),
                query.pattern
            )
            return QuerySuggestion(
                questions=[
                    f"搜索范围较大，可能找到很多 {file_type_desc} 文件。",
                    "是否限定在特定目录？",
                ],
                suggested_dirs=(suggested_dirs or [])[:self.max_suggested_dirs],
                reason=f"模式 '{query.pattern}' 搜索范围过大",
            )

        # 情况 3: 信息充足
        return None

    def is_ambiguous(self, query: SearchQuery) -> bool:
        """判断请求是否模糊

        Args:
            query: 解析后的搜索请求

        Returns:
            是否模糊
        """
        # 没有明确文件名
        if not query.pattern:
            return True

        # 是宽泛模式且没有目录
        if self._is_broad_pattern(query.pattern) and not query.directory:
            return True

        return False

    def _extract_file_patterns(self, text: str) -> List[str]:
        """从文本中提取文件名模式

        Args:
            text: 输入文本

        Returns:
            提取的文件名模式列表
        """
        matches = self._file_pattern_regex.findall(text)

        # 过滤并清理
        patterns = []
        for match in matches:
            # 确保是有效的文件模式
            if "." in match and len(match) > 2:
                patterns.append(match)

        return patterns

    def _extract_directories(self, text: str) -> List[Path]:
        """从文本中提取目录路径

        Args:
            text: 输入文本

        Returns:
            提取的目录路径列表
        """
        matches = self._path_regex.findall(text)

        directories = []
        for match in matches:
            try:
                path = Path(match).expanduser().resolve()
                if path.exists():
                    directories.append(path)
            except (OSError, ValueError):
                continue

        return directories

    def _is_specific(self, query: SearchQuery, raw_request: str) -> bool:
        """判断请求是否足够具体

        Args:
            query: 解析后的请求
            raw_request: 原始请求文本

        Returns:
            是否足够具体
        """
        # 有具体文件名（不是通配符）
        if query.pattern and not query.pattern.startswith("*"):
            return True

        # 有目录限制
        if query.directory:
            return True

        # 检查是否包含模糊关键词
        request_lower = raw_request.lower()
        vague_count = sum(1 for kw in self.VAGUE_KEYWORDS if kw in request_lower)

        # 模糊关键词太多
        if vague_count >= 2 and not query.pattern:
            return False

        return bool(query.pattern)

    def _is_broad_pattern(self, pattern: str) -> bool:
        """判断模式是否宽泛

        Args:
            pattern: 文件名模式

        Returns:
            是否宽泛
        """
        return pattern.lower() in self.BROAD_PATTERNS

    def _get_file_type(self, pattern: str) -> Optional[str]:
        """根据文件模式获取文件类型

        Args:
            pattern: 文件名模式

        Returns:
            文件类型描述
        """
        ext = self._get_extension(pattern)
        return self.FILE_TYPE_NAMES.get(ext)

    def _get_extension(self, pattern: str) -> str:
        """从模式中提取扩展名

        Args:
            pattern: 文件名模式

        Returns:
            扩展名（带点）
        """
        pattern = pattern.lstrip("*")
        if "." in pattern:
            return "." + pattern.rsplit(".", 1)[-1].lower()
        return ""
