import { useCallback } from 'react'
import { useChatStore, onChatUpdate } from '@/stores/chat'
import type { Attachment, Message, TimelineItem, ToolUseItem, ChatState } from '@/stores/chat'

// Re-export types for consumers
export type { Message, TimelineItem, ToolUseItem, Attachment, ChatState }

/**
 * Read active chat's state. Returns null when no chat is active (new chat screen).
 */
export function useActiveChatState(): ChatState | null {
  const activeChatId = useChatStore((s) => s.activeChatId)
  const chat = useChatStore((s) =>
    activeChatId ? s.chats[activeChatId] ?? null : null,
  )
  return chat
}

/**
 * Read a specific chat's isProcessing status (for sidebar indicators).
 * Each component calling this only re-renders when its specific chatId changes.
 */
export function useChatProcessing(chatId: string): boolean {
  return useChatStore((s) => s.chats[chatId]?.isProcessing ?? false)
}

/**
 * Chat actions.
 */
export function useChatActions(agentId: string) {
  const initChat = useChatStore((s) => s.initChat)
  const setActiveChatId = useChatStore((s) => s.setActiveChatId)
  const addUserMessage = useChatStore((s) => s.addUserMessage)
  const setProcessing = useChatStore((s) => s.setProcessing)
  const appendStreamText = useChatStore((s) => s.appendStreamText)
  const addToolUse = useChatStore((s) => s.addToolUse)
  const completeMessage = useChatStore((s) => s.completeMessage)
  const handleError = useChatStore((s) => s.handleError)
  const setMessages = useChatStore((s) => s.setMessages)
  const removeChat = useChatStore((s) => s.removeChat)

  const send = useCallback(
    async (
      prompt: string,
      attachments?: Attachment[],
    ) => {
      const store = useChatStore.getState()
      const currentChatId = store.activeChatId
      const effectiveChatId = currentChatId ?? `chat:${crypto.randomUUID()}`

      // Initialize chat entry in store
      initChat(effectiveChatId)
      setActiveChatId(effectiveChatId)

      // Add user message
      addUserMessage(effectiveChatId, {
        id: Date.now().toString(),
        role: 'user',
        content: prompt,
        timestamp: new Date().toISOString(),
        attachments,
      })

      // Set processing
      setProcessing(effectiveChatId, true)

      // Return chat ID for SSE connection
      return { chatId: effectiveChatId, agentId }
    },
    [agentId, initChat, setActiveChatId, addUserMessage, setProcessing]
  )

  const loadChat = useCallback(async (chatId: string) => {
    initChat(chatId)
    setActiveChatId(chatId)
    // In a real implementation, you would fetch messages from API here
  }, [initChat, setActiveChatId])

  const newChat = useCallback(() => {
    setActiveChatId(null)
  }, [setActiveChatId])

  const stop = useCallback(() => {
    const store = useChatStore.getState()
    const chatId = store.activeChatId
    if (!chatId) return

    setProcessing(chatId, false)
  }, [setProcessing])

  const deleteChat = useCallback((chatId: string) => {
    removeChat(chatId)
  }, [removeChat])

  return {
    send,
    loadChat,
    newChat,
    stop,
    deleteChat,
    appendStreamText,
    addToolUse,
    completeMessage,
    handleError,
    setMessages,
  }
}

// Re-export onChatUpdate for ChatProvider
export { onChatUpdate }
