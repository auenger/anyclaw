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
