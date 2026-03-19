"""配置文件加载器

支持从 JSON 配置文件加载设置。
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    """Provider 配置"""

    api_key: str = ""
    api_base: Optional[str] = None
    extra_headers: Optional[Dict[str, str]] = None


class LLMConfig(BaseModel):
    """LLM 配置"""

    model: str = "gpt-4o-mini"
    provider: str = "openai"
    max_tokens: int = 2000
    temperature: float = 0.7
    context_window_tokens: int = 128000


class ProvidersConfig(BaseModel):
    """所有 Provider 配置"""

    openai: ProviderConfig = Field(default_factory=ProviderConfig)
    anthropic: ProviderConfig = Field(default_factory=ProviderConfig)
    zai: ProviderConfig = Field(default_factory=ProviderConfig)
    deepseek: ProviderConfig = Field(default_factory=ProviderConfig)
    openrouter: ProviderConfig = Field(default_factory=ProviderConfig)
    ollama: ProviderConfig = Field(default_factory=ProviderConfig)
    custom: ProviderConfig = Field(default_factory=ProviderConfig)


class AgentConfig(BaseModel):
    """Agent 配置"""

    name: str = "AnyClaw"
    workspace: str = "~/.anyclaw/workspace"


class Config(BaseModel):
    """根配置"""

    agent: AgentConfig = Field(default_factory=AgentConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    providers: ProvidersConfig = Field(default_factory=ProvidersConfig)


# 配置文件路径
def get_config_path() -> Path:
    """获取配置文件路径"""
    return Path.home() / ".anyclaw" / "config.json"


def get_config_dir() -> Path:
    """获取配置目录"""
    path = Path.home() / ".anyclaw"
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_config(config_path: Optional[Path] = None) -> Config:
    """加载配置文件

    Args:
        config_path: 配置文件路径，默认 ~/.anyclaw/config.json

    Returns:
        Config 对象
    """
    path = config_path or get_config_path()

    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return Config.model_validate(data)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Failed to load config from {path}: {e}")
            print("Using default configuration.")

    return Config()


def save_config(config: Config, config_path: Optional[Path] = None) -> None:
    """保存配置到文件

    Args:
        config: Config 对象
        config_path: 配置文件路径
    """
    path = config_path or get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    data = config.model_dump(by_alias=True, exclude_none=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# 全局配置实例
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config() -> Config:
    """重新加载配置"""
    global _config
    _config = load_config()
    return _config


def get_api_key(provider: Optional[str] = None, model: Optional[str] = None) -> Optional[str]:
    """获取 API Key

    优先级：
    1. 环境变量 (OPENAI_API_KEY, ANTHROPIC_API_KEY 等)
    2. 配置文件中的设置

    Args:
        provider: Provider 名称
        model: 模型名称（用于自动检测 provider）

    Returns:
        API Key 或 None
    """
    import os

    config = get_config()

    # 自动检测 provider
    if provider is None and model:
        provider = detect_provider(model)

    provider = provider or config.llm.provider

    # 先检查环境变量
    env_key_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "zai": "ZAI_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }

    if provider in env_key_map:
        env_key = os.environ.get(env_key_map[provider])
        if env_key:
            return env_key

    # 从配置文件获取
    provider_config = getattr(config.providers, provider, None)
    if provider_config and provider_config.api_key:
        return provider_config.api_key

    return None


def detect_provider(model: str) -> str:
    """根据模型名称检测 provider

    Args:
        model: 模型名称

    Returns:
        Provider 名称
    """
    model_lower = model.lower()

    if model_lower.startswith("claude") or "anthropic" in model_lower:
        return "anthropic"
    if model_lower.startswith("gpt") or "openai" in model_lower:
        return "openai"
    if model_lower.startswith("zai/") or "zhipu" in model_lower or "glm" in model_lower:
        return "zai"
    if "deepseek" in model_lower:
        return "deepseek"
    if "openrouter" in model_lower:
        return "openrouter"
    if "ollama" in model_lower or model_lower.startswith("llama"):
        return "ollama"

    # 默认返回配置中的 provider
    return get_config().llm.provider
