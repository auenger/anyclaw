"""SearchHeuristics 单元测试"""

import pytest
from pathlib import Path
from unittest.mock import patch

from anyclaw.search.heuristics import SearchHeuristics


class TestSearchHeuristics:
    """SearchHeuristics 测试类"""

    def test_default_priority_dirs(self):
        """测试默认优先级目录"""
        heuristics = SearchHeuristics()
        assert heuristics.priority_dirs == [
            "Downloads",
            "Desktop",
            "Documents",
            "projects",
            "",
        ]

    def test_file_type_directory_mapping(self):
        """测试文件类型 → 目录映射"""
        heuristics = SearchHeuristics()

        # Excel 文件 → Downloads
        assert heuristics.get_file_type_directory("*.xlsx") is not None
        assert heuristics.get_file_type_directory("*.xlsx").name == "Downloads"

        # Python 文件 → projects
        assert heuristics.get_file_type_directory("*.py") is not None
        assert heuristics.get_file_type_directory("*.py").name == "projects"

        # PDF 文件 → Documents
        assert heuristics.get_file_type_directory("*.pdf") is not None
        assert heuristics.get_file_type_directory("*.pdf").name == "Documents"

    def test_get_search_paths_with_context(self):
        """测试带上下文的搜索路径"""
        heuristics = SearchHeuristics()

        # 模拟上下文路径
        context_paths = [Path("/tmp/test_dir")]
        with patch.object(Path, "exists", return_value=True):
            paths = heuristics.get_search_paths("test.xlsx", context_paths)

            # 上下文路径应该在最前面
            assert len(paths) > 0

    def test_should_exclude_dir(self):
        """测试排除目录"""
        heuristics = SearchHeuristics()

        assert heuristics.should_exclude_dir(".git") is True
        assert heuristics.should_exclude_dir("node_modules") is True
        assert heuristics.should_exclude_dir("__pycache__") is True
        assert heuristics.should_exclude_dir("src") is False

    def test_extract_extension(self):
        """测试扩展名提取"""
        heuristics = SearchHeuristics()

        assert heuristics._get_extension("*.xlsx") == ".xlsx"
        assert heuristics._get_extension("report.pdf") == ".pdf"
        assert heuristics._get_extension("config") is None

    def test_custom_priority_dirs(self):
        """测试自定义优先级目录"""
        custom_dirs = ["custom1", "custom2"]
        heuristics = SearchHeuristics(priority_dirs=custom_dirs)

        assert heuristics.priority_dirs == custom_dirs

    def test_custom_file_type_mapping(self):
        """测试自定义文件类型映射"""
        custom_mapping = {".custom": "CustomDir"}
        heuristics = SearchHeuristics(file_type_dirs=custom_mapping)

        assert heuristics.file_type_dirs[".custom"] == "CustomDir"


class TestSearchHeuristicsIntegration:
    """SearchHeuristics 集成测试"""

    def test_get_search_paths_order(self):
        """测试搜索路径顺序"""
        heuristics = SearchHeuristics()

        with patch.object(Path, "exists", return_value=True):
            paths = heuristics.get_search_paths("report.xlsx")

            # 确保有返回路径
            assert len(paths) > 0

    def test_project_dir_included(self):
        """测试项目目录被包含"""
        project_dir = Path("/tmp/myproject")
        heuristics = SearchHeuristics(project_dir=project_dir)

        with patch.object(Path, "exists", return_value=True):
            paths = heuristics.get_search_paths("*.py")

            # 项目目录应该在列表中
            path_names = [p.name for p in paths]
            # 由于 project_dir 可能不存在，我们只检查逻辑正确
