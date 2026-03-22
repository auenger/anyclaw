# feat-ui-pages-i18n: 其他页面 + 国际化

## 概述

复刻 youclaw 的其他管理页面（Agents、Tasks、Memory、Logs、Settings）和国际化支持。

**依赖**: feat-ui-design-core

**注意**: 积分和账号登录功能暂不实现。

## 价值点

### 1. Agents 管理页面

**参考**: `reference/youclaw/web/src/pages/Agents.tsx`

- Agent 列表 (SidePanel)
  - Agent 卡片显示
  - 创建新 Agent 按钮
- Agent 详情面板
  - 基本配置（名称、描述、系统提示）
  - 模型选择
  - 技能绑定
  - 浏览器配置文件绑定
  - MCP Server 绑定
  - 删除确认
- Agent 表单
  - 创建/编辑表单
  - 输入验证
- 技能市场 (Marketplace)
  - 推荐技能展示
  - 安装对话框

### 2. Tasks 定时任务页面

**参考**: `reference/youclaw/web/src/pages/Tasks.tsx`

- 任务列表 (SidePanel)
  - 任务卡片（名称、状态、调度信息）
  - 状态徽章 (active/paused/completed)
  - 创建新任务按钮
- 任务详情面板
  - 任务信息显示（名称、描述、Agent、调度、下次运行时间）
  - 运行历史记录（状态、时间、耗时、错误信息）
  - 操作按钮（编辑、克隆、暂停/启用、立即运行、删除）
- 任务表单
  - 创建/编辑表单
  - 调度类型选择（interval, cron, once）
  - Agent 选择
  - 输入验证

### 3. Memory 记忆页面（完整功能）

**参考**: `reference/youclaw/web/src/pages/Memory.tsx`

- 记忆选择器 (SidePanel)
  - Global Memory（全局记忆）
  - Agent Memory 列表

- 记忆内容编辑
  - Markdown 编辑器
  - 保存/取消操作

- 右侧面板（可折叠）
  - **每日日志** (Daily Logs)
    - 按日期分组展示
    - 点击展开查看内容
  - **对话归档** (Conversation Archives)
    - 历史对话记录列表
    - 点击展开查看内容
  - **搜索** (Search)
    - 跨 Agent 记忆搜索
    - 搜索结果显示（Agent、类型、片段）

### 4. Logs 日志页面（完整功能）

**参考**: `reference/youclaw/web/src/pages/Logs.tsx`

- 顶部工具栏
  - 日期选择器
  - 分类过滤按钮组 (All/Agent/Tool/Task/System)
  - 级别下拉选择 (All/DEBUG/INFO/WARN/ERROR)
  - 搜索框
  - 实时状态指示器（今天时显示 Live 动画）

- 日志列表
  - 终端风格显示（黑色背景）
  - 时间戳 + 级别 + 分类 + Agent + 消息
  - 级别颜色编码
  - 分类徽章颜色
  - 点击展开查看 JSON 详情
  - 滚动到顶部加载更早日志（分页）
  - 自动滚动到底部（实时模式）

- SSE 实时更新
  - 今天的日志实时推送
  - 自动过滤匹配当前筛选条件

### 5. Settings 设置对话框（完整功能）

**参考**: `reference/youclaw/web/src/components/settings/SettingsDialog.tsx`

- 对话框布局
  - 左侧标签栏
  - 右侧内容区
  - 关闭按钮

- **General 面板** (`reference/youclaw/web/src/components/settings/GeneralPanel.tsx`)
  - 主题切换（Light/Dark/System）
  - 语言切换（English/中文）
  - 服务端口配置（Tauri only）
  - 保存/重启按钮

- **Models 面板** (`reference/youclaw/web/src/components/settings/ModelsPanel.tsx`)
  - 活跃模型选择器
    - 内置模型（云端，离线模式隐藏）
    - 自定义 API
  - 内置模型列表（云端模式）
  - 自定义模型列表
    - 添加/编辑/删除
    - 表单字段：名称、Model ID、API Key、Base URL
    - 表单验证

- **Skills 面板**（复用 Skills 页面）
  - 技能列表
  - 技能详情
  - 重载按钮

