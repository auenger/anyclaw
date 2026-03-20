"""文件工具权限测试 - allow_all_access 配置"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from anyclaw.tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool
from anyclaw.security.path import PathGuard, PathSecurityError


class TestReadFileToolPermissions:
    """ReadFileTool allow_all_access 测试"""

    @pytest.mark.asyncio
    async def test_allow_all_access_can_read_any_path(self):
        """allow_all_access=true 时可读取任意路径"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文件
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("hello world")

            tool = ReadFileTool(workspace=Path.cwd())

            # 模拟 allow_all_access=True
            with patch('anyclaw.config.settings.settings') as mock_settings:
                mock_settings.allow_all_access = True

                result = await tool.execute(str(test_file))
                assert "hello world" in result
                assert "错误" not in result

    @pytest.mark.asyncio
    async def test_restrict_to_workspace_with_path_guard(self):
        """allow_all_access=false 时使用 path_guard 验证"""
        with tempfile.TemporaryDirectory() as workspace_dir:
            workspace = Path(workspace_dir)
            test_file = workspace / "test.txt"
            test_file.write_text("workspace file")

            path_guard = PathGuard(workspace=workspace)
            tool = ReadFileTool(workspace=workspace, path_guard=path_guard)

            # 模拟 allow_all_access=False
            with patch('anyclaw.config.settings.settings') as mock_settings:
                mock_settings.allow_all_access = False

                # 工作区内文件可读
                result = await tool.execute(str(test_file))
                assert "workspace file" in result

    @pytest.mark.asyncio
    async def test_path_guard_blocks_outside_access(self):
        """path_guard 阻止访问 workspace 外的文件"""
        with tempfile.TemporaryDirectory() as workspace_dir:
            with tempfile.TemporaryDirectory() as outside_dir:
                workspace = Path(workspace_dir)
                outside_file = Path(outside_dir) / "outside.txt"
                outside_file.write_text("outside content")

                path_guard = PathGuard(workspace=workspace, restrict_to_workspace=True)
                tool = ReadFileTool(workspace=workspace, path_guard=path_guard)

                # 模拟 allow_all_access=False
                with patch('anyclaw.config.settings.settings') as mock_settings:
                    mock_settings.allow_all_access = False

                    # workspace 外文件应被阻止
                    result = await tool.execute(str(outside_file))
                    assert "错误" in result or "Error" in result


