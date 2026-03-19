# AnyClaw vs nanobot - 完整对比分析

> **版本信息**
> - AnyClaw: 0.1.0-MVP
> - nanobot: 主分支 (2026-03-17)
> - 对比日期: 2026-03-20

## 📊 总览

| 维度 | AnyClaw | nanobot | 差异 |
|------|---------|---------|------|
| **项目定位** | 轻量级 AI 智能体框架 | 企业级 AI 智能体框架 | ⚠️ 功能范围差异 |
| **代码规模** | ~5,000 行 | ~15,000 行 | 🔴 nanobot 更完善 |
| **Provider 支持** | 3 (OpenAI, Anthropic, ZAI) | 15+ | 🔴 AnyClaw 缺少大量 Provider |
| **Channel 支持** | 4 (CLI, Feishu, Discord) | 12 | 🔴 AnyClaw 缺少 8 个 Channel |
| **工具数量** | 基础 6 个 | 基础 10+ | 🟡 AnyClaw 功能较少 |
| **配置系统** | Pydantic Settings | Pydantic Schema | 🟢 类似 |
| **Skills 系统** | Python + SKILL.md | SKILL.md only | 🟢 AnyClaw 更灵活 |
| **Memory 系统** | 有 | 有 | 🟢 类似 |

---

## 🏗️ 架构对比

### 目录结构

```
AnyClaw/
├── anyclaw/
│   ├── agent/          # Agent 系统
│   ├── channels/       # 交互频道
│   ├── skills/         # 技能系统
│   ├── tools/          # 工具系统
│   ├── config/         # 配置系统
│   ├── memory/         # 记忆系统
│   ├── providers/      # LLM Provider
│   ├── core/           # 核心服务
│   ├── utils/          # 工具模块
│   ├── bus/            # 消息总线
│   └── cli/            # CLI 应用
```

```
nanobot/
├── nanobot/
│   ├── agent/          # Agent 系统
│   ├── channels/       # 交互频道
│   ├── skills/         # 技能系统
│   ├── providers/      # LLM Provider
│   ├── config/         # 配置系统
│   ├── session/        # 会话管理
│   ├── heartbeat/      # 心跳服务
│   ├── cron/           # Cron 调度
│   ├── bus/            # 消息总线
│   ├── utils/          # 工具模块
│   └── cli/            # CLI 应用
```

### 差异分析

