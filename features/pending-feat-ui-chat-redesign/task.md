# feat-ui-chat-redesign: 任务分解

## Phase 1: 依赖安装 (0.5h)

- [ ] 1.1 安装 npm 依赖
  ```bash
  npm install streamdown @streamdown/code @streamdown/cjk shiki use-stick-to-bottom
  npm install @tauri-apps/plugin-dialog @tauri-apps/plugin-fs
  ```

## Phase 2: AI 组件基础 (2h)

- [ ] 2.1 创建 conversation.tsx
  - [ ] Conversation 容器
  - [ ] ConversationContent
  - [ ] ConversationScrollButton
  - [ ] useStickToBottom 集成

- [ ] 2.2 创建 message.tsx
  - [ ] Message 组件
  - [ ] MessageContent
  - [ ] MessageResponse (Markdown 渲染)

- [ ] 2.3 创建 code-block.tsx
  - [ ] Shiki 高亮集成
  - [ ] 复制按钮
  - [ ] 语言标签

## Phase 3: 聊天组件 (3h)

- [ ] 3.1 创建 ChatMessages.tsx
  - [ ] 消息列表渲染
  - [ ] 时间线构建
  - [ ] 流式消息显示
  - [ ] 思考状态

- [ ] 3.2 创建 UserMessage.tsx
  - [ ] 用户头像
  - [ ] 消息内容
  - [ ] 附件显示

- [ ] 3.3 创建 AssistantMessage.tsx
  - [ ] AI 头像
  - [ ] Markdown 渲染
  - [ ] 工具调用展示

- [ ] 3.4 创建 ToolUseBlock.tsx
  - [ ] 工具名称
  - [ ] 运行状态
  - [ ] 折叠/展开

- [ ] 3.5 创建 ChatWelcome.tsx
  - [ ] Logo 动画
  - [ ] 欢迎文字
  - [ ] 输入框居中布局

- [ ] 3.6 创建 timeline.ts
  - [ ] TimelineItem 类型
  - [ ] buildRenderableTimeline 函数

## Phase 4: 输入框组件 (2h)

- [ ] 4.1 创建 prompt-input.tsx
  - [ ] PromptInput 容器
  - [ ] PromptInputTextarea
  - [ ] PromptInputFooter
  - [ ] PromptInputSubmit
  - [ ] PromptInputTools
  - [ ] PromptInputSelect

- [ ] 4.2 创建 attachments.tsx
  - [ ] Attachment 组件
  - [ ] AttachmentPreview
  - [ ] AttachmentInfo
  - [ ] AttachmentRemove

- [ ] 4.3 创建 ChatInput.tsx
  - [ ] 集成 PromptInput
  - [ ] Agent 选择器
  - [ ] 附件按钮
  - [ ] 发送/停止逻辑

## Phase 5: 会话管理 (2h)

- [ ] 5.1 创建 chat-utils.ts
  - [ ] groupChatsByDate 函数
  - [ ] 日期格式化

- [ ] 5.2 创建 ChatListItem.tsx
  - [ ] 头像生成
  - [ ] 名称显示
  - [ ] 编辑/删除操作

- [ ] 5.3 创建 stores/chat.ts
  - [ ] chatId 状态
  - [ ] messages 状态
  - [ ] timelineItems 状态
  - [ ] 会话列表

- [ ] 5.4 创建 useChat.ts
  - [ ] send 函数
  - [ ] stop 函数
  - [ ] loadChat 函数
  - [ ] newChat 函数
  - [ ] deleteChat 函数

- [ ] 5.5 创建 useChatContext.tsx
  - [ ] ChatProvider
  - [ ] useChatContext hook

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

- [ ] 7.1 创建 sse-manager.ts
  - [ ] SSEManager 类
  - [ ] 自动重连
  - [ ] 事件解析

- [ ] 7.2 更新 useSSE.ts
  - [ ] 使用 SSEManager
  - [ ] 流式文本状态

## Phase 8: 测试 (1h)

- [ ] 8.1 功能测试
  - [ ] 消息发送
  - [ ] 流式响应
  - [ ] 附件上传
  - [ ] 会话切换
  - [ ] 删除会话
