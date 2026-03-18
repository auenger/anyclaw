# AnyClaw MVP 实施方案

## 文档信息

- **项目名称**: AnyClaw MVP
- **创建日期**: 2026-03-17
- **版本**: v0.1.0-MVP
- **预计完成时间**: 2-3周

---

## 目录

1. [MVP 目标和范围](#1-mvp-目标和范围)
2. [MVP 架构设计](#2-mvp-架构设计)
3. [技术栈简化](#3-技术栈简化)
4. [项目结构](#4-项目结构)
5. [实施步骤](#5-实施步骤)
6. [核心模块设计](#6-核心模块设计)
7. [配置方案](#7-配置方案)
8. [示例 Skill](#8-示例-skill)
9. [测试计划](#9-测试计划)
10. [快速开始](#10-快速开始)

---

## 1. MVP 目标和范围

### 1.1 MVP 核心目标

实现一个最简但完整的 AI 智能体系统：

```
用户输入（CLI） → Agent 处理 → Skill 执行 → LLM 响应 → 输出
```

### 1.2 功能范围

#### ✅ 包含功能

| 功能模块 | 说明 | 优先级 |
|---------|------|--------|
| **CLI 交互** | 命令行对话界面 | P0 |
| **Agent 引擎** | 核心处理循环、上下文管理 | P0 |
| **LLM 集成** | 支持主流 LLM 提供商 | P0 |
| **配置系统** | 可配置 Agent 名称、API Key 等 | P0 |
| **Skill 系统** | 基础技能加载和执行 | P0 |
| **基础工具** | 文件读取、时间获取等简单工具 | P1 |
| **对话历史** | 简单的上下文记忆 | P1 |

#### ❌ 暂不包含

- 多频道支持（仅 CLI）
- 复杂工具（Shell、Web 搜索）
- 长期记忆存储
- 技能依赖管理
- 定时任务
- Web UI

### 1.3 MVP 成功标准

1. ✅ 用户可以通过 CLI 与 Agent 对话
2. ✅ Agent 能理解和响应自然语言
3. ✅ Agent 能调用简单的技能
4. ✅ Agent 名称可配置（默认：AnyClaw）
5. ✅ 支持多轮对话（短期记忆）
6. ✅ 请求超时时间可配置（默认：60秒）
7. ✅ 在超时时间内正常响应并返回结果

---

## 2. MVP 架构设计

### 2.1 简化架构

```
┌─────────────────────────────────────────────────────┐
│                    AnyClaw MVP                       │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────┐         ┌──────────┐                 │
│  │   CLI    │────────▶│  Agent   │                 │
│  │  Channel │         │   Loop   │                 │
│  └──────────┘         └────┬─────┘                 │
│                             │                        │
│                             ▼                        │
│                      ┌──────────┐                   │
│                      │  Context │                   │
│                      │ Builder  │                   │
│                      └────┬─────┘                   │
│                           │                         │
│              ┌────────────┼────────────┐            │
│              ▼            ▼            ▼            │
│        ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│        │  Skills │  │  Tools  │  │   LLM   │       │
│        └─────────┘  └─────────┘  └─────────┘       │
│                                                       │
├─────────────────────────────────────────────────────┤
│                   Config & Settings                  │
└─────────────────────────────────────────────────────┘
```

### 2.2 核心流程

```
1. 用户在 CLI 输入消息
2. CLI Channel 将消息发送给 Agent Loop
3. Agent Loop 构建上下文（系统提示 + 对话历史 + 技能信息）
4. Agent Loop 调用 LLM
5. LLM 返回响应（可能包含工具/技能调用）
6. Agent Loop 执行技能/工具
7. Agent Loop 将结果返回给 CLI Channel
8. CLI 显示响应
```

---

## 3. 技术栈简化

### 3.1 核心依赖（最小化）

```toml
[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.12.0"
pydantic-settings = "^2.0.0"
typer = {extras = ["all"], version = "^0.20.0"}
rich = "^14.0.0"
litellm = "^1.82.1"
openai = "^1.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.23.0"
black = "^24.0.0"
ruff = "^0.3.0"
```

### 3.2 为什么选择这些依赖？

| 依赖 | 用途 | 原因 |
|-----|------|-----|
| **Pydantic** | 数据验证 | 类型安全、自动验证 |
| **Typer** | CLI 框架 | 简单易用、自动帮助文档 |
| **Rich** | 终端美化 | 提升用户体验 |
| **LiteLLM** | LLM 统一接口 | 支持多提供商 |
| **OpenAI** | OpenAI SDK | 直接支持，性能更好 |

---

## 4. 项目结构

### 4.1 MVP 项目结构

```
anyclaw/
├── anyclaw/                      # 主包
│   ├── __init__.py
│   ├── __main__.py              # 入口点：python -m anyclaw
│   │
│   ├── config/                   # 配置模块
│   │   ├── __init__.py
│   │   └── settings.py          # 配置定义
│   │
│   ├── agent/                    # Agent 核心模块
│   │   ├── __init__.py
│   │   ├── loop.py              # 主处理循环
│   │   ├── context.py           # 上下文构建器
│   │   └── history.py           # 对话历史管理
│   │
│   ├── skills/                   # 技能系统
│   │   ├── __init__.py
│   │   ├── loader.py            # 技能加载器
│   │   ├── base.py              # 技能基类
│   │   └── builtin/             # 内置技能
│   │       ├── __init__.py
│   │       ├── echo/            # Echo 技能示例
│   │       │   └── SKILL.md
│   │       └── time/            # 时间技能
│   │           └── SKILL.md
│   │
│   ├── tools/                    # 工具系统
│   │   ├── __init__.py
│   │   ├── base.py              # 工具基类
│   │   ├── registry.py          # 工具注册表
│   │   └── builtin/             # 内置工具
│   │       ├── __init__.py
│   │       ├── time.py          # 时间工具
│   │       └── file.py          # 文件读取工具
│   │
│   ├── providers/                # LLM 提供商
│   │   ├── __init__.py
│   │   └── base.py              # 提供商基类
│   │
│   ├── channels/                 # 频道系统
│   │   ├── __init__.py
│   │   ├── base.py              # 频道基类
│   │   └── cli.py               # CLI 频道
│   │
│   └── cli/                      # CLI 工具
│       ├── __init__.py
│       └── app.py               # 主 CLI 应用
│
├── config/                       # 配置文件目录
│   ├── default.yaml             # 默认配置
│   └── skills.yaml              # 技能配置
│
├── workspace/                    # 工作空间（运行时生成）
│   ├── MEMORY.md                # 长期记忆（未来）
│   └── HISTORY.md               # ���话历史（未来）
│
├── tests/                        # 测试
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_skills.py
│   └── test_tools.py
│
├── pyproject.toml                # 项目配置
├── README.md                     # 项目说明
├── .env.example                  # 环境变量示例
└── .gitignore
```

---

## 5. 实施步骤

### Phase 1: 项目初始化（1-2天）

#### Step 1.1: 创建项目骨架
```bash
# 创建项目目录
mkdir anyclaw
cd anyclaw

# 初始化 Poetry
poetry init --name anyclaw --version 0.1.0

# 添加依赖
poetry add pydantic pydantic-settings typer rich litellm openai
poetry add --group dev pytest pytest-asyncio black ruff

# 创建目录结构
mkdir -p anyclaw/{config,agent,skills,tools,providers,channels,cli}
mkdir -p anyclaw/skills/builtin/{echo,time}
mkdir -p anyclaw/tools/builtin
mkdir -p config workspace tests
```

#### Step 1.2: 配置开发工具
```bash
# black 配置
cat > pyproject.toml << EOF
[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]
EOF

# pre-commit 配置
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix]
EOF
```

### Phase 2: 配置系统（1天）

#### Step 2.1: 创建配置模块

`anyclaw/config/settings.py`:
```python
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

    # API Keys
    openai_api_key: str = Field(
        default="",
        description="OpenAI API Key"
    )
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API Key"
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
```

#### Step 2.2: 创建环境变量示例

`.env.example`:
```bash
# Agent 配置
AGENT_NAME=AnyClaw
AGENT_ROLE=You are a helpful AI assistant named {name}.

# LLM 配置
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
LLM_TIMEOUT=60

# API Keys
OPENAI_API_KEY=sk-your-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# CLI 配置
CLI_PROMPT="You: "

# 技能配置
SKILLS_DIR=anyclaw/skills/builtin

# 工作空间
WORKSPACE_DIR=workspace
```

### Phase 3: Agent 核心（2-3天）

#### Step 3.1: 对话历史管理

`anyclaw/agent/history.py`:
```python
from collections import deque
from typing import List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Message:
    """消息数据类"""
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ConversationHistory:
    """对话历史管理器"""

    def __init__(self, max_length: int = 10):
        self.messages: deque[Message] = deque(maxlen=max_length)

    def add_message(self, role: str, content: str) -> None:
        """添加消息"""
        self.messages.append(Message(role=role, content=content))

    def add_user_message(self, content: str) -> None:
        """添加用户消息"""
        self.add_message("user", content)

    def add_assistant_message(self, content: str) -> None:
        """添加助手消息"""
        self.add_message("assistant", content)

    def get_history(self) -> List[dict]:
        """获取历史记录（LLM 格式）"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages
        ]

    def clear(self) -> None:
        """清空历史"""
        self.messages.clear()

    def __len__(self) -> int:
        return len(self.messages)
```

#### Step 3.2: 上下文构建器

`anyclaw/agent/context.py`:
```python
from typing import List, Dict
from ..config import settings
from .history import ConversationHistory


class ContextBuilder:
    """上下文构建器"""

    def __init__(self, history: ConversationHistory, skills_info: List[Dict]):
        self.history = history
        self.skills_info = skills_info

    def build(self) -> List[Dict]:
        """构建完整上下文"""
        context = []

        # 1. 系统提示词
        system_prompt = self._build_system_prompt()
        context.append({"role": "system", "content": system_prompt})

        # 2. 历史对话
        context.extend(self.history.get_history())

        return context

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        base_prompt = settings.get_system_prompt()

        # 添加技能信息
        if self.skills_info:
            skills_desc = "\n\nYou have access to these skills:\n"
            for skill in self.skills_info:
                skills_desc += f"- {skill['name']}: {skill['description']}\n"
            base_prompt += skills_desc

        return base_prompt
```

#### Step 3.3: Agent 主循环

`anyclaw/agent/loop.py`:
```python
import asyncio
from typing import Optional
from litellm import acompletion
from ..config import settings
from .history import ConversationHistory
from .context import ContextBuilder


class AgentLoop:
    """Agent 主处理循环"""

    def __init__(self):
        self.history = ConversationHistory(max_length=10)
        self.skills_info = []

    async def process(self, user_input: str) -> str:
        """处理用户输入"""
        # 1. 添加用户消息到历史
        self.history.add_user_message(user_input)

        # 2. 构建上下文
        context_builder = ContextBuilder(self.history, self.skills_info)
        messages = context_builder.build()

        # 3. 调用 LLM
        response = await self._call_llm(messages)

        # 4. 添加助手响应到历史
        self.history.add_assistant_message(response)

        return response

    async def _call_llm(self, messages: list) -> str:
        """调用 LLM"""
        try:
            response = await acompletion(
                model=settings.llm_model,
                messages=messages,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout,
                api_key=settings.openai_api_key,
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error: {str(e)}"

    def clear_history(self) -> None:
        """清空对话历史"""
        self.history.clear()

    def set_skills(self, skills_info: list) -> None:
        """设置可用技能"""
        self.skills_info = skills_info
```

### Phase 4: CLI 频道（1天）

#### Step 4.1: CLI 频道实现

`anyclaw/channels/cli.py`:
```python
from typing import Callable
from rich.console import Console
from rich.prompt import Prompt
from ..config import settings


class CLIChannel:
    """CLI 频道"""

    def __init__(self):
        self.console = Console()
        self.running = False

    def print_welcome(self):
        """打印欢迎信息"""
        self.console.print(f"\n[bold blue]Welcome to {settings.agent_name}![/bold blue]")
        self.console.print("[dim]Type 'exit' or 'quit' to exit[/dim]")
        self.console.print("[dim]Type 'clear' to clear conversation history[/dim]\n")

    def print_response(self, response: str):
        """打印响应"""
        self.console.print(f"\n[bold green]{settings.agent_name}:[/bold green] {response}\n")

    def get_input(self) -> str:
        """获取用户输入"""
        return Prompt.ask(settings.cli_prompt, console=self.console)

    async def run(self, process_func: Callable[[str], str]):
        """运行 CLI 循环"""
        self.print_welcome()
        self.running = True

        while self.running:
            try:
                user_input = self.get_input()

                # 处理特殊命令
                if user_input.lower() in ['exit', 'quit']:
                    self.console.print("[yellow]Goodbye![/yellow]")
                    break

                if user_input.lower() == 'clear':
                    # 清空历史（需要在 process_func 中实现）
                    self.console.print("[yellow]Conversation cleared.[/yellow]")
                    continue

                if not user_input.strip():
                    continue

                # 处理用户输入
                response = await process_func(user_input)
                self.print_response(response)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
```

### Phase 5: 技能系统（1-2天）

#### Step 5.1: 技能基类

`anyclaw/skills/base.py`:
```python
from abc import ABC, abstractmethod
from typing import Dict, Any


class Skill(ABC):
    """技能基类"""

    def __init__(self):
        self.name = self.__class__.__name__
        self.description = self.__doc__ or "No description"

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """执行技能"""
        pass

    def get_info(self) -> Dict[str, str]:
        """获取技能信息"""
        return {
            "name": self.name,
            "description": self.description
        }
```

#### Step 5.2: 技能加载器

`anyclaw/skills/loader.py`:
```python
import os
import importlib
from typing import List, Dict
from pathlib import Path
from .base import Skill


class SkillLoader:
    """技能加载器"""

    def __init__(self, skills_dir: str):
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Skill] = {}

    def load_all(self) -> List[Dict]:
        """加载所有技能"""
        skills_info = []

        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir() and not skill_path.name.startswith('_'):
                skill = self._load_skill(skill_path)
                if skill:
                    self.skills[skill.name] = skill
                    skills_info.append(skill.get_info())

        return skills_info

    def _load_skill(self, skill_path: Path) -> Skill:
        """加载单个技能"""
        try:
            # 查找 skill.py 文件
            skill_file = skill_path / "skill.py"
            if not skill_file.exists():
                return None

            # 动态导入
            module_name = f"anyclaw.skills.builtin.{skill_path.name}.skill"
            module = importlib.import_module(module_name)

            # 查找 Skill 类
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Skill) and attr != Skill:
                    return attr()

        except Exception as e:
            print(f"Error loading skill {skill_path.name}: {e}")

        return None

    async def execute_skill(self, name: str, **kwargs) -> str:
        """执行技能"""
        skill = self.skills.get(name)
        if not skill:
            return f"Skill '{name}' not found"

        try:
            return await skill.execute(**kwargs)
        except Exception as e:
            return f"Error executing skill '{name}': {e}"
```

#### Step 5.3: 示例技能

`anyclaw/skills/builtin/echo/skill.py`:
```python
from anyclaw.skills.base import Skill


class EchoSkill(Skill):
    """Echo back the input message"""

    async def execute(self, message: str = "", **kwargs) -> str:
        """Echo the input message"""
        if not message:
            return "Please provide a message to echo"
        return f"Echo: {message}"
```

`anyclaw/skills/builtin/time/skill.py`:
```python
from datetime import datetime
from anyclaw.skills.base import Skill


class TimeSkill(Skill):
    """Get current time"""

    async def execute(self, **kwargs) -> str:
        """Get current time"""
        now = datetime.now()
        return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
```

### Phase 6: 主应用集成（1天）

#### Step 6.1: CLI 应用

`anyclaw/cli/app.py`:
```python
import typer
from rich.console import Console
from ..config import settings
from ..agent.loop import AgentLoop
from ..channels.cli import CLIChannel
from ..skills.loader import SkillLoader

app = typer.Typer()
console = Console()


@app.command()
def chat(
    agent_name: str = typer.Option(None, help="Agent name"),
    model: str = typer.Option(None, help="LLM model"),
):
    """Start interactive chat"""

    # 覆盖配置
    if agent_name:
        settings.agent_name = agent_name
    if model:
        settings.llm_model = model

    console.print(f"[bold blue]Starting {settings.agent_name}...[/bold blue]\n")

    # 初始化组件
    agent = AgentLoop()
    channel = CLIChannel()
    skill_loader = SkillLoader(settings.skills_dir)

    # 加载技能
    skills_info = skill_loader.load_all()
    agent.set_skills(skills_info)

    # 定义处理函数
    async def process(user_input: str) -> str:
        return await agent.process(user_input)

    # 运行 CLI
    import asyncio
    asyncio.run(channel.run(process))


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current config"),
):
    """Manage configuration"""

    if show:
        console.print("\n[bold]Current Configuration:[/bold]\n")
        console.print(f"Agent Name: {settings.agent_name}")
        console.print(f"LLM Provider: {settings.llm_provider}")
        console.print(f"LLM Model: {settings.llm_model}")
        console.print(f"Temperature: {settings.llm_temperature}")
        console.print(f"Max Tokens: {settings.llm_max_tokens}")
        console.print(f"Skills Dir: {settings.skills_dir}")
        console.print(f"Workspace Dir: {settings.workspace_dir}")


@app.command()
def version():
    """Show version"""
    console.print("AnyClaw v0.1.0-MVP")


if __name__ == "__main__":
    app()
```

#### Step 6.2: 入口点

`anyclaw/__main__.py`:
```python
from .cli.app import app

if __name__ == "__main__":
    app()
```

### Phase 7: 测试（1天）

#### Step 7.1: 单元测试

`tests/test_agent.py`:
```python
import pytest
import asyncio
from anyclaw.agent.loop import AgentLoop
from anyclaw.agent.history import ConversationHistory


def test_history():
    history = ConversationHistory(max_length=3)

    history.add_user_message("Hello")
    history.add_assistant_message("Hi there!")

    assert len(history) == 2
    messages = history.get_history()
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"


@pytest.mark.asyncio
async def test_agent_process():
    agent = AgentLoop()

    # 需要设置 API Key 才能测试
    # response = await agent.process("Hello")
    # assert response
```

---

## 6. 核心模块设计

### 6.1 模块关系图

```
┌─────────────────────────────────────────────────────┐
│                    CLI Application                   │
│                    (cli/app.py)                      │
└─────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Agent Loop   │ │ CLI Channel  │ │ Skill Loader │
└──────────────┘ └──────────────┘ └──────────────┘
        │
        ├──────────────┐
        ▼              ▼
┌──────────────┐ ┌──────────────┐
│ History      │ │Context Builder│
└──────────────┘ └──────────────┘
        │
        ▼
┌──────────────┐
│   Settings   │
└──────────────┘
```

### 6.2 数据流

```
User Input → CLI Channel → Agent Loop → Context Builder → LLM → Response
                                            ↑
                                    Skills Info
```

---

## 7. 配置方案

### 7.1 Agent 名称配置

Agent 名称可以通过多种方式配置，优先级从高到低：

1. **命令行参数**:
   ```bash
   poetry run anyclaw chat --agent-name "MyBot"
   ```

2. **环境变量**:
   ```bash
   export AGENT_NAME="MyBot"
   ```

3. **.env 文件**:
   ```bash
   AGENT_NAME=MyBot
   ```

4. **默认值**: "AnyClaw"

### 7.1.1 请求超时配置

LLM 请求超时时间可配置，默认为 60 秒。可通过以下方式调整：

1. **环境变量**:
   ```bash
   export LLM_TIMEOUT=120  # 设置为 120 秒
   ```

2. **.env 文件**:
   ```bash
   LLM_TIMEOUT=120
   ```

3. **YAML 配置文件**:
   ```yaml
   llm:
     timeout: 120
   ```

4. **默认值**: 60 秒

**注意**: 超时时间应根据实际使用场景调整：
- 简单对话：30-60 秒足够
- 复杂任务：可能需要 90-120 秒
- 不限制超时：设置较大的值（如 300 秒）

### 7.2 配置示例

创建 `config/default.yaml`:
```yaml
agent:
  name: AnyClaw
  role: "You are a helpful AI assistant named {name}."

llm:
  provider: openai
  model: gpt-4o-mini
  temperature: 0.7
  max_tokens: 2000
  timeout: 60  # 请求超时时间（秒）

cli:
  prompt: "You: "

skills:
  dir: anyclaw/skills/builtin

workspace:
  dir: workspace
```

---

## 8. 示例 Skill

### 8.1 Echo 技能

完整的 Echo 技能示例：

**目录结构**:
```
anyclaw/skills/builtin/echo/
├── skill.py
└── SKILL.md
```

**skill.py**:
```python
from anyclaw.skills.base import Skill


class EchoSkill(Skill):
    """Echo back the input message"""

    async def execute(self, message: str = "", **kwargs) -> str:
        """Echo the input message"""
        if not message:
            return "Please provide a message to echo"
        return f"Echo: {message}"
```

**SKILL.md**:
```markdown
# Echo Skill

## Description
Echoes back the input message.

## Usage
User: Echo hello world
AnyClaw: Echo: hello world
```

### 8.2 计算器技能

`anyclaw/skills/builtin/calculator/skill.py`:
```python
from anyclaw.skills.base import Skill


class CalculatorSkill(Skill):
    """Simple calculator for basic math operations"""

    async def execute(self, expression: str = "", **kwargs) -> str:
        """Calculate a math expression"""
        try:
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"
```

---

## 9. 测试计划

### 9.1 测试范围

| 测试类型 | 覆盖内容 | 优先级 |
|---------|---------|--------|
| **单元测试** | History, ContextBuilder, Skill | P0 |
| **集成测试** | Agent + LLM, CLI + Agent | P1 |
| **端到端测试** | 完整对话流程 | P1 |

### 9.2 测试用例

#### 用例 1: 基本对话
```bash
# 输入
Hello, AnyClaw!

# 期望输出
Hi! How can I help you today?
```

#### 用例 2: 技能调用
```bash
# 输入
What time is it?

# 期望输出
Current time: 2026-03-17 14:30:00
```

#### 用例 3: 多轮对话
```bash
# 输入 1
My name is Alice

# 输入 2
What's my name?

# 期望输出 2
Your name is Alice
```

---

## 10. 快速开始

### 10.1 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/anyclaw.git
cd anyclaw

# 安装依赖
poetry install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，添加 API Key
```

### 10.2 运行

```bash
# 启动默认 Agent
poetry run anyclaw chat

# 启动自定义 Agent
poetry run anyclaw chat --agent-name "MyAssistant"

# 查看配置
poetry run anyclaw config --show

# 查看版本
poetry run anyclaw version
```

### 10.3 使用示例

```bash
$ poetry run anyclaw chat

Welcome to AnyClaw!
Type 'exit' or 'quit' to exit
Type 'clear' to clear conversation history

You: Hello!
AnyClaw: Hi! How can I help you today?

You: What time is it?
AnyClaw: Current time: 2026-03-17 14:30:00

You: exit
Goodbye!
```

---

## 附录

### A. 开发检查清单

- [ ] 项目结构创建完成
- [ ] Poetry 配置完成
- [ ] 配置系统实现完成
- [ ] Agent 核心实现完成
- [ ] CLI 频道实现完成
- [ ] 技能系统实现完成
- [ ] 示例技能实现完成
- [ ] 单元测试编写完成
- [ ] README 文档编写完成
- [ ] 端到端测试通过

### B. MVP 后续计划

MVP 完成后，可以考虑添加：

1. 更多技能（天气、搜索等）
2. 工具系统（文件操作、Shell 命令）
3. 长期记忆存储
4. 更多 LLM 提供商支持
5. 多频道支持（Discord、Telegram）
6. Web UI
7. 配置文件支持

### C. 常见问题

**Q: 如何更改 Agent 名称？**
A: 可以通过命令行参数 `--agent-name`、环境变量 `AGENT_NAME` 或 `.env` 文件配置。

**Q: 如何添加新技能？**
A: 在 `anyclaw/skills/builtin/` 下创建新目录，添加 `skill.py` 文件，继承 `Skill` 基类。

**Q: 支持哪些 LLM？**
A: MVP 主要支持 OpenAI，但通过 LiteLLM 可以扩展支持其他提供商。

**Q: 如何调整请求超时时间？**
A: 可以通过环境变量 `LLM_TIMEOUT`、`.env` 文件或 YAML 配置文件设置超时时间（单位：秒），默认为 60 秒。

**Q: 响应时间太长怎么办？**
A: 可以尝试：
  1. 减少超时时间配置
  2. 使用更快的 LLM 模型（如 gpt-4o-mini）
  3. 减少 max_tokens 参数
  4. 检查网络连接

---

**文档版本**: v0.1.0-MVP
**最后更新**: 2026-03-18
**维护者**: AnyClaw Team
