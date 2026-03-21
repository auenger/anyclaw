import { ChatMessages } from '@/components/chat/ChatMessages'
import { ChatInput } from '@/components/chat/ChatInput'
import { ChatWelcome } from '@/components/chat/ChatWelcome'
import { ChatProvider, useChatContext } from '@/hooks/chatCtx'

// Inner component that uses chat context
function ChatContent() {
  const {
    timelineItems,
    streamingText,
    isProcessing,
    pendingToolUse,
    chatStatus,
    send,
    stop,
    agents,
    agentId,
    setAgentId,
  } = useChatContext()

  const hasMessages = timelineItems.length > 0
  const status = chatStatus === 'ready' ? 'ready' : chatStatus

  const handleSend = async (msg: { text: string; files: Array<{ id: string; filename: string; mediaType: string; filePath?: string }> }) => {
    await send(msg.text)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-hidden">
        {hasMessages ? (
          <ChatMessages
            timelineItems={timelineItems}
            streamingText={streamingText}
            isProcessing={isProcessing}
            pendingToolUse={pendingToolUse}
          />
        ) : (
          <ChatWelcome className="h-full" />
        )}
      </div>

      {/* Input area */}
      <ChatInput
        onSubmit={handleSend}
        onStop={stop}
        status={status}
        disabled={false}
        placeholder="Send a message to AnyClaw..."
        agents={agents}
        selectedAgentId={agentId}
        onAgentChange={setAgentId}
      />
    </div>
  )
}

// Outer component that provides context
export function Chat() {
  return (
    <ChatProvider
      agents={[
        { id: 'default', name: 'Default Agent' },
      ]}
    >
      <ChatContent />
    </ChatProvider>
  )
}

export default Chat
