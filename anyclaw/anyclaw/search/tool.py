"""增强搜索工具

集成启发式、缓存、上下文关联的智能文件搜索工具。
"""

import asyncio
import fnmatch
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from anyclaw.search.heuristics import SearchHeuristics
from anyclaw.search.context import ContextPathExtractor
from anyclaw.search.analyzer import SearchQueryAnalyzer, SearchQuery, QuerySuggestion
from anyclaw.search.cache import SearchCache
from anyclaw.search.authorizer import PathAuthorizer, AuthorizationRequiredError


@dataclass
class SearchResult:
    """搜索结果"""
    files: List[Tuple[Path, int]]  # (路径, 大小)
    search_time: float
    cache_hits: int
    paths_searched: List[Path]
    truncated: bool = False


@dataclass
class QueryResult:
    """搜索/询问结果"""
    success: bool
    result: Optional[SearchResult] = None
    suggestion: Optional[QuerySuggestion] = None
    authorization_required: Optional[AuthorizationRequiredError] = None
    error: Optional[str] = None


class SearchFilesTool:
    """智能文件搜索工具

    集成启发式规则、上下文关联、缓存和授权的搜索工具。

    Usage:
        tool = SearchFilesTool()

        # 执行搜索
        result = await tool.search(
            pattern="*.xlsx",
            conversation_history=messages,
        )

        # 如果需要更多信息
        if result.suggestion:
            # 显示询问建议
            pass
        elif result.authorization_required:
            # 请求授权
            pass
        elif result.success:
            # 显示搜索结果
            for path, size in result.result.files:
                print(f"{path} ({size} bytes)")
    """

    DEFAULT_TIMEOUT = 5.0  # 默认超时（秒）
    DEFAULT_MAX_DEPTH = 3  # 默认最大搜索深度
    DEFAULT_MAX_RESULTS = 100  # 默认最大结果数

    def __init__(
        self,
        heuristics: Optional[SearchHeuristics] = None,
        cache: Optional[SearchCache] = None,
        authorizer: Optional[PathAuthorizer] = None,
        context_extractor: Optional[ContextPathExtractor] = None,
        query_analyzer: Optional[SearchQueryAnalyzer] = None,
    ):
        """初始化搜索工具

        Args:
            heuristics: 搜索启发式引擎
            cache: 搜索缓存
            authorizer: 路径授权器
            context_extractor: 上下文路径提取器
            query_analyzer: 搜索请求分析器
        """
        self.heuristics = heuristics or SearchHeuristics()
        self.cache = cache or SearchCache()
        self.authorizer = authorizer or PathAuthorizer()
        self.context_extractor = context_extractor or ContextPathExtractor()
        self.query_analyzer = query_analyzer or SearchQueryAnalyzer()

    async def search(
        self,
        pattern: str,
        search_paths: Optional[List[Path]] = None,
        conversation_history: Optional[List[dict]] = None,
        file_type: Optional[str] = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
        use_cache: bool = True,
        timeout: float = DEFAULT_TIMEOUT,
        max_results: int = DEFAULT_MAX_RESULTS,
        check_info_sufficiency: bool = True,
    ) -> QueryResult:
        """执行智能文件搜索

        Args:
            pattern: 文件名模式（支持通配符）
            search_paths: 指定搜索路径（可选）
            conversation_history: 对话历史（用于上下文关联）
            file_type: 文件类型过滤
            max_depth: 最大搜索深度
            use_cache: 是否使用缓存
            timeout: 搜索超时（秒）
            max_results: 最大结果数
            check_info_sufficiency: 是否检查信息充足性

        Returns:
            QueryResult 对象
        """
        start_time = time.time()

        # 1. 检查信息是否充足
        if check_info_sufficiency:
            context_paths = []
            if conversation_history:
                context_paths = self.context_extractor.get_priority_paths(conversation_history)

            query = self.query_analyzer.analyze(pattern, context_paths)
            suggestion = self.query_analyzer.needs_more_info(query)

            if suggestion:
                return QueryResult(
                    success=False,
                    suggestion=suggestion,
                )

        # 2. 确定搜索路径
        if search_paths:
            paths = search_paths
        else:
            # 使用启发式 + 上下文
            context_paths = []
            if conversation_history:
                context_paths = self.context_extractor.get_priority_paths(conversation_history)
            paths = self.heuristics.get_search_paths(pattern, context_paths)

        # 3. 检查缓存
        cache_hits = 0
        if use_cache:
            cached_path = self.cache.get_cached_path(pattern.lstrip("*"))
            if cached_path and cached_path not in [p for p, _ in []]:
                # 缓存命中
                cache_hits += 1
                paths = [cached_path] + [p for p in paths if p != cached_path]

        # 4. 执行搜索
        try:
            result = await self._search_in_paths(
                pattern=pattern,
                paths=paths,
                max_depth=max_depth,
                timeout=timeout,
                max_results=max_results,
            )

            # 5. 记录缓存
            if use_cache and result.files:
                for path, _ in result.files[:10]:  # 只缓存前 10 个
                    self.cache.record_access(path)

            result.cache_hits = cache_hits
            result.search_time = time.time() - start_time

            return QueryResult(
                success=True,
                result=result,
            )

        except AuthorizationRequiredError as e:
            return QueryResult(
                success=False,
                authorization_required=e,
            )
        except asyncio.TimeoutError:
            return QueryResult(
                success=False,
                error=f"搜索超时（{timeout}秒）",
            )
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e),
            )

    async def _search_in_paths(
        self,
        pattern: str,
        paths: List[Path],
        max_depth: int,
        timeout: float,
        max_results: int,
    ) -> SearchResult:
        """在指定路径中搜索文件

        Args:
            pattern: 文件名模式
            paths: 搜索路径列表
            max_depth: 最大搜索深度
            timeout: 超时时间
            max_results: 最大结果数

        Returns:
            SearchResult 对象
        """
        files: List[Tuple[Path, int]] = []
        paths_searched: List[Path] = []
        truncated = False

        async def search_path(base_path: Path) -> None:
            nonlocal truncated

            if len(files) >= max_results:
                truncated = True
                return

            # 检查授权
            if not self.authorizer.is_authorized(base_path):
                # 检查是否为危险路径
                if self.authorizer.is_dangerous(base_path):
                    return  # 跳过危险路径

                # 抛出授权异常
                raise AuthorizationRequiredError(
                    path=base_path,
                    suggested_dir=base_path,
                )

            paths_searched.append(base_path)

            # 递归搜索
            for root, dirs, filenames in self._walk_with_depth(base_path, max_depth):
                # 排除特定目录
                dirs[:] = [d for d in dirs if not self.heuristics.should_exclude_dir(d)]

                for filename in filenames:
                    if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                        file_path = root / filename
                        try:
                            size = file_path.stat().st_size
                            files.append((file_path, size))

                            if len(files) >= max_results:
                                truncated = True
                                return
                        except OSError:
                            continue

        # 并发搜索多个路径
        tasks = [search_path(p) for p in paths if p.exists()]
        await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=timeout,
        )

        return SearchResult(
            files=files,
            search_time=0,  # 由调用者设置
            cache_hits=0,
            paths_searched=paths_searched,
            truncated=truncated,
        )

    def _walk_with_depth(self, root: Path, max_depth: int):
        """带深度限制的目录遍历

        Args:
            root: 根目录
            max_depth: 最大深度

        Yields:
            (root, dirs, files) 元组
        """
        root = root.resolve()

        for dirpath, dirnames, filenames in os.walk(root):
            # 计算当前深度
            rel_path = Path(dirpath).relative_to(root)
            depth = len(rel_path.parts)

            if depth > max_depth:
                dirnames[:] = []  # 不再递归
                continue

            yield Path(dirpath), dirnames, filenames

    def format_result(self, result: SearchResult) -> str:
        """格式化搜索结果

        Args:
            result: 搜索结果

        Returns:
            格式化的字符串
        """
        lines = []

        # 标题
        count = len(result.files)
        lines.append(f"找到 {count} 个匹配文件（搜索用时 {result.search_time:.1f}s")

        if result.cache_hits > 0:
            lines[-1] += f"，缓存命中 {result.cache_hits} 个"
        lines[-1] += "):"

        if not result.files:
            lines.append("  未找到匹配文件")
            return "\n".join(lines)

        # 文件列表
        for i, (path, size) in enumerate(result.files[:20], 1):
            size_str = self._format_size(size)
            lines.append(f"  {i}. {path} ({size_str})")

        if len(result.files) > 20:
            lines.append(f"  ... 还有 {len(result.files) - 20} 个文件")

        if result.truncated:
            lines.append(f"  （结果已截断，显示前 {len(result.files)} 个）")

        return "\n".join(lines)

    @staticmethod
    def _format_size(size: int) -> str:
        """格式化文件大小

        Args:
            size: 字节数

        Returns:
            格式化的字符串
        """
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


# 导入 os 用于目录遍历
import os
