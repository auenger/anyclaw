"""配置文件加载器

支持从 TOML 或 JSON 配置文件加载设置。
优先级: config.toml > config.json
"""

import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Literal, Union

from pydantic import BaseModel, Field

# TOML 支持
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


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


class CLIChannelConfig(BaseModel):
    """CLI Channel 配置"""

    enabled: bool = True
    allow_from: List[str] = Field(default_factory=lambda: ["*"])
    prompt: str = "You: "
    agent_name: str = "AnyClaw"
    interactive: bool = True  # False for serve mode (monitor only)


class FeishuChannelConfig(BaseModel):
    """飞书 Channel 配置"""

    enabled: bool = False
    app_id: str = ""
    app_secret: str = ""
    encrypt_key: str = ""
    verification_token: str = ""
    allow_from: List[str] = Field(default_factory=lambda: ["*"])


class DiscordChannelConfig(BaseModel):
    """Discord Channel 配置"""

    enabled: bool = False
    token: str = ""
    allow_from: List[str] = Field(default_factory=lambda: ["*"])
    group_policy: Literal["mention", "open"] = "mention"
    gateway_url: str = "wss://gateway.discord.gg/?v=10&encoding=json"
    intents: int = 37377  # GUILD_MESSAGES + DIRECT_MESSAGES + MESSAGE_CONTENT


class ChannelsConfig(BaseModel):
    """所有 Channel 配置"""

    cli: CLIChannelConfig = Field(default_factory=CLIChannelConfig)
    feishu: FeishuChannelConfig = Field(default_factory=FeishuChannelConfig)
    discord: DiscordChannelConfig = Field(default_factory=DiscordChannelConfig)


class MCPServerConfig(BaseModel):
    """MCP Server 配置"""

    command: str = ""
    args: List[str] = Field(default_factory=list)
    env: Optional[Dict[str, str]] = None
    tool_timeout: int = 60
    enabled_tools: List[str] = Field(default_factory=lambda: ["*"])


class SecurityConfig(BaseModel):
    """安全配置"""

    restrict_to_workspace: bool = True
    ssrf_enabled: bool = True
    exec_deny_patterns: List[str] = Field(default_factory=list)
    exec_allow_patterns: List[str] = Field(default_factory=list)


class MemoryConfig(BaseModel):
    """记忆系统配置"""

    enabled: bool = True
    max_chars: int = 10000
    daily_load_days: int = 2
    auto_update: bool = False


class CompressionConfig(BaseModel):
    """压缩配置"""

    enabled: bool = True
    threshold: int = 10
    keep_recent: int = 5
    strategy: str = "truncate"


class StreamingConfig(BaseModel):
    """流式输出配置"""

    enabled: bool = True
    buffer_size: int = 10


class ToolsConfig(BaseModel):
    """工具系统配置"""

    timeout: int = 60
    max_iterations: int = 10