- **About 面板** (`reference/youclaw/web/src/components/settings/AboutPanel.tsx`)
  - 应用版本
  - 框架信息
  - GitHub 链接
  - 许可证信息

### 6. 国际化 (i18n)

**参考**: `reference/youclaw/web/src/i18n/`

- 语言支持
  - 中文 (zh.ts)
  - 英文 (en.ts)
- 类型定义 (types.ts)
- 上下文 (context.tsx)
- 语言切换
  - 设置页面
  - 自动检测系统语言
  - 持久化偏好

## 验收标准

```gherkin
Feature: 其他页面 + 国际化

  # ===== Agents 页面 =====
  Scenario: Agent 创建
    Given 用户在 Agents 页面
    When 用户点击 "创建 Agent" 按钮
    Then 显示创建表单
    When 用户填写信息并保存
    Then Agent 创建成功
    And 显示在列表中

  Scenario: Agent 技能绑定
    Given 用户在 Agent 详情页
    When 用户点击 "绑定技能"
    Then 显示技能选择器
    When 用户选择技能并保存
    Then 技能绑定成功

  # ===== Tasks 页面 =====
  Scenario: 定时任务创建
    Given 用户在 Tasks 页面
    When 用户点击 "创建任务" 按钮
    Then 显示任务表单
    When 用户选择 interval 类型并设置 5 分钟
    Then 任务每 5 分钟执行一次

  Scenario: 任务立即运行
    Given 用户在任务详情页
    When 用户点击 "立即运行" 按钮
    Then 任务开始执行
    And 运行历史中添加记录

  # ===== Memory 页面 =====
  Scenario: 查看 Global Memory
    Given 用户在 Memory 页面
    When 用户选择 "Global Memory"
    Then 显示全局记忆内容
    And 可编辑保存

  Scenario: 查看 Agent 每日日志
    Given 用户选择了某个 Agent
    When 用户点击右侧面板 "Daily Logs" 标签
    Then 显示按日期分组的日志列表
    When 用户点击某个日期
    Then 展开显示该日日志内容

  Scenario: 查看对话归档
    Given 用户选择了某个 Agent
    When 用户点击右侧面板 "Archives" 标签
    Then 显示历史对话归档列表
    When 用户点击某个归档
    Then 展开显示对话内容

  Scenario: 搜索记忆
    Given 用户在 Memory 页面
    When 用户在搜索框输入关键词并搜索
    Then 显示跨 Agent 的搜索结果
    And 结果包含 Agent、类型、内容片段

  # ===== Logs 页面 =====
  Scenario: 日志过滤
    Given 用户在 Logs 页面
    When 用户选择日期 "2024-03-20"
    And 选择分类 "Agent"
    And 选择级别 "INFO"
    Then 日志列表只显示该日期的 Agent 分类 INFO 及以上级别的日志

  Scenario: 日志实时更新
    Given 用户查看今天的日志
    Then 显示 "Live" 实时状态指示器
    When 后端产生新日志
    Then 日志列表自动更新
    And 自动滚动到底部

  Scenario: 日志详情展开
    Given 日志列表有多条日志
    When 用户点击某条日志
    Then 展开显示完整 JSON 详情
    When 用户再次点击
    Then 收起详情

  Scenario: 加载更早日志
    Given 日志列表已显示
    When 用户滚动到顶部
    Then 自动加载更早的日志
    And 保持滚动位置

  # ===== Settings 对话框 =====
  Scenario: 打开设置对话框
    Given 用户点击侧边栏用户菜单
    When 用户点击 "设置"
    Then 打开设置对话框
    And 默认显示 General 面板

  Scenario: 主题切换
    Given 用户在 General 面板
    When 用户选择 "Dark" 主题
    Then 界面切换为暗色主题
    And 偏好持久化

  Scenario: 语言切换
    Given 用户在 General 面板
    When 用户选择 "简体中文"
    Then 所有界面文字更新为中文
    And 偏好持久化

  Scenario: 添加自定义模型
    Given 用户在 Models 面板
    When 用户点击 "添加自定义模型"
    Then 显示添加对话框
    When 用户填写名称、Model ID、API Key 并保存
    Then 模型添加成功
    And 显示在自定义模型列表中

  Scenario: 切换活跃模型
    Given 用户有多个自定义模型
    When 用户点击某个模型的 "设为默认"
    Then 该模型变为活跃模型
    And 显示选中状态

  # ===== 国际化 =====
  Scenario: 语言切换
    Given 应用当前为中文
    When 用户在设置中切换为英文
    Then 所有界面文字更新为英文
    And 设置持久化

  Scenario: 语言持久化
    Given 用户上次设置为英文
    When 用户重新打开应用
    Then 界面显示为英文
```

