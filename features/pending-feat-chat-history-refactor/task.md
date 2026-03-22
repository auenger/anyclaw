# feat-chat-history-refactor: 任务分解

## Phase 1: 前端 - 新建对话生成唯一 ID

### Task 1.1: chatCtx.tsx 修改
- [ ] `newChat()` 生成唯一 `conversation_id`（`conv_${Date.now()}`）
- [ ] `send()` 使用 `activeChatId` 或生成新 ID
- [ ] 确保切换对话时正确设置 `activeChatId`

### Task 1.2: api.ts 修改
- [ ] `sendMessage()` 传递 `conversation_id` 参数
- [ ] 确保后端能收到正确的 ID

## Phase 2: 后端 - Session Key 格式统一

### Task 2.1: chats.py 调整
- [ ] `_session_to_chat_item()` 返回完整 `chat_id`（含 channel 前缀）
- [ ] 添加 `conversation_id` 字段（不含前缀）
- [ ] 生成友好的显示名称（如 "Chat 3月22日 14:30"）

### Task 2.2: 历史加载验证
- [ ] `GET /api/chats/{chat_id}` 使用完整 key 查找
- [ ] 测试新建对话能正确保存
- [ ] 测试继续对话能加载历史

## Phase 3: 历史压缩（可选，后续迭代）

### Task 3.1: 简单切分
- [ ] 当消息数超过 N 条时，只保留最近 N 条
- [ ] 添加配置项控制切分阈值

### Task 3.2: 智能摘要（后续）
- [ ] LLM 生成历史摘要
- [ ] 摘要替换历史消息

## 依赖

无外部依赖

## 风险

1. **旧数据兼容** - `default.jsonl` 等旧文件需要特殊处理
2. **SSE 事件** - 确保 `chat_id` 在 SSE 事件中一致

## 预估工时

- Phase 1: 1h
- Phase 2: 1h
- Phase 3: 1h（可选）
- 测试验证: 0.5h
- **总计: 3.5h**
