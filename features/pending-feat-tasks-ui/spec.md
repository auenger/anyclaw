# feat-tasks-ui

## 概述

为 Tauri 桌面应用添加 Tasks 页面，提供定时任务的可视化管理界面。

## 背景

当前 AnyClaw 桌面应用没有 Tasks 页面，用户无法通过 UI 管理定时任务。

## 用户价值点

### VP5: 前端 UI

完整的任务管理界面。

**Gherkin 场景:**

```gherkin
Feature: 前端 Tasks 页面

  Scenario: 显示任务列表
    Given 用户访问 Tasks 页面
    Then 左侧显示所有任务列表
    And 每个任务显示名称、状态标签、调度信息

  Scenario: 任务状态标签
    Given 任务列表中有多个任务
    Then active 任务显示绿色 "Active" 标签
    And paused 任务显示黄色 "Paused" 标签
    And completed 任务显示灰色 "Completed" 标签

  Scenario: 空状态展示
    Given 没有任何任务
    Then 显示空状态图标和提示文字
    And 显示 "创建第一个任务" 提示

  Scenario: 查看任务详情
    Given 任务列表有任务
    When 用户点击任务
    Then 右侧显示任务详情面板
    And 显示基本信息 (名称、描述、Agent)
    And 显示调度配置 (类型、值、下次运行时间)
    And 显示执行历史 (最近 20 条)

  Scenario: 创建新任务入口
    Given 用户在任务列表页
    When 用户点击 "+" 按钮
    Then 显示任务创建表单

  Scenario: 创建任务 - 填写表单
    Given 用户在创建表单
    When 用户填写名称、描述、选择 Agent
    And 填写 Prompt
    And 选择调度类型 "interval"
    And 输入间隔 "30" 分钟
    And 点击 "创建" 按钮
    Then 任务创建成功
    And 返回任务详情视图

  Scenario: 创建任务 - cron 类型
    Given 用户在创建表单
    When 选择调度类型 "cron"
    And 输入 cron 表达式 "0 9 * * *"
    And 选择时区 "Asia/Shanghai"
    And 点击 "创建" 按钮
    Then 任务创建成功

  Scenario: 创建任务 - once 类型
    Given 用户在创建表单
    When 选择调度类型 "once"
    And 选择未来日期时间
    And 点击 "创建" 按钮
    Then 任务创建成功

  Scenario: 创建任务验证
    Given 用户在创建表单
    When 必填字段未填写
    And 点击 "创建" 按钮
    Then 显示验证错误提示

  Scenario: 编辑任务
    Given 用户在任务详情页
    When 用户点击编辑按钮
    Then 显示任务编辑表单
    And Agent 选择器禁用 (不可更改)
    And 修改后点击保存

  Scenario: 克隆任务
    Given 用户在任务详情页
    When 用户点击克隆按钮
    Then 创建新任务
    And 名称添加 "(copy)" 后缀
    And 显示新任务详情

  Scenario: 暂停/恢复任务
    Given 任务状态为 active
    When 用户点击暂停按钮
    Then 任务状态变为 paused
    And 按钮变为恢复图标

  Scenario: 手动执行任务
    Given 用户在任务详情页
    When 用户点击执行按钮
    Then 立即执行任务
    And 刷新执行历史

  Scenario: 删除任务
    Given 用户在任务详情页
    When 用户点击删除按钮
    Then 显示删除确认对话框
    And 确认后删除任务
    And 返回空详情状态

  Scenario: 执行历史展示
    Given 任务有执行历史
    Then 显示执行记录列表
    And 每条记录显示: 状态图标、执行时间、耗时
    And 失败记录显示红色错误信息

  Scenario: 国际化 - 中文
    Given 系统语言为中文
    Then 所有标签和按钮显示中文

  Scenario: 国际化 - 英文
    Given 系统语言为英文
    Then 所有标签和按钮显示英文
```

## 技术方案

### 页面布局

```
┌─────────────────────────────────────────────────────┐
│  AppSidebar  │  SidePanel (Tasks)  │  Detail Panel  │
│              │                     │                │
│   Chat       │  ┌──────────────┐   │  Task Detail   │
│   Agents     │  │ + New Task   │   │                │
│   Tasks  ←───│  ├──────────────┤   │  Name          │
│   Memory     │  │ Task 1       │   │  Agent         │
│   Logs       │  │ Task 2       │   │  Schedule      │
│   Settings   │  │ Task 3       │   │  Prompt        │
│              │  │ ...          │   │  Run History   │
│              │  └──────────────┘   │                │
│              │                     │  [Edit][Clone] │
│              │                     │  [Pause][Run]  │
│              │                     │  [Delete]      │
└─────────────────────────────────────────────────────┘
```

### 组件结构

