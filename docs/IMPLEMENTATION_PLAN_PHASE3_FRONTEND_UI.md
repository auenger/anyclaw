# 实施计划 Phase 3: 基础前端 UI

> **目标**：实现完整的 GUI 前端，参考 YouClaw 的设计，提供聊天、Agent 管理、Skills 管理、配置管理等功能

## 📋 概述

**时间估算**：5-7 天
**优先级**：P0（必须）
**依赖**：Phase 1 (FastAPI + SSE) 和 Phase 2 (Tauri Shell) 完成

## 🎯 核心目标

1. ✅ 实现 shadcn/ui 组件库集成
2. ✅ 实现主页布局（左侧 Agent 列表，右侧聊天窗口）
3. ✅ 实现 Agent 配置页面
4. ✅ 实现 Skills 管理页面
5. ✅ 实现配置管理页面
6. ✅ 实现系统托盘菜单（前端侧）

---

## 📂 目录结构

```
tauri-app/
├── src/
│   ├── components/           # UI 组件
│   │   ├── ui/             # shadcn/ui 基础组件
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── textarea.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── sheet.tsx
│   │   │   ├── table.tsx
│   │   │   ├── card.tsx
│   │   │   ├── select.tsx
│   │   │   ├── switch.tsx
│   │   │   ├── toast.tsx
│   │   │   └── ...
│   │   ├── layout/         # 布局组件
│   │   │   ├── sidebar.tsx
│   │   │   ├── header.tsx
│   │   │   ├── main.tsx
│   │   │   └── footer.tsx
│   │   ├── chat/           # 聊天相关组件
│   │   │   ├── chat-window.tsx
│   │   │   ├── message-bubble.tsx
│   │   │   ├── input-area.tsx
│   │   │   └── typing-indicator.tsx
│   │   ├── agents/         # Agent 相关组件
│   │   │   ├── agent-list.tsx
│   │   │   ├── agent-card.tsx
│   │   │   └── agent-config.tsx
│   │   ├── skills/         # Skills 相关组件
│   │   │   ├── skill-list.tsx
│   │   │   ├── skill-card.tsx
│   │   │   └── skill-editor.tsx
│   │   └── settings/       # 设置相关组件
│   │       ├── settings-panel.tsx
│   │       └── setting-item.tsx
│   ├── pages/              # 页面
│   │   ├── chat.tsx        # 聊天页面（主页）
│   │   ├── agents.tsx      # Agent 管理页面
│   │   ├── skills.tsx      # Skills 管理页面
│   │   ├── tasks.tsx       # 定时任务页面
│   │   ├── logs.tsx        # 日志页面
│   │   └── settings.tsx    # 设置页面
│   ├── lib/                # 工具库
│   │   ├── api.ts          # API 客户端
│   │   ├── store.ts        # 状态管理
│   │   └── utils.ts        # 工具函数
│   ├── hooks/              # React Hooks
│   │   ├── use-api.ts      # API 调用 hooks
│   │   ├── use-sse.ts      # SSE 流式 hooks
│   │   └── use-store.ts    # 状态管理 hooks
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

---

## 🔧 技术栈

### 核心依赖

```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.22.0",
    "@tauri-apps/api": "^2.0.0",
    "zustand": "^4.5.0",
    "axios": "^1.6.0",
    "eventsource": "^2.0.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2.0.0",
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "@types/react": "^18.3.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0"
  }
}
```

### shadcn/ui 配置

```bash
# 初始化 shadcn/ui
cd tauri-app
npx shadcn@latest init

