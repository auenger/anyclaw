/**
 * MessageList Component
 *
 * 显示聊天消息列表，支持流式消息显示和打字动画效果
 */

import { useRef, useEffect, useMemo, useState } from 'react';
import { ScrollArea } from '../ui/scroll-area';
import { cn } from '../../lib/utils';
import type { Message } from '../../types';
import beeImage from '../../assets/bee.png';

// 随机欢迎语
const GREETINGS = [
  "有什么我可以帮你的吗？",
  "今天想做点什么呢？",
  "准备好一起探索了吗？",
  "让我来帮你解决问题吧！",
  "有什么有趣的想法想聊聊？",
  "我在这里等你很久了～",
  "来吧，让我们开始这段旅程！",
];

// 思考中的动态文字
const THINKING_MESSAGES = [
  "正在思考中",
  "分析你的问题",
  "整理思路",
  "查找相关信息",
  "生成回复",
  "理解你的意图",
  "组织语言",
  "准备回答",
];

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

  // 随机选择一个欢迎语（使用 useMemo 确保只在组件挂载时选择一次）
  const greeting = useMemo(() => {
    return GREETINGS[Math.floor(Math.random() * GREETINGS.length)];
  }, []);

  // 动态思考文字
  const [thinkingIndex, setThinkingIndex] = useState(0);
  const [dots, setDots] = useState('');

  // 思考文字轮换动画
  useEffect(() => {
    if (!isLoading) return;

    const textInterval = setInterval(() => {
      setThinkingIndex((prev) => (prev + 1) % THINKING_MESSAGES.length);
    }, 2000);

    const dotsInterval = setInterval(() => {
      setDots((prev) => prev.length >= 3 ? '' : prev + '.');
    }, 400);

    return () => {
      clearInterval(textInterval);
      clearInterval(dotsInterval);
    };
  }, [isLoading]);

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
          <img
            src={beeImage}
            alt="AnyClaw"
            className="w-24 h-24 mx-auto mb-6 object-contain"
          />
          <h3 className="font-semibold text-lg mb-2">开始对话</h3>
          <p className="text-muted-foreground max-w-md mx-auto">
            {greeting}
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
            <div className="h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0">
              <img src={beeImage} alt="AnyClaw" className="w-full h-full object-contain" />
            </div>
            <div className="bg-muted px-4 py-2 rounded-lg max-w-[80%]">
              <p className="text-sm whitespace-pre-wrap">{currentContent}</p>
              <span className="inline-block w-2 h-4 bg-primary animate-pulse ml-1" />
            </div>
          </div>
        )}

        {/* 思考中状态 - 动态效果 */}
        {isLoading && !isStreaming && (
          <div className="flex gap-3">
            <div className="h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 animate-pulse">
              <img src={beeImage} alt="AnyClaw" className="w-full h-full object-contain" />
            </div>
            <div className="bg-muted px-4 py-2 rounded-lg">
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <span className="inline-flex items-center">
                  <span className="animate-spin inline-block w-3 h-3 border-2 border-primary border-t-transparent rounded-full mr-2" />
                  {THINKING_MESSAGES[thinkingIndex]}{dots}
                </span>
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
          <div className="h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0">
            <img src={beeImage} alt="AnyClaw" className="w-full h-full object-contain" />
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
