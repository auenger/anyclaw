/**
 * SSE (Server-Sent Events) Client
 *
 * 提供自动重连、错误处理和消息解析功能
 */

import type { SSEEvent, SSEEventType } from '../types';

export interface SSEClientOptions {
  url: string;
  onMessage?: (event: SSEEvent) => void;
  onError?: (error: Error) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

export class SSEClient {
  private eventSource: EventSource | null = null;
  private options: Required<SSEClientOptions>;
  private reconnectCount = 0;
  private isManualClose = false;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;

  constructor(options: SSEClientOptions) {
    this.options = {
      reconnectAttempts: 5,
      reconnectInterval: 3000,
      onMessage: () => {},
      onError: () => {},
      onConnect: () => {},
      onDisconnect: () => {},
      ...options,
    };
  }

  connect(): void {
    if (this.eventSource) {
      this.close();
    }

    this.isManualClose = false;

    try {
      this.eventSource = new EventSource(this.options.url);
      this.setupEventListeners();
    } catch (error) {
      this.handleError(error as Error);
    }
  }

  private setupEventListeners(): void {
    if (!this.eventSource) return;

    this.eventSource.onopen = () => {
      this.reconnectCount = 0;
      this.options.onConnect();

      // 发送连接成功事件
      this.options.onMessage({
        type: 'connected',
        data: {},
      });
    };

    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      } catch (error) {
        // 如果不是 JSON，作为原始文本处理
        this.handleMessage({
          type: 'content_delta',
          data: { content: event.data },
        });
      }
    };

    this.eventSource.onerror = () => {
      this.handleError(new Error('SSE connection error'));
    };

    // 监听自定义事件类型
    const eventTypes: SSEEventType[] = [
      'message_start',
      'content_delta',
      'message_end',
      'message:outbound',
      'agent:thinking',
      'tool:start',
      'tool:complete',
      'error',
    ];

    eventTypes.forEach((eventType) => {
      this.eventSource?.addEventListener(eventType, (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          this.handleMessage({
            type: eventType,
            data: data.data || data,
          });
        } catch {
          this.handleMessage({
            type: eventType,
            data: { content: event.data },
          });
        }
      });
    });
  }

  private handleMessage(data: any): void {
    // 标准化消息格式
    const event: SSEEvent = {
      type: data.type || 'content_delta',
      data: data.data || data.payload || data,
    };

    this.options.onMessage(event);
  }

  private handleError(error: Error): void {
    this.options.onError(error);

    if (!this.isManualClose && this.reconnectCount < this.options.reconnectAttempts) {
      this.scheduleReconnect();
    } else {
      this.options.onDisconnect();
    }
  }

  private scheduleReconnect(): void {
    this.reconnectCount++;

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    this.reconnectTimeout = setTimeout(() => {
      this.connect();
    }, this.options.reconnectInterval);
  }

  close(): void {
    this.isManualClose = true;

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }

    this.options.onDisconnect();
  }

  get isConnected(): boolean {
    return this.eventSource?.readyState === EventSource.OPEN;
  }
}

/**
 * 创建 SSE 客户端
 */
export function createSSEClient(options: SSEClientOptions): SSEClient {
  return new SSEClient(options);
}