# 安装常用组件
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add textarea
npx shadcn@latest add dialog
npx shadcn@latest add sheet
npx shadcn@latest add table
npx shadcn@latest add card
npx shadcn@latest add select
npx shadcn@latest add switch
npx shadcn@latest add toast
npx shadcn@latest add scroll-area
npx shadcn@latest add separator
npx shadcn@latest add dropdown-menu
npx shadcn@latest add label
npx shadcn@latest add badge
```

---

## 📝 详细任务清单

### Task 3.1: 配置 Tailwind CSS

**文件**：`tauri-app/tailwind.config.js`

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

**文件**：`tauri-app/src/index.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 224 71% 4%;
    --foreground: 213 31% 91%;
    --card: 224 71% 4%;
    --card-foreground: 213 Claw31% 91%;
    --popover: 224 71% 4%;
    --popover-foreground: 213 31% 91%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 222.2 47.4% 11.2%;
    --secondary-foreground: 210 40% 98%;
    --muted: 223 47% 11%;
    --muted-foreground: 215.4 16.3% 56.9%;
    --accent: 216 34% 17%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 63% 31%;
    --destructive-foreground: 210 40% 98%;
    --border: 216 34% 17%;
    --input: 216 34% 17%;
    --ring: 216 34% 17%;
    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
}
```

---

### Task 3.2: 实现 API 客户端

**文件**：`tauri-app/src/lib/api.ts`

```typescript
/** API client for AnyClaw backend */

import axios from 'axios';
import type { AxiosInstance } from 'axios';

// API 基础 URL（从 Tauri 设置读取）
const API_BASE_URL = 'http://127.0.0.1:62601';

export interface AgentInfo {
  id: string;
  name: string;
  model: string;
  description?: string;
  is_active: boolean;
}

export interface Message {
  id: string;
  agent_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
}

export interface SkillInfo {
  name: string;
  description: string;
  version: string;
  enabled: boolean;
}

export interface TaskInfo {
  id: string;
  name: string;
  schedule: string;
  enabled: boolean;
  next_run: string;
}

export interface SendMessageRequest {
  agent_id: string;
  content: string;
  conversation_id?: string;
  metadata?: Record<string, unknown>;
}

export interface SendMessageResponse {
  status: string;
  message_id: string;
  agent_id: string;
}

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = API_BASE_URL) {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => config,
      (error) => Promise.reject(error)
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  // Health
  async healthCheck() {
    const response = await this.client.get('/api/health');
    return response.data;
  }

  // Agents
  async listAgents(): Promise<AgentInfo[]> {
    const response = await this.client.get<AgentInfo[]>('/api/agents');
    return response.data;
  }

  async getAgent(agentId: string): Promise<AgentInfo> {
    const response = await this.client.get<AgentInfo>(`/api/agents/${agentId}`);
    return response.data;
  }

  async activateAgent(agentId: string): Promise<{ status: string; message: string }> {
    const response = await this.client.post(`/api/agents/${agentId}/activate`);
    return response.data;
  }

  async deactivateAgent(agentId: string): Promise<{ status: string; message: string }> {
    const response = await this.client.post(`/api/agents/${agentId}/deactivate`);
    return response.data;
  }

  // Messages
  async sendMessage(request: SendMessageRequest): Promise<SendMessageResponse> {
    const response = await this.client.post<SendMessageResponse>('/api/messages', request);
    return response.data;
  }

  // Skills
  async listSkills(): Promise<{ skills: SkillInfo[] }> {
    const response = await this.client.get('/api/skills');
    return response.data;
  }

  async getSkill(skillName: string): Promise<SkillInfo> {
    const response = await this.client.get<SkillInfo>(`/api/skills/${skillName}`);
    return response.data;
  }

  async enableSkill(skillName: string): Promise<{ status: string; message: string }> {
    const response = await this.client.post(`/api/skills/${skillName}/enable`);
    return response.data;
  }

  async disableSkill(skillName: string): Promise<{ status: string; message: string }> {
    const response = await this.client.post(`/api/skills/${skillName}/disable`);
    return response.data;
  }

  // Tasks
  async listTasks(): Promise<{ tasks: TaskInfo[] }> {
    const response = await this.client.get('/api/tasks');
    return response.data;
  }

  async createTask(task: Omit<TaskInfo, 'id' | 'next_run'>): Promise<TaskInfo> {
    const response = await this.client.post<TaskInfo>('/api/tasks', task);
    return response.data;
  }

  async deleteTask(taskId: string): Promise<{ status: string; message: string }> {
    const response = await this.client.delete(`/api/tasks/${taskId}`);
    return response.data;
  }
}

