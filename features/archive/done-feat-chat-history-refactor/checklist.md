# feat-chat-history-refactor: 完成检查清单

## 开始前

- [x] 确认当前问题可复现
- [x] 备份现有 session 文件

## 后端修改

### Session Key 格式
- [x] `serve.py` 中 session_key 使用 `{channel}:{chat_id}` 格式
- [x] `_get_session_path()` 正确转换 key 为文件名
- [x] `list_sessions()` 返回完整的 key

### API 端点
- [x] `GET /api/chats` 返回正确的 chat_id（完整 key）
- [x] `GET /api/chats/{chat_id}` 使用 `session_manager.get()` 只查找不创建
- [x] `POST /api/chats` 创建新对话并返回 chat_id
- [x] `DELETE /api/chats/{chat_id}` 正确删除 session 文件

### SessionManager
- [x] `get()` 方法只查找不创建
- [x] `get_last_message()` 提取最后一条消息

## 前端修改

### API 客户端
- [x] `getChats()` 适配新的数据结构
- [x] `createChat()` 调用新建对话 API
- [x] `getChat()` 使用完整 chat_id

### ChatProvider
- [x] 新建对话时先调用 `createChat()`
- [x] 使用后端返回的 chat_id
- [x] SSE 事件处理使用正确 chat_id

### UI 组件
- [x] ChatListItem 显示正确的名称
- [x] ChatListItem 显示最后消息预览
- [x] 对话列表按时间排序

## 测试验证

### 后端测试
- [x] `poetry run pytest tests/test_session*.py -v`
- [x] 手动测试 `/api/chats` 端点
- [x] 手动测试 `/api/chats/{chat_id}` 端点

### 前端测试
- [x] `npm run build` 编译成功
- [ ] 创建新对话并发送消息
- [ ] 刷新页面，对话列表仍显示
- [ ] 点击历史对话，消息正确加载
- [ ] 删除对话，确认 session 文件被删除

## 完成后

- [x] 更新 CLAUDE.md 文档（如有必要）
- [x] 提交代码
- [x] 标记特性为完成
