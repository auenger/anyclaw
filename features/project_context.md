---
last_updated: '2026-03-22'
version: 10
features_completed: 42
tests_passing: 588
---

# Project Context: AnyClaw

> This file contains critical rules and patterns that AI agents must follow when implementing code. Keep it concise and focused on non-obvious details.

---

## Technology Stack

| Category | Technology | Version | Notes |
|----------|-----------|---------|-------|
| Language | Python | 3.11+ | Type hints required, built-in tomllib |
| Package Manager | Poetry | 2.x | pyproject.toml |
| Config | Pydantic Settings | 2.x | .env / TOML file |
| CLI | Typer + Rich | 0.20+ / 14+ | Beautiful terminal |
| LLM | litellm | 1.82+ | Multi-provider |
| API | FastAPI + SSE | 0.115+ | Sidecar mode |
| Desktop | Tauri 2.0 | - | Rust + React |
| Testing | pytest + pytest-asyncio | 8.x / 0.23+ | Async tests |
| Code Style | Black + Ruff | - | line-length=100 |

## Directory Structure

```
anyclaw/
├── anyclaw/                   # Main package
│   ├── agent/                 # Agent engine
│   │   ├── loop.py            # Main processing loop (sync + stream)
│   │   ├── context.py         # Context builder
│   │   ├── history.py         # Conversation history
│   │   ├── tool_loop.py       # Tool calling loop
│   │   ├── subagent.py        # SubAgent manager
│   │   └── tools/             # Agent tools
│   │       ├── message.py     # MessageTool
│   │       └── spawn.py       # SpawnTool
│   ├── agents/                # Multi-Agent system
│   │   ├── manager.py         # AgentManager
│   │   ├── identity.py        # IdentityManager
│   │   └── cli/               # Agent CLI commands
│   ├── session/               # Session management
│   │   ├── manager.py         # SessionManager
│   │   ├── archive.py         # SessionArchiver
│   │   └── models.py          # Session models
│   ├── cron/                  # Cron scheduling
│   │   ├── service.py         # CronService
│   │   ├── tool.py            # CronTool
│   │   └── types.py           # Cron types
│   ├── channels/              # Channel plugins
│   │   ├── cli.py             # CLI channel (sync + stream)
│   │   ├── feishu.py          # Feishu channel
│   │   ├── discord.py         # Discord channel
│   │   ├── manager.py         # ChannelManager
│   │   └── bus.py             # MessageBus
│   ├── api/                   # API server
│   │   ├── server.py          # FastAPI server
│   │   ├── sse.py             # SSE streaming
│   │   ├── deps.py            # Dependencies
│   │   └── routes/            # API routes
│   │       ├── health.py      # Health check
│   │       ├── agents.py      # Agent management
│   │       ├── messages.py    # Message handling
│   │       ├── skills.py      # Skill management
│   │       └── tasks.py       # Task management
│   ├── security/              # Security module
│   │   ├── network.py         # SSRF protection
│   │   ├── path_guard.py      # Path traversal protection
│   │   ├── sanitizer.py       # Input validation
│   │   └── credentials.py     # Credential vault
│   ├── core/                  # Core services
│   │   ├── serve.py           # Multi-channel serve manager
│   │   └── daemon.py          # Daemon process management
│   ├── skills/                # Skill system
│   │   ├── base.py            # Skill base class
│   │   ├── loader.py          # Skill loader (dynamic + progressive)
│   │   ├── toolkit.py         # Skill toolkit
│   │   ├── conversation.py    # Skill conversation mode
│   │   └── builtin/           # Built-in skills (11 skills)
│   ├── providers/             # Provider system
│   │   ├── zai.py             # ZAI Provider
│   │   └── zai_detect.py      # Endpoint detection
│   ├── memory/                # Memory system
│   ├── workspace/             # Workspace system
│   ├── config/                # Configuration (40+ fields)
│   └── cli/                   # CLI application
│       ├── app.py             # Typer app
│       ├── serve_cmd.py       # Serve command
│       └── sidecar_cmd.py     # Sidecar command
├── tauri-app/                 # Tauri desktop app
│   ├── src/                   # React frontend
│   │   ├── App.tsx            # Main app
│   │   ├── components/        # UI components
│   │   └── index.css          # Tailwind styles
│   ├── src-tauri/             # Rust backend
│   │   ├── src/lib.rs         # Shell implementation
│   │   └── tauri.conf.json    # Tauri config
│   └── package.json           # npm dependencies
├── tests/                     # Test files (588 tests)
├── features/                  # Feature archive
├── pyproject.toml             # Project config
└── .env                       # Environment vars
```

## Critical Rules

### Must Follow