// 导出单例
export const api = new ApiClient();
```

---

### Task 3.3: 实现 SSE 流式 hooks

**文件**：`tauri-app/src/hooks/use-sse.ts`

```typescript
/** SSE streaming hooks */

import { useEffect, useState, useRef, useCallback } from 'react';

export interface SSEEvent {
  type: string;
  data: string;
  payload?: unknown;
}

export function useSSE(url: string = 'http://127.0.0.1:62601/api/stream') {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const listenersRef = useRef<Map<string, Set<(data: unknown) => void>>>(new Map());

  // 连接到 SSE 端点
  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const eventSource = new EventSource(url);

    eventSource.onopen = () => {
      setConnected(true);
      setError(null);
      console.log('SSE connected');
    };

    eventSource.onerror = (err) => {
      setConnected(false);
      setError('SSE connection error');
      console.error('SSE error:', err);
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const listeners = listenersRef.current.get('message') || new Set();
        listeners.forEach((callback) => callback(data));
      } catch (err) {
        console.error('Failed to parse SSE message:', err);
      }
    };

    // 监听特定事件类型
    const eventTypes = [
      'message:inbound',
      'message:outbound',
      'tool:start',
      'tool:complete',
      'agent:thinking',
    ];

    eventTypes.forEach((eventType) => {
      eventSource.addEventListener(eventType, (event: Event) => {
        const messageEvent = event as MessageEvent;
        try {
          const data = JSON.parse(messageEvent.data);
          const listeners = listenersRef.current.get(eventType) || new Set();
          listeners.forEach((callback) => callback(data));
        } catch (err) {
          console.error(`Failed to parse ${eventType}:`, err);
        }
      });
    });

    eventSourceRef.current = eventSource;
  }, [url]);

  // 断开连接
  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setConnected(false);
    }
  }, []);

  // 订阅事件
  const subscribe = useCallback((eventType: string, callback: (data: unknown) => void) => {
    if (!listenersRef.current.has(eventType)) {
      listenersRef.current.set(eventType, new Set());
    }
    listenersRef.current.get(eventType)!.add(callback);

    // 返回取消订阅函数
    return () => {
      listenersRef.current.get(eventType)?.delete(callback);
    };
  }, []);

  // 组件挂载时自动连接
  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    connected,
    error,
    connect,
    disconnect,
    subscribe,
  };
}
```

---

### Task 3.4: 实现状态管理

**文件**：`tauri-app/src/lib/store.ts`

```typescript
/** Global state management with Zustand */

import { create } from 'zustand';
import type { AgentInfo, Message } from './api';

interface AppState {
  // Selected agent
  selectedAgentId: string | null;
  setSelectedAgentId: (id: string | null) => void;

  // Messages
  messages: Record<string, Message[]>;
  addMessage: (agentId: string, message: Message) => void;
  clearMessages: (agentId: string) => void;

  // Sidecar status
  sidecarStatus: {
    status: 'Stopped' | 'Starting' | 'Running' | 'Stopping' | 'Error';
    port: number;
    pid: number | null;
    uptime_seconds: number;
    message: string;
  };
  setSidecarStatus: (status: AppState['sidecarStatus']) => void;

  // Settings
  apiPort: number;
  setApiPort: (port: number) => void;

  // UI state
  sidebarOpen: boolean;
  toggleSidebar: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Selected agent
  selectedAgentId: null,
  setSelectedAgentId: (id) => set({ selectedAgentId: id }),

  // Messages
  messages: {},
  addMessage: (agentId, message) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [agentId]: [...(state.messages[agentId] || []), message],
      },
    })),
  clearMessages: (agentId) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [agentId]: [],
      },
    })),

  // Sidecar status
  sidecarStatus: {
    status: 'Stopped',
    port: 62601,
    pid: null,
    uptime_seconds: 0,
    message: '',
  },
  setSidecarStatus: (status) => set({ sidecarStatus: status }),

  // Settings
  apiPort: 62601,
  setApiPort: (port) => set({ apiPort: port }),

  // UI state
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
```

---

### Task 3.5: 实现聊天窗口组件

**文件**：`tauri-app/src/components/chat/chat-window.tsx`

```tsx
/** Chat window component */