## 技术实现

### i18n 结构

```typescript
// src/i18n/types.ts
export interface Translations {
  nav: {
    chat: string;
    agents: string;
    tasks: string;
    memory: string;
    logs: string;
    skills: string;
    channels: string;
  };
  chat: {
    welcome: string;
    placeholder: string;
    thinking: string;
    today: string;
    yesterday: string;
    older: string;
    noConversations: string;
    deleteChat: string;
    confirmDelete: string;
    // ...
  };
  tasks: {
    title: string;
    createTask: string;
    noTasks: string;
    noTasksHint: string;
    selectTask: string;
    agent: string;
    schedule: string;
    nextRun: string;
    lastRun: string;
    recentRuns: string;
    noRuns: string;
    // ...
  };
  memory: {
    title: string;
    memoryFile: string;
    dailyLogs: string;
    noLogs: string;
    noContent: string;
    writePlaceholder: string;
    loadFailed: string;
    // ...
  };
  logs: {
    title: string;
    live: string;
    selectDate: string;
    allCategories: string;
    categoryAgent: string;
    categoryTool: string;
    categoryTask: string;
    categorySystem: string;
    allLevels: string;
    searchLogs: string;
    noLogs: string;
    loadOlder: string;
    totalEntries: string;
  };
  settings: {
    title: string;
    general: string;
    models: string;
    about: string;
    appearance: string;
    language: string;
    dark: string;
    light: string;
    system: string;
    serverPort: string;
    portHint: string;
    activeModel: string;
    builtinProvider: string;
    customProvider: string;
    customModels: string;
    addCustomModel: string;
    modelName: string;
    modelId: string;
    apiKeyPlaceholder: string;
    baseUrlPlaceholder: string;
    // ...
  };
  common: {
    cancel: string;
    save: string;
    delete: string;
    edit: string;
    create: string;
    confirm: string;
    loading: string;
  };
}

// src/i18n/zh.ts
export const zh: Translations = {
  nav: {
    chat: '聊天',
    agents: '智能体',
    tasks: '任务',
    memory: '记忆',
    logs: '日志',
    skills: '技能',
    channels: '频道',
  },
  // ...
};
```

### Memory 页面结构

```tsx
// src/pages/Memory.tsx
export function Memory() {
  const [selectedId, setSelectedId] = useState(GLOBAL_ID);
  const [memoryContent, setMemoryContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [panelOpen, setPanelOpen] = useState(true);
  const [panelTab, setPanelTab] = useState<'logs' | 'archives' | 'search'>('logs');

  return (
    <div className="flex h-full">
      {/* Left: Memory list */}
      <SidePanel>
        {/* Global + Agent 列表 */}
      </SidePanel>

      {/* Center: Memory content */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="h-12 flex items-center justify-between">
          <span>{selectedItem?.isGlobal ? 'Global MEMORY.md' : 'MEMORY.md'}</span>
          <div>
            {/* Edit/Save buttons */}
            {/* Toggle right panel */}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {isEditing ? <textarea /> : <div>{memoryContent}</div>}
        </div>
      </div>

      {/* Right panel: logs / archives / search */}
      {panelOpen && (
        <div className="w-[340px] border-l flex flex-col">
          {/* Tab switcher */}
          <div className="h-12 flex items-center gap-1">
            <button onClick={() => setPanelTab('logs')}>Daily Logs</button>
            <button onClick={() => setPanelTab('archives')}>Archives</button>
            <button onClick={() => setPanelTab('search')}>Search</button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto">
            {panelTab === 'logs' && renderLogs()}
            {panelTab === 'archives' && renderArchives()}
            {panelTab === 'search' && renderSearch()}
          </div>
        </div>
      )}
    </div>
  );
}
```

