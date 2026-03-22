import { create } from 'zustand'

// Tool call from LLM (for history messages)
export type ToolCall = {
  id: string
  type: 'function'
  function: {
    name: string
    arguments: string
  }
}

// Tool use item (for streaming/live tool calls)
export type ToolUseItem = {
  id: string
  name: string
  input?: string
  status: 'running' | 'done'
}

// Tool result (for displaying tool message)
export type ToolResult = {
  toolCallId: string
  name: string
  content: string
  status: 'success' | 'error'
  timestamp?: string
}

// Timeline item types
export type TimelineItem =
  | {
    id: string
    kind: 'message'
    role: 'user' | 'assistant'
    content: string
    timestamp: string
    toolUse?: ToolUseItem[]
    toolCalls?: ToolCall[]  // 历史消息中的工具调用
    toolResults?: ToolResult[]  // 关联的工具结果
    attachments?: Attachment[]
    errorCode?: string
  }
  | {
    id: string
    kind: 'assistant_stream'
    content: string
    timestamp: string
  }
  | {
    id: string
    kind: 'tool_use'
    name: string
    input?: string
    status: 'running' | 'done'
    timestamp: string
  }

// Message type (matches API ChatMessage)
export type Message = {
  id: string
  role: 'user' | 'assistant' | 'tool'
  content: string
  timestamp: string
  toolUse?: ToolUseItem[]  // 实时工具调用
  toolCalls?: ToolCall[]  // 历史消息中的工具调用
  toolResults?: ToolResult[]  // 关联的工具结果
  toolCallId?: string  // tool 消息关联 ID
  name?: string  // 工具名称 (role="tool" 时)
  attachments?: Attachment[]
  errorCode?: string
}

// Attachment type
export type Attachment = {
  filename: string
  mediaType: string
  filePath?: string
  data?: string
}

// Chat state
export interface ChatState {
  chatId: string
  messages: Message[]
  timelineItems: TimelineItem[]
  streamingText: string
  isProcessing: boolean
  pendingToolUse: ToolUseItem[]
  chatStatus: 'submitted' | 'streaming' | 'ready' | 'error'
}

// Callback for notifying external subscribers
type ChatUpdateListener = () => void
const chatUpdateListeners = new Set<ChatUpdateListener>()

export function onChatUpdate(listener: ChatUpdateListener): () => void {
  chatUpdateListeners.add(listener)
  return () => chatUpdateListeners.delete(listener)
}

function notifyChatUpdate() {
  for (const listener of chatUpdateListeners) {
    listener()
  }
}

function messageToTimelineItem(message: Message): TimelineItem | null {
  // Skip tool messages - they are attached to assistant messages via toolResults
  if (message.role === 'tool') {
    return null
  }
  return {
    id: `message:${message.id}`,
    kind: 'message',
    role: message.role as 'user' | 'assistant',
    content: message.content,
    timestamp: message.timestamp,
    toolUse: message.toolUse,
    toolCalls: message.toolCalls,
    toolResults: message.toolResults,
    attachments: message.attachments,
    errorCode: message.errorCode,
  }
}

function buildTimelineFromMessages(messages: Message[]): TimelineItem[] {
  return messages.map(messageToTimelineItem).filter((item): item is TimelineItem => item !== null)
}

function defaultChatState(chatId: string): ChatState {
  return {
    chatId,
    messages: [],
    timelineItems: [],
    streamingText: '',
    isProcessing: false,
    pendingToolUse: [],
    chatStatus: 'ready',
  }
}

// Helper to immutably update a specific chat in the record
function updateChat(
  chats: Record<string, ChatState>,
  chatId: string,
  updater: (chat: ChatState) => Partial<ChatState>
): Record<string, ChatState> {
  const chat = chats[chatId]
  if (!chat) return chats
  return { ...chats, [chatId]: { ...chat, ...updater(chat) } }
}

interface ChatStore {
  chats: Record<string, ChatState>
  activeChatId: string | null

  initChat(chatId: string): void
  appendStreamText(chatId: string, text: string): void
  setProcessing(chatId: string, isProcessing: boolean): void
  addToolUse(chatId: string, tool: ToolUseItem): void
  completeMessage(chatId: string, fullText: string, toolUse: ToolUseItem[]): void
  addUserMessage(chatId: string, message: Message): void
  setMessages(chatId: string, messages: Message[]): void
  handleError(chatId: string, error: string, errorCode?: string): void
  removeChat(chatId: string): void
  setActiveChatId(chatId: string | null): void
  clearActiveChat(): void
}

// For useChatProcessing hook - each component only re-renders when its specific chatId changes
export function useChatProcessing(chatId: string): boolean {
  return useChatStore((s) => s.chats[chatId]?.isProcessing ?? false)
}

