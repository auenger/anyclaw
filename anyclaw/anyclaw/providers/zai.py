"""ZAI Provider 实现"""
import logging
from typing import Optional, Dict, Any

from .base import Provider, ProviderInfo

logger = logging.getLogger(__name__)


# ZAI Endpoint 映射
ZAI_ENDPOINTS = {
    "coding": "https://open.bigmodel.cn/api/coding/paas/v4",  # GLM Coding Plan (默认)
    "global": "https://api.z.ai/api/paas/v4",
    "cn": "https://open.bigmodel.cn/api/paas/v4",
    "coding-global": "https://api.z.ai/api/paas/v4",
    "coding-cn": "https://open.bigmodel.cn/api/paas/v4",
}

# 默认 endpoint
ZAI_DEFAULT_ENDPOINT = "coding"

# 默认模型映射
ZAI_DEFAULT_MODELS = {
    "coding": "glm-4.7",
    "global": "glm-5",
    "cn": "glm-5",
    "coding-global": "glm-5",
    "coding-cn": "glm-5",
}

# 支持的模型列表
ZAI_SUPPORTED_MODELS = [
    "glm-5",
    "glm-4.7",
    "glm-4-plus",
    "glm-4-flash",
    "glm-4-air",
    "glm-4-airx",
    "glm-4-long",
    "glm-4v-plus",
    "glm-4v-flash",
]


class ZAIProvider(Provider):
    """ZAI Provider 实现"""

    def __init__(
        self,
        api_key: str = "",
        endpoint: str = "auto",
        base_url: Optional[str] = None,
        auto_detect: bool = True,
    ):
        """
        初始化 ZAI Provider

        Args:
            api_key: ZAI API Key
            endpoint: endpoint 名称 (auto/global/cn/coding-global/coding-cn)
            base_url: 自定义 base URL（覆盖 endpoint 设置）
            auto_detect: 是否自动检测 endpoint（当 endpoint="auto" 时）
        """
        super().__init__(api_key=api_key, endpoint=endpoint)
        self._custom_base_url = base_url
        self._auto_detect = auto_detect
        self._detected_endpoint: Optional[str] = None

        # 如果是 auto 模式且有 API Key，尝试自动检测
        if endpoint == "auto" and api_key and auto_detect:
            self._do_auto_detect()

    @property
    def info(self) -> ProviderInfo:
        """获取 Provider 信息"""
        return ProviderInfo(
            name="zai",
            display_name="Z.AI / GLM",
            description="Z.AI GLM 系列模型，支持全球和中国区 endpoint",
            default_model="glm-5",
            supported_models=ZAI_SUPPORTED_MODELS,
            api_key_env="ZAI_API_KEY",
            endpoints=ZAI_ENDPOINTS,
        )

    def get_model_prefix(self) -> str:
        """获取模型前缀"""
        return "zai/"

    def get_base_url(self) -> Optional[str]:
        """
        获取 API base URL

        Returns:
            base URL 或 None
        """
        # 优先使用自定义 base URL
        if self._custom_base_url:
            return self._custom_base_url

        # 获取有效 endpoint
        effective_endpoint = self._get_effective_endpoint()

        # 返回对应的 base URL
        return ZAI_ENDPOINTS.get(effective_endpoint)

    def _get_effective_endpoint(self) -> str:
        """获取有效的 endpoint"""
        if self.endpoint == "auto":
            if self._detected_endpoint:
                return self._detected_endpoint
            # 默认使用 coding (GLM Coding Plan)
            return ZAI_DEFAULT_ENDPOINT
        return self.endpoint

    def _do_auto_detect(self) -> None:
        """执行自动检测"""
        try:
            from .zai_detect import detect_zai_endpoint
            result = detect_zai_endpoint(self.api_key)
            self._detected_endpoint = result.get("endpoint", ZAI_DEFAULT_ENDPOINT)
            logger.info(f"ZAI endpoint auto-detected: {self._detected_endpoint}")
        except Exception as e:
            logger.warning(f"ZAI endpoint auto-detect failed: {e}")
            self._detected_endpoint = ZAI_DEFAULT_ENDPOINT

    def get_default_model(self) -> str:
        """获取默认模型"""
        effective_endpoint = self._get_effective_endpoint()
        return ZAI_DEFAULT_MODELS.get(effective_endpoint, "glm-4.7")

    def get_completion_kwargs(self, model: str) -> Dict[str, Any]:
        """获取 litellm acompletion 所需的额外参数

        ZAI 使用 OpenAI 兼容接口，所以使用 openai/ 前缀 + 自定义 api_base
        """
        kwargs = super().get_completion_kwargs(model)

        # 处理模型名：使用 openai/ 前缀（OpenAI 兼容接口）
        if model.startswith("openai/"):
            # 已经是正确格式，保持不变
            pass
        elif "/" not in model:
            # 没有 provider 前缀，添加 openai/ 前缀
            kwargs["_model_override"] = f"openai/{model}"

        return kwargs

    def is_coding_plan(self) -> bool:
        """检查是否是 Coding Plan endpoint"""
        effective_endpoint = self._get_effective_endpoint()
        return effective_endpoint in ("coding-global", "coding-cn")

    def get_status(self) -> Dict[str, Any]:
        """获取 Provider 状态"""
        return {
            "configured": self.is_configured(),
            "endpoint": self._get_effective_endpoint(),
            "base_url": self.get_base_url(),
            "default_model": self.get_default_model(),
            "is_coding_plan": self.is_coding_plan(),
            "api_key_set": bool(self.api_key),
        }


# 全局单例
_zai_provider: Optional[ZAIProvider] = None


def get_zai_provider() -> ZAIProvider:
    """获取 ZAI Provider 单例"""
    global _zai_provider

    if _zai_provider is None:
        from anyclaw.config.settings import settings
        _zai_provider = ZAIProvider(
            api_key=settings.zai_api_key,
            endpoint=settings.zai_endpoint,
            base_url=settings.zai_base_url or None,
        )

    return _zai_provider


def reset_zai_provider() -> None:
    """重置 ZAI Provider 单例（用于测试）"""
    global _zai_provider
    _zai_provider = None
