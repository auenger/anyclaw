/**
 * useSSE Hook
 *
 * 提供 SSE 连接管理、消息状态和断开/重连控制
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { SSEClient } from '../lib/sse';
import type { SSEEvent, SSEState, Message } from '../types';

export interface UseSSEOptions {
  url: string;
  enabled?: boolean;
  reconnectAttempts?: number;
  reconnectInterval?: number;
  onMessage?: (event: SSEEvent) => void;
  onError?: (error: Error) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

export interface UseSSEReturn {
  state: SSEState;
  messages: Message[];
  isStreaming: boolean;
  currentContent: string;
  connect: () => void;
  disconnect: () => void;
  clearMessages: () => void;
  stopStreaming: () => void;
}

export function useSSE(options: UseSSEOptions): UseSSEReturn {
  const {
    url,
    enabled = true,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
    onMessage,
    onError,
    onConnect,
    onDisconnect,
  } = options;

  const [state, setState] = useState<SSEState>({
    connected: false,
    reconnecting: false,
    error: null,
  });

  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentContent, setCurrentContent] = useState('');

  const clientRef = useRef<SSEClient | null>(null);
  const currentMessageRef = useRef<{ id: string; content: string } | null>(null);

  // 处理 SSE 事件
  const handleEvent = useCallback(
    (event: SSEEvent) => {
      // 先调用外部回调
      onMessage?.(event);

      switch (event.type) {
        case 'connected':
          setState((prev) => ({ ...prev, connected: true, reconnecting: false, error: null }));
          break;

        case 'message_start':
          setIsStreaming(true);
          setCurrentContent('');
          currentMessageRef.current = {
            id: event.data.message_id || `msg_${Date.now()}`,
            content: '',
          };
          break;

        case 'content_delta':
          if (event.data.delta) {
            setCurrentContent((prev) => prev + event.data.delta!);
            if (currentMessageRef.current) {
              currentMessageRef.current.content += event.data.delta!;
            }
          } else if (event.data.content) {
            setCurrentContent(event.data.content);
            if (currentMessageRef.current) {
              currentMessageRef.current.content = event.data.content;
            }
          }
          break;

        case 'message:outbound':
          // 完整消息到达
          const outboundMessage: Message = {
            id: event.data.payload?.id || event.data.message_id || `msg_${Date.now()}`,
            role: 'assistant',
            content: event.data.payload?.content || event.data.content || '',
            timestamp: event.data.timestamp || Date.now(),
          };
          setMessages((prev) => {
            // 避免重复
            if (prev.some((m) => m.id === outboundMessage.id)) {
              return prev;
            }
            return [...prev, outboundMessage];
          });
          setIsStreaming(false);
          setCurrentContent('');
          currentMessageRef.current = null;
          break;

        case 'message_end':
          // 流式消息结束，将累积的内容添加到消息列表
          if (currentMessageRef.current && currentMessageRef.current.content) {
            const finalMessage: Message = {
              id: currentMessageRef.current.id,
              role: 'assistant',
              content: currentMessageRef.current.content,
              timestamp: event.data.timestamp || Date.now(),
            };
            setMessages((prev) => {
              if (prev.some((m) => m.id === finalMessage.id)) {
                return prev;
              }
              return [...prev, finalMessage];
            });
          }
          setIsStreaming(false);
          setCurrentContent('');
          currentMessageRef.current = null;
          break;

        case 'agent:thinking':
          setIsStreaming(true);
          break;

        case 'tool:start':
        case 'tool:complete':
          // 工具调用事件，可以用于显示状态
          console.log(`Tool event: ${event.type}`, event.data);
          break;

        case 'error':
          setState((prev) => ({
            ...prev,
            error: event.data.error || 'Unknown error',
          }));
          setIsStreaming(false);
          break;
      }
    },
    [onMessage]
  );

  // 连接
  const connect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.close();
    }

    const client = new SSEClient({
      url,
      reconnectAttempts,
      reconnectInterval,
      onMessage: handleEvent,
      onError: (error: Error) => {
        setState((prev) => ({
          ...prev,
          connected: false,
          error: error.message,
        }));
        onError?.(error);
      },
      onConnect: () => {
        setState((prev) => ({
          ...prev,
          connected: true,
          reconnecting: false,
          error: null,
        }));
        onConnect?.();
      },
      onDisconnect: () => {
        setState((prev) => ({
          ...prev,
          connected: false,
        }));
        onDisconnect?.();
      },
    });

    clientRef.current = client;
    client.connect();
  }, [url, handleEvent, reconnectAttempts, reconnectInterval, onError, onConnect, onDisconnect]);

  // 断开
  const disconnect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.close();
      clientRef.current = null;
    }
    setState({
      connected: false,
      reconnecting: false,
      error: null,
    });
  }, []);

  // 清空消息
  const clearMessages = useCallback(() => {
    setMessages([]);
    setCurrentContent('');
    currentMessageRef.current = null;
  }, []);

  // 停止流式输出
  const stopStreaming = useCallback(() => {
    setIsStreaming(false);
    // 如果有累积的内容，将其保存为消息
    if (currentMessageRef.current && currentMessageRef.current.content) {
      const partialMessage: Message = {
        id: currentMessageRef.current.id,
        role: 'assistant',
        content: currentMessageRef.current.content + '\n\n[Stopped]',
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, partialMessage]);
    }
    setCurrentContent('');
    currentMessageRef.current = null;
  }, []);

  // 自动连接/断开
  useEffect(() => {
    if (enabled) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, connect, disconnect]);

  return {
    state,
    messages,
    isStreaming,
    currentContent,
    connect,
    disconnect,
    clearMessages,
    stopStreaming,
  };
}