import { useState, useEffect, useRef } from 'react';
import { useAppStore } from '../../lib/store';
import { api } from '../../lib/api';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { ScrollArea } from '../ui/scroll-area';
import { Send } from 'lucide-react';
import { useSSE } from '../../hooks/use-sse';
import type { Message } from '../../lib/api';

export function ChatWindow() {
  const { selectedAgentId, messages, addMessage, sidecarStatus } = useAppStore();
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // SSE 流式接收消息
  const { subscribe, connected } = useSSE();

  useEffect(() => {
    if (!selectedAgentId) return;

    // 订阅消息事件
    const unsubscribe = subscribe('message:outbound', (data: any) => {
      const message: Message = {
        id: data.id,
        agent_id: data.agent_id,
        role: 'assistant',
        content: data.content,
        timestamp: data.timestamp || Date.now(),
      };
      addMessage(data.agent_id, message);
      setIsLoading(false);
    });

    return () => {
      unsubscribe?.();
    };
  }, [selectedAgentId, subscribe, addMessage]);

  // 自动滚动到底部
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, selectedAgentId]);

  const handleSend = async () => {
    if (!input.trim() || !selectedAgentId) return;

    setIsLoading(true);

    // 添加用户消息
    const userMessage: Message = {
      id: `user_${Date.now()}`,
      agent_id: selectedAgentId,
      role: 'user',
      content: input,
      timestamp: Date.now(),
    };
    addMessage(selectedAgentId, userMessage);

    const messageContent = input;
    setInput('');

    try {
      // 发送到 API
      await api.sendMessage({
        agent_id: selectedAgentId,
        content: messageContent,
      });
    } catch (error) {
      console.error('Failed to send message:', error);
      setIsLoading(false);
    }
  };

  const currentMessages = selectedAgentId ? messages[selectedAgentId] || [] : [];

  if (sidecarStatus.status !== 'Running') {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-lg text-muted-foreground">Backend is not running</p>
          <Button onClick={() => window.invoke('start_sidecar')}>
            Start Backend
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-4 max-w-3xl mx-auto">
          {currentMessages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg px-4 py-2">
                <p className="text-sm text-muted-foreground">Thinking...</p>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="border-t p-4">
        <div className="max-w-3xl mx-auto flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type a message..."
            disabled={!selectedAgentId || isLoading}
            className="flex-1"
          />
          <Button
            onClick={handleSend}
            disabled={!selectedAgentId || isLoading || !input.trim()}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
```

---

### Task 3.6: 实现侧边栏（Agent 列表）

**文件**：`tauri-app/src/components/layout/sidebar.tsx`

```tsx
/** Sidebar with agent list */

import { useEffect, useState } from 'react';
import { useAppStore } from '../../lib/store';
import { api } from '../../lib/api';
import type { AgentInfo } from '../../lib/api';
import { Button } from '../ui/button';
import { ScrollArea } from '../ui/scroll-area';
import { Settings, MessageSquare } from 'lucide-react';
import { cn } from '../../lib/utils';

export function Sidebar() {
  const { selectedAgentId, setSelectedAgentId, sidebarOpen, toggleSidebar, sidecarStatus } = useAppStore();
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (sidecarStatus.status !== 'Running') return;

    const loadAgents = async () => {
      try {
        setLoading(true);
        const data = await api.listAgents();
        setAgents(data);
        // 默认选中第一个 agent
        if (!selectedAgentId && data.length > 0) {
          setSelectedAgentId(data[0].id);
        }
      } catch (error) {
        console.error('Failed to load agents:', error);
      } finally {
        setLoading(false);
      }
    };

    loadAgents();
  }, [sidecarStatus.status, selectedAgentId, setSelectedAgentId]);

  if (!sidebarOpen) {
    return (
      <div className="w-12 border-r flex flex-col items-center py-4 gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          title="Toggle sidebar"
        >
          <MessageSquare className="h-5 w-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => window.location.href = '#settings'}
          title="Settings"
        >
          <Settings className="h-5 w-5" />
        </Button>
      </div>
    );
  }

  return (
    <div className="w-64 border-r flex flex-col">
      {/* Header */}
      <div className="p-4 border-b">
        <h1 className="font-bold text-lg">AnyClaw</h1>
        <p className="text-sm text-muted-foreground">
          {sidecarStatus.status === 'Running' ? 'Online' : 'Offline'}
        </p>
      </div>

      {/* Agent List */}
      <ScrollArea className="flex-1 p-2">
        <div className="space-y-1">
          {loading ? (
            <p className="text-sm text-muted-foreground p-2">Loading agents...</p>
          ) : agents.length === 0 ? (
            <p className="text-sm text-muted-foreground p-2">No agents found</p>
          ) : (
            agents.map((agent) => (
              <button
                key={agent.id}
                onClick={() => setSelectedAgentId(agent.id)}
                className={cn(
                  'w-full text-left px-3 py-2 rounded-lg hover:bg-accent transition-colors',
                  selectedAgentId === agent.id && 'bg-accent'
                )}
              >
                <div className="font-medium text-sm">{agent.name}</div>
                <div className="text-xs text-muted-foreground truncate">
                  {agent.description || agent.model}
                </div>
              </button>
            ))
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-4 border-t space-y-2">
        <Button
          variant="ghost"
          className="w-full justify-start"
          onClick={() => window.location.href = '#settings'}
        >
          <Settings className="h-4 w-4 mr-2" />
          Settings
        </Button>
      </div>
    </div>
  );
}
```

---

### Task 3.7: 实现主页（聊天页面）

**文件**：`tauri-app/src/pages/chat.tsx`

```tsx
/** Chat page (main page) */

import { Sidebar } from '../components/layout/sidebar';
import { ChatWindow } from '../components/chat/chat-window';

export function ChatPage() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <ChatWindow />
    </div>
  );
}
```

**文件**：`tauri-app/src/App.tsx`（更新）

```tsx
import { ChatPage } from './pages/chat';
import { useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useAppStore } from './lib/store';

