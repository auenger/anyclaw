"""智能文件搜索工具 - Tool 包装器

将 SearchFilesTool 包装为可被 LLM 调用的 Tool。
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from anyclaw.tools.base import Tool
from anyclaw.search.tool import (
    SearchFilesTool as _InternalSearchTool,
    SearchResult,
)


class SearchFilesTool(Tool):
    """智能文件搜索工具

    集成启发式规则、上下文关联、缓存和授权的搜索工具。
    替代盲目使用 find/mdfind 命令。

    Features:
    - 按优先级搜索（Downloads > Desktop > Documents > Projects > Home）
    - 文件类型关联目录（.xlsx → Downloads）
    - 对话上下文关联（从历史提取路径）
    - 搜索缓存（加速重复搜索）
    - 信息不足时主动询问
    """

    DEFAULT_TIMEOUT = 5.0
    DEFAULT_MAX_DEPTH = 3
    DEFAULT_MAX_RESULTS = 50

    def __init__(
        self,
        workspace: Optional[Path] = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_depth: int = DEFAULT_MAX_DEPTH,
        max_results: int = DEFAULT_MAX_RESULTS,
    ):
        """初始化搜索工具

        Args:
            workspace: 工作区路径（用于确定默认搜索路径）
            timeout: 搜索超时（秒）
            max_depth: 最大搜索深度
            max_results: 最大结果数
        """
        self._workspace = workspace or Path.cwd()
        self._timeout = timeout
        self._max_depth = max_depth
        self._max_results = max_results

        # 初始化内部搜索工具
        self._search_tool = _InternalSearchTool()

    @property
    def name(self) -> str:
        return "search_files"

    @property
    def description(self) -> str:
        return """智能文件搜索工具。

使用启发式规则和缓存优化文件搜索，比直接使用 find/mdfind 命令更高效。

特性：
- 按优先级搜索：Downloads > Desktop > Documents > Projects > Home
- 文件类型关联：.xlsx/.xls 优先搜索 Downloads，.py 优先搜索项目目录
- 上下文关联：从对话历史提取相关路径
- 搜索缓存：加速重复搜索
- 信息不足时会主动询问更多信息

使用场景：
- 用户要求查找特定文件
- 需要定位配置文件、数据文件等
- 不确定文件确切位置时

注意：
- 搜索范围有限（默认深度 3 层）
- 如需搜索特定目录，请提供 search_paths 参数
"""

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "文件名模式（支持通配符，如 *.xlsx, config.*.json）",
                },
                "search_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "指定搜索路径（可选，默认使用智能优先级）",
                },
                "file_type": {
                    "type": "string",
                    "description": "文件类型过滤（可选，如 xlsx, py, md）",
                },
                "max_depth": {
                    "type": "integer",
                    "description": "最大搜索深度（默认 3）",
                    "default": 3,
                },
                "use_cache": {
                    "type": "boolean",
                    "description": "是否使用缓存（默认 true）",
                    "default": True,
                },
            },
            "required": ["pattern"],
        }

    async def execute(
        self,
        pattern: str,
        search_paths: Optional[List[str]] = None,
        file_type: Optional[str] = None,
        max_depth: Optional[int] = None,
        use_cache: bool = True,
        **kwargs,
    ) -> str:
        """执行智能文件搜索

        Args:
            pattern: 文件名模式
            search_paths: 指定搜索路径
            file_type: 文件类型过滤
            max_depth: 最大搜索深度
            use_cache: 是否使用缓存

        Returns:
            搜索结果或询问建议
        """
        # 转换路径
        paths = None
        if search_paths:
            paths = [Path(p) for p in search_paths]

        # 使用默认值
        if max_depth is None:
            max_depth = self._max_depth

        try:
            # 调用内部搜索工具
            result = await self._search_tool.search(
                pattern=pattern,
                search_paths=paths,
                file_type=file_type,
                max_depth=max_depth,
                use_cache=use_cache,
                timeout=self._timeout,
                max_results=self._max_results,
                check_info_sufficiency=True,
            )

            # 处理需要更多信息的情况
            if result.suggestion:
                return self._format_suggestion(result.suggestion)

            # 处理需要授权的情况
            if result.authorization_required:
                return self._format_authorization_request(result.authorization_required)

            # 处理错误
            if result.error:
                return f"搜索出错: {result.error}"

            # 格式化成功结果
            if result.success and result.result:
                return self._format_result(result.result)

            return "未找到匹配文件"

        except Exception as e:
            return f"搜索失败: {str(e)}"

    def _format_suggestion(self, suggestion) -> str:
        """格式化询问建议"""
        lines = ["需要更多信息才能进行搜索："]
        lines.append("")
        lines.append(f"**问题**: {suggestion.question}")
        if suggestion.suggestions:
            lines.append("")
            lines.append("**建议**:")
            for s in suggestion.suggestions:
                lines.append(f"- {s}")
        return "\n".join(lines)

    def _format_authorization_request(self, auth_error) -> str:
        """格式化授权请求"""
        return f"需要授权才能搜索路径: {auth_error.path}\n建议添加到允许目录: {auth_error.suggested_dir}"

    def _format_result(self, result: SearchResult) -> str:
        """格式化搜索结果"""
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
        """格式化文件大小"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}" if unit != "B" else f"{size} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
