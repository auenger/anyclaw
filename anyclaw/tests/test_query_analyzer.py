"""SearchQueryAnalyzer 单元测试"""

import pytest
from pathlib import Path

from anyclaw.search.analyzer import (
    SearchQueryAnalyzer,
    SearchQuery,
    QuerySuggestion,
)


class TestSearchQueryAnalyzer:
    """SearchQueryAnalyzer 测试类"""

    def test_analyze_with_filename(self):
        """测试分析带文件名的请求"""
        analyzer = SearchQueryAnalyzer()

        query = analyzer.analyze("帮我找 report.xlsx")

        assert query.pattern == "report.xlsx"
        assert query.file_type == "Excel 表格"
        assert query.is_specific is True

    def test_analyze_with_directory(self, tmp_path):
        """测试分析带目录的请求"""
        analyzer = SearchQueryAnalyzer()

        query = analyzer.analyze(f"找 {tmp_path} 里的 config.yaml")

        assert query.pattern == "config.yaml"
        assert query.directory == tmp_path

    def test_analyze_vague_request(self):
        """测试分析模糊请求"""
        analyzer = SearchQueryAnalyzer()

        query = analyzer.analyze("帮我找个文件")

        assert query.pattern is None
        assert query.is_specific is False

    def test_needs_more_info_no_pattern(self):
        """测试需要更多信息（无文件名）"""
        analyzer = SearchQueryAnalyzer()

        query = SearchQuery(raw_request="帮我找文件")
        suggestion = analyzer.needs_more_info(query)

        assert suggestion is not None
        assert len(suggestion.questions) > 0
        assert "文件名" in suggestion.questions[0]

    def test_needs_more_info_broad_pattern(self):
        """测试需要更多信息（宽泛模式）"""
        analyzer = SearchQueryAnalyzer()

        query = SearchQuery(pattern="*.py", raw_request="找所有 Python 文件")
        suggestion = analyzer.needs_more_info(query)

        # 宽泛模式 + 无目录限制 → 需要询问
        assert suggestion is not None
        assert "范围" in suggestion.reason or "过大" in suggestion.reason

    def test_needs_more_info_specific_request(self):
        """测试不需要更多信息（具体请求）"""
        analyzer = SearchQueryAnalyzer()

        query = SearchQuery(
            pattern="report.xlsx",
            directory=Path("/tmp"),
            is_specific=True,
            raw_request="找 /tmp 里的 report.xlsx",
        )
        suggestion = analyzer.needs_more_info(query)

        # 具体请求 → 不需要询问
        assert suggestion is None

    def test_is_ambiguous(self):
        """测试模糊请求判断"""
        analyzer = SearchQueryAnalyzer()

        # 模糊请求
        assert analyzer.is_ambiguous(SearchQuery(raw_request="找个文件")) is True
        assert analyzer.is_ambiguous(SearchQuery(pattern="*.py", raw_request="")) is True

        # 具体请求
        assert analyzer.is_ambiguous(SearchQuery(pattern="report.xlsx", raw_request="")) is False
        assert analyzer.is_ambiguous(
            SearchQuery(pattern="*.py", directory=Path("/tmp"), raw_request="")
        ) is False

    def test_extract_file_patterns(self):
        """测试提取文件模式"""
        analyzer = SearchQueryAnalyzer()

        patterns = analyzer._extract_file_patterns("找 *.xlsx 和 report.pdf")

        assert "*.xlsx" in patterns
        assert "report.pdf" in patterns

    def test_extract_directories(self, tmp_path):
        """测试提取目录"""
        analyzer = SearchQueryAnalyzer()

        text = f"文件在 {tmp_path} 目录里"
        directories = analyzer._extract_directories(text)

        assert tmp_path in directories

    def test_broad_pattern_detection(self):
        """测试宽泛模式检测"""
        analyzer = SearchQueryAnalyzer()

        # 宽泛模式
        assert analyzer._is_broad_pattern("*.py") is True
        assert analyzer._is_broad_pattern("*.js") is True
        assert analyzer._is_broad_pattern("*.md") is True

        # 具体模式
        assert analyzer._is_broad_pattern("config.yaml") is False
        assert analyzer._is_broad_pattern("report.xlsx") is False

    def test_file_type_detection(self):
        """测试文件类型检测"""
        analyzer = SearchQueryAnalyzer()

        assert analyzer._get_file_type("*.xlsx") == "Excel 表格"
        assert analyzer._get_file_type("*.pdf") == "PDF 文档"
        assert analyzer._get_file_type("*.py") == "Python 代码"

    def test_analyze_with_context_paths(self, tmp_path):
        """测试带上下文路径的分析"""
        analyzer = SearchQueryAnalyzer()

        context_paths = [tmp_path]
        query = analyzer.analyze("找 config.yaml", context_paths)

        # 上下文路径应该被用作默认目录
        assert query.directory == tmp_path


class TestSearchQuery:
    """SearchQuery 测试类"""

    def test_query_creation(self):
        """测试查询创建"""
        query = SearchQuery(
            pattern="report.xlsx",
            directory=Path("/tmp"),
            file_type="Excel 表格",
            is_specific=True,
            raw_request="找 /tmp 里的 report.xlsx",
        )

        assert query.pattern == "report.xlsx"
        assert query.directory == Path("/tmp")
        assert query.file_type == "Excel 表格"
        assert query.is_specific is True

    def test_query_defaults(self):
        """测试查询默认值"""
        query = SearchQuery(raw_request="测试")

        assert query.pattern is None
        assert query.directory is None
        assert query.file_type is None
        assert query.is_specific is False


class TestQuerySuggestion:
    """QuerySuggestion 测试类"""

    def test_suggestion_creation(self):
        """测试建议创建"""
        suggestion = QuerySuggestion(
            questions=["文件名是什么？", "在哪个目录？"],
            suggested_dirs=[Path("/tmp"), Path("/home")],
            reason="缺少文件名信息",
        )

        assert len(suggestion.questions) == 2
        assert len(suggestion.suggested_dirs) == 2
        assert suggestion.reason == "缺少文件名信息"

    def test_suggestion_defaults(self):
        """测试建议默认值"""
        suggestion = QuerySuggestion()

        assert suggestion.questions == []
        assert suggestion.suggested_dirs == []
        assert suggestion.reason == ""
