# feat-ui-chat-redesign: 完成检查清单

## 依赖

- [x] streamdown 已安装
- [x] @streamdown/code 已安装
- [x] @streamdown/cjk 已安装
- [x] shiki 已安装
- [x] use-stick-to-bottom 已安装
- [x] @tauri-apps/plugin-dialog 已安装
- [x] @tauri-apps/plugin-fs 已安装

## AI 组件

- [x] conversation.tsx 正常
- [x] message.tsx 正常
- [x] code-block.tsx 正常
- [x] 代码高亮工作正常

## 聊天组件

- [x] ChatMessages.tsx 正常
- [x] UserMessage.tsx 正常
- [x] AssistantMessage.tsx 正常
- [x] ToolUseBlock.tsx 正常
- [x] ChatWelcome.tsx 正常
- [x] timeline.ts 正常
- [ ] 流式消息显示正常（待集成测试）
- [ ] Markdown 渲染正常（待集成测试）

## 输入框组件

- [x] prompt-input.tsx 正常
- [x] attachments.tsx 正常
- [x] ChatInput.tsx 正常
- [ ] 自适应高度正常（待集成测试）
- [ ] 发送/停止按钮正常（待集成测试）
- [ ] Agent 选择器正常（待集成测试）

## 会话管理

- [x] chat-utils.ts 正常
- [x] ChatListItem.tsx 正常
- [x] stores/chat.ts 正常
- [x] useChat.ts 正常
- [x] chatCtx.tsx 正常
- [ ] 会话列表显示正常（待集成测试）
- [ ] 搜索功能正常（待集成测试）
- [ ] 按日期分组正常（待集成测试）

## 页面

- [ ] Chat.tsx 页面正常
- [ ] 欢迎页动画正常
- [ ] 输入框动画正常
- [ ] 会话切换正常

## SSE

- [x] sse-manager.ts 正常
- [ ] useSSE.ts 更新完成
- [ ] 流式响应正常
- [ ] 自动重连正常

## 集成测试

- [ ] 消息发送测试通过
- [ ] 流式响应测试通过
- [ ] 附件上传测试通过
- [ ] 会话管理测试通过
- [x] 无 TypeScript 错误
- [ ] 无 ESLint 警告
- [x] 构建成功
