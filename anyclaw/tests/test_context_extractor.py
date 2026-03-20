"""ContextPathExtractor 单元测试"""

import pytest
from pathlib import Path

from anyclaw.search.context import ContextPathExtractor, ContextPath


class TestContextPathExtractor:
    """ContextPathExtractor 测试类"""

    def test_extract_unix_path(self):
        """测试提取 Unix 路径"""
        extractor = ContextPathExtractor()

        text = "我在 /Users/ryan/projects/myapp 里有个配置文件"
        paths = extractor._extract_paths_from_text(text)

        assert "/Users/ryan/projects/myapp" in paths

    def test_extract_user_dir(self):
        """测试提取用户目录路径"""
        extractor = ContextPathExtractor()

        text = "文件在 ~/Downloads/report.xlsx"
        paths = extractor._extract_paths_from_text(text)

        assert "~/Downloads/report.xlsx" in paths

    def test_extract_relative_path(self):
        """测试提取相对路径"""
        extractor = ContextPathExtractor()

        text = "配置文件在 ./config/settings.yaml"
        paths = extractor._extract_paths_from_text(text)

        assert "./config/settings.yaml" in paths

    def test_exclude_system_paths(self):
        """测试排除系统路径"""
        extractor = ContextPathExtractor()

        text = "检查 /proc/cpuinfo 和 /dev/null"
        paths = extractor._extract_paths_from_text(text)

        # 系统路径应该被排除
        assert "/proc/cpuinfo" not in paths
        assert "/dev/null" not in paths

    def test_extract_from_history(self, tmp_path):
        """测试从对话历史提取路径"""
        extractor = ContextPathExtractor()

        # 创建临时目录
        test_dir = tmp_path / "myproject"
        test_dir.mkdir()

        messages = [
            {"role": "user", "content": f"我在 {test_dir} 里有个项目"},
            {"role": "assistant", "content": "好的，我来查看一下"},
            {"role": "user", "content": "帮我找 config.yaml"},
        ]

        context_paths = extractor.extract_from_history(messages)

        # 应该提取到路径
        assert len(context_paths) > 0
        assert context_paths[0].path == test_dir

    def test_context_path_ordering(self, tmp_path):
        """测试上下文路径排序（新鲜度优先）"""
        extractor = ContextPathExtractor()

        # 创建临时目录
        dir1 = tmp_path / "project1"
        dir2 = tmp_path / "project2"
        dir1.mkdir()
        dir2.mkdir()

        messages = [
            {"role": "user", "content": f"第一个项目在 {dir1}"},
            {"role": "assistant", "content": "好的"},
            {"role": "user", "content": f"第二个项目在 {dir2}"},
        ]

        context_paths = extractor.extract_from_history(messages)

        # 最后提到的路径应该在前面
        assert len(context_paths) >= 2
        # 由于按新鲜度排序，dir2 应该在 dir1 前面
        assert context_paths[0].path == dir2

    def test_mention_count(self, tmp_path):
        """测试提到次数计数"""
        extractor = ContextPathExtractor()

        test_dir = tmp_path / "frequent"
        test_dir.mkdir()

        messages = [
            {"role": "user", "content": f"项目在 {test_dir}"},
            {"role": "assistant", "content": "好的"},
            {"role": "user", "content": f"还是 {test_dir} 这个目录"},
            {"role": "assistant", "content": "明白了"},
            {"role": "user", "content": f"回到 {test_dir}"},
        ]

        context_paths = extractor.extract_from_history(messages)

        # 应该只有一个路径（合并了多次提到）
        assert len(context_paths) == 1
        assert context_paths[0].mention_count == 3

    def test_expired_context(self, tmp_path):
        """测试过期上下文过滤"""
        extractor = ContextPathExtractor(max_context_turns=3)

        test_dir = tmp_path / "old_project"
        test_dir.mkdir()

        messages = [
            {"role": "user", "content": f"旧项目在 {test_dir}"},
            {"role": "assistant", "content": "1"},
            {"role": "user", "content": "2"},
            {"role": "assistant", "content": "3"},
            {"role": "user", "content": "4"},
            {"role": "assistant", "content": "5"},
            {"role": "user", "content": "帮我找文件"},
        ]

        priority_paths = extractor.get_priority_paths(messages)

        # 旧路径应该被过滤（超过 3 轮）
        assert test_dir not in priority_paths


class TestContextPath:
    """ContextPath 测试类"""

    def test_hash_and_equality(self):
        """测试哈希和相等性"""
        path = Path("/tmp/test")

        cp1 = ContextPath(path=path, mention_turn=1)
        cp2 = ContextPath(path=path, mention_turn=2)  # 不同轮次
        cp3 = ContextPath(path=Path("/other"), mention_turn=1)

        # 相同路径应该相等
        assert cp1 == cp2

        # 不同路径应该不等
        assert cp1 != cp3

        # 哈希应该相同
        assert hash(cp1) == hash(cp2)
