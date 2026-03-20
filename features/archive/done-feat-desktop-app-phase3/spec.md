# feat-desktop-app-phase3

> **ID**: feat-desktop-app-phase3
> **Status**: pending
> **Priority**: 75
> **Size**: L
> **Created**: 2026-03-20
> **Dependencies**: feat-desktop-app (Phase 1-2)

## 概述

完成 Tauri 桌面应用 Phase 3 - React 前端 UI 完善，实现完整的桌面应用用户体验。

## 背景

Phase 1-2 已完成：
- ✅ FastAPI + SSE 后端 (13 个端点)
- ✅ Tauri Shell 进程管理
- ✅ 基础聊天 UI (80%)
- ✅ Tailwind CSS + shadcn/ui

Phase 3 需要完成：
- SSE 实时消息流
- Settings 页面
- Skills 管理页面
- Tasks 页面

---

## 用户价值点

### VP1: SSE 实时消息流

**价值描述**: 实时接收 AI 响应，无需等待完整响应，提升用户体验。

**验收场景**:

```gherkin
Feature: SSE 实时消息流

  Scenario: 发送消息并接收流式响应
    Given 用户在聊天界面
    And 后端 Sidecar 已启动
    When 用户发送消息 "你好"
    Then 消息逐字显示在聊天窗口
    And 显示打字动画效果

  Scenario: 流式响应中断处理
    Given 正在接收流式响应
    When 用户点击停止按钮
    Then 响应立即停止
    And 显示已接收的部分内容

  Scenario: 网络断开重连
    Given 正在接收流式响应
    When 网络断开
    Then 显示重连提示
    And 自动尝试重连
    And 重连成功后继续接收
```

### VP2: Settings 页面

**价值描述**: 提供可视化配置管理，无需手动编辑配置文件。

**验收场景**:

```gherkin
Feature: Settings 页面

  Scenario: 查看 LLM 配置
    Given 用户打开 Settings 页面
    Then 显示当前 LLM 配置
    And 显示 model、temperature、max_tokens 等选项

  Scenario: 修改模型配置
    Given 用户在 Settings 页面
    When 用户选择模型 "gpt-4o"
    And 点击保存
    Then 配置立即生效
    And 显示保存成功提示

  Scenario: 配置 API Key
    Given 用户在 Settings 页面
    When 用户输入 API Key
    And 点击保存
    Then API Key 被安全存储
    And 显示为遮蔽字符

  Scenario: 重置配置
    Given 用户在 Settings 页面
    When 用户点击 "重置为默认"
    Then 所有配置恢复默认值
    And 显示确认提示
```

### VP3: Skills 管理页面

**价值描述**: 可视化管理技能，支持查看、启用/禁用、热重载。

**验收场景**:

```gherkin
Feature: Skills 管理页面

  Scenario: 查看技能列表
    Given 用户打开 Skills 页面
    Then 显示所有可用技能
    And 每个技能显示名称、描述、状态

  Scenario: 查看技能详情
    Given 用户在 Skills 页面
    When 用户点击技能 "weather"
    Then 显示技能详细描述
    And 显示技能参数定义
    And 显示使用示例

  Scenario: 热重载技能
    Given 用户修改了技能文件
    When 用户点击 "重载技能"
    Then 技能被重新加载
    And 显示重载成功提示

  Scenario: 搜索技能
    Given 用户在 Skills 页面
    When 用户输入搜索关键词 "file"
    Then 显示名称或描述匹配的技能
```

### VP4: Tasks 页面

**价值描述**: 管理后台任务（SubAgent、Cron），查看执行状态。

**验收场景**:

```gherkin
Feature: Tasks 页面

  Scenario: 查看运行中的任务
    Given 有 SubAgent 正在执行
    When 用户打开 Tasks 页面
    Then 显示所有运行中的任务
    And 每个任务显示 ID、状态、开始时间

  Scenario: 查看任务详情
    Given 用户在 Tasks 页面
    When 用户点击任务 ID
    Then 显示任务详细输出
    And 显示执行日志

  Scenario: 取消任务
    Given 有正在运行的任务
    When 用户点击 "取消" 按钮
    Then 任务被终止
    And 显示已取消状态

  Scenario: 查看 Cron 任务
    Given 用户配置了定时任务
    When 用户切换到 "Cron" 标签
    Then 显示所有定时任务
    And 显示下次执行时间
```

---

## 技术设计

### 目录结构

```
tauri-app/src/
├── App.tsx                 # 主应用 (更新路由)
├── components/
│   ├── chat/
│   │   ├── ChatWindow.tsx  # 聊天窗口 (已有)
│   │   ├── MessageList.tsx # 消息列表 (更新 SSE)
│   │   └── InputArea.tsx   # 输入区域 (已有)
│   ├── settings/
│   │   ├── SettingsPage.tsx    # 设置页面 (NEW)
│   │   ├── LLMSettings.tsx     # LLM 配置 (NEW)
│   │   └── ProviderSettings.tsx # Provider 配置 (NEW)
│   ├── skills/
│   │   ├── SkillsPage.tsx      # 技能页面 (NEW)
│   │   ├── SkillCard.tsx       # 技能卡片 (NEW)
│   │   └── SkillDetail.tsx     # 技能详情 (NEW)
│   └── tasks/
│       ├── TasksPage.tsx       # 任务页面 (NEW)
│       ├── SubAgentList.tsx    # SubAgent 列表 (NEW)
│       └── CronList.tsx        # Cron 列表 (NEW)
├── hooks/
│   ├── useSSE.ts           # SSE Hook (NEW)
│   ├── useSettings.ts      # Settings Hook (NEW)
│   └── useTasks.ts         # Tasks Hook (NEW)
├── lib/
│   ├── api.ts              # API 客户端 (更新)
│   └── sse.ts              # SSE 客户端 (NEW)
└── types/
    └── index.ts            # 类型定义 (更新)
```

### API 端点 (已实现)

| 端点 | 方法 | 用途 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/agents` | GET | 列出 Agents |
| `/api/agents/{id}/chat` | POST | 发送消息 |
| `/api/stream` | GET | SSE 流式消息 |
| `/api/skills` | GET | 列出技能 |
| `/api/tasks` | GET | 列出任务 |
| `/api/config` | GET/PUT | 配置管理 |

### SSE 事件格式

```typescript
interface SSEEvent {
  type: 'message_start' | 'content_delta' | 'message_end' | 'error';
  data: {
    content?: string;
    message_id?: string;
    error?: string;
  };
}
```

---

## 依赖

- feat-desktop-app (Phase 1-2) - 已完成 80%

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| SSE 兼容性 | 部分浏览器不支持 | 使用 polyfill，降级为轮询 |
| Tauri 热更新 | 开发效率 | 使用 Vite HMR |
| 状态管理复杂度 | 代码可维护性 | 使用 React Context 或 Zustand |

---

## 后续扩展

- Agent 切换
- 多会话管理
- 主题切换 (暗色/亮色)
- 国际化 (i18n)
