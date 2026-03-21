# feat-ui-chat-redesign: 完成检查清单

## 依赖

- [ ] streamdown 已安装
- [ ] @streamdown/code 已安装
- [ ] shiki 已安装
- [ ] use-stick-to-bottom 已安装
- [ ] @tauri-apps/plugin-dialog 已安装
- [ ] @tauri-apps/plugin-fs 已安装

## AI 组件

- [ ] conversation.tsx 正常
- [ ] message.tsx 正常
- [ ] code-block.tsx 正常
- [ ] 代码高亮工作正常

## 聊天组件

- [ ] ChatMessages.tsx 正常
- [ ] UserMessage.tsx 正常
- [ ] AssistantMessage.tsx 正常
- [ ] ToolUseBlock.tsx 正常
- [ ] ChatWelcome.tsx 正常
- [ ] timeline.ts 正常
- [ ] 流式消息显示正常
- [ ] Markdown 渲染正常

## 输入框组件

- [ ] prompt-input.tsx 正常
- [ ] attachments.tsx 正常
- [ ] ChatInput.tsx 正常
- [ ] 自适应高度正常
- [ ] 发送/停止按钮正常
- [ ] Agent 选择器正常

## 会话管理

- [ ] chat-utils.ts 正常
- [ ] ChatListItem.tsx 正常
- [ ] stores/chat.ts 正常
- [ ] useChat.ts 正常
- [ ] useChatContext.tsx 正常
- [ ] 会话列表显示正常
- [ ] 搜索功能正常
- [ ] 按日期分组正常

## 页面

- [ ] Chat.tsx 页面正常
- [ ] 欢迎页动画正常
- [ ] 输入框动画正常
- [ ] 会话切换正常

## SSE

- [ ] sse-manager.ts 正常
- [ ] useSSE.ts 更新完成
- [ ] 流式响应正常
- [ ] 自动重连正常

## 集成测试

- [ ] 消息发送测试通过
- [ ] 流式响应测试通过
- [ ] 附件上传测试通过
- [ ] 会话管理测试通过
- [ ] 无 TypeScript 错误
- [ ] 无 ESLint 警告
- [ ] 构建成功
