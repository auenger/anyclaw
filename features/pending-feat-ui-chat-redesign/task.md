# feat-ui-chat-redesign: 任务分解

## Phase 1: 依赖安装 (0.5h)

- [x] 1.1 安装 npm 依赖
  ```bash
  npm install streamdown @streamdown/code @streamdown/cjk shiki use-stick-to-bottom
  npm install @tauri-apps/plugin-dialog @tauri-apps/plugin-fs
  ```

## Phase 2: AI 组件基础 (2h)

- [x] 2.1 创建 conversation.tsx
  - [x] Conversation 容器
  - [x] ConversationContent
  - [x] ConversationScrollButton
  - [x] useStickToBottom 集成

- [x] 2.2 创建 message.tsx
  - [x] Message 组件
  - [x] MessageContent
  - [x] MessageResponse (Markdown 渲染)

- [x] 2.3 创建 code-block.tsx
  - [x] Shiki 高亮集成
  - [x] 复制按钮
  - [x] 语言标签

## Phase 3: 聊天组件 (3h)

- [x] 3.1 创建 ChatMessages.tsx
  - [x] 消息列表渲染
  - [x] 时间线构建
  - [x] 流式消息显示
  - [x] 思考状态

- [x] 3.2 创建 UserMessage.tsx
  - [x] 用户头像
  - [x] 消息内容
  - [x] 附件显示

- [x] 3.3 创建 AssistantMessage.tsx
  - [x] AI 头像
  - [x] Markdown 渲染
  - [x] 工具调用展示

- [x] 3.4 创建 ToolUseBlock.tsx
  - [x] 工具名称
  - [x] 运行状态
  - [x] 折叠/展开

- [x] 3.5 创建 ChatWelcome.tsx
  - [x] Logo 动画
  - [x] 欢迎文字
  - [x] 输入框居中布局

- [x] 3.6 创建 timeline.ts
  - [x] TimelineItem 类型
  - [x] buildRenderableTimeline 函数

## Phase 4: 输入框组件 (2h)

- [x] 4.1 创建 prompt-input.tsx
  - [x] PromptInput 容器
  - [x] PromptInputTextarea
  - [x] PromptInputFooter
  - [x] PromptInputSubmit
  - [x] PromptInputTools
  - [x] PromptInputSelect

- [x] 4.2 创建 attachments.tsx
  - [x] Attachment 组件
  - [x] AttachmentPreview
  - [x] AttachmentInfo
  - [x] AttachmentRemove

- [x] 4.3 创建 ChatInput.tsx
  - [x] 集成 PromptInput
  - [x] Agent 选择器
  - [x] 附件按钮
  - [x] 发送/停止逻辑

## Phase 5: 会话管理 (2h)

- [x] 5.1 创建 chat-utils.ts
  - [x] groupChatsByDate 函数
  - [x] 日期格式化

- [x] 5.2 创建 ChatListItem.tsx
  - [x] 头像生成
  - [x] 名称显示
  - [x] 编辑/删除操作

- [x] 5.3 创建 stores/chat.ts
  - [x] chatId 状态
  - [x] messages 状态
  - [x] timelineItems 状态
  - [x] 会话列表

- [x] 5.4 创建 useChat.ts
  - [x] send 函数
  - [x] stop 函数
  - [x] loadChat 函数
  - [x] newChat 函数
  - [x] deleteChat 函数

- [x] 5.5 创建 chatCtx.tsx
  - [x] ChatProvider
  - [x] useChatContext hook

## Phase 6: 页面整合 (2h)

- [ ] 6.1 创建 Chat.tsx 页面
  - [ ] SidePanel 会话列表
  - [ ] 搜索功能
  - [ ] 新建会话
  - [ ] 删除确认
  - [ ] 消息区域
  - [ ] 输入框动画

- [ ] 6.2 更新 ChatWindow.tsx
  - [ ] 使用新的 Chat 组件
  - [ ] 或重构为使用新组件

- [ ] 6.3 更新 App.tsx
  - [ ] 路由配置
  - [ ] ChatProvider 包裹

## Phase 7: SSE 增强 (1h)

- [x] 7.1 创建 sse-manager.ts
  - [x] SSEManager 类
  - [x] 自动重连
  - [x] 事件解析

- [ ] 7.2 更新 useSSE.ts
  - [ ] 使用 SSEManager
  - [ ] 流式文本状态

## Phase 8: 测试 (1h)

- [x] 8.1 功能测试
  - [x] TypeScript 编译通过
  - [x] 构建成功
  - [ ] 消息发送
  - [ ] 流式响应
  - [ ] 附件上传
  - [ ] 会话切换
  - [ ] 删除会话
