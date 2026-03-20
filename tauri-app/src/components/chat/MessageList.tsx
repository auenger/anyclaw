/**
 * MessageList Component
 *
 * 显示聊天消息列表，支持流式消息显示和打字动画效果
 */

import { useRef, useEffect } from 'react';
import { Bot } from 'lucide-react';
import { ScrollArea } from '../ui/scroll-area';
import { cn } from '../../lib/utils';
import type { Message } from '../../types';

export interface MessageListProps {
  messages: Message[];
  isStreaming?: boolean;
  currentContent?: string;
  isLoading?: boolean;
  className?: string;
}

export function MessageList({
  messages,
  isStreaming = false,
  currentContent = '',
  isLoading = false,
  className,
}: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, currentContent]);

  if (messages.length === 0 && !isStreaming && !isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center py-12">
          <div className="h-16 w-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white">
            <Bot className="h-8 w-8" />
          </div>
          <h3 className="font-semibold text-lg mb-2">开始对话</h3>
          <p className="text-muted-foreground max-w-md mx-auto">
            发送消息开始与 AnyClaw 智能体对话
          </p>
        </div>
      </div>
    );
  }

  return (
    <ScrollArea className={cn('h-full', className)}>
      <div ref={scrollRef} className="max-w-3xl mx-auto p-6 space-y-4">
        {messages.map((message) => (
          <MessageItem key={message.id} message={message} />
        ))}

        {/* 流式输出中的内容 */}
        {isStreaming && currentContent && (
          <div className="flex gap-3">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white flex-shrink-0">
              <Bot className="h-4 w-4" />
            </div>
            <div className="bg-muted px-4 py-2 rounded-lg max-w-[80%]">
              <p className="text-sm whitespace-pre-wrap">{currentContent}</p>
              <span className="inline-block w-2 h-4 bg-primary animate-pulse ml-1" />
            </div>
          </div>
        )}

        {/* 思考中状态 */}
        {isLoading && !isStreaming && (
          <div className="flex gap-3">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white flex-shrink-0">
              <Bot className="h-4 w-4" />
            </div>
            <div className="bg-muted px-4 py-2 rounded-lg">
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <span className="animate-pulse">●</span>
                思考中...
              </p>
            </div>
          </div>
        )}
      </div>
    </ScrollArea>
  );
}

export interface MessageItemProps {
  message: Message;
  className?: string;
}

export function MessageItem({ message, className }: MessageItemProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={cn(
        'flex gap-3',
        isUser ? 'justify-end' : 'justify-start',
        className
      )}
    >
      {isUser ? (
        <div className="bg-primary text-primary-foreground px-4 py-2 rounded-lg max-w-[80%]">
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>
      ) : (
        <>
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white flex-shrink-0">
            <Bot className="h-4 w-4" />
          </div>
          <div className="bg-muted px-4 py-2 rounded-lg max-w-[80%]">
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          </div>
        </>
      )}
    </div>
  );
}

export default MessageList;