function App() {
  const { setSidecarStatus } = useAppStore();

  useEffect(() => {
    // 监听 sidecar 状态变化
    const unlisten = invoke('listen', { event: 'sidecar-status' })
      .then((unlisten: any) => {
        // 订阅 Tauri 事件
        const listener = (event: any) => {
          setSidecarStatus(event.payload);
        };
        // 这里需要实际的 Tauri 事件监听
        return unlisten;
      })
      .catch(console.error);

    return () => {
      unlisten.then((fn: any) => fn?.());
    };
  }, [setSidecarStatus]);

  return <ChatPage />;
}

export default App;
```

---

### Task 3.8: 实现设置页面

**文件**：`tauri-app/src/pages/settings.tsx`

```tsx
/** Settings page */

import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useAppStore } from '../lib/store';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Switch } from '../components/ui/switch';
import { Save, Play, Square } from 'lucide-react';

interface SidecarStatus {
  status: 'Stopped' | 'Starting' | 'Running' | 'Stopping' | 'Error';
  port: number;
  pid: number | null;
  uptime_seconds: number;
  message: string;
}

export function SettingsPage() {
  const { apiPort, setApiPort, sidecarStatus } = useAppStore();
  const [port, setPort] = useState(apiPort);
  const [autoStart, setAutoStart] = useState(false);
  const [minimizeToTray, setMinimizeToTray] = useState(true);

  const handleSave = () => {
    setApiPort(port);
    // 保存到 Tauri Store
    invoke('set_setting', { key: 'preferred_port', value: port });
    invoke('set_setting', { key: 'auto_start', value: autoStart });
    invoke('set_setting', { key: 'minimize_to_tray', value: minimizeToTray });
  };

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

  return (
    <div className="h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-2xl space-y-6 p-8">
        <h1 className="text-3xl font-bold">Settings</h1>

        {/* Backend Status */}
        <Card>
          <CardHeader>
            <CardTitle>Backend Status</CardTitle>
            <CardDescription>
              Python sidecar process status
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Status</p>
                <p className="text-sm text-muted-foreground">{sidecarStatus.status}</p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handleStart}
                  disabled={sidecarStatus.status === 'Running'}
                >
                  <Play className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handleStop}
                  disabled={sidecarStatus.status !== 'Running'}
                >
                  <Square className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div>
              <p className="text-sm text-muted-foreground">Port: {sidecarStatus.port}</p>
              <p className="text-sm text-muted-foreground">PID: {sidecarStatus.pid || 'N/A'}</p>
              <p className="text-sm text-muted-foreground">Uptime: {sidecarStatus.uptime_seconds}s</p>
            </div>

            {sidecarStatus.message && (
              <p className="text-sm text-muted-foreground">{sidecarStatus.message}</p>
            )}
          </CardContent>
        </Card>

        {/* API Settings */}
        <Card>
          <CardHeader>
            <CardTitle>API Settings</CardTitle>
            <CardDescription>
              Configure the HTTP API server
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="port">API Port</Label>
              <Input
                id="port"
                type="number"
                value={port}
                onChange={(e) => setPort(parseInt(e.target.value))}
                min="1024"
                max="65535"
              />
            </div>
          </CardContent>
        </Card>

        {/* General Settings */}
        <Card>
          <CardHeader>
            <CardTitle>General</CardTitle>
            <CardDescription>
              General application settings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Auto-start Backend</Label>
                <p className="text-sm text-muted-foreground">
                  Automatically start the backend on app launch
                </p>
              </div>
              <Switch
                checked={autoStart}
                onCheckedChange={setAutoStart}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Minimize to Tray</Label>
                <p className="text-sm text-muted-foreground">
                  Minimize app to system tray instead of taskbar
                </p>
              </div>
              <Switch
                checked={minimizeToTray}
                onCheckedChange={setMinimizeToTray}
              />
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-2">
          <Button onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" />
            Save Settings
          </Button>
        </div>
      </div>
    </div>
  );
}
```

---

## ✅ 验收标准

### 功能验收

- [ ] shadcn/ui 组件库集成完成
- [ ] 聊天窗口功能完整（发送、接收、显示）
- [ ] 侧边栏显示 Agent 列表
- [ ] 切换 Agent 正常工作
- [ ] SSE 流式接收消息正常
- [ ] 设置页面可以修改配置
- [ ] 主题切换（暗色模式）

### UI/UX 验收

- [ ] 布局响应式适配
- [ ] 深色/浅色主题切换
- [ ] 动画流畅自然
- [ ] 无障碍支持（键盘导航、ARIA）

### 性能验收

- [ ] 页面加载时间 < 1 秒
- [ ] 消息渲染流畅（100+ 消息不卡顿）
- [ ] 内存占用 < 150MB

---

## 📅 时间线

| 任务 | 预计时间 | 状态 |
|------|---------|------|
| Task 3.1: 配置 Tailwind CSS | 1h | ⬜ 待开始 |
| Task 3.2: 实现 API 客户端 | 2h | ⬜ 待开始 |
| Task 3.3: 实现 SSE 流式 hooks | 3h | ⬜ 待开始 |
| Task 3.4: 实现状态管理 | 2h | ⬜ 待开始 |
| Task 3.5: 实现聊天窗口组件 | 4h | ⬜ 待开始 |
| Task 3.6: 实现侧边栏（Agent 列表） | 3h | ⬜ 待开始 |
| Task 3.7: 实现主页（聊天页面） | 1h | ⬜ 待开始 |
| Task 3.8: 实现设置页面 | 3h | ⬜ 待开始 |

**总计**: ~19 小时 (2.5 工作日)

---

## 🚀 下一步

完成所有三个阶段后：

1. **端到端测试**：完整流程测试
2. **打包发布**：跨平台打包
3. **文档编写**：用户文档、开发者文档
4. **后续优化**：性能优化、功能扩展

---

**记录时间**: 2026-03-20 04:25 (Asia/Shanghai)
**状态**: ✅ 计划完成，准备实施
