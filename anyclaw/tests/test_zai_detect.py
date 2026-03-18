"""ZAI Endpoint 检测测试"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from anyclaw.providers.zai_detect import (
    detect_zai_endpoint,
    detect_zai_endpoint_async,
    list_available_endpoints,
    get_endpoint_info,
    ZAI_ENDPOINTS_CONFIG,
)


class TestZAIDetect:
    """ZAI Endpoint 检测测试"""

    def test_list_available_endpoints(self):
        """测试列出可用 endpoints"""
        endpoints = list_available_endpoints()

        assert len(endpoints) == 4
        endpoint_names = [e["name"] for e in endpoints]
        assert "coding-global" in endpoint_names
        assert "coding-cn" in endpoint_names
        assert "global" in endpoint_names
        assert "cn" in endpoint_names

    def test_get_endpoint_info(self):
        """测试获取 endpoint 信息"""
        info = get_endpoint_info("coding-global")

        assert info is not None
        assert info["default_model"] == "glm-5"
        assert "base_url" in info

    def test_get_endpoint_info_unknown(self):
        """测试获取未知 endpoint 信息"""
        info = get_endpoint_info("unknown")
        assert info is None

    def test_detect_zai_endpoint_no_key(self):
        """测试无 API Key 时的检测"""
        result = detect_zai_endpoint("")

        assert result["success"] is False
        assert result["endpoint"] == "coding-global"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_detect_zai_endpoint_async_no_key(self):
        """测试异步检测无 API Key"""
        result = await detect_zai_endpoint_async("")

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    @patch("anyclaw.providers.zai_detect.httpx.AsyncClient")
    async def test_detect_zai_endpoint_async_success(self, mock_client):
        """测试异步检测成功"""
        # Mock 响应
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_context = AsyncMock()
        mock_context.post.return_value = mock_response
        mock_context.__aenter__.return_value = mock_context
        mock_context.__aexit__.return_value = None

        mock_client.return_value = mock_context

        result = await detect_zai_endpoint_async("test-api-key")

        assert result["success"] is True
        assert result["endpoint"] == "coding-global"

    @pytest.mark.asyncio
    @patch("anyclaw.providers.zai_detect.httpx.AsyncClient")
    async def test_detect_zai_endpoint_async_auth_failed(self, mock_client):
        """测试异步检测认证失败"""
        # Mock 响应
        mock_response = MagicMock()
        mock_response.status_code = 401

        mock_context = AsyncMock()
        mock_context.post.return_value = mock_response
        mock_context.__aenter__.return_value = mock_context
        mock_context.__aexit__.return_value = None

        mock_client.return_value = mock_context

        result = await detect_zai_endpoint_async("invalid-key")

        # 所有 endpoint 都失败后返回默认值
        assert result["success"] is False
        assert "error" in result


class TestZAIEndpointsConfig:
    """ZAI Endpoint 配置测试"""

    def test_all_endpoints_have_required_fields(self):
        """测试所有 endpoint 配置都有必要字段"""
        required_fields = ["base_url", "test_endpoint", "default_model", "description"]

        for name, config in ZAI_ENDPOINTS_CONFIG.items():
            for field in required_fields:
                assert field in config, f"Endpoint {name} missing field {field}"

    def test_coding_endpoints_use_same_base_url(self):
        """测试 coding endpoints 使用相同的 base URL"""
        coding_global = ZAI_ENDPOINTS_CONFIG["coding-global"]
        coding_cn = ZAI_ENDPOINTS_CONFIG["coding-cn"]
        regular_global = ZAI_ENDPOINTS_CONFIG["global"]
        regular_cn = ZAI_ENDPOINTS_CONFIG["cn"]

        # Coding Plan 和普通 API 使用相同的 base URL
        assert coding_global["base_url"] == regular_global["base_url"]
        assert coding_cn["base_url"] == regular_cn["base_url"]
