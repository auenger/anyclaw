# feat-ui-chat-redesign: 聊天功能复刻

## 概述

复刻 youclaw 的聊天功能，包括会话管理、消息渲染、输入框增强、附件支持等。

**依赖**: feat-ui-design-core

## 价值点

### 1. 会话管理

**参考**: `reference/youclaw/web/src/pages/Chat.tsx`

- 会话列表 (SidePanel)
  - 按日期分组 (今天、昨天、更早)
  - 搜索过滤
  - 创建新会话
  - 删除会话确认
- ChatListItem 组件
  - 头像生成
  - 名称编辑
  - 删除操作

### 2. 消息渲染

**参考**:
- `reference/youclaw/web/src/components/chat/ChatMessages.tsx`
- `reference/youclaw/web/src/components/chat/AssistantMessage.tsx`
- `reference/youclaw/web/src/components/chat/UserMessage.tsx`
- `reference/youclaw/web/src/components/chat/ToolUseBlock.tsx`

- 消息组件
  - Conversation 容器 (use-stick-to-bottom)
  - UserMessage 用户消息
  - AssistantMessage 助手消息
  - StreamingAssistantItem 流式消息
  - ToolUseBlock 工具调用展示
  - DocumentStatus 文档处理状态

- Markdown 渲染
  - streamdown 库
  - @streamdown/code 代码高亮
  - @streamdown/cjk 中文优化

### 3. 输入框增强

**参考**:
- `reference/youclaw/web/src/components/chat/ChatInput.tsx`
- `reference/youclaw/web/src/components/ai-elements/prompt-input.tsx`

- PromptInput 组件系统
  - PromptInputTextarea 自适应高度
  - PromptInputFooter 底部工具栏
  - PromptInputTools 工具按钮区
  - PromptInputSubmit 发送/停止按钮
  - PromptInputSelect Agent 选择器

- 附件系统
  - attachments.tsx 附件预览
  - 拖拽上传
  - 文件类型过滤
  - 大小限制 (10MB)

### 4. 欢迎页动画

**参考**: `reference/youclaw/web/src/components/chat/ChatWelcome.tsx`

- 新会话欢迎页
  - Logo 动画 (hover scale + rotate)
  - 欢迎文字
  - 输入框居中
- 发送消息后
  - 输入框滑动到底部
  - 欢迎内容淡出

### 5. SSE 流式处理

**参考**:
- `reference/youclaw/web/src/lib/sse-manager.ts`
- `reference/youclaw/web/src/hooks/useChat.ts`

- SSEManager
  - 自动重连
  - 事件解析
  - 状态管理

- useChat Hook
  - 会话状态 (chatId, messages, timelineItems)
  - 发送/停止
  - 流式文本 (streamingText)
  - 处理状态 (isProcessing)

## 验收标准

```gherkin
Feature: 聊天功能复刻

  Scenario: 创建新会话
    Given 用户在聊天页面
    When 用户点击 "新建会话" 按钮
    Then 显示欢迎页
    And 输入框居中显示
    And Logo 可 hover 动画

  Scenario: 发送消息
    Given 用户在新会话中
    When 用户输入消息并点击发送
    Then 输入框滑动到底部
    And 欢迎内容淡出
    And 用户消息显示在列表中
    And 显示 "思考中..." 状态

  Scenario: 流式响应
    Given 用户已发送消息
    When 助手开始回复
    Then 消息逐字显示
    And Markdown 正确渲染
    And 代码块有语法高亮
    And 自动滚动到底部

  Scenario: 工具调用显示
    Given 助手正在执行工具
    When 工具开始执行
    Then 显示工具名称和状态
    When 工具执行完成
    Then 显示完成状态

  Scenario: 附件上传
    Given 用户在输入框
    When 用户点击附件按钮选择图片
    Then 图片预览显示在输入框上方
    When 用户发送消息
    Then 图片随消息发送

  Scenario: Agent 选择
    Given 系统有多个 Agent
    When 用户点击 Agent 选择器
    Then 显示 Agent 列表
    When 用户选择其他 Agent
    Then 后续消息使用新 Agent

  Scenario: 会话列表搜索
    Given 用户有多个会话
    When 用户在搜索框输入关键词
    Then 会话列表实时过滤
    And 按日期分组显示

  Scenario: 会话切换
    Given 用户在会话 A
    When 用户点击会话 B
    Then 切换到会话 B
    And 加载会话 B 的历史消息
    And 输入框自动聚焦

  Scenario: 删除会话
    Given 用户在会话列表
    When 用户点击删除按钮
    Then 显示确认对话框
    When 用户确认删除
    Then 会话从列表中移除

  Scenario: 停止生成
    Given 助手正在生成回复
    When 用户点击停止按钮
    Then 停止流式响应
    And 显示部分响应内容
```

