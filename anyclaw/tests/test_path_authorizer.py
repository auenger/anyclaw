"""PathAuthorizer 单元测试"""

import pytest
from pathlib import Path
import tempfile

from anyclaw.search.authorizer import (
    PathAuthorizer,
    AuthorizationRequiredError,
    get_authorizer,
)


class TestPathAuthorizer:
    """PathAuthorizer 测试类"""

    def setup_method(self):
        """每个测试前重置单例"""
        PathAuthorizer._instance = None

    def test_singleton_pattern(self):
        """测试单例模式"""
        authorizer1 = PathAuthorizer()
        authorizer2 = PathAuthorizer()

        assert authorizer1 is authorizer2

    def test_authorize_session(self):
        """测试临时授权"""
        authorizer = PathAuthorizer()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # 授权
            result = authorizer.authorize(test_dir, persist=False)
            assert result is True

            # 检查授权
            assert authorizer.is_authorized(test_dir)
            assert authorizer.is_authorized(test_dir / "subdir")

    def test_authorize_persist(self):
        """测试持久化授权"""
        authorizer = PathAuthorizer()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # 持久化授权
            result = authorizer.authorize(test_dir, persist=True)
            assert result is True

            # 检查持久化列表
            persistent = authorizer.get_persistent_authorizations()
            assert test_dir in persistent

    def test_dangerous_path_rejected(self):
        """测试危险路径被拒绝"""
        authorizer = PathAuthorizer()

        # ~/.ssh 是危险路径
        ssh_dir = Path.home() / ".ssh"
        result = authorizer.authorize(ssh_dir)
        assert result is False

        # 检查危险路径
        assert authorizer.is_dangerous(ssh_dir)

    def test_is_authorized(self):
        """测试授权检查"""
        authorizer = PathAuthorizer()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # 未授权
            assert authorizer.is_authorized(test_dir) is False

            # 授权后
            authorizer.authorize(test_dir)
            assert authorizer.is_authorized(test_dir) is True

    def test_revoke_session_authorization(self):
        """测试撤销会话授权"""
        authorizer = PathAuthorizer()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # 授权
            authorizer.authorize(test_dir)
            assert authorizer.is_authorized(test_dir)

            # 撤销
            authorizer.revoke_session_authorization(test_dir)
            assert authorizer.is_authorized(test_dir) is False

    def test_clear_session_authorizations(self):
        """测试清除所有会话授权"""
        authorizer = PathAuthorizer()

        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                # 授权两个目录
                authorizer.authorize(Path(tmpdir1))
                authorizer.authorize(Path(tmpdir2))

                # 清除
                authorizer.clear_session_authorizations()

                assert len(authorizer.get_session_authorizations()) == 0

    def test_get_authorizer_function(self):
        """测试 get_authorizer 函数"""
        authorizer = get_authorizer()
        assert isinstance(authorizer, PathAuthorizer)


class TestAuthorizationRequiredError:
    """AuthorizationRequiredError 测试类"""

    def test_error_creation(self):
        """测试异常创建"""
        path = Path("/tmp/test/file.txt")
        suggested_dir = Path("/tmp/test")

        error = AuthorizationRequiredError(
            path=path,
            suggested_dir=suggested_dir,
        )

        assert error.path == path
        assert error.suggested_dir == suggested_dir
        assert "需要授权" in str(error)

    def test_custom_message(self):
        """测试自定义消息"""
        error = AuthorizationRequiredError(
            path=Path("/tmp/test"),
            suggested_dir=Path("/tmp"),
            message="自定义消息",
        )

        assert error.message == "自定义消息"


class TestPathAuthorizerThreadSafety:
    """PathAuthorizer 线程安全测试"""

    def setup_method(self):
        """每个测试前重置单例"""
        PathAuthorizer._instance = None

    def test_concurrent_authorization(self):
        """测试并发授权"""
        import threading

        authorizer = PathAuthorizer()
        results = []
        errors = []

        def authorize(tmpdir):
            try:
                result = authorizer.authorize(Path(tmpdir))
                results.append(result)
            except Exception as e:
                errors.append(e)

        threads = []
        with tempfile.TemporaryDirectory() as tmpdir:
            for _ in range(10):
                t = threading.Thread(target=authorize, args=(tmpdir,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

        assert len(errors) == 0
        assert all(results)
