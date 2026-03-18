"""Persona 人设加载器单元测试"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from anyclaw.workspace.persona import (
    PersonaLoader,
    get_persona_loader,
    reset_persona_loader,
)
from anyclaw.workspace.manager import WorkspaceManager
from anyclaw.workspace.templates import (
    SOUL_TEMPLATE,
    USER_TEMPLATE,
    IDENTITY_TEMPLATE,
    TOOLS_TEMPLATE,
)


class TestPersonaLoader:
    """PersonaLoader 测试"""

    def test_init_default(self):
        """测试默认初始化"""
        loader = PersonaLoader()
        assert loader.workspace is not None
        assert loader.max_chars == PersonaLoader.DEFAULT_MAX_CHARS

    def test_init_with_workspace(self):
        """测试带工作区初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = WorkspaceManager(workspace_path=tmpdir)
            loader = PersonaLoader(workspace=workspace)
            assert loader.workspace.path == workspace.path

    def test_init_with_max_chars(self):
        """测试自定义最大字符数"""
        loader = PersonaLoader(max_chars=5000)
        assert loader.max_chars == 5000

    def test_load_file_not_exists(self):
        """测试加载不存在的文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = WorkspaceManager(workspace_path=tmpdir)
            loader = PersonaLoader(workspace=workspace)

            content = loader._load_file("NONEXISTENT.md")
            assert content is None

    def test_load_file_exists(self):
        """测试加载存在的文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = WorkspaceManager(workspace_path=tmpdir)
            loader = PersonaLoader(workspace=workspace)

            # 创建测试文件
            test_file = workspace.path / "TEST.md"
            test_content = "Test content"
            test_file.write_text(test_content)

            content = loader._load_file("TEST.md")
            assert content == test_content

    def test_load_file_truncation(self):
        """测试文件截断"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = WorkspaceManager(workspace_path=tmpdir)
            loader = PersonaLoader(workspace=workspace, max_chars=100)

            # 创建超长文件
            test_file = workspace.path / "LONG.md"
            long_content = "x" * 200
            test_file.write_text(long_content)

            content = loader._load_file("LONG.md")
            # 截断后长度应该小于原长度，且包含截断标记
            assert len(content) < len(long_content)
            assert "截断" in content or "truncated" in content.lower()

    def test_load_all_empty(self):
        """测试加载空工作区"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = WorkspaceManager(workspace_path=tmpdir)
            loader = PersonaLoader(workspace=workspace)

            persona = loader.load_all(is_private=True)

            assert persona["soul"] is None
            assert persona["user"] is None
            assert persona["identity"] is None
            assert persona["tools"] is None

    def test_load_all_with_files(self):
        """测试加载有文件的工作区"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = WorkspaceManager(workspace_path=tmpdir)
            loader = PersonaLoader(workspace=workspace)

            # 创建测试文件
            (workspace.path / "SOUL.md").write_text("Soul content")
            (workspace.path / "USER.md").write_text("User content")
            (workspace.path / "IDENTITY.md").write_text("Identity content")
            (workspace.path / "TOOLS.md").write_text("Tools content")

            # 私密会话
            persona = loader.load_all(is_private=True)
            assert persona["soul"] == "Soul content"
            assert persona["user"] == "User content"
            assert persona["identity"] == "Identity content"
            assert persona["tools"] == "Tools content"

            # 公开会话 - user 键不存在
            persona = loader.load_all(is_private=False)
            assert persona["soul"] == "Soul content"
            assert "user" not in persona  # 公开会话不包含用户信息键

    def test_build_system_prompt_empty(self):
        """测试构建空系统提示"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = WorkspaceManager(workspace_path=tmpdir)
            loader = PersonaLoader(workspace=workspace)

            prompt = loader.build_system_prompt()
            assert prompt == ""

    def test_build_system_prompt_with_files(self):
        """测试构建有内容的系统提示"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = WorkspaceManager(workspace_path=tmpdir)
            loader = PersonaLoader(workspace=workspace)

            (workspace.path / "SOUL.md").write_text("Soul content")
            (workspace.path / "USER.md").write_text("User content")

            prompt = loader.build_system_prompt(is_private=True)
            assert "Soul content" in prompt
            assert "User content" in prompt

            prompt = loader.build_system_prompt(is_private=False)
            assert "Soul content" in prompt
            assert "User content" not in prompt

    def test_create_default_files(self):
        """测试创建默认文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = WorkspaceManager(workspace_path=tmpdir)
            loader = PersonaLoader(workspace=workspace)

            loader.create_default_files()

            assert (workspace.path / "SOUL.md").exists()
            assert (workspace.path / "USER.md").exists()
            assert (workspace.path / "IDENTITY.md").exists()
            assert (workspace.path / "TOOLS.md").exists()

    def test_create_default_files_not_overwrite(self):
        """测试不覆盖已存在的文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = WorkspaceManager(workspace_path=tmpdir)
            loader = PersonaLoader(workspace=workspace)

            # 创建自定义文件
            (workspace.path / "SOUL.md").write_text("Custom soul")

            loader.create_default_files()

            # 不应覆盖
            assert (workspace.path / "SOUL.md").read_text() == "Custom soul"

    def test_get_file_path(self):
        """测试获取文件路径"""
        loader = PersonaLoader()
        path = loader.get_file_path("SOUL.md")
        assert path == loader.workspace.path / "SOUL.md"

    def test_file_exists(self):
        """测试文件是否存在"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = WorkspaceManager(workspace_path=tmpdir)
            loader = PersonaLoader(workspace=workspace)

            assert loader.file_exists("SOUL.md") is False

            (workspace.path / "SOUL.md").write_text("content")
            assert loader.file_exists("SOUL.md") is True

    def test_get_status(self):
        """测试获取状态"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = WorkspaceManager(workspace_path=tmpdir)
            loader = PersonaLoader(workspace=workspace)

            (workspace.path / "SOUL.md").write_text("content")

            status = loader.get_status()

            assert "workspace_path" in status
            assert "files" in status
            assert status["files"]["SOUL.md"]["exists"] is True
            assert status["files"]["USER.md"]["exists"] is False

    def test_clear_cache(self):
        """测试清除缓存"""
        loader = PersonaLoader()
        loader._cache["test"] = "value"
        loader.clear_cache()
        assert loader._cache == {}


class TestPersonaLoaderGlobal:
    """全局加载器测试"""

    def test_get_persona_loader(self):
        """测试获取全局加载器"""
        reset_persona_loader()
        loader1 = get_persona_loader()
        loader2 = get_persona_loader()
        assert loader1 is loader2

    def test_reset_persona_loader(self):
        """测试重置全局加载器"""
        loader1 = get_persona_loader()
        reset_persona_loader()
        loader2 = get_persona_loader()
        assert loader1 is not loader2


class TestPersonaTemplates:
    """人设模板测试"""

    def test_soul_template(self):
        """测试人设模板"""
        assert len(SOUL_TEMPLATE) > 0

    def test_user_template(self):
        """测试用户模板"""
        assert len(USER_TEMPLATE) > 0

    def test_identity_template(self):
        """测试身份模板"""
        assert len(IDENTITY_TEMPLATE) > 0

    def test_tools_template(self):
        """测试工具模板"""
        assert len(TOOLS_TEMPLATE) > 0
