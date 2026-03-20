"""路径守卫模块测试

测试 PathGuard 的各种安全防护功能：
- 路径遍历防护
- 家目录访问阻止
- 环境变量展开阻止
- 符号链接检查
- 允许目录范围验证
- URL 编码绕过防护
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from anyclaw.security.path import (
    PathGuard,
    PathSecurityError,
    create_path_guard_from_settings,
)


class TestPathGuardBasic:
    """基础功能测试"""

    def test_init(self, tmp_path):
        """测试初始化"""
        guard = PathGuard(workspace=tmp_path)
        assert guard.workspace == tmp_path.resolve()
        assert guard.extra_allowed_dirs == []
        assert guard.allow_symlinks_in_workspace is True
        assert guard.restrict_to_workspace is True

    def test_init_with_extra_dirs(self, tmp_path):
        """测试初始化 - 额外允许目录"""
        extra_dir = tmp_path / "extra"
        extra_dir.mkdir()
        guard = PathGuard(
            workspace=tmp_path,
            extra_allowed_dirs=[extra_dir],
        )
        assert len(guard.extra_allowed_dirs) == 1
        assert guard.extra_allowed_dirs[0] == extra_dir.resolve()

    def test_resolve_and_validate_normal_path(self, tmp_path):
        """测试正常路径验证"""
        guard = PathGuard(workspace=tmp_path)

        # 创建一个测试文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        result = guard.resolve_and_validate("test.txt")
        assert result == test_file.resolve()

    def test_resolve_and_validate_subdirectory(self, tmp_path):
        """测试子目录路径验证"""
        guard = PathGuard(workspace=tmp_path)

        # 创建子目录和文件
        subdir = tmp_path / "src" / "main"
        subdir.mkdir(parents=True)
        test_file = subdir / "app.py"
        test_file.write_text("# app")

        result = guard.resolve_and_validate("src/main/app.py")
        assert result == test_file.resolve()

    def test_is_safe_path(self, tmp_path):
        """测试 is_safe_path 方法"""
        guard = PathGuard(workspace=tmp_path)

        # 安全路径
        assert guard.is_safe_path("test.txt") is True
        assert guard.is_safe_path("src/main.py") is True

        # 不安全路径
        assert guard.is_safe_path("../../../etc/passwd") is False
        assert guard.is_safe_path("/etc/passwd") is False


class TestPathTraversal:
    """路径遍历防护测试"""

    def test_block_relative_traversal_unix(self, tmp_path):
        """测试阻止 Unix 相对路径遍历"""
        guard = PathGuard(workspace=tmp_path)

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("../../../etc/passwd")
        assert "traversal" in str(exc_info.value).lower()

    def test_block_relative_traversal_windows(self, tmp_path):
        """测试阻止 Windows 相对路径遍历"""
        guard = PathGuard(workspace=tmp_path)

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("..\\..\\..\\windows\\system32")
        assert "traversal" in str(exc_info.value).lower()

    def test_block_dotdot_only(self, tmp_path):
        """测试阻止纯 '..' 路径"""
        guard = PathGuard(workspace=tmp_path)

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("..")
        assert "traversal" in str(exc_info.value).lower()

    def test_block_absolute_path_outside_workspace(self, tmp_path):
        """测试阻止绝对路径访问工作区外"""
        guard = PathGuard(workspace=tmp_path)

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("/etc/passwd")
        assert "outside" in str(exc_info.value).lower()

    def test_block_path_with_slash_dotdot(self, tmp_path):
        """测试阻止 /.. 模式"""
        guard = PathGuard(workspace=tmp_path)

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("src/../../../etc/passwd")
        assert "traversal" in str(exc_info.value).lower()


class TestHomeDirectory:
    """家目录访问防护测试"""

    def test_block_tilde_expansion(self, tmp_path):
        """测试阻止 ~ 家目录访问"""
        guard = PathGuard(workspace=tmp_path)

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("~/.ssh/id_rsa")
        assert "outside" in str(exc_info.value).lower()

    def test_block_home_env_variable(self, tmp_path):
        """测试阻止 $HOME 环境变量"""
        guard = PathGuard(workspace=tmp_path)

        with patch.dict(os.environ, {"HOME": "/home/testuser"}):
            with pytest.raises(PathSecurityError) as exc_info:
                guard.resolve_and_validate("$HOME/.bashrc")
            assert "outside" in str(exc_info.value).lower()

    def test_block_home_env_variable_braces(self, tmp_path):
        """测试阻止 ${HOME} 环境变量"""
        guard = PathGuard(workspace=tmp_path)

        with patch.dict(os.environ, {"HOME": "/home/testuser"}):
            with pytest.raises(PathSecurityError) as exc_info:
                guard.resolve_and_validate("${HOME}/.config")
            assert "outside" in str(exc_info.value).lower()


class TestEncodedTraversal:
    """URL 编码绕过防护测试"""

    def test_block_url_encoded_traversal(self, tmp_path):
        """测试阻止 URL 编码的路径遍历"""
        guard = PathGuard(workspace=tmp_path)

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("%2e%2e%2f%2e%2e%2fetc/passwd")
        assert "encoded" in str(exc_info.value).lower()

    def test_block_partial_encoded_traversal(self, tmp_path):
        """测试阻止部分 URL 编码的路径遍历"""
        guard = PathGuard(workspace=tmp_path)

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("%2e%2e/etc/passwd")
        assert "encoded" in str(exc_info.value).lower()

    def test_block_double_encoded_traversal(self, tmp_path):
        """测试阻止双重 URL 编码的路径遍历"""
        guard = PathGuard(workspace=tmp_path)

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("%252e%252e%252f")
        assert "encoded" in str(exc_info.value).lower()


class TestNullByteInjection:
    """空字节注入防护测试"""

    def test_block_null_byte(self, tmp_path):
        """测试阻止空字节注入"""
        guard = PathGuard(workspace=tmp_path)

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("test\x00.txt")
        assert "null byte" in str(exc_info.value).lower()

    def test_block_url_encoded_null_byte(self, tmp_path):
        """测试阻止 URL 编码的空字节"""
        guard = PathGuard(workspace=tmp_path)

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("test%00.txt")
        assert "null byte" in str(exc_info.value).lower()


class TestDangerousProtocols:
    """危险协议防护测试"""

    def test_block_file_protocol(self, tmp_path):
        """测试阻止 file:// 协议"""
        guard = PathGuard(workspace=tmp_path)

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("file:///etc/passwd")
        assert "protocol" in str(exc_info.value).lower()

    def test_block_ftp_protocol(self, tmp_path):
        """测试阻止 ftp:// 协议"""
        guard = PathGuard(workspace=tmp_path)

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("ftp://evil.com/malware")
        assert "protocol" in str(exc_info.value).lower()


