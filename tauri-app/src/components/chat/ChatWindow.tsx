/**
 * ChatWindow Component
 *
 * 完整的聊天窗口，集成 SSE 流式消息
 */

import { useState, useCallback } from 'react';
import { MessageList } from './MessageList';
import { InputArea } from './InputArea';
import { useSSE } from '../../hooks/useSSE';
import { getApiClient } from '../../lib/api';
import type { Message, SidecarStatus } from '../../types';

export interface ChatWindowProps {
  agentId?: string;
  sidecarStatus: SidecarStatus;
}

export function ChatWindow({
  agentId = 'default',
  sidecarStatus,
}: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);

  const isSidecarRunning = sidecarStatus.status === 'Running';
  const streamUrl = isSidecarRunning
    ? `http://127.0.0.1:${sidecarStatus.port}/api/stream`
    : '';

  // 稳定的 onMessage 回调（使用 ref 避免依赖变化）
  const handleSSEMessage = useCallback((event: { type: string; data: any }) => {
    // 处理完整消息
    if (event.type === 'message:outbound') {
      const newMessage: Message = {
        id: event.data.payload?.id || `msg_${Date.now()}`,
        role: 'assistant',
        content: event.data.payload?.content || event.data.content || '',
        timestamp: event.data.timestamp || Date.now(),
      };
      setMessages((prev) => {
        if (prev.some((m) => m.id === newMessage.id)) {
          return prev;
        }
        return [...prev, newMessage];
      });
      setIsSending(false);
    }
  }, []);

  const handleSSEError = useCallback((error: Error) => {
    console.error('SSE error:', error);
  }, []);

  // SSE 连接
  const {
    isStreaming,
    currentContent,
    stopStreaming,
  } = useSSE({
    url: streamUrl,
    enabled: isSidecarRunning,
    onMessage: handleSSEMessage,
    onError: handleSSEError,
  });

  // 发送消息
  const handleSend = useCallback(
    async (content: string) => {
      if (!isSidecarRunning) return;

      // 添加用户消息
      const userMessage: Message = {
        id: `user_${Date.now()}`,
        role: 'user',
        content,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsSending(true);

      try {
        const api = getApiClient(sidecarStatus.port);
        await api.sendMessage(agentId, content);
      } catch (error) {
        console.error('Failed to send message:', error);
        setIsSending(false);

        // 添加错误消息
        const errorMessage: Message = {
          id: `error_${Date.now()}`,
          role: 'system',
          content: `发送失败: ${(error as Error).message}`,
          timestamp: Date.now(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    },
    [agentId, isSidecarRunning, sidecarStatus.port]
  );

  // 停止生成
  const handleStop = useCallback(() => {
    stopStreaming();
    setIsSending(false);
  }, [stopStreaming]);

  return (
    <div className="flex flex-col h-full">
      {/* 消息列表 */}
      <MessageList
        messages={messages}
        isStreaming={isStreaming}
        currentContent={currentContent}
        isLoading={isSending && !isStreaming}
        className="flex-1"
      />

      {/* 输入区域 */}
      <InputArea
        onSend={handleSend}
        onStop={handleStop}
        isStreaming={isStreaming}
        isLoading={isSending && !isStreaming}
        disabled={!isSidecarRunning}
        placeholder={
          isSidecarRunning ? '输入消息...' : '等待后端启动...'
        }
      />
    </div>
  );
}

export default ChatWindow;
