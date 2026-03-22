# feat-chat-history - 完成检查清单

## 开发前检查

- [ ] 确认开发环境正常（`npm run tauri:dev` 可启动）
- [ ] 阅读 `reference/youclaw` 相关代码
- [ ] 了解现有 `useChatStore` 和 `chatCtx` 结构

## Phase 1: 前端 UI 组件

### Task 1.1: ChatListItem 组件

- [ ] ChatListItem 显示头像、名称、时间、最后消息
- [ ] 头像点击弹出颜色选择器
- [ ] 下拉菜单包含编辑头像、编辑标题、删除选项
- [ ] 内联编辑标题功能
- [ ] 删除确认对话框
- [ ] 处理中状态显示旋转动画
- [ ] 悬停效果和过渡动画

### Task 1.2: Chat.tsx 页面

- [ ] 左侧 SidePanel 包含聊天列表
- [ ] 搜索框可展开/收起
- [ ] 搜索实时过滤聊天列表
- [ ] 新建对话按钮
- [ ] 聊天按日期分组（今天、昨天、更早）
- [ ] 点击聊天项切换对话
- [ ] 新对话时显示欢迎界面

### Task 1.3: ChatProvider 更新

- [ ] chatList 状态管理
- [ ] refreshChats() 方法
- [ ] deleteChat() 方法
- [ ] updateChat() 方法
- [ ] agents 列表获取
- [ ] agentId 持久化

## Phase 2: API 集成

### Task 2.1: API Client

- [ ] getChats() 方法
- [ ] getChat(chatId) 方法
- [ ] deleteChat(chatId) 方法
- [ ] updateChat(chatId, data) 方法

### Task 2.2: 后端 API（可选）

- [ ] GET /api/chats 端点
- [ ] GET /api/chats/:id 端点
- [ ] DELETE /api/chats/:id 端点
- [ ] PATCH /api/chats/:id 端点
- [ ] API 单元测试

## Phase 3: Agent 集成

### Task 3.1: Agent 选择器

- [ ] ChatInput 显示 Agent 下拉菜单
- [ ] 从 API 获取 Agent 列表
- [ ] Agent ID 持久化到 localStorage
- [ ] 新对话使用当前选择的 Agent

## Phase 4: 测试与验收

### 功能测试

- [ ] 聊天列表正确显示
- [ ] 新建对话功能正常
- [ ] 删除对话功能正常
- [ ] 搜索对话功能正常
- [ ] 切换对话功能正常
- [ ] 编辑对话标题功能正常
- [ ] Agent 选择功能正常
- [ ] Agent 持久化正常

### 边界测试

- [ ] 空聊天列表显示提示
- [ ] 网络错误处理
- [ ] API 错误处理
- [ ] 长消息截断显示

### UI/UX 检查

- [ ] 响应式布局正常
- [ ] 过渡动画流畅
- [ ] 暗色主题兼容
- [ ] macOS traffic light 间距正确

## 完成后检查

- [ ] TypeScript 编译无错误
- [ ] 无 console 警告或错误
- [ ] 代码格式化（Prettier/ESLint）
- [ ] 更新相关文档
- [ ] 提交信息清晰描述变更

## 验收标准

所有 Gherkin 场景通过：

**VP1: 聊天历史列表 UI**
- [ ] 显示聊天历史列表
- [ ] 创建新对话
- [ ] 删除对话
- [ ] 搜索对话
- [ ] 切换对话
- [ ] 编辑对话标题

**VP2: Agent 选择集成**
- [ ] 显示 Agent 列表
- [ ] 切换 Agent
- [ ] 新对话使用当前 Agent

**VP3: 聊天历史持久化**
- [ ] 保存新对话
- [ ] 加载历史消息
- [ ] 更新对话最后消息
