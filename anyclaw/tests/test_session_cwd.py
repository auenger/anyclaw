"""Session cwd 功能测试"""

import os
import tempfile
from pathlib import Path

import pytest

from anyclaw.session.models import Session


class TestSessionCwd:
    """Session cwd 方法测试"""

    def test_get_cwd_default(self):
        """默认返回 os.getcwd()"""
        session = Session(key="test:123")
        assert session.get_cwd() == os.getcwd()

    def test_set_cwd_absolute_path(self):
        """设置绝对路径"""
        session = Session(key="test:123")

        with tempfile.TemporaryDirectory() as tmpdir:
            result = session.set_cwd(tmpdir)
            assert result is True
            assert session.get_cwd() == str(Path(tmpdir).resolve())

    def test_set_cwd_relative_path_resolved(self):
        """相对路径被解析为绝对路径"""
        session = Session(key="test:123")

        with tempfile.TemporaryDirectory() as tmpdir:
            # 设置一个有效路径
            session.set_cwd(tmpdir)
            # 相对路径 "." 应该解析为当前目录
            result = session.set_cwd(".")
            assert result is True
            # get_cwd 返回解析后的绝对路径
            assert os.path.isabs(session.get_cwd())

    def test_set_cwd_invalid_path(self):
        """无效路径不更新 cwd"""
        session = Session(key="test:123")
        original_cwd = session.get_cwd()

        result = session.set_cwd("/nonexistent/path/12345")
        assert result is False
        assert session.get_cwd() == original_cwd

    def test_set_cwd_file_not_dir(self):
        """文件路径不更新 cwd（必须是目录）"""
        session = Session(key="test:123")
        original_cwd = session.get_cwd()

        with tempfile.NamedTemporaryFile() as tmpfile:
            result = session.set_cwd(tmpfile.name)
            assert result is False
            assert session.get_cwd() == original_cwd

    def test_cwd_persistence(self):
        """cwd 保存在 metadata 中，可持久化"""
        session = Session(key="test:123")

        with tempfile.TemporaryDirectory() as tmpdir:
            session.set_cwd(tmpdir)

            # 验证 cwd 存储在 metadata 中
            assert "cwd" in session.metadata
            assert session.metadata["cwd"] == str(Path(tmpdir).resolve())

    def test_set_cwd_expanduser(self):
        """~ 路径被展开"""
        session = Session(key="test:123")

        # 设置 home 目录
        result = session.set_cwd("~")
        assert result is True
        assert session.get_cwd() == str(Path.home())

    def test_get_cwd_after_clear(self):
        """清空 metadata 后返回默认值"""
        session = Session(key="test:123")

        with tempfile.TemporaryDirectory() as tmpdir:
            session.set_cwd(tmpdir)
            assert session.get_cwd() == str(Path(tmpdir).resolve())

            # 清空 metadata
            session.metadata = {}
            assert session.get_cwd() == os.getcwd()

    def test_updated_at_changes_on_set_cwd(self):
        """set_cwd 更新 updated_at"""
        session = Session(key="test:123")
        original_updated_at = session.updated_at

        # 等待一小段时间确保时间戳变化
        import time
        time.sleep(0.01)

        with tempfile.TemporaryDirectory() as tmpdir:
            session.set_cwd(tmpdir)
            assert session.updated_at > original_updated_at