- Rule 1: **Async First** - All agent processing, LLM calls, skill execution must use async/await
- Rule 2: **Type Hints Required** - All functions must have complete type annotations
- Rule 3: **Pydantic for Data** - Use Pydantic models for all data validation
- Rule 4: **Settings from Env** - Configuration via Pydantic Settings, env vars take precedence
- Rule 5: **Model Prefix Routing** - Use provider prefix for model selection (zai/glm-5, gpt-4o)
- Rule 6: **Streaming Support** - New features should support streaming when applicable
- Rule 7: **Security First** - Validate inputs, sanitize outputs, protect credentials

### Must Avoid

- Anti-pattern 1: **Synchronous LLM calls** - Always use acompletion
- Anti-pattern 2: **Hardcoded API keys** - Use settings or environment variables
- Anti-pattern 3: **Blocking I/O** - Use async httpx instead of requests
- Anti-pattern 4: **Mutable default args** - Use None and create new instances
- Anti-pattern 5: **Unvalidated paths** - Always use PathGuard for file operations
- Anti-pattern 6: **Plaintext credentials** - Use CredentialVault for sensitive data

## Code Patterns

### Naming Conventions

- Files: `snake_case.py`
- Classes: `PascalCase` (e.g., `AgentLoop`, `SkillLoader`)
- Functions: `snake_case` (e.g., `get_zai_provider`, `detect_zai_endpoint`)
- Private: `_leading_underscore` (e.g., `_call_llm`, `_get_provider_kwargs`)
- Async generators: `*_stream` suffix (e.g., `process_stream`, `_stream_llm`)

### Import Patterns

```python
# Standard library first
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator

# Third-party next
from litellm import acompletion
from pydantic import Field

# Local imports last
from anyclaw.config.settings import settings
from .history import ConversationHistory
```

### Error Handling

```python
# Standard error handling pattern
try:
    response = await acompletion(**kwargs)
    return response.choices[0].message.content
except Exception as e:
    return f"Error: {str(e)}"
```

### Streaming Pattern

```python
# Streaming output pattern
async def process_stream(self, user_input: str) -> AsyncGenerator[str, None]:
    """Stream response chunks"""
    self.history.add_user_message(user_input)

    full_response = []
    async for chunk in self._stream_llm(messages):
        full_response.append(chunk)
        yield chunk

    self.history.add_assistant_message("".join(full_response))
```

### Provider Pattern

```python
# Get provider-specific kwargs based on model prefix
def _get_provider_kwargs(model: str) -> Dict[str, Any]:
    if model.startswith("zai/"):
        from anyclaw.providers.zai import get_zai_provider
        provider = get_zai_provider()
        return provider.get_completion_kwargs(model)
    return {}
```

### Skill Pattern

```python
# Skill implementation pattern
class MySkill(Skill):
    """Skill description"""

    async def execute(self, **kwargs) -> str:
        """Execute skill

        Args:
            param1: Description

        Returns:
            Result string
        """
        # Implementation
        return result
```

### Security Pattern

```python
# Path validation pattern
from anyclaw.security.path_guard import PathGuard

guard = PathGuard(workspace_path)
safe_path = guard.validate(user_provided_path)  # Raises if invalid
```

## Testing Patterns

### Unit Tests

- Test file location: `tests/` directory
- Naming: `test_{module}.py`
- Async tests: Use `@pytest.mark.asyncio` decorator

```python
@pytest.mark.asyncio
async def test_process_stream():
    agent = AgentLoop(enable_tools=False)
    chunks = []
    async for chunk in agent.process_stream("test"):
        chunks.append(chunk)
    assert len(chunks) > 0
```

### Fixtures

```python
@pytest.fixture
def mock_settings():
    with patch("anyclaw.config.settings") as mock:
        mock.zai_api_key = "test-key"
        yield mock
```

## Provider Configuration

### ZAI Endpoints

| Endpoint | Base URL | Use Case |
|----------|----------|----------|
| coding-global | api.z.ai/api/paas/v4 | GLM Coding Plan (Global) |
| coding-cn | open.bigmodel.cn/api/paas/v4 | GLM Coding Plan (China) |
| global | api.z.ai/api/paas/v4 | Standard Z.AI API |
| cn | open.bigmodel.cn/api/paas/v4 | Z.AI China API |

### Model Routing

```python
# Model prefix determines provider
"zai/glm-5"        → ZAI Provider
"zai/glm-4.7"      → ZAI Provider
"gpt-4o-mini"      → OpenAI (default)
"claude-3-5-sonnet" → Anthropic
```

## Configuration Reference

### Key Settings

```python
# Agent settings
agent_name: str = "AnyClaw"
agent_role: str = "You are a helpful AI assistant..."

# LLM settings
llm_provider: str = "openai"
llm_model: str = "gpt-4o-mini"
llm_temperature: float = 0.7
llm_max_tokens: int = 2000

# Streaming settings
stream_enabled: bool = True
stream_buffer_size: int = 10

# Memory settings
memory_enabled: bool = True
memory_max_chars: int = 10000
memory_daily_load_days: int = 2

# Token settings
token_soft_limit: int = 100000
token_hard_limit: int = 200000

# Security settings
restrict_to_workspace: bool = True
ssrf_enabled: bool = True
credential_encryption: bool = True
```

