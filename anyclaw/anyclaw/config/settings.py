"""AnyClaw 配置系统

支持从多个来源加载配置：
1. 环境变量 (.env 文件)
2. JSON 配置文件 (~/.anyclaw/config.json)
3. 默认值
"""

from pathlib import Path
from typing import Dict, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from anyclaw.tools.mcp.config import MCPServerConfig

# 获取包内技能目录的绝对路径
_BUILTIN_SKILLS_DIR = str(Path(__file__).parent.parent / "skills" / "builtin")
_MANAGED_SKILLS_DIR = str(Path.home() / ".anyclaw" / "managed-skills")
_WORKSPACE_SKILLS_DIR = str(Path.home() / ".anyclaw" / "workspace" / "skills")


class Settings(BaseSettings):
    """AnyClaw 配置"""

    # Agent 配置
    agent_name: str = Field(
        default="AnyClaw",
        description="Agent 显示名称"
    )
    agent_role: str = Field(
        default="You are a helpful AI assistant named {name}.",
        description="Agent 系统提示词"
    )

    # LLM 配置
    llm_provider: str = Field(
        default="openai",
        description="LLM 提供商"
    )
    llm_model: str = Field(
        default="gpt-4o-mini",
        description="LLM 模型"
    )
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="LLM 温度参数"
    )
    llm_max_tokens: int = Field(
        default=2000,
        ge=1,
        description="LLM 最大生成分数"
    )
    llm_timeout: int = Field(
        default=60,
        ge=1,
        description="LLM 请求超时时间（秒）"
    )

    # Tool Calling 配置
    tool_timeout: int = Field(
        default=60,
        ge=1,
        description="Tool 执行超时时间（秒）"
    )
    tool_max_iterations: int = Field(
        default=10,
        ge=1,
        description="Tool Calling 最大迭代次数"
    )

    # API Keys（优先从配置文件读取）
    openai_api_key: str = Field(
        default="",
        description="OpenAI API Key"
    )
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API Key"
    )

    # ZAI Provider 配置
    zai_api_key: str = Field(
        default="",
        description="ZAI API Key"
    )
    zai_endpoint: str = Field(
        default="coding",
        description="ZAI endpoint: coding/global/cn (默认使用 coding 即 GLM Coding Plan)"
    )
    zai_base_url: str = Field(
        default="",
        description="自定义 ZAI base URL (覆盖 endpoint 设置)"
    )

    # CLI 配置
    cli_prompt: str = Field(
        default="You: ",
        description="CLI 输入提示符"
    )

    # 技能配置（使用包内绝对路径）
    skills_dir: str = Field(
        default=_BUILTIN_SKILLS_DIR,
        description="技能目录（向后兼容）"
    )

    # 多目录技能配置
    skills_dirs: List[str] = Field(
        default_factory=lambda: [_BUILTIN_SKILLS_DIR],
        description="多个技能目录（按优先级顺序）"
    )
    skills_managed_dir: str = Field(
        default=_MANAGED_SKILLS_DIR,
        description="管理的技能目录（用户安装）"
    )
    skills_workspace_dir: str = Field(
        default=_WORKSPACE_SKILLS_DIR,
        description="工作空间技能目录（最高优先级）"
    )

    # 工作空间
    workspace_dir: str = Field(
        default="workspace",
        description="工作空间目录"
    )

    # Workspace 配置
    workspace: str = Field(
        default="~/.anyclaw/workspace",
        description="工作区路径"
    )
    skip_bootstrap: bool = Field(
        default=False,
        description="跳过引导文件创建"
    )
    bootstrap_max_chars: int = Field(
        default=20000,
        ge=1000,
        description="单个引导文件最大字符数"
    )
    bootstrap_total_max_chars: int = Field(
        default=150000,
        ge=10000,
        description="引导文件总最大字符数"
    )

    # Token 管理配置
    token_soft_limit: int = Field(
        default=100000,
        ge=1000,
        description="Token 软限制（触发警告）"
    )
    token_hard_limit: int = Field(
        default=200000,
        ge=1000,
        description="Token 硬限制（阻止输入）"
    )
    token_warning_threshold: float = Field(
        default=0.8,
        ge=0.5,
        le=1.0,
        description="Token 警告阈值（相对于软限制）"
    )
    token_warning_enabled: bool = Field(
        default=True,
        description="是否启用 token 警告"
    )

    # Persona 人设配置
    persona_enabled: bool = Field(
        default=True,
        description="是否启用人设系统"
    )
    persona_max_chars: int = Field(
        default=10000,
        ge=1000,
        description="单个人设文件最大字符数"
    )

    # 压缩配置
    compress_enabled: bool = Field(
        default=True,
        description="是否启用自动压缩"
    )
    compress_threshold: int = Field(
        default=10,
        ge=2,
        description="触发压缩的消息数阈值"
    )
    compress_keep_recent: int = Field(
        default=5,
        ge=1,
        description="压缩时保留的最近消息数"
    )
    compress_strategy: str = Field(
        default="truncate",
        description="压缩策略: summary/truncate/key_points"
    )

    # 滑动窗口配置
    window_enabled: bool = Field(
        default=True,
        description="是否启用滑动窗口"
    )
    window_size: int = Field(
        default=20,
        ge=5,
        description="滑动窗口大小"
    )

    # 检查点配置
    checkpoint_dir: str = Field(
        default="~/.anyclaw/checkpoints",
        description="检查点存储目录"
    )

    # 记忆系统配置
    memory_enabled: bool = Field(
        default=True,
        description="是否启用记忆系统"
    )
    memory_max_chars: int = Field(
        default=10000,
        ge=1000,
        description="长期记忆最大字符数"
    )
    memory_daily_load_days: int = Field(
        default=2,
        ge=1,
        le=30,
        description="加载最近几天的日志"
    )
    memory_auto_update: bool = Field(
        default=False,
        description="是否自动更新记忆（无需确认）"
    )

    # 流式输出配置
    stream_enabled: bool = Field(
        default=True,
        description="是否启用流式输出"
    )

    # 安全配置
    restrict_to_workspace: bool = Field(
        default=True,
        description="是否限制文件写入到 workspace 内（提升安全性）"
    )

    # ExecTool 安全配置
    exec_deny_patterns: List[str] = Field(
        default_factory=list,
        description="用户自定义的命令黑名单模式（正则表达式）"
    )
    exec_allow_patterns: List[str] = Field(
        default_factory=list,
        description="用户自定义的命令白名单模式（设置后启用白名单模式）"
    )
    stream_buffer_size: int = Field(
        default=10,
        ge=1,
        description="流式输出缓冲块数"
    )

    # MCP Server 配置
    mcp_servers: Dict[str, MCPServerConfig] = Field(
        default_factory=dict,
        description="MCP Server 配置字典"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return self.agent_role.format(name=self.agent_name)

    def get_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        """获取 API Key

        优先级：
        1. 环境变量
        2. 配置文件
        3. 当前 settings 中的值

        Args:
            provider: Provider 名称，默认使用当前配置的 provider

        Returns:
            API Key 或 None
        """
        import os

        provider = provider or self.llm_provider

        # 环境变量映射
        env_key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "zai": "ZAI_API_KEY",
        }

        # 1. 先检查环境变量
        if provider in env_key_map:
            env_val = os.environ.get(env_key_map[provider])
            if env_val:
                return env_val

        # 2. 尝试从配置文件加载
        try:
            from anyclaw.config.loader import get_api_key as load_api_key
            key = load_api_key(provider)
            if key:
                return key
        except Exception:
            pass

        # 3. 使用当前 settings 中的值
        key_map = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "zai": self.zai_api_key,
        }

        return key_map.get(provider, "")

    def get_effective_api_key(self) -> Optional[str]:
        """获取当前配置的有效 API Key"""
        return self.get_api_key(self.llm_provider)


