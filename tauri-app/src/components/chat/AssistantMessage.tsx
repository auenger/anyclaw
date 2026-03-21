import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  Message as AIMessage,
  MessageContent,
  MessageResponse,
  MessageActions,
  MessageAction,
} from '@/components/ai-elements/message'
import { ToolUseBlock } from './ToolUseBlock'
import type { Message } from '@/stores/chat'

// Simple i18n placeholder
const t = {
  chat: {
    assistant: 'Assistant',
    copied: 'Copied!',
    copyCode: 'Copy',
  },
}

interface AssistantMessageProps {
  message: Message & { role: 'assistant' }
}

export function AssistantMessage({ message }: AssistantMessageProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <AIMessage from="assistant" data-testid="message-assistant">
      <div className="group flex gap-3 py-3">
        <Avatar className="h-8 w-8 mt-0.5">
          <AvatarImage src="/icon.svg" alt="AnyClaw" />
          <AvatarFallback className="bg-gradient-to-br from-violet-500/20 to-purple-500/20 text-[10px] font-semibold">
            AI
          </AvatarFallback>
        </Avatar>
        <div className="flex-1 min-w-0">
          <div className="text-xs font-medium text-muted-foreground mb-1.5">
            {t.chat.assistant}
            <span className="ml-2 text-[10px] opacity-60">
              {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
          {message.toolUse && message.toolUse.length > 0 && (
            <ToolUseBlock items={message.toolUse} />
          )}
          <div className="relative">
            <MessageContent>
              <MessageResponse>{message.content}</MessageResponse>
            </MessageContent>
            <MessageActions className="mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <MessageAction
                tooltip={copied ? t.chat.copied : t.chat.copyCode}
                onClick={handleCopy}
              >
                {copied ? <Check className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3.5 w-3.5" />}
              </MessageAction>
            </MessageActions>
          </div>
        </div>
      </div>
    </AIMessage>
  )
}