```
web/src/pages/Tasks.tsx
├── Tasks()              # 主页面组件
│   ├── SidePanel        # 左侧任务列表
│   │   ├── Header       # 标题 + 新建按钮
│   │   └── TaskList     # 任务列表
│   │       └── TaskItem # 单个任务卡片
│   └── DetailPanel      # 右侧详情/表单
│       ├── TaskDetail   # 任务详情
│       │   ├── Header   # 名称 + 操作按钮
│       │   ├── InfoGrid # 基本信息
│       │   ├── Prompt   # Prompt 展示
│       │   └── RunLogs  # 执行历史
│       └── TaskForm     # 创建/编辑表单
│           ├── NameInput
│           ├── DescInput
│           ├── AgentSelect
│           ├── PromptInput
│           └── ScheduleInput
└── components/
    └── StatusBadge      # 状态标签组件
```

### API 集成

```typescript
// web/src/api/client.ts (扩展)

// 任务管理
export async function getCronJobs(enabled?: boolean): Promise<CronJob[]>
export async function createCronJob(data: CreateJobRequest): Promise<CronJob>
export async function getCronJob(id: string): Promise<CronJob>
export async function updateCronJob(id: string, data: UpdateJobRequest): Promise<CronJob>
export async function deleteCronJob(id: string): Promise<void>
export async function cloneCronJob(id: string): Promise<CronJob>
export async function runCronJob(id: string): Promise<RunResult>
export async function getCronJobLogs(id: string, limit?: number): Promise<RunLog[]>

// 类型定义
interface CronJob {
  id: string
  name: string
  description: string | null
  agent_id: string
  chat_id: string
  prompt: string
  enabled: boolean
  schedule: {
    type: 'interval' | 'cron' | 'once'
    value_ms?: number
    expr?: string
    tz?: string
    at_ms?: number
  }
  state: {
    next_run_at_ms: number | null
    last_run_at_ms: number | null
    consecutive_failures: number
  }
  created_at_ms: number
}

interface RunLog {
  id: number
  job_id: string
  run_at_ms: number
  duration_ms: number
  status: 'success' | 'error'
  result: string | null
  error: string | null
}
```

### i18n 翻译

```typescript
// web/src/i18n/zh.ts
tasks: {
  title: '定时任务',
  createTask: '创建任务',
  noTasks: '暂无定时任务',
  noTasksHint: '点击右上角 + 创建第一个任务',
  selectTask: '选择一个任务查看详情',
  name: '任务名称',
  description: '描述',
  agent: '关联 Agent',
  prompt: '执行 Prompt',
  scheduleType: '调度类型',
  interval: '固定间隔',
  cron: 'Cron 表达式',
  once: '一次性',
  intervalMinutes: '间隔 (分钟)',
  cronExpression: 'Cron 表达式',
  cronHelp: '例如: 0 9 * * * (每天 9:00)',
  runAt: '执行时间',
  status: '状态',
  nextRun: '下次执行',
  lastRun: '上次执行',
  recentRuns: '最近执行',
  noRuns: '暂无执行记录',
  clone: '克隆',
  runNow: '立即执行',
  enable: '启用',
  disable: '暂停',
  confirmDelete: '确定删除此任务吗？',
  createTitle: '创建定时任务',
  editTitle: '编辑任务',
  // ...
}
```

## 任务分解

### Phase 1: API 集成 (0.5 天)
- [ ] 扩展 `api/client.ts` 添加 cron API
- [ ] 定义 TypeScript 类型
- [ ] 测试 API 调用

### Phase 2: 基础布局 (0.5 天)
- [ ] 创建 `Tasks.tsx` 页面
- [ ] 实现左右布局
- [ ] 创建 `SidePanel` 任务列表

### Phase 3: 任务列表 (0.5 天)
- [ ] 实现 `TaskList` 组件
- [ ] 实现 `TaskItem` 组件
- [ ] 实现 `StatusBadge` 组件
- [ ] 实现空状态展示

### Phase 4: 任务详情 (0.5 天)
- [ ] 实现 `TaskDetail` 组件
- [ ] 显示基本信息
- [ ] 显示调度配置
- [ ] 显示 Prompt
- [ ] 显示执行历史

### Phase 5: 任务表单 (1 天)
- [ ] 实现 `TaskForm` 组件
- [ ] 名称/描述输入
- [ ] Agent 选择器
- [ ] Prompt 输入
- [ ] 调度类型切换
- [ ] Interval 输入 (分钟)
- [ ] Cron 输入 + 帮助
- [ ] Once 日期时间选择
- [ ] 表单验证
- [ ] 创建/编辑切换

### Phase 6: 操作功能 (0.5 天)
- [ ] 实现编辑功能
- [ ] 实现克隆功能
- [ ] 实现暂停/恢复
- [ ] 实现手动执行
- [ ] 实现删除 + 确认

### Phase 7: i18n (0.25 天)
- [ ] 添加中文翻译
- [ ] 添加英文翻译

### Phase 8: 测试 (0.25 天)
- [ ] E2E 测试: 任务 CRUD
- [ ] E2E 测试: 任务执行

## 验收标准

- [ ] 所有 Gherkin 场景通过
- [ ] UI 与 YouClaw 风格一致
- [ ] 中英文国际化完整
- [ ] 响应式布局正常

## 预计工作量

2 天

## 依赖

- feat-cron-api (需要 REST API)

## 父特性

feat-tasks-alignment