## 技术实现

### 消息时间线

```tsx
// timeline.ts
type TimelineItem =
  | { kind: 'message'; id: string; role: 'user' | 'assistant'; content: string }
  | { kind: 'assistant_stream'; id: string; content: string }
  | { kind: 'tool_use'; id: string; name: string; input?: string; status: 'running' | 'done' }
  | { kind: 'document_status'; id: string; filename: string; status: 'parsing' | 'parsed' | 'failed' }

function buildRenderableTimeline(items: TimelineItem[]): RenderableTimelineItem[] {
  // 将连续的 tool_use 合并为 tool_use_group
}
```

### 附件处理

```tsx
const MAX_FILES = 10;
const ACCEPT_TYPES = 'image/jpeg,image/png,image/gif,image/webp,application/pdf,text/plain,text/markdown,text/csv,text/html,application/vnd.openxmlformats-officedocument.*';

function usePromptInputAttachments() {
  const [files, setFiles] = useState<AttachmentFile[]>([]);

  const openFileDialog = async () => {
    const selected = await open({ multiple: true, filters: [...] });
    // 添加文件
  };

  const remove = (id: string) => { /* ... */ };

  return { files, openFileDialog, remove };
}
```

### 滚动到底部

```tsx
import { useStickToBottom } from 'use-stick-to-bottom';

function Conversation({ children }) {
  const { scrollRef, contentRef, scrollToBottom } = useStickToBottom();

  return (
    <div ref={scrollRef} className="overflow-y-auto">
      <div ref={contentRef}>{children}</div>
    </div>
  );
}
```

## 文件清单

### 需要修改

- `src/components/chat/ChatWindow.tsx` - 使用新组件
- `src/hooks/useSSE.ts` - 增强 SSE 处理

### 需要创建

- `src/pages/Chat.tsx` - 聊天页面
- `src/components/chat/ChatMessages.tsx`
- `src/components/chat/ChatInput.tsx`
- `src/components/chat/ChatListItem.tsx`
- `src/components/chat/ChatWelcome.tsx`
- `src/components/chat/AssistantMessage.tsx`
- `src/components/chat/UserMessage.tsx`
- `src/components/chat/ToolUseBlock.tsx`
- `src/components/chat/timeline.ts`
- `src/components/ai-elements/prompt-input.tsx`
- `src/components/ai-elements/message.tsx`
- `src/components/ai-elements/conversation.tsx`
- `src/components/ai-elements/attachments.tsx`
- `src/components/ai-elements/code-block.tsx`
- `src/hooks/useChat.ts`
- `src/hooks/useChatContext.tsx`
- `src/hooks/chatCtx.ts`
- `src/stores/chat.ts`
- `src/lib/sse-manager.ts`
- `src/lib/chat-utils.ts`

## 依赖

```json
{
  "streamdown": "^2.4.0",
  "@streamdown/code": "^1.1.0",
  "@streamdown/cjk": "^1.0.2",
  "shiki": "^4.0.2",
  "use-stick-to-bottom": "^1.1.3",
  "@tauri-apps/plugin-dialog": "^2.6.0",
  "@tauri-apps/plugin-fs": "^2.4.5"
}
```

## 风险

1. streamdown 与现有 SSE 逻辑集成
2. 附件上传 API 兼容性
3. 消息状态管理复杂度