### Logs 页面结构

```tsx
// src/pages/Logs.tsx
export function Logs() {
  const [selectedDate, setSelectedDate] = useState('');
  const [category, setCategory] = useState('');
  const [level, setLevel] = useState('');
  const [search, setSearch] = useState('');
  const [entries, setEntries] = useState<LogEntry[]>([]);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  // SSE for real-time updates
  useLogSSE(isToday, handleSSEEntry);

  return (
    <div className="flex flex-col h-full">
      {/* Top bar: filters */}
      <div className="p-4 border-b space-y-3">
        <div className="flex items-center gap-2">
          <h1>Logs</h1>
          {isToday && <span className="live-indicator">Live</span>}
        </div>
        <div className="flex items-center gap-2">
          <Select value={selectedDate} onValueChange={setSelectedDate} />
          <div className="category-buttons" />
          <Select value={level} onValueChange={setLevel} />
          <input className="search-box" />
        </div>
      </div>

      {/* Log content */}
      <div ref={scrollContainerRef} className="flex-1 overflow-y-auto p-4">
        <div className="terminal-style">
          {entries.map((entry, idx) => (
            <div key={idx} onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}>
              <div className="log-line">
                <span>{formatTime(entry.time)}</span>
                <span className={levelColor}>{LEVEL_LABELS[entry.level]}</span>
                <span className={categoryColor}>{entry.category}</span>
                <span>{entry.msg}</span>
              </div>
              {expandedIdx === idx && (
                <pre>{JSON.stringify(entry, null, 2)}</pre>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

### Settings 对话框结构

```tsx
// src/components/settings/SettingsDialog.tsx
type Tab = "general" | "models" | "skills" | "about";

export function SettingsDialog({ open, onOpenChange, initialTab }) {
  const [currentTab, setCurrentTab] = useState<Tab>(initialTab ?? "general");

  const tabs = [
    { id: "general", label: t.settings.general, icon: Palette },
    { id: "models", label: t.settings.models, icon: Cpu },
    { id: "skills", label: t.nav.skills, icon: Wrench },
    { id: "about", label: t.settings.about, icon: Info },
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-[90vw] max-w-5xl h-[85vh] flex">
        {/* Sidebar */}
        <div className="w-[200px] border-r p-4">
          <h3>{t.settings.title}</h3>
          <div className="space-y-0.5">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setCurrentTab(tab.id)}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl",
                  currentTab === tab.id
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-accent"
                )}
              >
                <tab.icon size={16} />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-8">
          {currentTab === "general" && <GeneralPanel />}
          {currentTab === "models" && <ModelsPanel />}
          {currentTab === "skills" && <Skills />}
          {currentTab === "about" && <AboutPanel />}
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

## 文件清单

### 需要创建

**页面**
- `src/pages/Agents.tsx`
- `src/pages/Memory.tsx`
- `src/pages/Logs.tsx`

**设置组件**
- `src/components/settings/SettingsDialog.tsx`
- `src/components/settings/GeneralPanel.tsx`
- `src/components/settings/ModelsPanel.tsx`
- `src/components/settings/AboutPanel.tsx`

**Hooks**
- `src/hooks/useLogSSE.ts`

**i18n**
- `src/i18n/index.ts`
- `src/i18n/types.ts`
- `src/i18n/context.tsx`
- `src/i18n/zh.ts`
- `src/i18n/en.ts`

### 需要更新

- `src/App.tsx` - 添加路由
- `src/components/tasks/TasksPage.tsx` - 重构
- `src/hooks/useSettings.ts` - 添加语言/主题设置
- `src/stores/app.ts` - 添加 locale/theme 状态

## 依赖

```json
{
  "react-router-dom": "^7.13.1"
}
```

## 风险

1. 路由配置与现有代码冲突
2. i18n 上下文传递复杂度
3. Settings 对话框与现有设置页面整合
4. Logs SSE 实时更新性能
