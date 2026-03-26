import { createContext, useContext, useMemo, useCallback, useEffect, useState } from 'react'
import type { Message, TimelineItem, ToolUseItem, Attachment } from './useChat'
import { useChatStore, onChatUpdate } from '@/stores/chat'
import type { ChatItem } from '@/lib/chat-utils'

type Agent = { id: string; name: string }

export interface ChatContextType {
  chatId: string | null
  messages: Message[]
  timelineItems: TimelineItem[]
  streamingText: string
  isProcessing: boolean
  pendingToolUse: ToolUseItem[]
  chatStatus: 'submitted' | 'streaming' | 'ready' | 'error'
  send: (prompt: string, attachments?: Attachment[]) => Promise<void>
  loadChat: (chatId: string) => Promise<void>
  newChat: () => void
  stop: () => void

  chatList: ChatItem[]
  refreshChats: () => void
  searchQuery: string
  setSearchQuery: (q: string) => void
  deleteChat: (chatId: string) => void
  updateChat: (chatId: string, data: { name?: string; avatar?: string }) => void

  agentId: string
  setAgentId: (id: string) => void
  agents: Agent[]
}

export const ChatContext = createContext<ChatContextType | null>(null)

export function useChatContext() {
  const ctx = useContext(ChatContext)
  if (!ctx) throw new Error('useChatContext must be used within ChatProvider')
  return ctx
}

interface ChatProviderProps {
  children: React.ReactNode
  agents?: Agent[]
  initialAgentId?: string
  onSendMessage?: (chatId: string, prompt: string, agentId: string, attachments?: Attachment[]) => Promise<void>
  onLoadChat?: (chatId: string) => Promise<Message[]>
  onDeleteChat?: (chatId: string) => Promise<void>
  onUpdateChat?: (chatId: string, data: { name?: string; avatar?: string }) => Promise<void>
  onFetchChatList?: () => Promise<ChatItem[]>
  refreshTrigger?: number  // External trigger to refresh chat list
}

// localStorage key for persisting agent selection
const LAST_AGENT_ID_KEY = 'anyclaw_lastAgentId'

export function ChatProvider({
  children,
  agents = [{ id: 'default', name: 'Default Agent' }],
  initialAgentId,
  onSendMessage,
  onLoadChat,
  onDeleteChat,
  onUpdateChat,
  onFetchChatList,
  refreshTrigger,
}: ChatProviderProps) {
  // Initialize agentId from: initialAgentId > localStorage > first agent > 'default'
  const [agentId, setAgentIdState] = useState(() => {
    // Priority: initialAgentId > localStorage > first agent > 'default'
    if (initialAgentId) return initialAgentId
    const saved = localStorage.getItem(LAST_AGENT_ID_KEY)
    if (saved && agents.some(a => a.id === saved)) return saved
    return agents[0]?.id || 'default'
  })
  const [chatList, setChatList] = useState<ChatItem[]>([])
  const [searchQuery, setSearchQuery] = useState('')

  // Wrapper for setAgentId that persists to localStorage
  const setAgentId = useCallback((id: string) => {
    setAgentIdState(id)
    localStorage.setItem(LAST_AGENT_ID_KEY, id)
  }, [])

  const activeChatId = useChatStore((s) => s.activeChatId)
  const chats = useChatStore((s) => s.chats)
  const initChat = useChatStore((s) => s.initChat)
  const setActiveChatId = useChatStore((s) => s.setActiveChatId)
  const addUserMessage = useChatStore((s) => s.addUserMessage)
  const setProcessing = useChatStore((s) => s.setProcessing)
  const setMessages = useChatStore((s) => s.setMessages)
  const removeChat = useChatStore((s) => s.removeChat)

  const currentChat = activeChatId ? chats[activeChatId] : null

  // Refresh chat list
  const refreshChats = useCallback(async () => {
    if (onFetchChatList) {
      const list = await onFetchChatList()
      setChatList(list)
    }
  }, [onFetchChatList])

  // Initial load and subscribe to updates
  useEffect(() => {
    refreshChats()
    return onChatUpdate(refreshChats)
  }, [refreshChats, refreshTrigger])  // Re-fetch when refreshTrigger changes

  // Send message
  const send = useCallback(async (prompt: string, attachments?: Attachment[]) => {
    // Use full session key format (api:conv_XXX) to match backend SSE events
    // This prevents creating duplicate chat states when SSE returns api:conv_XXX
    const effectiveChatId = activeChatId ?? `api:conv_${Date.now()}`

    // Initialize chat entry
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

    // Call external handler
    if (onSendMessage) {
      await onSendMessage(effectiveChatId, prompt, agentId, attachments)
    }
  }, [activeChatId, agentId, initChat, setActiveChatId, addUserMessage, setProcessing, onSendMessage])

  // Load chat
  const loadChat = useCallback(async (chatId: string) => {
    initChat(chatId)
    setActiveChatId(chatId)

    if (onLoadChat) {
      const messages = await onLoadChat(chatId)
      setMessages(chatId, messages)
    }
  }, [initChat, setActiveChatId, onLoadChat, setMessages])

  // New chat
  const newChat = useCallback(() => {
    setActiveChatId(null)
  }, [setActiveChatId])

  // Stop
  const stop = useCallback(() => {
    if (activeChatId) {
      setProcessing(activeChatId, false)
    }
  }, [activeChatId, setProcessing])

  // Delete chat
  const deleteChat = useCallback(async (chatId: string) => {
    if (onDeleteChat) {
      await onDeleteChat(chatId)
    }
    removeChat(chatId)
  }, [onDeleteChat, removeChat])

  // Update chat
  const updateChat = useCallback(async (chatId: string, data: { name?: string; avatar?: string }) => {
    if (onUpdateChat) {
      await onUpdateChat(chatId, data)
    }
    // Refresh list after update
    refreshChats()
  }, [onUpdateChat, refreshChats])

  // Filter chats by search query
  const filteredChatList = useMemo(() => {
    if (!searchQuery.trim()) return chatList
    const q = searchQuery.toLowerCase()
    return chatList.filter(chat =>
      chat.name.toLowerCase().includes(q) ||
      (chat.last_message && chat.last_message.toLowerCase().includes(q))
    )
  }, [chatList, searchQuery])

  const value = useMemo<ChatContextType>(() => ({
    chatId: activeChatId,
    messages: currentChat?.messages ?? [],
    timelineItems: currentChat?.timelineItems ?? [],
    streamingText: currentChat?.streamingText ?? '',
    isProcessing: currentChat?.isProcessing ?? false,
    pendingToolUse: currentChat?.pendingToolUse ?? [],
    chatStatus: currentChat?.chatStatus ?? 'ready',
    send,
    loadChat,
    newChat,
    stop,
    chatList: filteredChatList,
    refreshChats,
    searchQuery,
    setSearchQuery,
    deleteChat,
    updateChat,
    agentId,
    setAgentId,
    agents,
  }), [
    activeChatId,
    currentChat,
    send,
    loadChat,
    newChat,
    stop,
    filteredChatList,
    refreshChats,
    searchQuery,
    deleteChat,
    updateChat,
    agentId,
    agents,
  ])

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  )
}