class TestSymlinkProtection:
    """符号链接防护测试"""

    def test_block_symlink_outside_workspace(self, tmp_path):
        """测试阻止指向工作区外的符号链接"""
        guard = PathGuard(workspace=tmp_path)

        # 创建一个指向系统目录的符号链接
        link_path = tmp_path / "link_to_etc"
        try:
            link_path.symlink_to("/etc")
        except (OSError, PermissionError):
            pytest.skip("Cannot create symlink in this environment")

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("link_to_etc/passwd")
        assert "outside" in str(exc_info.value).lower()

    def test_allow_symlink_inside_workspace(self, tmp_path):
        """测试允许工作区内的符号链接"""
        guard = PathGuard(workspace=tmp_path, allow_symlinks_in_workspace=True)

        # 创建目录和符号链接
        real_dir = tmp_path / "real"
        real_dir.mkdir()
        real_file = real_dir / "data.txt"
        real_file.write_text("data")

        link_dir = tmp_path / "link"
        try:
            link_dir.symlink_to(real_dir)
        except (OSError, PermissionError):
            pytest.skip("Cannot create symlink in this environment")

        result = guard.resolve_and_validate("link/data.txt")
        assert result == real_file.resolve()

    def test_block_all_symlinks_when_disabled(self, tmp_path):
        """测试禁用符号链接时阻止所有符号链接"""
        guard = PathGuard(
            workspace=tmp_path,
            allow_symlinks_in_workspace=False,
        )

        # 创建符号链接
        real_file = tmp_path / "real.txt"
        real_file.write_text("data")
        link_path = tmp_path / "link.txt"
        try:
            link_path.symlink_to(real_file)
        except (OSError, PermissionError):
            pytest.skip("Cannot create symlink in this environment")

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("link.txt")
        assert "symlink" in str(exc_info.value).lower()