| 组件 | AnyClaw | nanobot | 影响 |
|------|---------|---------|------|
| **session/** | ❌ 没有 | ✅ 有 | 🔴 AnyClaw 缺少会话管理 |
| **heartbeat/** | ❌ 没有 | ✅ 有 | 🟡 AnyClaw 用 HEARTBEAT.md 替代 |
| **cron/** | ❌ 没有 | ✅ 有 | 🔴 AnyClaw 缺少定时任务 |
| **core/** | ✅ 有 | ❌ 没有 | ℹ️ 不同的组织方式 |
| **tools/** | 独立目录 | 在 agent/tools/ | ℹ️ 不同的组织方式 |

---

## ⚙️ 配置系统对比

### nanobot 配置结构 (config/schema.py)

```python
class Config(BaseSettings):
    agents: AgentsConfig              # Agent 配置
    channels: ChannelsConfig          # Channel 配置
    providers: ProvidersConfig        # 15+ Provider 配置
    gateway: GatewayConfig            # Gateway 服务配置
    tools: ToolsConfig               # 工具配置

class ProvidersConfig(Base):
    custom: ProviderConfig            # 自定义 Provider
    azure_openai: ProviderConfig      # Azure OpenAI
    anthropic: ProviderConfig        # Anthropic
    openai: ProviderConfig           # OpenAI
    openrouter: ProviderConfig        # OpenRouter
    deepseek: ProviderConfig         # DeepSeek
    groq: ProviderConfig             # Groq
    zhipu: ProviderConfig            # 智谱 GLM
    dashscope: ProviderConfig        # 阿里 DashScope
    vllm: ProviderConfig            # vLLM 本地
    ollama: ProviderConfig           # Ollama 本地
    gemini: ProviderConfig           # Google Gemini
    moonshot: ProviderConfig         # 月之暗面
    minimax: ProviderConfig          # MiniMax
    aihubmix: ProviderConfig         # AiHubMix
    siliconflow: ProviderConfig      # 硅基流动
    volcengine: ProviderConfig       # 火山引擎
    # ... 更多 Provider
```

### AnyClaw 配置结构 (config/settings.py)

```python
class Settings(BaseSettings):
    # Agent 配置
    agent_name: str
    agent_role: str

    # LLM 配置
    llm_provider: str
    llm_model: str
    llm_temperature: float
    llm_max_tokens: int
    llm_timeout: int

    # API Keys
    openai_api_key: str
    anthropic_api_key: str
    zai_api_key: str
    zai_endpoint: str
    zai_base_url: str

    # 技能配置
    skills_dir: str
    skills_dirs: List[str]
    skills_managed_dir: str
    skills_workspace_dir: str

    # 其他配置...
```

### 差异分析

| 配置项 | AnyClaw | nanobot | 优先级 |
|--------|---------|---------|--------|
| **Provider 支持** | 3 | 15+ | 🔴 **高优先级** |
| **自动 Provider 匹配** | 部分支持 | ✅ 完整支持 | 🟡 **高优先级** |
| **Gateway 配置** | ❌ 没有 | ✅ 有 | 🔴 **高优先级** |
| **Heartbeat 配置** | ❌ 没有 | ✅ 有 | 🟡 **中优先级** |
| **Cron 配置** | ❌ 没有 | ✅ 有 | 🔴 **高优先级** |
| **Web 代理配置** | ❌ 没有 | ✅ 有 | 🟡 **中优先级** |
| **配置验证** | 基础 | ✅ 详细 | 🟡 **中优先级** |

---

## 📡 Channel 系统对比

### nanobot 支持的 Channel (channels/)

| Channel | 文件 | 功能 | AnyClaw 支持 |
|---------|------|------|--------------|
| CLI | cli.py | 命令行交互 | ✅ |
| Discord | discord.py | Discord Bot | ✅ |
| Feishu | feishu.py | 飞书 | ✅ |
| Telegram | telegram.py | Telegram Bot | ❌ |
| WhatsApp | whatsapp.py | WhatsApp | ❌ |
| Slack | slack.py | Slack | ❌ |
| Email | email.py | 邮件 | ❌ |
| DingTalk | dingtalk.py | 钉钉 | ❌ |
| WeChat Work | wecom.py | 企业微信 | ❌ |
| Matrix | matrix.py | Matrix | ❌ |
| MoChat | mochat.py | 企业微信 | ❌ |
| QQ | qq.py | QQ | ❌ |

### AnyClaw 支持的 Channel (channels/)

| Channel | 文件 | 功能 | nanobot 支持 |
|---------|------|------|-------------|
| CLI | cli.py | 命令行交互 | ✅ |
| Discord | discord.py | Discord Bot | ✅ |
| Feishu | feishu.py | 飞书 | ✅ |

### Channel 功能差异

| 功能 | AnyClaw Discord | nanobot Discord | 差异 |
|------|----------------|----------------|------|
| **音频转写** | ❌ | ✅ Groq Whisper | 🔴 |
| **进度消息过滤** | ❌ | ✅ | 🔴 |
| **文件上传** | ✅ | ✅ | 🟢 |
| **消息分片** | ✅ | ✅ | 🟢 |
| **Typing 指示** | ✅ | ✅ | 🟢 |
| **Rate Limit 处理** | ✅ | ✅ | 🟢 |

---

## 🤖 Agent Loop 对比

### nanobot Agent Loop (agent/loop.py)

```python
class AgentLoop:
    """Agent 主处理循环"""

    def __init__(
        self,
        bus: MessageBus,
        provider: LLMProvider,
        workspace: Path,
        model: str | None = None,
        max_iterations: int = 40,  # ✅ 默认 40
        context_window_tokens: int = 65_536,  # ✅ 上下文窗口
        web_search_config: WebSearchConfig | None = None,  # ✅ Web 搜索
        web_proxy: str | None = None,  # ✅ Web 代理
        exec_config: ExecToolConfig | None = None,  # ✅ Exec 配置
        cron_service: CronService | None = None,  # ✅ Cron 支持
        restrict_to_workspace: bool = False,
        session_manager: SessionManager | None = None,  # ✅ 会话管理
        mcp_servers: dict | None = None,
        channels_config: ChannelsConfig | None = None,  # ✅ Channel 配置
    ):
        # ... 初始化
```

### AnyClaw Agent Loop (agent/loop.py)

```python
class AgentLoop:
    """Agent 主处理循环"""

    def __init__(
        self,
        enable_tools: bool = True,  # ✅ 工具开关
        workspace: Optional[Path] = None,
    ):
        # ... 初始化
        self.history = ConversationHistory(max_length=10)  # 🟡 硬编码
        self.skills: Dict[str, SkillDefinition] = {}
        self.enable_tools = enable_tools
        self.workspace = workspace or Path.cwd()

        # MCP 连接管理
        self._mcp_stack: Optional[AsyncExitStack] = None
```

### 差异分析

| 特性 | AnyClaw | nanobot | 优先级 |
|------|---------|---------|--------|
| **最大迭代次数** | 10 (硬编码) | 40 (可配置) | 🟡 **中优先级** |
| **上下文窗口** | ❌ 没有 | ✅ 65K tokens | 🟡 **中优先级** |
| **Web 搜索** | ❌ 没有 | ✅ 集成 | 🔴 **高优先级** |
| **Web 代理** | ❌ 没有 | ✅ 支持 | 🟡 **中优先级** |
| **Cron 支持** | ❌ 没有 | ✅ 集成 | 🔴 **高优先级** |
| **会话管理** | ❌ 没有 | ✅ SessionManager | 🔴 **高优先级** |
| **Progress 回调** | ❌ 没有 | ✅ | 🟡 **中优先级** |
| **Memory 整合** | 部分支持 | ✅ 完整 | 🟡 **中优先级** |

---

## 🎯 Skills 系统对比

### nanobot Skills (agent/skills.py)

```python
class SkillsLoader:
    """Skills 加载器 - 仅支持 SKILL.md 格式"""

    BUILTIN_SKILLS_DIR = Path(__file__).parent.parent / "skills"

    def __init__(self, workspace: Path, builtin_skills_dir: Path | None = None):
        self.workspace = workspace
        self.workspace_skills = workspace / "skills"
        self.builtin_skills = builtin_skills_dir

    def list_skills(self, filter_unavailable: bool = True) -> list[dict[str, str]]:
        """列出所有技能（支持依赖检查）"""
        # ...

    def load_skill(self, name: str) -> str | None:
        """加载技能内容"""
        # ...

    def build_skills_summary(self) -> str:
        """构建技能摘要（XML 格式，渐进式加载）"""
        # ...

    def get_always_skills(self) -> list[str]:
        """获取总是加载的技能"""
        # ...
```

### AnyClaw Skills (skills/loader.py)

```python
class SkillLoader:
    """技能加载器 - 支持 Python 类和 SKILL.md 格式"""

    SOURCE_PRIORITY = {
        "workspace": 100,
        "managed": 50,
        "bundled": 10,
    }

    def __init__(
        self,
        skills_dirs: Optional[List[str]] = None,
        skills_dir: Optional[str] = None,
        skills_dir_types: Optional[Dict[str, str]] = None,
    ):
        # ✅ 支持多目录优先级
        # ✅ 支持动态 Python 类加载
        # ✅ 支持热重载

    def load_all(self) -> List[Dict]:
        """加载所有技能（Python + SKILL.md）"""
        # ...

    def reload(self, name: str) -> bool:
        """热重载单个技能"""
        # ...
```

### 差异分析

| 特性 | AnyClaw | nanobot | 差异 |
|------|---------|---------|------|
| **Python Skill 类** | ✅ | ❌ | 🟢 AnyClaw 优势 |
| **SKILL.md 格式** | ✅ | ✅ | 🟢 相同 |
| **多目录优先级** | ✅ | ❌ | 🟢 AnyClaw 优势 |
| **热重载** | ✅ | ❌ | 🟢 AnyClaw 优势 |
| **依赖检查** | ✅ | ✅ | 🟢 相同 |
| **Always 加载** | ❌ | ✅ | 🟡 nanobot 优势 |
| **渐进式加载** | ✅ | ✅ | 🟢 相同 |
| **Skills 工具链** | ✅ (toolkit/) | ❌ | 🟢 AnyClaw 优势 |

---

## 🔧 Tools 系统对比

### nanobot Tools (agent/tools/)

| Tool | 文件 | 功能 | AnyClaw 支持 |
|------|------|------|--------------|
| **base.py** | 工具基类 | ✅ | ✅ |
| **filesystem.py** | ReadFile, WriteFile, EditFile, ListDir | ✅ | ✅ |
| **shell.py** | ExecTool (执行命令) | ✅ | ✅ |
| **web.py** | WebSearch, WebFetch | ✅ | ❌ |
| **message.py** | MessageTool (发送消息) | ✅ | ❌ |
| **spawn.py** | SpawnTool (创建子 Agent) | ✅ | ❌ |
| **cron.py** | CronTool (定时任务) | ✅ | ❌ |
| **mcp.py** | MCP 客户端 | ✅ | ✅ |

### AnyClaw Tools (tools/)

| Tool | 文件 | 功能 | nanobot 支持 |
|------|------|------|-------------|
| **base.py** | 工具基类 | ✅ | ✅ |
| **filesystem.py** | ReadFile, WriteFile, ListDir | ✅ | ✅ |
| **shell.py** | ExecTool (执行命令) | ✅ | ✅ |
| **mcp/** | MCP 客户端 | ✅ | ✅ |
| **memory.py** | SaveMemory, UpdatePersona | ✅ | 部分支持 |

### ExecTool 差异详细对比

| 特性 | AnyClaw | nanobot | 影响 |
|------|---------|---------|------|
| **最大超时** | 300 秒 | 600 秒 | 🔴 AnyClaw 更短 |
| **Kill 等待时间** | 5 秒 | 5 秒 | 🟢 相同 |
| **进程组 kill** | ❌ | ❌ | 🔴 都没有 |
| **路径遍历检查** | 基础 | ✅ 详细 | 🟡 nanobot 更安全 |
| **内部 URL 检查** | ❌ | ✅ 有 | 🔴 AnyClaw 缺少 SSRF 防护 |
| **输出截断** | 仅头部 | 头部 + 尾部 | 🟡 nanobot 更友好 |
| **绝对路径提取** | 简单 | Windows + POSIX + home | 🟡 nanobot 更全面 |

### ListDirTool 差异详细对比

| 特性 | AnyClaw | nanobot | 影响 |
|------|---------|---------|------|
| **超时控制** | ❌ 没有 | ❌ 没有 | 🔴 **共同问题** |
| **输出限制** | ❌ 没有 | ✅ max_entries (默认 200) | 🔴 AnyClaw 缺少 |
| **忽略列表** | ❌ 没有 | ✅ 内置 | 🟡 nanobot 更智能 |
| **递归支持** | ❌ 没有 | ✅ 有 | ℹ️ 功能差异 |
| **路径解析** | 简单 | ✅ expanduser + resolve | 🟡 nanobot 更健壮 |

---

## 🌐 Providers 系统对比

### nanobot Providers (providers/)

| Provider | 文件 | 功能 | AnyClaw 支持 |
|----------|------|------|--------------|
| **base.py** | Provider 基类 | ✅ | ✅ |
| **registry.py** | Provider 注册表 | ✅ | ❌ |
| **litellm_provider.py** | LiteLLM 集成 | ✅ | ✅ (间接) |
| **openai_codex_provider.py** | OpenAI Codex (OAuth) | ✅ | ❌ |
| **azure_openai_provider.py** | Azure OpenAI | ✅ | ❌ |
| **custom_provider.py** | 自定义 Provider | ✅ | ❌ |
| **transcription.py** | Groq 音频转写 | ✅ | ❌ |

### AnyClaw Providers (providers/)

| Provider | 文件 | 功能 | nanobot 支持 |
|----------|------|------|-------------|
| **base.py** | Provider 基类 | ✅ | ✅ |
| **zai.py** | ZAI/GLM Provider | ✅ | 部分支持 |
| **zai_detect.py** | ZAI 模型检测 | ✅ | ❌ |

### 差异分析

| 特性 | AnyClaw | nanobot | 优先级 |
|------|---------|---------|--------|
| **Provider 数量** | 1 (ZAI) | 15+ | 🔴 **高优先级** |
| **Provider 注册表** | ❌ 没有 | ✅ 动态注册 | 🔴 **高优先级** |
| **自动 Provider 匹配** | 简单 | ✅ 完整 | 🔴 **高优先级** |
| **OAuth 支持** | ❌ 没有 | ✅ (OpenAI Codex, GitHub Copilot) | 🟡 **中优先级** |
| **本地模型** | ❌ 没有 | ✅ (vLLM, Ollama) | 🟡 **中优先级** |
| **音频转写** | ❌ 没有 | ✅ Groq Whisper | 🟡 **中优先级** |
| **Gateway Providers** | ❌ 没有 | ✅ 硅基流动等 | 🟡 **中优先级** |

---

## 💾 Memory 系统对比

### nanobot Memory (agent/memory.py)

```python
class MemoryConsolidator:
    """记忆整合器 - 自动压缩和总结"""

    def __init__(
        self,
        workspace: Path,
        provider: LLMProvider,
        model: str,
        sessions: SessionManager,
        context_window_tokens: int = 65_536,
        build_messages: Callable,
        get_tool_definitions: Callable,
    ):
        # ✅ LLM 驱动的自动压缩
        # ✅ 上下文窗口感知
        # ✅ 会话管理集成
```

### AnyClaw Memory (memory/)

```python
class MemoryManager:
    """记忆管理器"""

    def __init__(
        self,
        workspace: Path,
        max_chars: int = 10000,
    ):
        # ✅ 基础记忆管理
        # ✅ 手动更新机制
```

class MemoryAutomation:
    """记忆自动化"""

    def __init__(
        self,
        workspace: Path,
        provider: Optional[LLMProvider] = None,
        model: str = "zai/glm-4.7",
    ):
        # ✅ 定期自动更新
        # ✅ LLM 驱动
```

### 差异分析

| 特性 | AnyClaw | nanobot | 优先级 |
|------|---------|---------|--------|
| **LLM 驱动压缩** | ✅ (automation.py) | ✅ | 🟢 相同 |
| **上下文窗口感知** | ❌ | ✅ | 🔴 **高优先级** |
| **会话管理集成** | ❌ | ✅ | 🔴 **高优先级** |
| **手动更新** | ✅ | ❌ | 🟢 AnyClaw 优势 |
| **定期自动更新** | ✅ (automation.py) | ✅ | 🟢 相同 |
| **每日加载天数** | ✅ | ❌ | 🟢 AnyClaw 优势 |

---

## 🔒 Security 对比

### nanobot Security (security/network.py)

```python
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    # ... 更多私有网络
]

def validate_url_target(url: str) -> tuple[bool, str]:
    """验证 URL 目标是否安全（SSRF 防护）"""
    # ✅ DNS 解析检查
    # ✅ 私有 IP 检测
    # ✅ 网络白名单
```

### AnyClaw Security (security/network.py)

```python
_BLOCKED_NETWORKS = [
    # 类似的私有网络列表
]

def validate_url_target(url: str) -> tuple[bool, str]:
    """验证 URL 目标是否安全（SSRF 防护）"""
    # ✅ 类似的实现
```

### 差异分析

| 特性 | AnyClaw | nanobot | 差异 |
|------|---------|---------|------|
| **私有网络检查** | ✅ | ✅ | 🟢 相同 |
| **URL 验证** | ✅ | ✅ | 🟢 相同 |
| **网络白名单** | ✅ | ✅ | 🟢 相同 |
| **域名白名单** | ✅ | ✅ | 🟢 相同 |

---

## 📅 Cron/Heartbeat 对比

### nanobot Cron (cron/)

```python
class CronService:
    """Cron 调度服务"""

    def __init__(self, schedule_path: Path, bus: MessageBus):
        self.schedule_path = schedule_path
        self.bus = bus
        self.cron_tasks: dict[str, CronJob] = {}
        self._running = False

    async def start(self):
        """启动 Cron 服务"""
        # ✅ 从文件加载调度
        # ✅ 支持复杂表达式
        # ✅ 自动触发任务

    async def stop(self):
        """停止 Cron 服务"""
        # ...
```

### nanobot Heartbeat (heartbeat/)

```python
class HeartbeatService:
    """心跳服务"""

    def __init__(self, interval_s: int, bus: MessageBus):
        self.interval_s = interval_s
        self.bus = bus

    async def start(self):
        """启动心跳"""
        # ✅ 定期发送心跳消息
        # ✅ 检查健康状态
```

### AnyClaw Cron/Heartbeat

| 组件 | 文件 | 功能 | nanobot 支持 |
|--------|------|------|-------------|
| **Cron** | ❌ 没有 | 定时任务 | ❌ |
| **Heartbeat** | ❌ 没有 | 定期检查 | ❌ (用 HEARTBEAT.md) |

### 差异分析

| 特性 | AnyClaw | nanobot | 优先级 |
|------|---------|---------|--------|
| **Cron 调度** | ❌ | ✅ | 🔴 **高优先级** |
| **文件驱动配置** | ❌ | ✅ | 🟡 **中优先级** |
| **Heartbeat 服务** | ❌ | ✅ | 🟡 **中优先级** |
| **健康检查** | ❌ | ✅ | 🟡 **中优先级** |
| **HEARTBEAT.md** | ✅ | ❌ | 🟢 AnyClaw 优势 |

---

## 🎛️ CLI 命令对比

### nanobot CLI (cli/)

| 命令 | 功能 | AnyClaw 支持 |
|------|------|--------------|
| `agent` | Agent 命令 | ❌ |
| `channels` | Channel 管理 | ❌ |
| `config` | 配置管理 | ✅ |
| `providers` | Provider 管理 | ❌ |
| `skills` | Skills 管理 | ✅ |
| `web` | Web 界面 | ✅ (有但不同) |
| `serve` | 启动服务 | ✅ |
| `doctor` | 诊断 | ❌ |

### AnyClaw CLI (cli/)

| 命令 | 功能 | nanobot 支持 |
|------|------|-------------|
| `chat` | 启动聊天 | ❌ |
| `serve` | 多通道服务 | ✅ |
| `setup` | 初始化工作区 | ❌ |
| `init` | 在项目目录初始化 | ❌ |
| `config` | 配置管理 | ✅ |
| `skill` | Skills 管理 | ✅ |
| `mcp` | MCP 管理 | ✅ |
| `persona` | 人设管理 | ❌ |
| `compress` | 压缩配置 | ❌ |
| `memory` | 记忆管理 | ✅ |
| `token` | Token 管理 | ❌ |
| `workspace` | 工作区管理 | ❌ |
| `onboard` | 配置向导 | ❌ |
| `security` | 安全管理 | ❌ |
| `version` | 显示版本 | ❌ |

### 差异分析

| 特性 | AnyClaw | nanobot | 优先级 |
|------|---------|---------|--------|
| **Provider 管理** | ❌ | ✅ | 🔴 **高优先级** |
| **Agent 管理** | ❌ | ✅ | 🟡 **中优先级** |
| **Channels 管理** | ❌ | ✅ | 🟡 **中优先级** |
| **Skills 工具链** | ✅ | ❌ | 🟢 AnyClaw 优势 |
| **Persona 管理** | ✅ | ❌ | 🟢 AnyClaw 优势 |
| **Compress 管理** | ✅ | ❌ | 🟢 AnyClaw 优势 |
| **Token 管理** | ✅ | ❌ | 🟢 AnyClaw 优势 |
| **Workspace 管理** | ✅ | ❌ | 🟢 AnyClaw 优势 |

---

## 🔴 关键差异总结

### 高优先级 - 必须补齐

1. **Provider 支持** (AnyClaw 缺少 14+ 个 Provider)
   - 需要实现 Provider 注册表
   - 需要添加 OAuth 支持
   - 需要添加本地模型支持 (vLLM, Ollama)

2. **Channel 支持** (AnyClaw 缺少 8 个 Channel)
   - Telegram Bot
   - WhatsApp
   - Slack
   - Email
   - DingTalk
   - WeChat Work
   - Matrix
   - QQ

3. **Web 工具集成**
   - WebSearch 工具
   - WebFetch 工具
   - Web 代理支持

4. **Cron 调度系统**
   - 文件驱动的配置
   - Cron 表达式支持
   - 自动触发

5. **会话管理**
   - SessionManager
   - 多会话支持
   - 会话隔离

6. **Agent Loop 增强**
   - 上下文窗口支持
   - Progress 回调
   - 更大的迭代次数

7. **ExecTool/ListDirTool 改进**
   - 超时控制
   - 输出限制
   - 更好的进程清理

### 中优先级 - 建议补齐

1. **音频转写**
   - Groq Whisper 集成
   - 支持多种音频格式

2. **子 Agent 管理**
   - SpawnTool
   - 子 Agent 通信
   - 任务分发

3. **Message 工具**
   - 跨会话消息发送
   - 消息转发

4. **Provider 管理 CLI**
   - 列出 Provider
   - 配置 API Keys
   - 测试连接

5. **Gateway 配置**
   - Host/Port 配置
   - Gateway 服务模式

6. **Heartbeat 服务**
   - 定期健康检查
   - 自动唤醒

### 低优先级 - 可选补齐

1. **Web 界面**
   - Dashboard
   - 配置 UI
   - 日志查看

2. **更多 Channel 特性**
   - 群组管理
   - 文件管理
   - 消息编辑

---

## 🛠️ 实施路线图

### Phase 1: 核心功能补齐 (Week 1-2)

**目标**: 完成高优先级功能

#### 1.1 Provider 系统
- [ ] 实现 `providers/registry.py`
- [ ] 添加 14+ 个 Provider
- [ ] 实现 OAuth 支持
- [ ] 添加本地模型支持 (vLLM, Ollama)
- [ ] 实现自动 Provider 匹配

#### 1.2 Web 工具
- [ ] 实现 `tools/web.py` (WebSearch, WebFetch)
- [ ] 添加 Web 代理支持
- [ ] 更新配置系统

#### 1.3 ExecTool/ListDirTool 改进
- [ ] 添加超时控制
- [ ] 添加输出限制
- [ ] 改进进程清理
- [ ] 添加路径遍历检查
- [ ] 添加 SSRF 防护

#### 1.4 Agent Loop 增强
- [ ] 添加上下文窗口支持
- [ ] 添加 Progress 回调
- [ ] 增加最大迭代次数到 40

### Phase 2: Channel 扩展 (Week 3-4)

**目标**: 添加缺失的 Channel

#### 2.1 Channel 实现
- [ ] Telegram Channel
- [ ] WhatsApp Channel
- [ ] Slack Channel
- [ ] DingTalk Channel
- [ ] WeChat Work Channel

#### 2.2 Channel 增强
- [ ] 音频转写集成
- [ ] 进度消息过滤
- [ ] 消息编辑支持

### Phase 3: 高级功能 (Week 5-6)

**目标**: 完成中优先级功能

#### 3.1 Cron/Heartbeat
- [ ] 实现 `cron/` 模块
- [ ] 实现 `heartbeat/` 模块
- [ ] 文件驱动配置
- [ ] 自动触发和健康检查

#### 3.2 会话管理
- [ ] 实现 `session/` 模块
- [ ] SessionManager
- [ ] 多会话支持
- [ ] 会话隔离

#### 3.3 子 Agent
- [ ] 实现 `agent/subagent.py`
- [ ] SpawnTool
- [ ] 子 Agent 通信

### Phase 4: CLI 和配置 (Week 7-8)

**目标**: 完善 CLI 和配置

#### 4.1 Provider 管理 CLI
- [ ] `anyclaw providers list`
- [ ] `anyclaw providers config`
- [ ] `anyclaw providers test`

#### 4.2 Gateway 配置
- [ ] Gateway 服务模式
- [ ] Host/Port 配置
- [ ] Gateway 启动/停止

#### 4.3 Agent 管理 CLI
- [ ] `anyclaw agent list`
- [ ] `anyclaw agent create`
- [ ] `anyclaw agent start`

---

## 📝 配置迁移指南

### nanobot → AnyClaw 配置映射

| nanobot 配置 | AnyClaw 配置 | 说明 |
|--------------|----------------|------|
| `providers.openai.api_key` | `openai_api_key` | 直接映射 |
| `providers.anthropic.api_key` | `anthropic_api_key` | 直接映射 |
| `agents.defaults.model` | `llm_model` | 模型名称 |
| `agents.defaults.provider` | `llm_provider` | Provider 名称 |
| `agents.defaults.max_tokens` | `llm_max_tokens` | 最大 tokens |
| `tools.exec.timeout` | `tool_timeout` | 工具超时 |
| `tools.restrict_to_workspace` | `restrict_to_workspace` | 工作区限制 |
| `tools.mcp_servers` | `mcp_servers` | MCP 服务器 |
| `channels.send_progress` | ❌ 没有 | 进度消息（待实现）|
| `channels.send_tool_hints` | ❌ 没有 | 工具提示（待实现）|

---

## 🔧 测试计划

### 单元测试

```bash
# Provider 测试
poetry run pytest tests/test_providers.py -v

# Tools 测试
poetry run pytest tests/test_tools.py -v

# Channel 测试
poetry run pytest tests/test_channels.py -v

# Agent Loop 测试
poetry run pytest tests/test_agent_loop.py -v
```

### 集成测试

```bash
# 端到端测试
poetry run pytest tests/integration/ -v

# Provider 集成测试
poetry run pytest tests/integration/providers/ -v

# Channel 集成测试
poetry run pytest tests/integration/channels/ -v
```

### 性能测试

```bash
# Agent Loop 性能
poetry run pytest tests/performance/agent_loop.py -v

# Tools 性能
poetry run pytest tests/performance/tools.py -v

# Memory 性能
poetry run pytest tests/performance/memory.py -v
```

---

## 📊 总结

### AnyClaw 的优势

1. ✅ **更灵活的 Skills 系统** - 支持 Python 类 + SKILL.md
2. ✅ **多目录优先级** - Workspace > Managed > Bundled
3. ✅ **热重载** - 运行时重新加载技能
4. ✅ **Skills 工具链** - 创建、验证、打包技能
5. ✅ **Persona 管理** - 独立的人设系统
6. ✅ **Compress 管理** - 压缩策略配置
7. ✅ **Token 管理** - Token 限制和警告
8. ✅ **Workspace 管理** - 初始化和模板同步
9. ✅ **HEARTBEAT.md** - 简单的心跳机制
10. ✅ **详细 CLI** - 更多子命令

### nanobot 的优势

1. ✅ **更多 Provider** - 15+ vs 3
2. ✅ **更多 Channel** - 12 vs 4
3. ✅ **Web 工具集成** - 搜索和抓取
4. ✅ **Cron 调度** - 定时任务系统
5. ✅ **会话管理** - SessionManager
6. ✅ **音频转写** - Groq Whisper
7. ✅ **子 Agent** - SpawnTool
8. ✅ **OAuth 支持** - GitHub Copilot, OpenAI Codex
9. ✅ **本地模型** - vLLM, Ollama
10. ✅ **更完善的工具** - 更多功能

### 建议

1. **优先补齐高优先级功能** - Provider, Channel, Web 工具
2. **保持 AnyClaw 的优势** - Skills 系统, 多目录优先级
3. **参考 nanobot 的实现** - 更成熟的代码结构
4. **渐进式迁移** - 逐个功能实现和测试
5. **完善文档** - 每个新功能都要有文档和示例

---

**文档生成时间**: 2026-03-20
**对比基准**: nanobot (2026-03-17) vs AnyClaw (0.1.0-MVP)
**建议**: 按照实施路线图逐步补齐功能

---

## 🔧 工具修复总结（2026-03-20）

### 已完成的修复

#### 1. **ListDirTool 改进** ✅

**文件**: `anyclaw/tools/filesystem.py`

**新增功能**:
- ✅ 超时控制（默认 30 秒，可配置）
- ✅ 输出限制（默认 200 条目，可配置）
- ✅ 异步执行（使用 `asyncio.run_in_executor` 避免阻塞事件循环）
- ✅ 忽略列表（`.git`, `node_modules`, `__pycache__` 等）
- ✅ 截断提示（显示前 N 个，共 M 个）

**新增配置项**:
```python
list_dir_timeout: int = 30  # 超时时间（秒）
list_dir_max_entries: int = 200  # 最大条目数
```

#### 2. **ExecTool 改进** ✅

**文件**: `anyclaw/tools/shell.py`

**改进功能**:
- ✅ 最大超时从 300 秒增加到 600 秒（与 nanobot 一致）
- ✅ 渐进式 kill 策略（SIGTERM 10 秒 → SIGKILL 3 秒 → 进程组 kill）
- ✅ 更好的进程清理（确保在任何情况下都清理）
- ✅ 路径遍历检查（阻止 `../` 和 `..\` 模式）
- ✅ SSRF 防护（阻止内部/私有 URL）
- ✅ 输出截断改进（保留头部 + 尾部，与 nanobot 一致）
- ✅ 绝对路径提取（Windows + POSIX + home，与 nanobot 一致）

**新增常量**:
```python
_MAX_TIMEOUT = 600  # 最大超时时间
_GRACEFUL_WAIT = 10  # SIGTERM 等待时间
_FORCE_WAIT = 3       # SIGKILL 等待时间
```

#### 3. **配置系统更新** ✅

**文件**: `anyclaw/config/settings.py`

**新增配置项**:
```python
list_dir_timeout: int = 30
list_dir_max_entries: int = 200
```

#### 4. **Agent Loop 更新** ✅

**文件**: `anyclaw/agent/loop.py`

**改进功能**:
- ✅ ListDirTool 超时配置
- ✅ ListDirTool 最大条目配置

### 测试结果

**测试文件**: `test_fixes.py`

| 测试 | 结果 | 说明 |
|------|------|------|
| ListDirTool 超时 | ✅ 通过 | 正常列出目录 |
| ListDirTool 最大条目限制 | ✅ 通过 | 正确截断到 5 个条目 |
| ListDirTool 忽略列表 | ✅ 通过 | 正确忽略噪声目录 |
| ExecTool 超时 | ✅ 通过 | 正确检测并处理超时 |
| ExecTool 路径遍历检查 | ✅ 通过 | 正确阻止 `../` |
| ExecTool 内部 URL 检查 | ✅ 通过 | 正确阻止内部 URL |
| ExecTool 输出截断 | ✅ 通过 | 正确截断到 10036 字符 |

**总计**: 7/7 测试通过 ✅

### 与 nanobot 的对比

| 功能 | 修复前 | 修复后 | nanobot | 状态 |
|------|--------|--------|---------|------|
| **ListDirTool 超时** | ❌ 没有 | ✅ 30 秒 | ❌ 没有 | 🟢 AnyClaw 优势 |
| **ListDirTool 输出限制** | ❌ 没有 | ✅ 200 条目 | ✅ 有 | ✅ 对齐 |
| **ListDirTool 忽略列表** | ❌ 没有 | ✅ 内置 | ✅ 有 | ✅ 对齐 |
| **ExecTool 最大超时** | 300 秒 | 600 秒 | 600 秒 | ✅ 对齐 |
| **ExecTool Kill 策略** | 5 秒 kill | 渐进式 kill | 5 秒 kill | 🟢 AnyClaw 优势 |
| **ExecTool SSRF 防护** | ❌ 没有 | ✅ 有 | ✅ 有 | ✅ 对齐 |
| **ExecTool 输出截断** | 仅头部 | 头部+尾部 | 头部+尾部 | ✅ 对齐 |
| **ExecTool 路径遍历** | 简单 | 详细 | 详细 | ✅ 对齐 |

### 下一步

1. ✅ **立即测试**: 在 Discord 中测试 git 命令，确认不再卡死
2. 🔄 **持续监控**: 观察是否有其他超时或进程问题
3. 📋 **按路线图继续**: 参考 `COMPARISON_WITH_NANOBOT.md` 的 Phase 2-4 计划

---

**修复完成时间**: 2026-03-20 00:50
**修复人员**: Yilia
**测试状态**: ✅ 全部通过