export const useChatStore = create<ChatStore>((set) => ({
  chats: {},
  activeChatId: null,

  initChat: (chatId) =>
    set((state) => {
      if (state.chats[chatId]) return state
      return { chats: { ...state.chats, [chatId]: defaultChatState(chatId) } }
    }),

  appendStreamText: (chatId, text) =>
    set((state) => ({
      chats: updateChat(state.chats, chatId, (chat) => ({
        streamingText: chat.streamingText + text,
        timelineItems: (() => {
          const timestamp = new Date().toISOString()
          const normalizedItems = chat.timelineItems.map((item) =>
            item.kind === 'tool_use' && item.status === 'running'
              ? { ...item, status: 'done' as const }
              : item
          )
          const lastItem = normalizedItems[normalizedItems.length - 1]

          if (lastItem?.kind === 'assistant_stream') {
            return [
              ...normalizedItems.slice(0, -1),
              {
                ...lastItem,
                content: lastItem.content + text,
              },
            ]
          }

          return [
            ...normalizedItems,
            {
              id: `assistant_stream:${timestamp}:${crypto.randomUUID()}`,
              kind: 'assistant_stream',
              content: text,
              timestamp,
            },
          ]
        })(),
        chatStatus: chat.isProcessing ? 'streaming' : chat.chatStatus,
      })),
    })),

  setProcessing: (chatId, isProcessing) =>
    set((state) => ({
      chats: updateChat(state.chats, chatId, () => {
        if (isProcessing) {
          return { isProcessing: true, chatStatus: 'submitted' as const }
        }
        return {
          isProcessing: false,
          streamingText: '',
          pendingToolUse: [],
          chatStatus: 'ready' as const,
        }
      }),
    })),

  addToolUse: (chatId, tool) =>
    set((state) => ({
      chats: updateChat(state.chats, chatId, (chat) => {
        const timelineItems = chat.timelineItems.map((item) =>
          item.kind === 'tool_use' && item.status === 'running'
            ? { ...item, status: 'done' as const }
            : item
        )
        const updated = chat.pendingToolUse.map((t) =>
          t.status === 'running' ? { ...t, status: 'done' as const } : t
        )
        return {
          pendingToolUse: [...updated, tool],
          timelineItems: [
            ...timelineItems,
            {
              id: `tool:${tool.id}`,
              kind: 'tool_use',
              name: tool.name,
              input: tool.input,
              status: tool.status,
              timestamp: new Date().toISOString(),
            },
          ],
        }
      }),
    })),

  completeMessage: (chatId, fullText, toolUse) => {
    set((state) => ({
      chats: updateChat(state.chats, chatId, (chat) => {
        const timestamp = new Date().toISOString()
        const nextMessage: Message = {
          id: Date.now().toString(),
          role: 'assistant' as const,
          content: fullText,
          timestamp,
          toolUse: toolUse.length > 0 ? toolUse : undefined,
        }
        const hasLiveAssistantText = chat.streamingText.trim().length > 0
        const timelineItems = chat.timelineItems.map((item) =>
          item.kind === 'tool_use' && item.status === 'running'
            ? { ...item, status: 'done' as const }
            : item
        )

        if (!hasLiveAssistantText && fullText.trim()) {
          timelineItems.push({
            id: `assistant_stream:${timestamp}:${crypto.randomUUID()}`,
            kind: 'assistant_stream',
            content: fullText,
            timestamp,
          })
        }

        return {
          messages: [...chat.messages, nextMessage],
          timelineItems,
          streamingText: '',
          pendingToolUse: [],
        }
      }),
    }))
    // Notify after state is committed
    queueMicrotask(notifyChatUpdate)
  },

  addUserMessage: (chatId, message) => {
    set((state) => {
      const timelineItem = messageToTimelineItem(message)
      return {
        chats: updateChat(state.chats, chatId, (chat) => ({
          messages: [...chat.messages, message],
          timelineItems: timelineItem ? [...chat.timelineItems, timelineItem] : chat.timelineItems,
        })),
      }
    })
    // Notify after state is committed
    queueMicrotask(notifyChatUpdate)
  },

  setMessages: (chatId, messages) =>
    set((state) => ({
      chats: updateChat(state.chats, chatId, () => ({
        messages,
        timelineItems: buildTimelineFromMessages(messages),
      })),
    })),

  handleError: (chatId, error, errorCode) =>
    set((state) => {
      const chat = state.chats[chatId]
      if (!chat) return state

      let messages = chat.messages
      if (error) {
        messages = [
          ...messages,
          {
            id: Date.now().toString(),
            role: 'assistant' as const,
            content: `⚠️ ${error}`,
            timestamp: new Date().toISOString(),
            errorCode,
          },
        ]
      }

      const errorTimelineItems = buildTimelineFromMessages(messages)

      // Reset error status after 2 seconds
      setTimeout(() => {
        set((s) => ({
          chats: updateChat(s.chats, chatId, (c) => ({
            chatStatus: c.chatStatus === 'error' ? ('ready' as const) : c.chatStatus,
          })),
        }))
      }, 2000)

      return {
        chats: {
          ...state.chats,
          [chatId]: {
            ...chat,
            messages,
            timelineItems: errorTimelineItems,
            streamingText: '',
            isProcessing: false,
            pendingToolUse: [],
            chatStatus: 'error' as const,
          },
        },
      }
    }),

  removeChat: (chatId) =>
    set((state) => {
      const rest = { ...state.chats }
      delete rest[chatId]
      return {
        chats: rest,
        activeChatId: state.activeChatId === chatId ? null : state.activeChatId,
      }
    }),

  setActiveChatId: (chatId) => set({ activeChatId: chatId }),

  clearActiveChat: () => set({ activeChatId: null }),
}))
