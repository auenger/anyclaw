import { useChatStore } from '@/stores/chat'
import type { ToolUseItem } from '@/stores/chat'

type SSEEvent = {
  type: string
  agentId?: string
  chatId?: string
  text?: string
  fullText?: string
  error?: string
  errorCode?: string
  isProcessing?: boolean
  tool?: string
  input?: string
}

class SSEManager {
  private connections = new Map<string, EventSource>()
  private lastEventTime = new Map<string, number>()
  private fallbackTimers = new Map<string, ReturnType<typeof setInterval>>()

  constructor() {
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', () => this.disconnectAll())
    }
  }

  connect(chatId: string, baseUrl: string = 'http://127.0.0.1:62601'): void {
    if (this.connections.has(chatId)) return

    const es = new EventSource(
      `${baseUrl}/api/stream/${encodeURIComponent(chatId)}`,
    )
    this.connections.set(chatId, es)
    this.lastEventTime.set(chatId, Date.now())

    const handleEvent = (e: Event) => {
      try {
        const me = e as MessageEvent
        const data = JSON.parse(me.data) as SSEEvent
        this.lastEventTime.set(chatId, Date.now())
        this.handleSSEEvent(chatId, data)
      } catch {
        // Ignore parse errors
      }
    }

    es.addEventListener('stream', handleEvent)
    es.addEventListener('content_delta', handleEvent)
    es.addEventListener('complete', handleEvent)
    es.addEventListener('message_end', handleEvent)
    es.addEventListener('error', handleEvent)
    es.addEventListener('processing', handleEvent)
    es.addEventListener('tool_use', handleEvent)

    es.onerror = () => {
      // Auto-reconnect handled by EventSource
    }

    // Start fallback timer: polls backend every 5s if no SSE event for 8s
    const timer = setInterval(() => {
      const lastTime = this.lastEventTime.get(chatId) ?? 0
      if (Date.now() - lastTime < 8000) return

      const store = useChatStore.getState()
      const chat = store.chats[chatId]
      if (!chat?.isProcessing) return

      // If no events for 8s and still processing, something went wrong
      // Set processing to false
      store.setProcessing(chatId, false)
    }, 5000)
    this.fallbackTimers.set(chatId, timer)
  }

  disconnect(chatId: string): void {
    const es = this.connections.get(chatId)
    if (es) {
      es.close()
      this.connections.delete(chatId)
    }
    const timer = this.fallbackTimers.get(chatId)
    if (timer) {
      clearInterval(timer)
      this.fallbackTimers.delete(chatId)
    }
    this.lastEventTime.delete(chatId)
  }

  disconnectAll(): void {
    for (const chatId of this.connections.keys()) {
      this.disconnect(chatId)
    }
  }

  isConnected(chatId: string): boolean {
    return this.connections.has(chatId)
  }

  private handleSSEEvent(chatId: string, event: SSEEvent): void {
    const store = useChatStore.getState()

    switch (event.type) {
      case 'stream':
      case 'content_delta':
        store.appendStreamText(chatId, event.text ?? '')
        break

      case 'tool_use': {
        const tool: ToolUseItem = {
          id: Date.now().toString(),
          name: event.tool ?? 'unknown',
          input: event.input,
          status: 'running',
        }
        store.addToolUse(chatId, tool)
        break
      }

      case 'complete':
      case 'message_end': {
        const chatState = store.chats[chatId]
        const finalToolUse = (chatState?.pendingToolUse ?? []).map((t) => ({
          ...t,
          status: 'done' as const,
        }))
        store.completeMessage(chatId, event.fullText ?? '', finalToolUse)
        break
      }

      case 'processing':
        store.setProcessing(chatId, event.isProcessing ?? false)
        if (!event.isProcessing) {
          this.disconnect(chatId)
        }
        break

      case 'error':
        store.handleError(chatId, event.error ?? '', event.errorCode)
        this.disconnect(chatId)
        break
    }
  }
}

// Singleton instance
export const sseManager = new SSEManager()
