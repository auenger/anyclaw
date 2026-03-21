import { useEffect } from 'react'
import { Loader2 } from 'lucide-react'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from '@/components/ai-elements/conversation'
import { useStickToBottomContext } from 'use-stick-to-bottom'
import {
  Message as AIMessage,
  MessageContent,
  MessageResponse,
} from '@/components/ai-elements/message'
import { UserMessage } from './UserMessage'
import { AssistantMessage } from './AssistantMessage'
import { ToolUseBlock } from './ToolUseBlock'
import type { TimelineItem, ToolUseItem } from '@/stores/chat'
import { buildRenderableTimeline, type RenderableTimelineItem } from './timeline'

// Simple i18n placeholder
const t = {
  chat: {
    thinking: 'Thinking...',
    assistant: 'Assistant',
  },
}

interface ChatMessagesProps {
  timelineItems: TimelineItem[]
  streamingText: string
  isProcessing: boolean
  pendingToolUse: ToolUseItem[]
}

export function ChatMessages({
  timelineItems,
  streamingText,
  isProcessing,
  pendingToolUse,
}: ChatMessagesProps) {
  const renderableItems = buildRenderableTimeline(timelineItems)

  return (
    <Conversation data-testid="message-list">
      <ConversationContent className="max-w-3xl mx-auto w-full px-4 py-6 gap-1">
        {renderableItems.map((item) => (
          <TimelineRow key={item.id} item={item} />
        ))}

        {/* Thinking state */}
        {isProcessing && !streamingText && pendingToolUse.length === 0 && (
          <div className="flex gap-3 py-3">
            <Avatar className="h-8 w-8 mt-0.5">
              <AvatarImage src="/icon.svg" alt="AnyClaw" />
              <AvatarFallback className="bg-gradient-to-br from-violet-500/20 to-purple-500/20 text-[10px] font-semibold">
                AI
              </AvatarFallback>
            </Avatar>
            <div className="flex items-center gap-2 text-muted-foreground text-sm pt-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              {t.chat.thinking}
            </div>
          </div>
        )}
        <ScrollOnChange messageCount={renderableItems.length} isProcessing={isProcessing} />
      </ConversationContent>
      <ConversationScrollButton />
    </Conversation>
  )
}

function TimelineRow({ item }: { item: RenderableTimelineItem }) {
  if (item.kind === 'tool_use_group') {
    return <ToolUseTimelineGroup items={item.items} />
  }

  switch (item.kind) {
    case 'message':
      return item.role === 'user'
        ? <UserMessage message={{ ...item, role: 'user' as const }} />
        : <AssistantMessage message={{ ...item, role: 'assistant' as const }} />
    case 'assistant_stream':
      return <StreamingAssistantItem content={item.content} />
    case 'tool_use':
      return <ToolUseTimelineItem item={item} />
    default:
      return null
  }
}

function StreamingAssistantItem({ content }: { content: string }) {
  return (
    <AIMessage from="assistant">
      <div className="flex gap-3 py-3">
        <Avatar className="h-8 w-8 mt-0.5">
          <AvatarImage src="/icon.svg" alt="AnyClaw" />
          <AvatarFallback className="bg-gradient-to-br from-violet-500/20 to-purple-500/20 text-[10px] font-semibold">
            AI
          </AvatarFallback>
        </Avatar>
        <div className="flex-1 min-w-0">
          <div className="text-xs font-medium text-muted-foreground mb-1.5">
            {t.chat.assistant}
          </div>
          <MessageContent>
            <MessageResponse parseIncompleteMarkdown>{content}</MessageResponse>
          </MessageContent>
        </div>
      </div>
    </AIMessage>
  )
}

function ToolUseTimelineGroup({ items }: { items: ToolUseItem[] }) {
  return (
    <AIMessage from="assistant">
      <div className="flex gap-3 py-2">
        <Avatar className="h-8 w-8 mt-0.5">
          <AvatarImage src="/icon.svg" alt="AnyClaw" />
          <AvatarFallback className="bg-gradient-to-br from-violet-500/20 to-purple-500/20 text-[10px] font-semibold">
            AI
          </AvatarFallback>
        </Avatar>
        <div className="flex-1 min-w-0">
          <ToolUseBlock items={items} />
        </div>
      </div>
    </AIMessage>
  )
}

function ToolUseTimelineItem({ item }: { item: Extract<TimelineItem, { kind: 'tool_use' }> }) {
  return (
    <AIMessage from="assistant">
      <div className="flex gap-3 py-2">
        <Avatar className="h-8 w-8 mt-0.5">
          <AvatarImage src="/icon.svg" alt="AnyClaw" />
          <AvatarFallback className="bg-gradient-to-br from-violet-500/20 to-purple-500/20 text-[10px] font-semibold">
            AI
          </AvatarFallback>
        </Avatar>
        <div className="flex-1 min-w-0">
          <ToolUseBlock items={[{ id: item.id, name: item.name, input: item.input, status: item.status }]} />
        </div>
      </div>
    </AIMessage>
  )
}

/** Auto-scroll to bottom when message count changes or processing starts */
function ScrollOnChange({ messageCount, isProcessing }: { messageCount: number; isProcessing: boolean }) {
  const { scrollToBottom } = useStickToBottomContext()

  useEffect(() => {
    scrollToBottom()
  }, [messageCount, isProcessing, scrollToBottom])

  return null
}
