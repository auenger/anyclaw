"""凭证管理系统测试

测试覆盖：
- 凭证加密存储和读取
- 脱敏功能
- 凭证验证
- 日志过滤器
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from anyclaw.security.credentials import (
    CredentialManager,
    CredentialMetadata,
    SensitiveDataFilter,
    mask_sensitive,
    get_credential_manager,
)


class TestCredentialManager:
    """CredentialManager 测试"""

    @pytest.fixture
    def temp_config_dir(self):
        """创建临时配置目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self, temp_config_dir):
        """创建 CredentialManager 实例"""
        return CredentialManager(config_dir=temp_config_dir)

    def test_store_and_retrieve(self, manager):
        """测试加密存储和读取"""
        # 存储
        manager.store("test_key", "sk-test12345678901234567890")

        # 读取
        value = manager.retrieve("test_key")
        assert value == "sk-test12345678901234567890"

    def test_store_with_expiration(self, manager):
        """测试带过期时间的存储"""
        manager.store("expiring_key", "value123", expires_days=14)

        # 检查过期状态
        expiring, days = manager.check_expiration("expiring_key")
        assert not expiring  # 14 天不应该过期（警告阈值是 7 天）
        assert days >= 13  # 允许 +/- 1 天的误差

    def test_delete_credential(self, manager):
        """测试删除凭证"""
        manager.store("to_delete", "value")
        assert manager.retrieve("to_delete") == "value"

        # 删除
        result = manager.delete("to_delete")
        assert result is True
        assert manager.retrieve("to_delete") is None

    def test_delete_nonexistent(self, manager):
        """测试删除不存在的凭证"""
        result = manager.delete("nonexistent")
        assert result is False

    def test_list_credentials(self, manager):
        """测试列出凭证"""
        manager.store("key1", "value1")
        manager.store("key2", "value2")

        keys = manager.list_credentials()
        assert "key1" in keys
        assert "key2" in keys

    def test_retrieve_nonexistent(self, manager):
        """测试读取不存在的凭证"""
        value = manager.retrieve("nonexistent")
        assert value is None


class TestMasking:
    """脱敏功能测试"""

    @pytest.fixture
    def manager(self):
        """创建 CredentialManager 实例"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield CredentialManager(config_dir=Path(tmpdir))

    def test_mask_openai_key(self, manager):
        """测试 OpenAI API Key 脱敏"""
        text = "Using API Key: sk-proj-abcdefghijklmnopqrstuvwxyz123456"
        masked = manager.mask(text)
        assert "sk-proj-***" in masked
        assert "abcdefghijklmnopqrstuvwxyz123456" not in masked

    def test_mask_simple_openai_key(self, manager):
        """测试简单 OpenAI API Key 脱敏"""
        text = "Key: sk-abcdefghijklmnopqrstuvwxyz1234"
        masked = manager.mask(text)
        assert "sk-***" in masked
        assert "abcdefghijklmnopqrstuvwxyz1234" not in masked

    def test_mask_github_pat(self, manager):
        """测试 GitHub PAT 脱敏"""
        text = "Token: ghp_abcdefghijklmnopqrstuvwxyz1234567890"
        masked = manager.mask(text)
        assert "ghp_***" in masked
        assert "abcdefghijklmnopqrstuvwxyz1234567890" not in masked

    def test_mask_aws_key(self, manager):
        """测试 AWS Access Key 脱敏"""
        text = "AWS Key: AKIAIOSFODNN7EXAMPLE"
        masked = manager.mask(text)
        assert "AKI***" in masked
        assert "AKIAIOSFODNN7EXAMPLE" not in masked

    def test_mask_anthropic_key(self, manager):
        """测试 Anthropic API Key 脱敏"""
        text = "Anthropic Key: sk-ant-api03-abcdefghijklmnopqrstuvwxyz"
        masked = manager.mask(text)
        assert "sk-ant-***" in masked

    def test_mask_value_short(self, manager):
        """测试短值脱敏"""
        assert manager.mask_value("") == "***"
        assert manager.mask_value("abc") == "***"

    def test_mask_value_normal(self, manager):
        """测试正常值脱敏"""
        masked = manager.mask_value("sk-12345678901234567890", visible_chars=4)
        assert masked == "***7890"

    def test_is_sensitive_field(self, manager):
        """测试敏感字段检测"""
        assert manager.is_sensitive_field("api_key") is True
        assert manager.is_sensitive_field("API_KEY") is True
        assert manager.is_sensitive_field("secret_key") is True
        assert manager.is_sensitive_field("access_token") is True
        assert manager.is_sensitive_field("password") is True
        assert manager.is_sensitive_field("name") is False
        assert manager.is_sensitive_field("model") is False


class TestValidation:
    """凭证验证测试"""

    @pytest.fixture
    def manager(self):
        """创建 CredentialManager 实例"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield CredentialManager(config_dir=Path(tmpdir))

    def test_validate_openai_key_valid(self, manager):
        """测试有效的 OpenAI Key 格式"""
        valid, msg = manager.validate_format("openai", "sk-abcdefghijklmnopqrstuvwxyz1234")
        assert valid is True
        assert msg is None

    def test_validate_openai_key_invalid(self, manager):
        """测试无效的 OpenAI Key 格式"""
        valid, msg = manager.validate_format("openai", "invalid-key")
        assert valid is False
        assert "OpenAI" in msg

    def test_validate_anthropic_key_valid(self, manager):
        """测试有效的 Anthropic Key 格式"""
        valid, msg = manager.validate_format(
            "anthropic", "sk-ant-api03-abcdefghijklmnopqrstuvwxyz"
        )
        assert valid is True

    def test_validate_github_pat_valid(self, manager):
        """测试有效的 GitHub PAT 格式"""
        valid, msg = manager.validate_format(
            "github", "ghp_abcdefghijklmnopqrstuvwxyz1234567890"
        )
        assert valid is True

    def test_validate_unknown_provider(self, manager):
        """测试未知 provider 不验证"""
        valid, msg = manager.validate_format("unknown", "any-key")
        assert valid is True
        assert msg is None


