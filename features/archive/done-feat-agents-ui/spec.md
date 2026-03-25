# feat-agents-ui: Agents 页面前端优化

## 概述

优化 Tauri 桌面应用的 Agents 页面，连接后端真实 API，实现完整的 Agent CRUD 操作 UI。

## 背景

当前状态：
- 前端 Agents 页面使用 mock 数据
- 没有创建 Agent 功能
- 编辑/删除按钮未实现
- 未调用真实 API

## 依赖

- **feat-agents-api** - 后端 API 必须先完成

## 用户价值点

### VP1: 显示真实 Agent 列表

**场景**: 页面加载获取真实数据
```gherkin
Given 后端 API 可用
When 用户打开 Agents 页面
Then 显示 AgentManager 中的真实 agent 列表
And 显示每个 agent 的名称、emoji、描述
And 高亮当前激活的 agent
```

### VP2: 创建 Agent 表单

**场景**: 打开创建表单
```gherkin
Given 用户在 Agents 页面
When 点击 "+" 按钮
Then 弹出创建 Agent 对话框
And 显示名称、emoji、creature、vibe 输入字段

场景**: 提交创建
```gherkin
Given 创建表单已打开
When 填写名称 "Research Bot" 和 emoji "🔬"
And 点击创建按钮
Then 调用 POST /api/agents
And 新 agent 出现在列表中
And 显示成功提示
```

### VP3: 编辑 Agent

**场景**: 编辑 Agent 信息
```gherkin
Given Agent "Research Bot" 已存在
When 点击编辑按钮
Then 弹出编辑对话框，预填当前信息
When 修改名称为 "Research Assistant"
Then 调用 PATCH /api/agents/research_bot
And 列表中显示更新后的名称
```

### VP4: 删除 Agent

**场景**: 删除确认
```gherkin
Given Agent "Research Bot" 已存在
When 点击删除按钮
Then 弹出确认对话框 "确定删除 Research Bot？"
When 确认删除
Then 调用 DELETE /api/agents/research_bot
And agent 从列表中移除
```

## UI 设计

### 布局结构

```
┌─────────────────────────────────────────────────────┐
│ Agents Page                                         │
├─────────────────┬───────────────────────────────────┤
│ SidePanel       │ Detail Panel                      │
│ ┌─────────────┐ │ ┌───────────────────────────────┐ │
│ │ Agents  [+] │ │ │ Agent Name        [Edit][Del]│ │
│ ├─────────────┤ │ ├───────────────────────────────┤ │
│ │ 🤖 Default  │ │ │ ID: default                    │ │
│ │ 🔬 Research │ │ │ Model: glm-4.7                 │ │
│ │ 📝 Writer   │ │ │ Workspace: ~/.anyclaw/...      │ │
│ └─────────────┘ │ │ Emoji: 🤖                      │ │
│                 │ │                                │ │
│                 │ │ [Activate] [Deactivate]        │ │
│                 │ └───────────────────────────────┘ │
└─────────────────┴───────────────────────────────────┘
```

### 创建表单

```
┌─────────────────────────────────┐
│ Create New Agent                │
├─────────────────────────────────┤
│ Name *                          │
│ [___________________________]   │
│                                 │
│ Emoji                           │
│ [🤖] [Select...]                │
│                                 │
│ Creature                        │
│ [AI          ▼]                 │
│                                 │
│ Vibe                            │
│ [helpful     ▼]                 │
│                                 │
│ Workspace (optional)            │
│ [___________________________]   │
│                                 │
│         [Cancel]  [Create]      │
└─────────────────────────────────┘
```

## 技术方案

### 1. API Hook

```typescript
// hooks/useAgents.ts
export function useAgents() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)

  const fetchAgents = async () => {
    const res = await fetch('/api/agents')
    const data = await res.json()
    setAgents(data)
    setLoading(false)
  }

  const createAgent = async (data: CreateAgentRequest) => {
    const res = await fetch('/api/agents', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (res.ok) {
      await fetchAgents()
      return true
    }
    return false
  }

  // ... updateAgent, deleteAgent, activateAgent

  useEffect(() => { fetchAgents() }, [])

  return { agents, loading, createAgent, updateAgent, deleteAgent, activateAgent }
}
```

### 2. 组件结构

```
pages/Agents.tsx          # 主页面（改造）
  ├── components/agents/
  │   ├── AgentList.tsx       # Agent 列表
  │   ├── AgentDetail.tsx     # Agent 详情
  │   ├── CreateAgentDialog.tsx  # 创建对话框
  │   └── EditAgentDialog.tsx    # 编辑对话框
```

### 3. i18n 支持

```json
{
  "agents": {
    "title": "Agents",
    "createAgent": "Create Agent",
    "editAgent": "Edit Agent",
    "deleteAgent": "Delete Agent",
    "confirmDelete": "Are you sure you want to delete {name}?",
    "name": "Name",
    "emoji": "Emoji",
    "creature": "Creature",
    "vibe": "Vibe",
    "workspace": "Workspace",
    "activate": "Activate",
    "deactivate": "Deactivate"
  }
}
```

## 验收标准

- [ ] 页面加载显示真实 agent 列表
- [ ] 点击 "+" 打开创建表单
- [ ] 创建表单提交成功
- [ ] 点击编辑打开编辑表单
- [ ] 编辑提交成功更新列表
- [ ] 点击删除弹出确认
- [ ] 确认后删除成功
- [ ] 激活/禁用按钮功能正常
- [ ] 加载状态显示
- [ ] 错误处理友好提示

## 预计工作量

- API Hook: 30 分钟
- 组件开发: 1.5 小时
- i18n + 样式: 30 分钟
- **总计**: 约 2.5 小时
