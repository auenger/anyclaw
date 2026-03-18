"""Provider 基类定义"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class ProviderInfo:
    """Provider 信息"""
    name: str
    display_name: str
    description: str
    default_model: str
    supported_models: list[str] = field(default_factory=list)
    api_key_env: str = ""
    endpoints: Dict[str, str] = field(default_factory=dict)


class Provider(ABC):
    """Provider 抽象基类"""

    def __init__(self, api_key: str = "", endpoint: str = "default", **kwargs):
        """
        初始化 Provider

        Args:
            api_key: API Key
            endpoint: endpoint 名称
            **kwargs: 额外配置
        """
        self.api_key = api_key
        self.endpoint = endpoint
        self.config = kwargs

    @property
    @abstractmethod
    def info(self) -> ProviderInfo:
        """获取 Provider 信息"""
        pass

    @abstractmethod
    def get_base_url(self) -> Optional[str]:
        """
        获取 API base URL

        Returns:
            base URL 或 None（使用默认）
        """
        pass

    @abstractmethod
    def get_model_prefix(self) -> str:
        """
        获取模型前缀

        Returns:
            模型前缀，如 "zai/"、"openai/"
        """
        pass

    def get_api_key(self) -> str:
        """获取 API Key"""
        return self.api_key

    def get_model_name(self, model: str) -> str:
        """
        获取完整模型名称

        Args:
            model: 模型名称（可能有前缀）

        Returns:
            完整模型名称
        """
        prefix = self.get_model_prefix()
        if model.startswith(prefix):
            return model
        return f"{prefix}{model}"

    def get_completion_kwargs(self, model: str) -> Dict[str, Any]:
        """
        获取 litellm acompletion 所需的额外参数

        Args:
            model: 模型名称

        Returns:
            参数字典
        """
        kwargs: Dict[str, Any] = {}

        if self.api_key:
            kwargs["api_key"] = self.api_key

        base_url = self.get_base_url()
        if base_url:
            kwargs["api_base"] = base_url

        return kwargs

    def is_configured(self) -> bool:
        """检查 Provider 是否已配置"""
        return bool(self.api_key)
