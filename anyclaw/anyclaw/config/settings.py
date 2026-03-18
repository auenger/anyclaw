"""AnyClaw 配置系统"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # API Keys
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
        default="auto",
        description="ZAI endpoint: auto/global/cn/coding-global/coding-cn"
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

    # 技能配置
    skills_dir: str = Field(
        default="anyclaw/skills/builtin",
        description="技能目录"
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
    stream_buffer_size: int = Field(
        default=10,
        ge=1,
        description="流式输出缓冲块数"
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


# 全局配置实例
settings = Settings()