## Recent Changes

| Date | Feature | Impact |
|------|---------|--------|
| 2026-03-21 | feat-smart-file-search | Intelligent file search with heuristics and context awareness |
| 2026-03-20 | feat-security-config-enhancement | Enhanced security config with allow_all_access |
| 2026-03-20 | feat-desktop-app-phase3 | Tauri desktop app Phase 3 complete |
| 2026-03-20 | feat-session-archive | Session archiving system |
| 2026-03-20 | feat-input-sanitizer | Input validation and sanitization |
| 2026-03-20 | feat-path-guard | Path traversal protection |
| 2026-03-20 | feat-credential-vault | Secure credential management |
| 2026-03-20 | feat-skill-conversation-mode | Skill conversation mode |
| 2026-03-20 | feat-skill-progressive-loading | Progressive skill loading |
| 2026-03-20 | feat-skill-dynamic-loader | Dynamic skill loading |
| 2026-03-20 | feat-desktop-app | Tauri desktop app (Phase 1-2, 80%) |
| 2026-03-20 | feat-multi-agent | Multi-Agent system (OpenClaw-style) |
| 2026-03-20 | feat-session-manager | SessionManager with JSONL persistence |
| 2026-03-20 | feat-subagent | SubAgent background tasks (SpawnTool) |
| 2026-03-20 | feat-message-tool | MessageTool for cross-session messaging |
| 2026-03-20 | feat-cron | Cron scheduling (at/every/cron) |
| 2026-03-20 | feat-im-channels | Channel integration (Discord/Feishu) |
| 2026-03-19 | feat-serve-mode | Multi-channel serve mode with daemon support |
| 2026-03-19 | feat-ssrf-guard | SSRF protection module |
| 2026-03-18 | feat-streaming-output | Added streaming output support |
| 2026-03-18 | feat-mvp-* | MVP implementation complete |

## CLI Commands Reference

```bash
# Chat
anyclaw chat [--stream/--no-stream] [--model MODEL]

# Multi-channel Serve Mode
anyclaw serve                    # Foreground mode
anyclaw serve --debug            # Debug mode (detailed logs)
anyclaw serve --verbose          # Verbose output
anyclaw serve --quiet            # Quiet mode (warnings only)
anyclaw serve --daemon           # Background daemon mode
anyclaw serve --status           # Check daemon status
anyclaw serve --stop             # Stop daemon
anyclaw serve --logs             # Follow daemon logs

# Configuration
anyclaw config --show
anyclaw config --show --provider zai

# Onboarding
anyclaw onboard --auth-choice zai-coding-global
anyclaw onboard detect-zai --api-key KEY --save

# Workspace
anyclaw setup [--workspace PATH]
anyclaw workspace status

# Token
anyclaw token count --text "..."
anyclaw token status

# Persona
anyclaw persona list
anyclaw persona show default

# Memory
anyclaw memory show
anyclaw memory log "entry"
anyclaw memory search "keyword"
anyclaw memory stats

# Compress
anyclaw compress status
anyclaw compress run

# Agent (Multi-Agent)
anyclaw agent list
anyclaw agent create <name>
anyclaw agent switch <name>
```

## Update Log

- 2026-03-20: Completed 40 features, 588 tests passing
- 2026-03-20: Added feat-security-config-enhancement - Enhanced security config
- 2026-03-20: Added feat-desktop-app-phase3 - Tauri desktop app Phase 3
- 2026-03-20: Added feat-session-archive - Session archiving system
- 2026-03-20: Added feat-input-sanitizer - Input validation and sanitization
- 2026-03-20: Added feat-path-guard - Path traversal protection
- 2026-03-20: Added feat-credential-vault - Secure credential management
- 2026-03-20: Added feat-skill-conversation-mode - Skill conversation mode
- 2026-03-20: Added feat-skill-progressive-loading - Progressive skill loading
- 2026-03-20: Added feat-skill-dynamic-loader - Dynamic skill loading
- 2026-03-20: Added feat-desktop-app - Tauri desktop app (80%)
- 2026-03-20: Added feat-multi-agent - Multi-Agent system (OpenClaw-style)
- 2026-03-20: Added feat-session-manager - SessionManager (nanobot compatible)
- 2026-03-20: Added feat-subagent - SubAgent background tasks
- 2026-03-20: Added feat-message-tool - MessageTool cross-session messaging
- 2026-03-20: Added feat-cron - Cron scheduling (at/every/cron)
- 2026-03-20: Added feat-im-channels - Channel integration complete
- 2026-03-19: Added feat-serve-mode - Multi-channel serve mode
- 2026-03-19: Added feat-ssrf-guard - SSRF protection
- 2026-03-18: Initial MVP features completed (5 features)
- 2026-03-18: Project context created
