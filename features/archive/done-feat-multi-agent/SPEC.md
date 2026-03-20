# feat-multi-agent

**状态**: ✅ 已完成
**完成时间**: 2026-03-20
**优先级**: 90
**大小**: L
**提交**: 9c38ef8, 5f69a15

## 描述

实现 Multi-Agent 多代理系统，支持多 Agent 管理、Identity 人设、独立 Workspace，采用 OpenClaw 风格架构。

## 价值点

1. **Identity 人设管理**
   - AgentIdentity: Name, Creature, Vibe, Emoji, Avatar
   - IDENTITY.md 模板化创建
   - 动态身份切换

2. **Agent 管理**
   - 创建/删除/列出/启用/切换 Agent
   - 独立工作区 (files/, skills/, config/)
   - 工具目录 (tools.json)
   - 会话计数追踪

3. **Workspace 隔离**
   - AgentWorkspace 独立文件系统
   - 相对/绝对路径支持
   - 自动创建目录结构

4. **CLI 命令**
   - `agents list` - 列出所有 Agent
   - `agents create` - 创建新 Agent
   - `agents delete` - 删除 Agent
   - `agents switch` - 切换默认 Agent
   - `agents identity` - 查看/编辑身份
   - `agents tools` - 列出工具目录
   - `agents status` - 查看管理器状态

## 实现文件

- `anyclaw/agents/__init__.py` - 模块导出
- `anyclaw/agents/identity.py` - IdentityManager, AgentIdentity
- `anyclaw/agents/manager.py` - AgentManager, Agent, AgentWorkspace, AgentToolCatalog
- `anyclaw/agents/cli/agents_cmd.py` - CLI 命令实现
- `anyclaw/templates/IDENTITY.md` - 身份模板
- `anyclaw/templates/SOUL.md` - 人设模板

## 目录结构

```
~/.anyclaw/agents/
├── default/
│   ├── IDENTITY.md      # 身份定义
│   ├── SOUL.md          # 人设模板
│   ├── workspace/
│   │   ├── files/       # 文件存储
│   │   ├── skills/      # 技能目录
│   │   └── config/      # 配置文件
│   └── tools.json       # 工具目录
├── assistant/
│   └── ...
└── researcher/
    └── ...
```

## 使用示例

### CLI 命令

```bash
# 列出所有 Agent
anyclaw agents list

# 创建新 Agent
anyclaw agents create assistant --name "小助手" --creature "猫" --vibe "友好"

# 切换默认 Agent
anyclaw agents switch assistant

# 查看身份
anyclaw agents identity

# 编辑身份
anyclaw agents identity --edit

# 列出工具
anyclaw agents tools

# 删除 Agent
anyclaw agents delete old_agent
```

### Python API

```python
from anyclaw.agents import AgentManager, IdentityManager

# 创建管理器
manager = AgentManager(agents_dir="~/.anyclaw/agents")

# 创建新 Agent
agent = manager.create_agent(
    id="assistant",
    name="小助手",
    creature="猫",
    vibe="友好热情"
)

# 列出所有 Agent
agents = manager.list_agents()

# 切换默认 Agent
manager.switch_agent("assistant")

# 获取当前 Agent
current = manager.get_current_agent()

# 获取 Agent 工作区
workspace = agent.workspace
workspace.get_files_path()  # ~/.../files/
workspace.get_skills_path() # ~/.../skills/
```

## Identity 模板

### IDENTITY.md

```markdown
# Identity

name: 小助手
creature: 猫
vibe: 友好热情，乐于助人
emoji: 🐱
avatar: https://example.com/avatar.png
```

### SOUL.md

```markdown
# Soul

你是一个友好热情的 AI 助手...

## 性格特点
- 热情开朗
- 乐于助人
- 专业可靠

## 沟通风格
- 简洁明了
- 友善温和
```

## 数据结构

```python
@dataclass
class AgentIdentity:
    name: str
    creature: Optional[str] = None
    vibe: Optional[str] = None
    emoji: Optional[str] = None
    avatar: Optional[str] = None

@dataclass
class AgentWorkspace:
    base_path: Path
    files_path: Path
    skills_path: Path
    config_path: Path

@dataclass
class Agent:
    id: str
    identity: AgentIdentity
    workspace: AgentWorkspace
    tool_catalog: AgentToolCatalog
    enabled: bool = True
    session_count: int = 0
```

## 架构图

```
┌─────────────────────────────────────────────┐
│              AgentManager                    │
├─────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │ Agent 1 │  │ Agent 2 │  │ Agent 3 │     │
│  │ (默认)  │  │         │  │         │     │
│  └────┬────┘  └────┬────┘  └────┬────┘     │
│       │            │            │           │
│       ▼            ▼            ▼           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │Workspace│  │Workspace│  │Workspace│     │
│  ├─────────┤  ├─────────┤  ├─────────┤     │
│  │Identity │  │Identity │  │Identity │     │
│  ├─────────┤  ├─────────┤  ├─────────┤     │
│  │  Tools  │  │  Tools  │  │  Tools  │     │
│  └─────────┘  └─────────┘  └─────────┘     │
└─────────────────────────────────────────────┘
```

## 与 OpenClaw 对比

| 特性 | OpenClaw | AnyClaw | 状态 |
|------|----------|---------|------|
| 多 Agent 管理 | ✅ | ✅ | 完全兼容 |
| Identity 人设 | ✅ | ✅ | 完全兼容 |
| 独立 Workspace | ✅ | ✅ | 完全兼容 |
| 工具目录 | ✅ | ✅ | 完全兼容 |
| CLI 管理 | ✅ | ✅ | 完全兼容 |
| IDENTITY.md 模板 | ✅ | ✅ | 完全兼容 |
