"""Tests for session project utilities."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from anyclaw.session.project import (
    find_git_root,
    get_git_branch,
    get_git_remote_url,
    make_safe_dirname,
    get_project_identifier,
    get_channel_identifier,
    get_project_info,
)


class TestFindGitRoot:
    """Tests for find_git_root function."""

    @patch("subprocess.run")
    def test_find_git_root_success(self, mock_run):
        """Test finding git root successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/home/user/project\n"
        mock_run.return_value = mock_result

        result = find_git_root(Path("/home/user/project/subdir"))

        assert result == Path("/home/user/project")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_find_git_root_not_git_repo(self, mock_run):
        """Test when not in a git repo."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = find_git_root(Path("/tmp/not-git"))

        assert result is None

    @patch("subprocess.run")
    def test_find_git_root_timeout(self, mock_run):
        """Test handling timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("git", 5)

        result = find_git_root(Path("/some/path"))

        assert result is None


class TestGetGitBranch:
    """Tests for get_git_branch function."""

    @patch("subprocess.run")
    def test_get_git_branch_success(self, mock_run):
        """Test getting git branch successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "feature/test\n"
        mock_run.return_value = mock_result

        result = get_git_branch(Path("/home/user/project"))

        assert result == "feature/test"

    @patch("subprocess.run")
    def test_get_git_branch_detached_head(self, mock_run):
        """Test handling detached HEAD."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "HEAD\n"
        mock_run.return_value = mock_result

        result = get_git_branch(Path("/home/user/project"))

        assert result is None


class TestGetGitRemoteUrl:
    """Tests for get_git_remote_url function."""

    @patch("subprocess.run")
    def test_get_git_remote_url_success(self, mock_run):
        """Test getting remote URL successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "https://github.com/user/repo.git\n"
        mock_run.return_value = mock_result

        result = get_git_remote_url(Path("/home/user/project"))

        assert result == "https://github.com/user/repo.git"

    @patch("subprocess.run")
    def test_get_git_remote_url_no_remote(self, mock_run):
        """Test when no remote configured."""
        mock_result = MagicMock()
        mock_result.returncode = 128
        mock_run.return_value = mock_result

        result = get_git_remote_url(Path("/home/user/project"))

        assert result is None


class TestMakeSafeDirname:
    """Tests for make_safe_dirname function."""

    def test_simple_path(self):
        """Test simple path conversion."""
        result = make_safe_dirname("/home/user/project")
        # Leading slashes are removed
        assert result == "home-user-project"

    def test_windows_path(self):
        """Test Windows-style path."""
        result = make_safe_dirname("C:\\Users\\test\\project")
        assert "C" in result
        assert "Users" in result

    def test_path_with_special_chars(self):
        """Test path with special characters."""
        result = make_safe_dirname("/home/user/test@project")
        # Special chars should be replaced
        assert "@" not in result

    def test_empty_path(self):
        """Test empty path."""
        result = make_safe_dirname("")
        assert result == "unknown"

    def test_long_path(self):
        """Test path truncation for long paths."""
        long_path = "/home/user/" + "a" * 200
        result = make_safe_dirname(long_path)
        assert len(result) <= 100

    def test_leading_slashes(self):
        """Test removing leading slashes."""
        result = make_safe_dirname("///home/user")
        assert not result.startswith("-")


class TestGetProjectIdentifier:
    """Tests for get_project_identifier function."""

    @patch("anyclaw.session.project.find_git_root")
    def test_git_project(self, mock_find_git):
        """Test identifier for git project."""
        mock_find_git.return_value = Path("/home/user/myproject")

        result = get_project_identifier(Path("/home/user/myproject/subdir"))

        assert "myproject" in result

    @patch("anyclaw.session.project.find_git_root")
    def test_non_git_project(self, mock_find_git):
        """Test identifier for non-git project."""
        mock_find_git.return_value = None

        result = get_project_identifier(Path("/tmp/test-project"))

        assert "test-project" in result

    @patch("anyclaw.session.project.find_git_root")
    def test_disable_git_root(self, mock_find_git):
        """Test with git root disabled."""
        result = get_project_identifier(
            Path("/tmp/test-project"),
            use_git_root=False
        )

        # Should not call find_git_root
        mock_find_git.assert_not_called()
        assert "test-project" in result


class TestGetChannelIdentifier:
    """Tests for get_channel_identifier function."""

    def test_cli_channel(self):
        """Test CLI channel identifier."""
        result = get_channel_identifier("cli", "default")
        assert result == "cli_default"

    def test_feishu_channel(self):
        """Test Feishu channel identifier."""
        result = get_channel_identifier("feishu", "chat_12345")
        assert result == "feishu_chat_12345"

    def test_discord_channel(self):
        """Test Discord channel identifier."""
        result = get_channel_identifier("discord", "channel_67890")
        assert result == "discord_channel_67890"


class TestGetProjectInfo:
    """Tests for get_project_info function."""

    @patch("anyclaw.session.project.find_git_root")
    @patch("anyclaw.session.project.get_git_branch")
    @patch("anyclaw.session.project.get_git_remote_url")
    def test_get_project_info_git(
        self, mock_remote, mock_branch, mock_find_git
    ):
        """Test getting project info for git repo."""
        mock_find_git.return_value = Path("/home/user/myproject")
        mock_branch.return_value = "main"
        mock_remote.return_value = "https://github.com/user/repo.git"

        info = get_project_info(Path("/home/user/myproject"))

        assert info["git_root"] is not None
        assert info["git_branch"] == "main"
        assert info["git_url"] == "https://github.com/user/repo.git"
        assert "project_id" in info

    @patch("anyclaw.session.project.find_git_root")
    def test_get_project_info_non_git(self, mock_find_git):
        """Test getting project info for non-git directory."""
        mock_find_git.return_value = None

        info = get_project_info(Path("/tmp/test"))

        assert info["git_root"] is None
        assert info["git_branch"] is None
        assert info["git_url"] is None