class TestWriteFileToolPermissions:
    """WriteFileTool allow_all_access 测试"""

    @pytest.mark.asyncio
    async def test_allow_all_access_can_write_any_path(self):
        """allow_all_access=true 时可写入任意路径"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"

            tool = WriteFileTool(workspace=Path.cwd())

            # 模拟 allow_all_access=True
            with patch('anyclaw.config.settings.settings') as mock_settings:
                mock_settings.allow_all_access = True

                result = await tool.execute(str(test_file), "test content")
                assert "成功" in result
                assert test_file.read_text() == "test content"

    @pytest.mark.asyncio
    async def test_path_guard_validates_write_path(self):
        """path_guard 验证写入路径"""
        with tempfile.TemporaryDirectory() as workspace_dir:
            workspace = Path(workspace_dir)
            test_file = workspace / "test.txt"

            path_guard = PathGuard(workspace=workspace)
            tool = WriteFileTool(workspace=workspace, path_guard=path_guard)

            # 模拟 allow_all_access=False
            with patch('anyclaw.config.settings.settings') as mock_settings:
                mock_settings.allow_all_access = False

                result = await tool.execute(str(test_file), "test content")
                assert "成功" in result

    @pytest.mark.asyncio
    async def test_path_guard_blocks_outside_write(self):
        """path_guard 阻止写入 workspace 外的文件"""
        with tempfile.TemporaryDirectory() as workspace_dir:
            with tempfile.TemporaryDirectory() as outside_dir:
                workspace = Path(workspace_dir)
                outside_file = Path(outside_dir) / "outside.txt"

                path_guard = PathGuard(workspace=workspace, restrict_to_workspace=True)
                tool = WriteFileTool(workspace=workspace, path_guard=path_guard)

                # 模拟 allow_all_access=False
                with patch('anyclaw.config.settings.settings') as mock_settings:
                    mock_settings.allow_all_access = False

                    result = await tool.execute(str(outside_file), "outside content")
                    assert "错误" in result or "Error" in result


class TestListDirToolPermissions:
    """ListDirTool allow_all_access 测试"""

    @pytest.mark.asyncio
    async def test_allow_all_access_can_list_any_dir(self):
        """allow_all_access=true 时可列出任意目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文件
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("content")

            tool = ListDirTool(workspace=Path.cwd())

            # 模拟 allow_all_access=True
            with patch('anyclaw.config.settings.settings') as mock_settings:
                mock_settings.allow_all_access = True

                result = await tool.execute(tmpdir)
                assert "test.txt" in result
                assert "错误" not in result

    @pytest.mark.asyncio
    async def test_path_guard_validates_list_path(self):
        """path_guard 验证列出路径"""
        with tempfile.TemporaryDirectory() as workspace_dir:
            workspace = Path(workspace_dir)
            test_file = workspace / "test.txt"
            test_file.write_text("content")

            path_guard = PathGuard(workspace=workspace)
            tool = ListDirTool(workspace=workspace, path_guard=path_guard)

            # 模拟 allow_all_access=False
            with patch('anyclaw.config.settings.settings') as mock_settings:
                mock_settings.allow_all_access = False

                result = await tool.execute(str(workspace))
                assert "test.txt" in result

    @pytest.mark.asyncio
    async def test_path_guard_blocks_outside_list(self):
        """path_guard 阻止列出 workspace 外的目录"""
        with tempfile.TemporaryDirectory() as workspace_dir:
            with tempfile.TemporaryDirectory() as outside_dir:
                workspace = Path(workspace_dir)
                outside_file = Path(outside_dir) / "outside.txt"
                outside_file.write_text("content")

                path_guard = PathGuard(workspace=workspace, restrict_to_workspace=True)
                tool = ListDirTool(workspace=workspace, path_guard=path_guard)

                # 模拟 allow_all_access=False
                with patch('anyclaw.config.settings.settings') as mock_settings:
                    mock_settings.allow_all_access = False

                    result = await tool.execute(outside_dir)
                    assert "错误" in result or "Error" in result


class TestPathGuardIntegration:
    """PathGuard 传递和生效测试"""

    def test_path_guard_passed_to_read_tool(self):
        """path_guard 正确传递给 ReadFileTool"""
        workspace = Path.cwd()
        path_guard = PathGuard(workspace=workspace)

        tool = ReadFileTool(workspace=workspace, path_guard=path_guard)
        assert tool.path_guard is path_guard

    def test_path_guard_passed_to_write_tool(self):
        """path_guard 正确传递给 WriteFileTool"""
        workspace = Path.cwd()
        path_guard = PathGuard(workspace=workspace)

        tool = WriteFileTool(workspace=workspace, path_guard=path_guard)
        assert tool.path_guard is path_guard

    def test_path_guard_passed_to_list_tool(self):
        """path_guard 正确传递给 ListDirTool"""
        workspace = Path.cwd()
        path_guard = PathGuard(workspace=workspace)

        tool = ListDirTool(workspace=workspace, path_guard=path_guard)
        assert tool.path_guard is path_guard

    @pytest.mark.asyncio
    async def test_consistent_behavior_across_tools(self):
        """所有文件工具行为一致"""
        with tempfile.TemporaryDirectory() as workspace_dir:
            with tempfile.TemporaryDirectory() as outside_dir:
                workspace = Path(workspace_dir)
                path_guard = PathGuard(workspace=workspace, restrict_to_workspace=True)

                # 创建工具
                read_tool = ReadFileTool(workspace=workspace, path_guard=path_guard)
                write_tool = WriteFileTool(workspace=workspace, path_guard=path_guard)
                list_tool = ListDirTool(workspace=workspace, path_guard=path_guard)

                # 模拟 allow_all_access=False
                with patch('anyclaw.config.settings.settings') as mock_settings:
                    mock_settings.allow_all_access = False

                    # 所有工具都应该阻止访问 workspace 外
                    outside_file = Path(outside_dir) / "test.txt"
                    outside_file.write_text("content")

                    read_result = await read_tool.execute(str(outside_file))
                    write_result = await write_tool.execute(str(outside_file), "new")
                    list_result = await list_tool.execute(outside_dir)

                    assert "错误" in read_result or "Error" in read_result
                    assert "错误" in write_result or "Error" in write_result
                    assert "错误" in list_result or "Error" in list_result