class TestExtraAllowedDirs:
    """额外允许目录测试"""

    def test_extra_allowed_dir_access(self, tmp_path):
        """测试额外允许目录可以访问"""
        extra_dir = tmp_path / "extra"
        extra_dir.mkdir()
        test_file = extra_dir / "config.json"
        test_file.write_text("{}")

        guard = PathGuard(
            workspace=tmp_path,
            extra_allowed_dirs=[extra_dir],
        )

        result = guard.resolve_and_validate(str(test_file))
        assert result == test_file.resolve()

    def test_extra_allowed_dir_subdirectory(self, tmp_path):
        """测试额外允许目录的子目录可以访问"""
        extra_dir = tmp_path / "config"
        extra_dir.mkdir()
        sub_dir = extra_dir / "anyclaw"
        sub_dir.mkdir()
        test_file = sub_dir / "settings.json"
        test_file.write_text("{}")

        guard = PathGuard(
            workspace=tmp_path,
            extra_allowed_dirs=[extra_dir],
        )

        result = guard.resolve_and_validate(str(test_file))
        assert result == test_file.resolve()

    def test_add_allowed_dir_dynamically(self, tmp_path):
        """测试动态添加允许目录"""
        # 使用一个真正在 workspace 外的目录
        import tempfile
        with tempfile.TemporaryDirectory() as external_dir:
            external_path = Path(external_dir)
            test_file = external_path / "file.txt"
            test_file.write_text("data")

            guard = PathGuard(workspace=tmp_path)

            # 初始应该无法访问（因为是绝对路径且在工作区外）
            with pytest.raises(PathSecurityError):
                guard.resolve_and_validate(str(test_file))

            # 添加允许目录后可以访问
            guard.add_allowed_dir(external_path)
            result = guard.resolve_and_validate(str(test_file))
            assert result == test_file.resolve()


class TestRestrictToWorkspace:
    """restrict_to_workspace 配置测试"""

    def test_restrict_disabled_allows_outside(self, tmp_path):
        """测试禁用限制时允许访问外部"""
        guard = PathGuard(
            workspace=tmp_path,
            restrict_to_workspace=False,
        )

        # 应该不抛出异常（虽然文件可能不存在）
        try:
            result = guard.resolve_and_validate("/tmp/some_file.txt")
            # 如果没抛出异常，说明检查被跳过
        except PathSecurityError as e:
            # 只有路径遍历相关的错误才应该被抛出
            assert "outside" not in str(e).lower()

    def test_restrict_enabled_blocks_outside(self, tmp_path):
        """测试启用限制时阻止访问外部"""
        guard = PathGuard(
            workspace=tmp_path,
            restrict_to_workspace=True,
        )

        with pytest.raises(PathSecurityError) as exc_info:
            guard.resolve_and_validate("/etc/passwd")
        assert "outside" in str(exc_info.value).lower()


