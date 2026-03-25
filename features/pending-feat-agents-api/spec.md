# feat-agents-api: 多 Agent 后端 API 完善

## 概述

完善 AnyClaw 的多 Agent 后端 API，将现有的 AgentManager 集成到 FastAPI 路由中，替换 mock 数据，实现完整的 CRUD 操作。

## 背景

当前状态：
- `AgentManager` 和 `IdentityManager` 已完整实现
- API 路由 `/api/agents` 存在，但返回 mock 数据
- AgentManager 未注入到 API 依赖系统

## 用户价值点

### VP1: AgentManager 注入 API

**场景**: API 获取真实 Agent 数据
```gherkin
Given AgentManager 已在 sidecar 启动时初始化
When 调用 GET /api/agents
Then 返回 AgentManager 中真实的 agent 列表
And 每个 agent 包含 id, name, emoji, avatar, enabled 字段
```

### VP2: 创建 Agent API

**场景**: 通过 API 创建新 Agent
```gherkin
Given 用户有创建 Agent 的权限
When 调用 POST /api/agents
    {
      "name": "Research Assistant",
      "creature": "AI",
      "vibe": "helpful",
      "emoji": "🔬",
      "workspace": ""
    }
Then 返回 201 和创建的 agent 信息
And agent 目录在 ~/.anyclaw/workspace/agents/ 下创建
And IDENTITY.md 和 SOUL.md 模板文件生成
```

### VP3: 更新/删除 Agent API

**场景**: 更新 Agent 配置
```gherkin
Given Agent "researcher" 已存在
When 调用 PATCH /api/agents/researcher
    {"name": "Research Bot", "emoji": "🤖"}
Then 返回更新后的 agent 信息
And IDENTITY.md 文件更新

场景: 删除 Agent
```gherkin
Given Agent "researcher" 已存在
When 调用 DELETE /api/agents/researcher
Then 返回 204 No Content
And agent 目录被删除
```

### VP4: Agent 切换/启用禁用

**场景**: 切换默认 Agent
```gherkin
Given 多个 Agent 存在
When 调用 POST /api/agents/researcher/activate
Then researcher 成为默认 agent
And 后续聊天使用该 agent

场景: 禁用 Agent
```gherkin
Given Agent "researcher" 已启用
When 调用 POST /api/agents/researcher/deactivate
Then researcher 被禁用
And agent.enabled = false
```

## API 端点设计

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/agents | 列出所有 agent |
| POST | /api/agents | 创建新 agent |
| GET | /api/agents/{id} | 获取单个 agent |
| PATCH | /api/agents/{id} | 更新 agent |
| DELETE | /api/agents/{id} | 删除 agent |
| POST | /api/agents/{id}/activate | 激活为默认 |
| POST | /api/agents/{id}/deactivate | 禁用 agent |

## 技术方案

### 1. 依赖注入改造

修改 `api/deps.py`:
```python
_agent_manager: Optional[AgentManager] = None

def set_agent_manager(manager: AgentManager) -> None:
    global _agent_manager
    _agent_manager = manager

def get_agent_manager() -> AgentManager:
    if _agent_manager is None:
        raise RuntimeError("AgentManager not initialized")
    return _agent_manager
```

### 2. sidecar_cmd.py 初始化

```python
# 创建 AgentManager
identity_manager = IdentityManager(workspace_path)
agent_manager = AgentManager(workspace_path, identity_manager)
await agent_manager.load_all_agents()

# 注入到 API
from anyclaw.api.deps import set_agent_manager
set_agent_manager(agent_manager)
```

### 3. API 路由完善

```python
# routes/agents.py
@router.post("", response_model=AgentInfo, status_code=201)
async def create_agent(data: CreateAgentRequest):
    manager = get_agent_manager()
    agent = manager.create_agent(
        name=data.name,
        creature=data.creature,
        vibe=data.vibe,
        emoji=data.emoji,
        workspace=data.workspace,
    )
    return AgentInfo.from_agent(agent)
```

## 验收标准

- [ ] GET /api/agents 返回真实数据
- [ ] POST /api/agents 创建成功
- [ ] PATCH /api/agents/{id} 更新成功
- [ ] DELETE /api/agents/{id} 删除成功
- [ ] activate/deactivate 功能正常
- [ ] 单元测试覆盖
- [ ] API 文档更新

## 依赖

无

## 阻塞

- feat-agents-ui（前端需要此 API）
