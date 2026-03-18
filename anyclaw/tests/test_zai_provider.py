"""ZAI Provider 单元测试"""
import pytest
from unittest.mock import patch, MagicMock

from anyclaw.providers.base import Provider, ProviderInfo
from anyclaw.providers.zai import (
    ZAIProvider,
    ZAI_ENDPOINTS,
    ZAI_SUPPORTED_MODELS,
    get_zai_provider,
    reset_zai_provider,
)


class TestZAIProvider:
    """ZAI Provider 测试"""

    def setup_method(self):
        """每个测试前重置单例"""
        reset_zai_provider()

    def test_provider_info(self):
        """测试 Provider 信息"""
        provider = ZAIProvider()
        info = provider.info

        assert info.name == "zai"
        assert info.display_name == "Z.AI / GLM"
        assert info.default_model == "glm-5"
        assert "glm-5" in info.supported_models

    def test_model_prefix(self):
        """测试模型前缀"""
        provider = ZAIProvider()
        assert provider.get_model_prefix() == "zai/"

    def test_get_base_url_coding_global(self):
        """测试 coding-global endpoint"""
        provider = ZAIProvider(api_key="test-key", endpoint="coding-global")
        assert provider.get_base_url() == ZAI_ENDPOINTS["coding-global"]

    def test_get_base_url_coding_cn(self):
        """测试 coding-cn endpoint"""
        provider = ZAIProvider(api_key="test-key", endpoint="coding-cn")
        assert provider.get_base_url() == ZAI_ENDPOINTS["coding-cn"]

    def test_get_base_url_global(self):
        """测试 global endpoint"""
        provider = ZAIProvider(api_key="test-key", endpoint="global")
        assert provider.get_base_url() == ZAI_ENDPOINTS["global"]

    def test_get_base_url_cn(self):
        """测试 cn endpoint"""
        provider = ZAIProvider(api_key="test-key", endpoint="cn")
        assert provider.get_base_url() == ZAI_ENDPOINTS["cn"]

    def test_get_base_url_custom(self):
        """测试自定义 base URL"""
        custom_url = "https://custom.api.z.ai/v4"
        provider = ZAIProvider(
            api_key="test-key",
            endpoint="coding-global",
            base_url=custom_url
        )
        assert provider.get_base_url() == custom_url

    def test_get_base_url_auto_default(self):
        """测试 auto endpoint 默认值"""
        provider = ZAIProvider(api_key="test-key", endpoint="auto", auto_detect=False)
        # auto 模式默认使用 coding-global
        assert provider.get_base_url() == ZAI_ENDPOINTS["coding-global"]

    def test_is_configured(self):
        """测试配置检查"""
        provider_no_key = ZAIProvider()
        assert not provider_no_key.is_configured()

        provider_with_key = ZAIProvider(api_key="test-key")
        assert provider_with_key.is_configured()

    def test_is_coding_plan(self):
        """测试 Coding Plan 检测"""
        coding_global = ZAIProvider(api_key="test-key", endpoint="coding-global")
        assert coding_global.is_coding_plan()

        coding_cn = ZAIProvider(api_key="test-key", endpoint="coding-cn")
        assert coding_cn.is_coding_plan()

        regular = ZAIProvider(api_key="test-key", endpoint="global")
        assert not regular.is_coding_plan()

    def test_get_default_model(self):
        """测试默认模型"""
        provider = ZAIProvider(api_key="test-key", endpoint="coding-global")
        assert provider.get_default_model() == "glm-5"

    def test_get_completion_kwargs(self):
        """测试 litellm 调用参数"""
        provider = ZAIProvider(api_key="test-key", endpoint="coding-global")
        kwargs = provider.get_completion_kwargs("glm-5")

        assert "api_key" in kwargs
        assert kwargs["api_key"] == "test-key"
        assert "api_base" in kwargs

    def test_get_status(self):
        """测试状态获取"""
        provider = ZAIProvider(api_key="test-key", endpoint="coding-global")
        status = provider.get_status()

        assert status["configured"] is True
        assert status["endpoint"] == "coding-global"
        assert status["is_coding_plan"] is True
        assert status["api_key_set"] is True


class TestZAIProviderSingleton:
    """ZAI Provider 单例测试"""

    def setup_method(self):
        """每个测试前重置单例"""
        reset_zai_provider()

    def test_get_zai_provider_singleton(self):
        """测试单例模式"""
        # 直接创建 provider 测试单例逻辑
        from anyclaw.providers.zai import _zai_provider

        # 重置后应该为 None
        assert _zai_provider is None

        # 手动设置单例
        provider1 = ZAIProvider(api_key="test-key", endpoint="coding-global")
        from anyclaw.providers import zai
        zai._zai_provider = provider1

        provider2 = get_zai_provider()
        assert provider1 is provider2

        # 清理
        reset_zai_provider()

    def test_reset_zai_provider(self):
        """测试重置单例"""
        from anyclaw.providers.zai import _zai_provider

        # 重置后应该为 None
        reset_zai_provider()
        from anyclaw.providers import zai
        assert zai._zai_provider is None


class TestZAIEndpoints:
    """ZAI Endpoint 测试"""

    def test_all_endpoints_defined(self):
        """测试所有 endpoint 都已定义"""
        expected_endpoints = ["global", "cn", "coding-global", "coding-cn"]
        for endpoint in expected_endpoints:
            assert endpoint in ZAI_ENDPOINTS
            assert ZAI_ENDPOINTS[endpoint].startswith("https://")

    def test_supported_models_list(self):
        """测试支持的模型列表"""
        assert "glm-5" in ZAI_SUPPORTED_MODELS
        assert "glm-4.7" in ZAI_SUPPORTED_MODELS
        assert len(ZAI_SUPPORTED_MODELS) > 0