class Config(BaseModel):
    """根配置"""

    agent: AgentConfig = Field(default_factory=AgentConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    providers: ProvidersConfig = Field(default_factory=ProvidersConfig)
    channels: ChannelsConfig = Field(default_factory=ChannelsConfig)
    mcp_servers: Dict[str, MCPServerConfig] = Field(default_factory=dict)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    compression: CompressionConfig = Field(default_factory=CompressionConfig)
    streaming: StreamingConfig = Field(default_factory=StreamingConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)


# 配置文件路径
def get_config_dir() -> Path:
    """获取配置目录"""
    path = Path.home() / ".anyclaw"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_path() -> Path:
    """获取配置文件路径（优先 TOML）"""
    config_dir = get_config_dir()
    toml_path = config_dir / "config.toml"
    json_path = config_dir / "config.json"

    if toml_path.exists():
        return toml_path
    return json_path


def get_template_path() -> Path:
    """获取配置模板路径"""
    return Path(__file__).parent / "config.template.toml"


def load_config(config_path: Optional[Path] = None) -> Config:
    """加载配置文件

    优先级: config.toml > config.json

    Args:
        config_path: 配置文件路径，默认自动检测

    Returns:
        Config 对象
    """
    config_dir = get_config_dir()

    # 优先尝试 TOML
    toml_path = config_dir / "config.toml"
    json_path = config_dir / "config.json"

    if config_path is None:
        if toml_path.exists():
            config_path = toml_path
        elif json_path.exists():
            config_path = json_path

    if config_path and config_path.exists():
        try:
            if config_path.suffix == ".toml":
                data = _load_toml(config_path)
            else:
                data = _load_json(config_path)

            # 处理旧版配置兼容
            data = _migrate_config(data)

            return Config.model_validate(data)
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
            print("Using default configuration.")

    return Config()


def _load_toml(path: Path) -> Dict[str, Any]:
    """加载 TOML 文件"""
    if tomllib is None:
        raise ImportError(
            "TOML support requires Python 3.11+ or tomli package. "
            "Install with: pip install tomli"
        )
    with open(path, "rb") as f:
        return tomllib.load(f)


def _load_json(path: Path) -> Dict[str, Any]:
    """加载 JSON 文件"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _migrate_config(data: Dict[str, Any]) -> Dict[str, Any]:
    """迁移旧版配置格式"""
    # 兼容旧的 channels.feishu 结构
    if "channels" in data:
        channels = data["channels"]
        # 处理 feishu
        if "feishu" in channels and isinstance(channels["feishu"], dict):
            feishu = channels["feishu"]
            # 确保有 allow_from 字段
            if "allow_from" not in feishu:
                feishu["allow_from"] = ["*"]
        # 处理 discord
        if "discord" in channels and isinstance(channels["discord"], dict):
            discord = channels["discord"]
            if "allow_from" not in discord:
                discord["allow_from"] = ["*"]

    return data


def save_config(config: Config, config_path: Optional[Path] = None, format: str = "toml") -> None:
    """保存配置到文件

    Args:
        config: Config 对象
        config_path: 配置文件路径
        format: 保存格式 (toml/json)
    """
    path = config_path or get_config_path()

    # 如果没有指定路径，根据格式选择
    if config_path is None:
        if format == "toml":
            path = get_config_dir() / "config.toml"
        else:
            path = get_config_dir() / "config.json"

    path.parent.mkdir(parents=True, exist_ok=True)

    data = config.model_dump(by_alias=True, exclude_none=True)

    if path.suffix == ".toml":
        _save_toml(data, path)
    else:
        _save_json(data, path)


def _save_toml(data: Dict[str, Any], path: Path) -> None:
    """保存为 TOML 文件"""
    try:
        import tomli_w
    except ImportError:
        # 如果没有 tomli_w，回退到 JSON
        json_path = path.with_suffix(".json")
        _save_json(data, json_path)
        print(f"Warning: tomli_w not installed, saved as JSON: {json_path}")
        return

    with open(path, "wb") as f:
        tomli_w.dump(data, f)


def _save_json(data: Dict[str, Any], path: Path) -> None:
    """保存为 JSON 文件"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def init_config(force: bool = False, format: str = "toml") -> Path:
    """初始化配置文件

    从模板创建配置文件

    Args:
        force: 是否强制覆盖
        format: 配置格式 (toml/json)

    Returns:
        配置文件路径
    """
    config_dir = get_config_dir()

    if format == "toml":
        config_path = config_dir / "config.toml"
    else:
        config_path = config_dir / "config.json"

    if config_path.exists() and not force:
        return config_path

    if format == "toml":
        # 复制模板文件
        template_path = get_template_path()
        if template_path.exists():
            import shutil
            shutil.copy(template_path, config_path)
        else:
            # 创建默认配置
            config = Config()
            save_config(config, config_path, format="toml")
    else:
        # 创建 JSON 配置
        config = Config()
        save_config(config, config_path, format="json")

    return config_path


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
