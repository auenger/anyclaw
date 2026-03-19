"""测试 workspace 写入限制功能"""

import asyncio
import os
import tempfile
from pathlib import Path

import pytest

from anyclaw.tools.filesystem import WriteFileTool


class TestWriteFileToolRestrict:
    """测试 WriteFileTool 的 workspace 限制功能"""

    @pytest.fixture
    def temp_workspace(self, tmp_path: Path) -> Path:
        """创建临时 workspace 目录"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        return workspace

    @pytest.fixture
    def temp_outside(self, tmp_path: Path) -> Path:
        """创建临时外部目录"""
        outside = tmp_path / "outside"
        outside.mkdir()
        return outside

    @pytest.mark.asyncio
    async def test_default_restrict_enabled(self, temp_workspace: Path):
        """测试默认启用限制"""
        tool = WriteFileTool(workspace=temp_workspace)
        assert tool.restrict_to_workspace is True

    @pytest.mark.asyncio
    async def test_write_inside_workspace_allowed(self, temp_workspace: Path):
        """测试允许写入 workspace 内的文件"""
        tool = WriteFileTool(workspace=temp_workspace, restrict_to_workspace=True)

        result = await tool.execute("test.md", "# Hello")
        assert "成功" in result
        assert (temp_workspace / "test.md").exists()

    @pytest.mark.asyncio
    async def test_write_subdir_allowed(self, temp_workspace: Path):
        """测试允许写入 workspace 子目录内的文件"""
        tool = WriteFileTool(workspace=temp_workspace, restrict_to_workspace=True)

        result = await tool.execute("memory/test.md", "# Memory")
        assert "成功" in result
        assert (temp_workspace / "memory" / "test.md").exists()

    @pytest.mark.asyncio
    async def test_write_outside_blocked(self, temp_workspace: Path, temp_outside: Path):
        """测试阻止写入 workspace 外的文件"""
        tool = WriteFileTool(
            workspace=temp_workspace,
            allowed_dir=temp_workspace,
            restrict_to_workspace=True,
        )

        # 尝试写入外部路径（使用绝对路径）
        outside_file = temp_outside / "hack.md"
        result = await tool.execute(str(outside_file), "# Hacked")

        assert "权限错误" in result
        assert not outside_file.exists()

    @pytest.mark.asyncio
    async def test_write_absolute_path_outside_blocked(self, temp_workspace: Path):
        """测试阻止使用绝对路径写入 workspace 外"""
        tool = WriteFileTool(
            workspace=temp_workspace,
            allowed_dir=temp_workspace,
            restrict_to_workspace=True,
        )

        # 使用系统临时目录（在 workspace 外）
        result = await tool.execute("/tmp/hack.md", "# Hacked")
        assert "权限错误" in result

    @pytest.mark.asyncio
    async def test_write_absolute_path_inside_allowed(self, temp_workspace: Path):
        """测试允许使用绝对路径写入 workspace 内"""
        tool = WriteFileTool(
            workspace=temp_workspace,
            allowed_dir=temp_workspace,
            restrict_to_workspace=True,
        )

        # 使用绝对路径写入 workspace 内
        inside_file = temp_workspace / "absolute.md"
        result = await tool.execute(str(inside_file), "# Absolute")
        assert "成功" in result

    @pytest.mark.asyncio
    async def test_restrict_disabled_allows_outside(self, temp_workspace: Path, temp_outside: Path):
        """测试禁用限制时允许写入任意路径"""
        tool = WriteFileTool(
            workspace=temp_workspace,
            restrict_to_workspace=False,
        )

        outside_file = temp_outside / "free.md"
        result = await tool.execute(str(outside_file), "# Free")
        assert "成功" in result
        assert outside_file.exists()

    @pytest.mark.asyncio
    async def test_symlink_outside_blocked(self, temp_workspace: Path, temp_outside: Path):
        """测试阻止通过符号链接写入 workspace 外"""
        tool = WriteFileTool(
            workspace=temp_workspace,
            allowed_dir=temp_workspace,
            restrict_to_workspace=True,
        )

        # 在 workspace 内创建指向外部的符号链接
        link_path = temp_workspace / "outside_link"
        try:
            link_path.symlink_to(temp_outside)
        except OSError:
            # 某些系统可能不允许创建符号链接
            pytest.skip("无法创建符号链接")

        # 尝试通过符号链接写入
        result = await tool.execute("outside_link/hack.md", "# Hacked")
        assert "权限错误" in result

    @pytest.mark.asyncio
    async def test_path_traversal_blocked(self, temp_workspace: Path, tmp_path: Path):
        """测试阻止路径遍历攻击"""
        tool = WriteFileTool(
            workspace=temp_workspace,
            allowed_dir=temp_workspace,
            restrict_to_workspace=True,
        )

        # 尝试使用 ../ 遍历到上级目录
        result = await tool.execute("../../../etc/passwd", "# Hacked")
        assert "权限错误" in result

    @pytest.mark.asyncio
    async def test_error_message_format(self, temp_workspace: Path):
        """测试错误信息格式"""
        tool = WriteFileTool(
            workspace=temp_workspace,
            allowed_dir=temp_workspace,
            restrict_to_workspace=True,
        )

        result = await tool.execute("/tmp/test.md", "# Test")
        assert "权限错误" in result
        assert "超出 workspace 范围" in result
        assert "restrict_to_workspace=false" in result


class TestWriteFileToolIntegration:
    """集成测试：WriteFileTool 与 Settings 配合"""

    @pytest.mark.asyncio
    async def test_with_settings_restrict(self, tmp_path: Path):
        """测试与 settings 集成（启用限制）"""
        from anyclaw.config.settings import Settings

        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # 模拟 settings
        settings = Settings(restrict_to_workspace=True)

        tool = WriteFileTool(
            workspace=workspace,
            restrict_to_workspace=settings.restrict_to_workspace,
        )

        # 应该能写入内部
        result = await tool.execute("inside.md", "# Inside")
        assert "成功" in result

        # 不应该能写入外部
        result = await tool.execute("/tmp/outside.md", "# Outside")
        assert "权限错误" in result

    @pytest.mark.asyncio
    async def test_with_settings_no_restrict(self, tmp_path: Path):
        """测试与 settings 集成（禁用限制）"""
        from anyclaw.config.settings import Settings

        workspace = tmp_path / "workspace"
        workspace.mkdir()
        outside = tmp_path / "outside"
        outside.mkdir()

        # 模拟 settings
        settings = Settings(restrict_to_workspace=False)

        tool = WriteFileTool(
            workspace=workspace,
            restrict_to_workspace=settings.restrict_to_workspace,
        )

        # 应该能写入外部
        outside_file = outside / "free.md"
        result = await tool.execute(str(outside_file), "# Free")
        assert "成功" in result
