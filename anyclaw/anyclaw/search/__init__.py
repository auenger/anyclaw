"""Smart File Search - 智能文件搜索模块

提供智能文件搜索功能，包括：
- SearchHeuristics: 搜索启发式规则引擎
- ContextPathExtractor: 对话上下文路径提取器
- SearchQueryAnalyzer: 搜索请求分析器
- SearchCache: 搜索缓存管理器
- PathAuthorizer: 动态路径授权器
- SearchFilesTool: 增强搜索工具
"""

from anyclaw.search.heuristics import SearchHeuristics
from anyclaw.search.context import ContextPathExtractor, ContextPath
from anyclaw.search.analyzer import SearchQueryAnalyzer, SearchQuery, QuerySuggestion
from anyclaw.search.cache import SearchCache
from anyclaw.search.authorizer import PathAuthorizer, AuthorizationRequiredError

__all__ = [
    "SearchHeuristics",
    "ContextPathExtractor",
    "ContextPath",
    "SearchQueryAnalyzer",
    "SearchQuery",
    "QuerySuggestion",
    "SearchCache",
    "PathAuthorizer",
    "AuthorizationRequiredError",
]
