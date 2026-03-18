"""Workspace Manager 单元测试"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from anyclaw.workspace.manager import WorkspaceManager
from anyclaw.workspace.bootstrap import BootstrapLoader
from anyclaw.workspace.templates import BOOTSTRAP_TEMPLATE, GITIGNORE_TEMPLATE


class TestWorkspaceManager:
    """WorkspaceManager 测试"""

    def test_default_path(self):
        """测试默认路径"""
        manager = WorkspaceManager()
        expected = Path.home() / ".anyclaw" / "workspace"
        assert manager.path == expected

    def test_custom_path(self):
        """测试自定义路径"""
        custom_path = "/tmp/custom-workspace"
        manager = WorkspaceManager(workspace_path=custom_path)
        assert manager.path == Path(custom_path).resolve()

    def test_profile_path_default(self):
        """测试 default profile 路径"""
        manager = WorkspaceManager(profile="default")
        expected = Path.home() / ".anyclaw" / "workspace"
        assert manager.path == expected

    def test_profile_path_custom(self):
        """测试自定义 profile 路径"""
        manager = WorkspaceManager(profile="work")
        expected = Path.home() / ".anyclaw" / "workspace-work"
        assert manager.path == expected

    @patch.dict(os.environ, {"ANYCLAW_PROFILE": "test"})
    def test_profile_from_env(self):
        """测试从环境变量读取 profile"""
        manager = WorkspaceManager()
        expected = Path.home() / ".anyclaw" / "workspace-test"
        assert manager.path == expected

    def test_state_dir(self):
        """测试状态目录"""
        manager = WorkspaceManager()
        expected = Path.home() / ".anyclaw"
        assert manager.state_dir == expected

    def test_exists_false(self):
        """测试工作区不存在"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = WorkspaceManager(workspace_path=f"{tmpdir}/nonexistent")
            assert manager.exists() is False

    def test_create_and_exists(self):
        """测试创建工作区"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)

            assert manager.exists() is False
            manager.create(init_git=False)
            assert manager.exists() is True

    def test_create_default_files(self):
        """测试创建默认文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=False)

            # 检查文件是否创建
            assert (manager.path / "BOOTSTRAP.md").exists()
            assert (manager.path / ".gitignore").exists()
            assert (manager.path / "SOUL.md").exists()
            assert (manager.path / "USER.md").exists()

    def test_create_with_git(self):
        """测试创建时初始化 git"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=True)

            assert manager.is_git_repo() is True

    def test_create_without_git(self):
        """测试创建时不初始化 git"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=False)

            assert manager.is_git_repo() is False

    def test_get_files(self):
        """测试获取文件列表"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=False)

            files = manager.get_files()
            file_names = [f["name"] for f in files]

            assert "BOOTSTRAP.md" in file_names
            assert "SOUL.md" in file_names
            assert "USER.md" in file_names

    def test_get_bootstrap_files(self):
        """测试获取引导文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=False)

            bootstrap_files = manager.get_bootstrap_files()
            assert len(bootstrap_files) == 1
            assert bootstrap_files[0]["name"] == "BOOTSTRAP.md"
            assert "content" in bootstrap_files[0]

    def test_delete_bootstrap(self):
        """测试删除引导文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=False)

            assert (manager.path / "BOOTSTRAP.md").exists()

            result = manager.delete_bootstrap()
            assert result is True
            assert not (manager.path / "BOOTSTRAP.md").exists()

    def test_get_status(self):
        """测试获取状态"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=False)

            status = manager.get_status()

            assert status["exists"] is True
            assert status["path"] == str(manager.path)
            assert status["is_git_repo"] is False
            assert len(status["files"]) > 0

    def test_force_recreate(self):
        """测试强制重新创建"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=False)

            # 修改一个文件
            test_file = manager.path / "test.txt"
            test_file.write_text("test content")

            # 强制重新创建
            manager.create(init_git=False, force=True)

            # 之前创建的文件应该不存在
            assert not test_file.exists()


class TestBootstrapLoader:
    """BootstrapLoader 测试"""

    def test_load_empty(self):
        """测试加载空工作区"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=False)

            # 删除 BOOTSTRAP.md
            (manager.path / "BOOTSTRAP.md").unlink()

            loader = BootstrapLoader(manager)
            content, truncated = loader.load()

            assert content == ""
            assert truncated is False

    def test_load_with_bootstrap(self):
        """测试加载引导文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=False)

            loader = BootstrapLoader(manager)
            content, truncated = loader.load()

            assert "BOOTSTRAP.md" in content
            assert "欢迎使用" in content
            assert truncated is False

    def test_has_bootstrap(self):
        """测试检查引导文件存在"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=False)

            loader = BootstrapLoader(manager)
            assert loader.has_bootstrap() is True

    def test_is_completed(self):
        """测试检查引导完成"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=False)

            loader = BootstrapLoader(manager)
            assert loader.is_completed() is False

            loader.mark_completed()
            assert loader.is_completed() is True

    def test_mark_completed(self):
        """测试标记完成"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=False)

            loader = BootstrapLoader(manager)
            result = loader.mark_completed()

            assert result is True
            assert not (manager.path / "BOOTSTRAP.md").exists()

    def test_truncation(self):
        """测试内容截断"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=False)

            # 创建超长内容
            long_content = "x" * 30000
            (manager.path / "BOOTSTRAP.md").write_text(long_content)

            loader = BootstrapLoader(manager, max_chars=1000)
            content, truncated = loader.load()

            assert truncated is True
            assert len(content) < 30000

    def test_get_bootstrap_prompt(self):
        """测试获取引导提示词"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_path = f"{tmpdir}/test-workspace"
            manager = WorkspaceManager(workspace_path=workspace_path)
            manager.create(init_git=False)

            loader = BootstrapLoader(manager)
            prompt = loader.get_bootstrap_prompt()

            assert "首次运行引导" in prompt
            assert "BOOTSTRAP.md" in prompt


class TestTemplates:
    """模板测试"""

    def test_bootstrap_template(self):
        """测试引导模板"""
        assert "欢迎使用" in BOOTSTRAP_TEMPLATE
        assert "AnyClaw" in BOOTSTRAP_TEMPLATE

    def test_gitignore_template(self):
        """测试 gitignore 模板"""
        assert ".DS_Store" in GITIGNORE_TEMPLATE
        assert ".env" in GITIGNORE_TEMPLATE
