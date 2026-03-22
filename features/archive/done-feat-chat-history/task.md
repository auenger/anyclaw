# feat-chat-history - 任务分解

## 任务列表

### Phase 1: 前端 UI 组件

#### Task 1.1: 完善 ChatListItem 组件
**优先级**: P0
**预估**: 1h

- [ ] 参考 youclaw 实现，完善 ChatListItem 组件
- [ ] 添加头像选择器（Popover + 渐变色预设）
- [ ] 添加编辑标题功能（内联编辑）
- [ ] 添加下拉菜单（编辑头像、编辑标题、删除）
- [ ] 添加删除确认对话框
- [ ] 添加处理中状态指示器（Loader2 动画）

**文件**:
- `src/components/chat/ChatListItem.tsx`

**参考**: `reference/youclaw/web/src/components/chat/ChatListItem.tsx`

---

#### Task 1.2: 重构 Chat.tsx 页面布局
**优先级**: P0
**预估**: 1.5h

- [ ] 添加左侧聊天列表区域（使用 SidePanel 组件）
- [ ] 实现搜索框（可展开/收起）
- [ ] 实现按日期分组的聊天列表（groupChatsByDate）
- [ ] 实现新建对话按钮
- [ ] 更新右侧聊天区域布局（保持现有 ChatMessages + ChatInput）
- [ ] 处理新对话时的欢迎界面过渡动画

**文件**:
- `src/pages/Chat.tsx`

**参考**: `reference/youclaw/web/src/pages/Chat.tsx`

---

#### Task 1.3: 更新 ChatProvider 集成
**优先级**: P0
**预估**: 1h

- [ ] 更新 `chatCtx.tsx` 添加聊天列表管理方法
- [ ] 添加 `deleteChat`、`updateChat`、`refreshChats` 方法
- [ ] 添加 Agent 列表获取逻辑
- [ ] 集成 API 调用（或 mock 数据）
- [ ] 添加持久化回调 props

**文件**:
- `src/hooks/chatCtx.tsx`

**参考**: `reference/youclaw/web/src/hooks/useChatContext.tsx`

---

### Phase 2: API 集成

#### Task 2.1: 扩展 API Client
**优先级**: P1
**预估**: 0.5h

- [ ] 添加 `getChats()` 方法
- [ ] 添加 `getChat(chatId)` 方法
- [ ] 添加 `deleteChat(chatId)` 方法
- [ ] 添加 `updateChat(chatId, data)` 方法

**文件**:
- `src/lib/api.ts`

---

#### Task 2.2: 后端 API 端点（可选）
**优先级**: P2
**预估**: 2h

如果后端没有对应端点，需要添加：

- [ ] `GET /api/chats` - 获取聊天列表
- [ ] `GET /api/chats/:id` - 获取聊天消息
- [ ] `DELETE /api/chats/:id` - 删除聊天
- [ ] `PATCH /api/chats/:id` - 更新聊天

**文件**:
- `anyclaw/api/routes/chats.py`（新建）

---

### Phase 3: Agent 集成

#### Task 3.1: Agent 选择器
**优先级**: P1
**预估**: 0.5h

- [ ] 在 ChatInput 中添加 Agent 选择下拉菜单
- [ ] 从 API 获取 Agent 列表（`listAgents()`）
- [ ] 持久化当前选择的 Agent ID
- [ ] 新对话时使用当前选择的 Agent

**文件**:
- `src/components/chat/ChatInput.tsx`
- `src/hooks/chatCtx.tsx`

---

### Phase 4: 测试与优化

#### Task 4.1: 集成测试
**优先级**: P1
**预估**: 1h

- [ ] 测试聊天列表显示
- [ ] 测试新建/删除/搜索对话
- [ ] 测试 Agent 选择和切换
- [ ] 测试历史消息加载
- [ ] 测试错误处理（网络失败、API 错误）

---

## 任务依赖图

```
Task 1.1 (ChatListItem)
    │
    ▼
Task 1.2 (Chat.tsx) ──────┬──────► Task 1.3 (ChatProvider)
                          │              │
                          │              ▼
                          │      Task 2.1 (API Client)
                          │              │
                          │              ▼
                          │      Task 2.2 (后端 API) [可选]
                          │
                          └──────► Task 3.1 (Agent 选择器)
                                         │
                                         ▼
                                 Task 4.1 (集成测试)
```

## 总预估时间

- Phase 1: 3.5h
- Phase 2: 2.5h（含可选后端）
- Phase 3: 0.5h
- Phase 4: 1h

**总计**: ~7.5h

## 开发顺序建议

1. **Task 1.1** - ChatListItem 组件（可独立开发）
2. **Task 1.3** - ChatProvider 更新（使用 mock 数据）
3. **Task 1.2** - Chat.tsx 页面重构
4. **Task 2.1** - API Client 扩展
5. **Task 3.1** - Agent 选择器
6. **Task 4.1** - 集成测试
7. **Task 2.2** - 后端 API（如需要）