class TestCreatePathGuardFromSettings:
    """从配置创建 PathGuard 测试"""

    def test_create_from_settings_defaults(self, tmp_path):
        """测试使用默认配置创建"""
        with patch("anyclaw.config.settings.settings") as mock_settings:
            mock_settings.workspace = str(tmp_path)
            mock_settings.restrict_to_workspace = True
            mock_settings.path_extra_allowed_dirs = []
            mock_settings.path_allow_symlinks_in_workspace = True
            mock_settings.allow_all_access = False  # 新增：关闭全开放模式

            guard = create_path_guard_from_settings(tmp_path)
            assert guard.workspace == tmp_path.resolve()
            assert guard.restrict_to_workspace is True

    def test_create_from_settings_with_extra_dirs(self, tmp_path):
        """测试使用额外目录配置创建"""
        extra_dir = tmp_path / "extra"
        extra_dir.mkdir()

        with patch("anyclaw.config.settings.settings") as mock_settings:
            mock_settings.workspace = str(tmp_path)
            mock_settings.restrict_to_workspace = True
            mock_settings.path_extra_allowed_dirs = [str(extra_dir)]
            mock_settings.path_allow_symlinks_in_workspace = True
            mock_settings.allow_all_access = False  # 新增：关闭全开放模式

            guard = create_path_guard_from_settings(tmp_path)
            assert len(guard.extra_allowed_dirs) == 1

    def test_create_from_settings_allow_all_access(self, tmp_path):
        """测试 allow_all_access 模式"""
        with patch("anyclaw.config.settings.settings") as mock_settings:
            mock_settings.workspace = str(tmp_path)
            mock_settings.allow_all_access = True  # 开启全开放模式

            guard = create_path_guard_from_settings(tmp_path)
            assert guard.restrict_to_workspace is False
            assert guard.allow_symlinks_in_workspace is True


class TestEdgeCases:
    """边界情况测试"""

    def test_empty_path(self, tmp_path):
        """测试空路径"""
        guard = PathGuard(workspace=tmp_path)

        # 空路径会解析为 workspace 本身
        result = guard.resolve_and_validate("")
        assert result == tmp_path.resolve()

    def test_dot_path(self, tmp_path):
        """测试当前目录路径"""
        guard = PathGuard(workspace=tmp_path)

        result = guard.resolve_and_validate(".")
        assert result == tmp_path.resolve()

    def test_nonexistent_path(self, tmp_path):
        """测试不存在的路径（应该允许，因为可能用于写入）"""
        guard = PathGuard(workspace=tmp_path)

        result = guard.resolve_and_validate("nonexistent/file.txt")
        assert tmp_path.resolve() in result.parents

    def test_path_with_spaces(self, tmp_path):
        """测试带空格的路径"""
        guard = PathGuard(workspace=tmp_path)

        # 创建带空格的目录
        spaced_dir = tmp_path / "my folder"
        spaced_dir.mkdir()
        test_file = spaced_dir / "my file.txt"
        test_file.write_text("data")

        result = guard.resolve_and_validate("my folder/my file.txt")
        assert result == test_file.resolve()

    def test_unicode_path(self, tmp_path):
        """测试 Unicode 路径"""
        guard = PathGuard(workspace=tmp_path)

        # 创建 Unicode 目录和文件
        unicode_dir = tmp_path / "中文目录"
        unicode_dir.mkdir()
        test_file = unicode_dir / "文件.txt"
        test_file.write_text("内容")

        result = guard.resolve_and_validate("中文目录/文件.txt")
        assert result == test_file.resolve()

    def test_repr(self, tmp_path):
        """测试 __repr__"""
        guard = PathGuard(workspace=tmp_path)
        repr_str = repr(guard)
        assert "PathGuard" in repr_str
        assert str(tmp_path.resolve()) in repr_str


class TestLongPath:
    """长路径攻击测试"""

    def test_very_long_path(self, tmp_path):
        """测试非常长的路径"""
        guard = PathGuard(workspace=tmp_path)

        # 构建一个很长的路径
        long_path = "a" * 1000 + "/file.txt"

        # 应该不崩溃（可能会因为路径太长失败，但不应该是安全错误）
        try:
            result = guard.resolve_and_validate(long_path)
            # 如果成功，应该在 workspace 内
            assert tmp_path.resolve() in result.parents or result == tmp_path.resolve()
        except PathSecurityError:
            pass  # 路径遍历被检测到也可以
        except OSError:
            pass  # 路径太长导致的系统错误也可以
