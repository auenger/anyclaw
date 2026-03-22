import { useState } from 'react'
import { CheckCircle, XCircle, ChevronDown, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface ToolResultBlockProps {
  toolCallId: string
  name: string
  content: string
  status: 'success' | 'error'
  timestamp?: string
}

const MAX_PREVIEW_LENGTH = 200

/**
 * Detect tool result status from content
 * Checks for "Exit code: 0" (success) or "Exit code: 1" (error)
 */
function detectStatus(content: string): 'success' | 'error' {
  if (/Exit code:\s*0/i.test(content)) return 'success'
  if (/Exit code:\s*[1-9]/i.test(content)) return 'error'
  if (/error/i.test(content) && !/no error/i.test(content)) return 'error'
  return 'success'
}

/**
 * ToolResultBlock - Displays tool execution result with collapse/expand
 */
export function ToolResultBlock({
  name,
  content,
  status: propStatus,
  timestamp,
}: ToolResultBlockProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [showFullContent, setShowFullContent] = useState(false)

  const status = propStatus || detectStatus(content)
  const isSuccess = status === 'success'
  const isLongContent = content.length > MAX_PREVIEW_LENGTH
  const previewContent = isLongContent && !showFullContent
    ? content.slice(0, MAX_PREVIEW_LENGTH) + '...'
    : content

  const statusColor = isSuccess
    ? 'border-l-green-500/50 bg-green-500/5'
    : 'border-l-red-500/50 bg-red-500/5'

  const StatusIcon = isSuccess ? CheckCircle : XCircle
  const iconColor = isSuccess ? 'text-green-500' : 'text-red-500'

  return (
    <div className={cn('my-1 border-l-2 rounded-r px-2 py-1 text-xs', statusColor)}>
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-1.5 w-full text-left hover:bg-muted/30 rounded px-0.5 -mx-0.5 transition-colors"
      >
        {isExpanded ? (
          <ChevronDown className="h-3 w-3 shrink-0 text-muted-foreground" />
        ) : (
          <ChevronRight className="h-3 w-3 shrink-0 text-muted-foreground" />
        )}
        <StatusIcon className={cn('h-3.5 w-3.5 shrink-0', iconColor)} />
        <span className="font-mono text-muted-foreground truncate">{name}</span>
        {timestamp && (
          <span className="text-muted-foreground/60 ml-auto shrink-0">
            {new Date(timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
          </span>
        )}
      </button>

      {/* Content (collapsed by default) */}
      {isExpanded && (
        <div className="mt-1.5 pl-5">
          <pre className="whitespace-pre-wrap break-all font-mono text-muted-foreground bg-muted/30 rounded p-1.5 max-h-64 overflow-auto">
            {previewContent}
          </pre>
          {isLongContent && !showFullContent && (
            <button
              onClick={() => setShowFullContent(true)}
              className="text-primary hover:underline mt-1"
            >
              展开全文 ({content.length} 字符)
            </button>
          )}
          {showFullContent && isLongContent && (
            <button
              onClick={() => setShowFullContent(false)}
              className="text-primary hover:underline mt-1"
            >
              收起
            </button>
          )}
        </div>
      )}
    </div>
  )
}
