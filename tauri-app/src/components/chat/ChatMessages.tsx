import { useEffect, useState, useMemo } from 'react'
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
import type { TimelineItem, ToolUseItem, ToolResult } from '@/stores/chat'
import { buildRenderableTimeline, type RenderableTimelineItem } from './timeline'
import { useI18n } from '@/i18n'
import beeImage from '@/assets/bee.png'

// 思考中的动态文字 - 中文
const THINKING_MESSAGES_ZH = [
  "正在思考中",
  "分析你的问题",
  "整理思路",
  "查找相关信息",
  "生成回复",
  "理解你的意图",
  "组织语言",
  "准备回答",
]

// 思考中的动态文字 - 英文
const THINKING_MESSAGES_EN = [
  "Thinking",
  "Analyzing your question",
  "Organizing thoughts",
  "Finding information",
  "Generating response",
  "Understanding your intent",
  "Preparing answer",
]

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
  const { locale } = useI18n()
  const renderableItems = buildRenderableTimeline(timelineItems)

  // 根据语言选择思考文字数组
  const thinkingMessages = locale === 'zh' ? THINKING_MESSAGES_ZH : THINKING_MESSAGES_EN

  // 动态思考文字
  const [thinkingIndex, setThinkingIndex] = useState(0)
  const [dots, setDots] = useState('')

  // Build tool results map from tool messages
  const toolResultsMap = useMemo(() => {
    const map = new Map<string, ToolResult>()
    for (const item of timelineItems) {
      if (item.kind === 'message' && item.role === 'assistant' && item.toolResults) {
        for (const result of item.toolResults) {
          map.set(result.toolCallId, result)
        }
      }
    }
    return map
  }, [timelineItems])

  // 思考文字轮换动画
  useEffect(() => {
    if (!isProcessing) {
      setThinkingIndex(0)
      setDots('')
      return
    }

    const textInterval = setInterval(() => {
      setThinkingIndex((prev) => (prev + 1) % thinkingMessages.length)
    }, 2000)

    const dotsInterval = setInterval(() => {
      setDots((prev) => prev.length >= 3 ? '' : prev + '.')
    }, 400)

    return () => {
      clearInterval(textInterval)
      clearInterval(dotsInterval)
    }
  }, [isProcessing, thinkingMessages.length])

  return (
    <Conversation data-testid="message-list">
      <ConversationContent className="max-w-3xl mx-auto w-full px-4 py-6 gap-1">
        {renderableItems.map((item) => (
          <TimelineRow key={item.id} item={item} toolResultsMap={toolResultsMap} />
        ))}

        {/* Thinking state */}
        {isProcessing && !streamingText && pendingToolUse.length === 0 && (
          <div className="flex gap-3 py-3">
            <div className="h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 animate-pulse">
              <img src={beeImage} alt="AnyClaw" className="w-full h-full object-contain" />
            </div>
            <div className="bg-muted px-4 py-2 rounded-lg">
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <span className="inline-flex items-center">
                  <span className="animate-spin inline-block w-3 h-3 border-2 border-primary border-t-transparent rounded-full mr-2" />
                  {thinkingMessages[thinkingIndex]}{dots}
                </span>
              </p>
            </div>
          </div>
        )}
        <ScrollOnChange messageCount={renderableItems.length} isProcessing={isProcessing} />
      </ConversationContent>
      <ConversationScrollButton />
    </Conversation>
  )
}

function TimelineRow({
  item,
  toolResultsMap
}: {
  item: RenderableTimelineItem
  toolResultsMap: Map<string, ToolResult>
}) {
  if (item.kind === 'tool_use_group') {
    return <ToolUseTimelineGroup items={item.items} />
  }

  switch (item.kind) {
    case 'message':
      return item.role === 'user'
        ? <UserMessage message={{ ...item, role: 'user' as const }} />
        : <AssistantMessage
            message={{ ...item, role: 'assistant' as const }}
            toolResults={toolResultsMap}
          />
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
        <div className="h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0">
          <img src={beeImage} alt="AnyClaw" className="w-full h-full object-contain" />
        </div>
        <div className="flex-1 min-w-0">
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
        <div className="h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0">
          <img src={beeImage} alt="AnyClaw" className="w-full h-full object-contain" />
        </div>
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
        <div className="h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0">
          <img src={beeImage} alt="AnyClaw" className="w-full h-full object-contain" />
        </div>
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