def _load_from_config_file(settings: Settings) -> Settings:
    """从配置文件加载设置覆盖默认值"""
    try:
        from anyclaw.config.loader import get_config

        config = get_config()

        # 覆盖 agent 设置
        if config.agent.name:
            settings.agent_name = config.agent.name
        if config.agent.workspace:
            settings.workspace = config.agent.workspace

        # 覆盖 LLM 设置
        if config.llm.model:
            settings.llm_model = config.llm.model
        if config.llm.provider:
            settings.llm_provider = config.llm.provider
        if config.llm.max_tokens:
            settings.llm_max_tokens = config.llm.max_tokens
        if config.llm.temperature:
            settings.llm_temperature = config.llm.temperature

        # 覆盖 API Keys（只有当环境变量为空时）
        import os
        if not os.environ.get("OPENAI_API_KEY") and config.providers.openai.api_key:
            settings.openai_api_key = config.providers.openai.api_key
        if not os.environ.get("ANTHROPIC_API_KEY") and config.providers.anthropic.api_key:
            settings.anthropic_api_key = config.providers.anthropic.api_key
        if not os.environ.get("ZAI_API_KEY") and config.providers.zai.api_key:
            settings.zai_api_key = config.providers.zai.api_key

    except Exception:
        pass

    return settings


# 全局配置实例
settings = _load_from_config_file(Settings())
