# feat-chat-history - 聊天历史与 Agent 管理

## 概述

为 Tauri 桌面应用的 Chat 页面添加完整的聊天历史管理功能和 Agent 选择功能。参考 `reference/youclaw` 的实现，包括：
- 左侧聊天历史列表（新建、删除、搜索、切换）
- Agent 选择器（从 API 获取 Agent 列表）
- 聊天历史持久化（API 端点 + 前端集成）

## 用户价值点

### VP1: 聊天历史列表 UI

用户可以查看、搜索、创建和删除历史对话，快速在不同对话之间切换。

**Gherkin 场景：**

```gherkin
Feature: 聊天历史列表

  Scenario: 显示聊天历史列表
    Given 用户打开 Chat 页面
    When 侧边栏加载完成
    Then 应显示按日期分组的聊天历史列表（今天、昨天、更早）
    And 每个聊天项显示头像、名称、最后消息和时间

  Scenario: 创建新对话
    Given 用户在 Chat 页面
    When 用户点击"新建对话"按钮
    Then 当前对话切换到新的空白对话
    And 输入框获得焦点

  Scenario: 删除对话
    Given 用户有一个已存在的对话
    When 用户点击对话项的菜单并选择删除
    Then 显示删除确认对话框
    And 确认后对话从列表中移除

  Scenario: 搜索对话
    Given 用户有多个历史对话
    When 用户在搜索框输入关键词
    Then 列表实时过滤只显示匹配的对话

  Scenario: 切换对话
    Given 用户有多个历史对话
    When 用户点击某个对话项
    Then 加载该对话的历史消息
    And 消息列表滚动到最新消息

  Scenario: 编辑对话标题
    Given 用户有一个已存在的对话
    When 用户点击编辑按钮并修改名称
    Then 对话标题更新为新名称
```

### VP2: Agent 选择集成

用户可以选择不同的 Agent 进行对话，每个对话关联一个特定的 Agent。

**Gherkin 场景：**

```gherkin
Feature: Agent 选择

  Scenario: 显示 Agent 列表
    Given 用户在 Chat 页面
    When 输入区域加载完成
    Then 显示 Agent 选择下拉菜单
    And 下拉菜单包含从 API 获取的 Agent 列表

  Scenario: 切换 Agent
    Given 用户当前使用 Default Agent
    When 用户从下拉菜单选择另一个 Agent
    Then 后续消息将使用新选择的 Agent 处理
    And Agent 选择持久化到本地存储

  Scenario: 新对话使用当前 Agent
    Given 用户选择了 Agent-A
    When 用户创建新对话并发送消息
    Then 该对话关联到 Agent-A
```

### VP3: 聊天历史持久化

聊天数据通过后端 API 持久化，应用重启后可恢复历史对话。

**Gherkin 场景：**

```gherkin
Feature: 聊天历史持久化

  Scenario: 保存新对话
    Given 用户创建新对话并发送第一条消息
    When AI 响应完成
    Then 对话通过 API 保存到后端
    And 对话出现在历史列表中

  Scenario: 加载历史消息
    Given 用户有历史对话
    When 用户点击某个历史对话
    Then 通过 API 加载该对话的所有消息
    And 消息按时间顺序显示在聊天区域

  Scenario: 更新对话最后消息
    Given 用户在某个对话中发送新消息
    When AI 响应完成
    Then 对话的 last_message 和 last_message_time 更新
    And 对话在列表中移动到顶部
```

## 技术设计

### 前端组件

```
src/
├── components/
│   └── chat/
│       ├── ChatListItem.tsx    # 聊天列表项（已存在，需完善）
│       └── ChatWindow.tsx      # 主聊天区域（需更新集成）
├── pages/
│   └── Chat.tsx                # 聊天页面（需重构布局）
└── lib/
    └── api.ts                  # API 客户端（需添加聊天相关方法）
```

### API 端点（需后端支持）

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/chats` | GET | 获取聊天列表 |
| `/api/chats/:id` | GET | 获取单个聊天的消息 |
| `/api/chats/:id` | DELETE | 删除聊天 |
| `/api/chats/:id` | PATCH | 更新聊天（名称、头像） |

### 状态管理

使用现有的 `useChatStore` (Zustand)：
- `chatList`: ChatItem[]
- `activeChatId`: string | null
- `agents`: Agent[]

## 依赖关系

- **前置依赖**: 无
- **关联特性**: feat-ui-chat-redesign（父特性 feat-ui-redesign）

## 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 后端 API 可能不完整 | 先实现前端 UI，使用 mock 数据，后端 API 可独立开发 |
| Session 数据结构不匹配 | 检查现有 SessionManager，适配前端所需格式 |

## 验收标准

- [ ] 聊天历史列表正确显示并按日期分组
- [ ] 新建/删除/搜索/切换对话功能正常
- [ ] Agent 选择器显示 API 返回的 Agent 列表
- [ ] Agent 切换后新对话使用正确的 Agent
- [ ] 聊天历史通过 API 持久化
- [ ] 所有 Gherkin 场景通过
