import { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, Settings, Plus } from 'lucide-react';
import { invoke } from '@tauri-apps/api/core';
import { Button } from './components/ui';
import { Input } from './components/ui';
import { ScrollArea } from './components/ui';
import { cn } from './lib/utils';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
}

interface SidecarStatus {
  status: 'Stopped' | 'Starting' | 'Running' | 'Stopping' | 'Error';
  port: number;
  pid: number | null;
  uptime_seconds: number;
  message: string;
}

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState('default');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  
  const [sidecarStatus, setSidecarStatus] = useState<SidecarStatus>({
    status: 'Stopped',
    port: 62601,
    pid: null,
    uptime_seconds: 0,
    message: '',
  });

  // 监听 sidecar 状态变化
  useEffect(() => {
    const unlisten = invoke('listen', { event: 'sidecar-status' })
      .then((unlisten: any) => {
        const listener = (event: any) => {
          setSidecarStatus(event.payload);
        };
        return unlisten;
      })
      .catch(console.error);

    return () => {
      unlisten.then((fn: any) => fn?.());
    };
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // SSE 流式接收消息
  useEffect(() => {
    if (sidecarStatus.status !== 'Running') return;

    const eventSource = new EventSource(`http://127.0.0.1:${sidecarStatus.port}/api/stream`);
    console.log('SSE connected to:', `http://127.0.0.1:${sidecarStatus.port}/api/stream`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('SSE event:', data);

        if (data.type === 'message:outbound') {
          const assistantMessage: Message = {
            id: data.payload.id || `assistant_${Date.now()}`,
            role: 'assistant',
            content: data.payload.content,
            timestamp: data.payload.timestamp || Date.now(),
          };
          setMessages(prev => [...prev, assistantMessage]);
          setIsLoading(false);
        } else if (data.type === 'agent:thinking') {
          console.log('Agent thinking:', data.payload);
          setIsLoading(true);
        } else if (data.type === 'tool:start') {
          console.log('Tool started:', data.payload);
        } else if (data.type === 'tool:complete') {
          console.log('Tool completed:', data.payload);
        }
      } catch (error) {
        console.error('Failed to parse SSE message:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      eventSource.close();
    };

    return () => {
      console.log('Closing SSE connection');
      eventSource.close();
    };
  }, [sidecarStatus.status, sidecarStatus.port]);

  const handleStart = async () => {
    try {
      await invoke('start_sidecar');
    } catch (error) {
      console.error('Failed to start sidecar:', error);
    }
  };

  const handleStop = async () => {
    try {
      await invoke('stop_sidecar');
    } catch (error) {
      console.error('Failed to stop sidecar:', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || sidecarStatus.status !== 'Running') return;

    setIsLoading(true);

    // 添加用户消息
    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: Date.now(),
    };
    setMessages([...messages, userMessage]);

    const messageContent = input;
    setInput('');

    try {
      // 发送到 API
      const response = await fetch(`http://127.0.0.1:${sidecarStatus.port}/api/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_id: selectedAgent,
          content: messageContent,
        }),
      });

      const data = await response.json();
      console.log('Message sent:', data);
      // 注意：响应会通过 SSE 流式接收，不在这里处理

    } catch (error) {
      console.error('Failed to send message:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-background">
      {/* 侧边栏 */}
      {sidebarOpen && (
        <aside className="w-64 border-r bg-card flex flex-col">
          {/* 标题 */}
          <div className="p-4 border-b">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white font-bold">
                A
              </div>
              <div>
                <h1 className="font-bold text-lg">AnyClaw</h1>
                <p className="text-xs text-muted-foreground">
                  {sidecarStatus.status === 'Running' ? 'Online' : 'Offline'}
                </p>
              </div>
            </div>
          </div>

          {/* Agent 列表 */}
          <ScrollArea className="flex-1">
            <div className="p-2 space-y-1">
              <button
                onClick={() => setSelectedAgent('default')}
                className={cn(
                  "w-full text-left px-3 py-2 rounded-lg hover:bg-accent transition-colors",
                  selectedAgent === 'default' && 'bg-accent'
                )}
              >
                <div className="flex items-center gap-2">
                  <Bot className="h-4 w-4" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm">Default Agent</div>
                    <div className="text-xs text-muted-foreground truncate">
                      claude-sonnet-4
                    </div>
                  </div>
                </div>
              </button>

              <button className="w-full text-left px-3 py-2 rounded-lg hover:bg-accent transition-colors">
                <div className="flex items-center gap-2">
                  <Plus className="h-4 w-4" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm">Create Agent</div>
                    <div className="text-xs text-muted-foreground">
                      Add a new agent
                    </div>
                  </div>
                </div>
              </button>
            </div>
          </ScrollArea>

          {/* 底部按钮 */}
          <div className="p-4 border-t space-y-2">
            <Button
              variant="ghost"
              className="w-full justify-start"
              onClick={() => console.log('Open settings')}
            >
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
          </div>
        </aside>
      )}

      {/* 主内容区 */}
      <main className="flex-1 flex flex-col">
        {/* 顶部栏 */}
        <div className="h-14 border-b flex items-center px-4 justify-between">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              <User className="h-5 w-5" />
            </Button>
            <div>
              <h2 className="font-semibold">Chat</h2>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className={cn(
              "text-sm px-2 py-1 rounded-full",
              sidecarStatus.status === 'Running' ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100" :
              sidecarStatus.status === 'Error' ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100" :
              "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100"
            )}>
              {sidecarStatus.status}
            </span>
          </div>
        </div>

        {/* 聊天消息区 */}
        <div className="flex-1 overflow-hidden">
          {sidecarStatus.status !== 'Running' ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center space-y-4">
                <p className="text-lg text-muted-foreground">Backend is not running</p>
                <Button onClick={handleStart}>
                  Start Backend
                </Button>
              </div>
            </div>
          ) : (
            <ScrollArea className="h-full">
              <div ref={scrollRef} className="max-w-3xl mx-auto p-6 space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="h-16 w-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white">
                      <Bot className="h-8 w-8" />
                    </div>
                    <h3 className="font-semibold text-lg mb-2">Start a conversation</h3>
                    <p className="text-muted-foreground max-w-md mx-auto">
                      Send a message to start chatting with AnyClaw agent.
                    </p>
                  </div>
                ) : (
                  messages.map((message) => (
                    <div
                      key={message.id}
                      className={cn(
                        "flex gap-3",
                        message.role === 'user' ? 'justify-end' : 'justify-start'
                      )}
                    >
                      {message.role === 'user' ? (
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
                  ))
                )}

                {isLoading && (
                  <div className="flex gap-3">
                    <div className="h-8 w-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white flex-shrink-0">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="bg-muted px-4 py-2 rounded-lg">
                      <p className="text-sm text-muted-foreground">Thinking...</p>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>
          )}
        </div>

        {/* 输入框 */}
        <div className="border-t p-4">
          <div className="max-w-3xl mx-auto flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type a message..."
              disabled={sidecarStatus.status !== 'Running' || isLoading}
              className="flex-1"
            />
            <Button
              onClick={handleSend}
              disabled={sidecarStatus.status !== 'Running' || isLoading || !input.trim()}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