class TestExpiration:
    """过期检测测试"""

    @pytest.fixture
    def manager(self):
        """创建 CredentialManager 实例"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield CredentialManager(config_dir=Path(tmpdir))

    def test_check_expiration_not_set(self, manager):
        """测试未设置过期的凭证"""
        manager.store("no_expiry", "value")
        expiring, days = manager.check_expiration("no_expiry")
        assert expiring is False
        assert days is None

    def test_check_expiration_future(self, manager):
        """测试未来过期的凭证"""
        manager.store("future_expiry", "value", expires_days=30)
        expiring, days = manager.check_expiration("future_expiry")
        assert expiring is False  # 30 天不会触发警告
        assert days >= 29  # 允许 +/- 1 天的误差

    def test_get_expiration_warnings(self, manager):
        """测试获取过期警告"""
        manager.store("expiring_soon", "value", expires_days=3)
        manager.store("not_expiring", "value", expires_days=30)

        warnings = manager.get_expiration_warnings()
        assert len(warnings) == 1
        assert warnings[0][0] == "expiring_soon"
        assert warnings[0][1] >= 2  # 允许 +/- 1 天的误差


class TestSensitiveDataFilter:
    """日志过滤器测试"""

    @pytest.fixture
    def filter_instance(self):
        """创建过滤器实例"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CredentialManager(config_dir=Path(tmpdir))
            return SensitiveDataFilter(manager)

    def test_filter_message(self, filter_instance):
        """测试过滤日志消息"""
        class MockRecord:
            msg = "Using API Key: sk-abcdefghijklmnopqrstuvwxyz1234"
            args = None

        record = MockRecord()
        result = filter_instance.filter(record)

        assert result is True
        assert "sk-***" in record.msg
        assert "abcdefghijklmnopqrstuvwxyz1234" not in record.msg

    def test_filter_dict_args(self, filter_instance):
        """测试过滤字典参数"""
        class MockRecord:
            msg = "Config: %(key)s"
            args = {"key": "sk-abcdefghijklmnopqrstuvwxyz1234"}

        record = MockRecord()
        filter_instance.filter(record)

        assert "sk-***" in record.args["key"]

    def test_filter_tuple_args(self, filter_instance):
        """测试过滤元组参数"""
        class MockRecord:
            msg = "Keys: %s, %s"
            args = ("sk-abcdefghijklmnopqrstuvwxyz1234", "normal_value")

        record = MockRecord()
        filter_instance.filter(record)

        assert "sk-***" in record.args[0]
        assert record.args[1] == "normal_value"


class TestConvenienceFunctions:
    """便捷函数测试"""

    def test_mask_sensitive(self):
        """测试 mask_sensitive 便捷函数"""
        text = "API Key: sk-abcdefghijklmnopqrstuvwxyz1234"
        masked = mask_sensitive(text)
        assert "sk-***" in masked

    def test_get_credential_manager_singleton(self):
        """测试全局单例"""
        manager1 = get_credential_manager()
        manager2 = get_credential_manager()
        assert manager1 is manager2


class TestCredentialMetadata:
    """元数据测试"""

    def test_metadata_creation(self):
        """测试元数据创建"""
        meta = CredentialMetadata(
            key_name="test_key",
            created_at="2024-01-01T00:00:00",
            expires_at="2024-12-31T23:59:59",
        )
        assert meta.key_name == "test_key"
        assert meta.created_at == "2024-01-01T00:00:00"
        assert meta.expires_at == "2024-12-31T23:59:59"


class TestEdgeCases:
    """边缘情况测试"""

    @pytest.fixture
    def manager(self):
        """创建 CredentialManager 实例"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield CredentialManager(config_dir=Path(tmpdir))

    def test_empty_value(self, manager):
        """测试空值"""
        manager.store("empty", "")
        value = manager.retrieve("empty")
        assert value == ""

    def test_unicode_value(self, manager):
        """测试 Unicode 值"""
        manager.store("unicode", "中文测试🔑")
        value = manager.retrieve("unicode")
        assert value == "中文测试🔑"

    def test_very_long_value(self, manager):
        """测试超长值"""
        long_value = "sk-" + "a" * 1000
        manager.store("long", long_value)
        value = manager.retrieve("long")
        assert value == long_value

    def test_special_characters(self, manager):
        """测试特殊字符"""
        special = "key-with_special.chars!@#$%^&*()"
        manager.store("special", special)
        value = manager.retrieve("special")
        assert value == special

    def test_mask_preserves_structure(self, manager):
        """测试脱敏保留文本结构"""
        text = "Config: api_key=sk-abcdefghijklmnopqrstuvwxyz1234, model=gpt-4"
        masked = manager.mask(text)
        # 应该保留非敏感部分
        assert "Config:" in masked
        assert "model=gpt-4" in masked
