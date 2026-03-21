import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { Shell } from './components/layout';
import { ChatWindow } from './components/chat';
import { TasksPage } from './components/tasks';
import type { SidecarStatus } from './types';

// 占位页面组件
function AgentsPage() {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center space-y-2">
        <h2 className="text-lg font-semibold">Agents</h2>
        <p className="text-muted-foreground">Agent 管理页面（开发中）</p>
      </div>
    </div>
  );
}

function MemoryPage() {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center space-y-2">
        <h2 className="text-lg font-semibold">Memory</h2>
        <p className="text-muted-foreground">记忆管理页面（开发中）</p>
      </div>
    </div>
  );
}

function LogsPage() {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center space-y-2">
        <h2 className="text-lg font-semibold">Logs</h2>
        <p className="text-muted-foreground">日志查看页面（开发中）</p>
      </div>
    </div>
  );
}

// 聊天页面包装器
function ChatPage({ sidecarStatus }: { sidecarStatus: SidecarStatus }) {
  if (sidecarStatus.status !== 'Running') {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-lg text-muted-foreground">后端服务未运行</p>
          <button
            className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90"
            onClick={async () => {
              try {
                await invoke('start_sidecar');
              } catch (error) {
                console.error('Failed to start sidecar:', error);
              }
            }}
          >
            启动后端
          </button>
        </div>
      </div>
    );
  }

  return (
    <ChatWindow
      agentId="default"
      sidecarStatus={sidecarStatus}
    />
  );
}

export default function App() {
  const [sidecarStatus, setSidecarStatus] = useState<SidecarStatus>({
    status: 'Stopped',
    port: 62601,
    pid: null,
    uptime_seconds: 0,
    message: '',
  });

  // 监听 sidecar 状态变化
  useEffect(() => {
    let unlisten: (() => void) | null = null;

    const setupListener = async () => {
      try {
        unlisten = await listen<SidecarStatus>('sidecar-status', (event) => {
          setSidecarStatus(event.payload);
        });
      } catch (error) {
        console.error('Failed to setup sidecar listener:', error);
      }
    };

    setupListener();

    return () => {
      if (unlisten) {
        unlisten();
      }
    };
  }, []);

  const handleOpenSettings = (tab?: string) => {
    // 未来可以通过 navigate 实现设置对话框
    console.log('Open settings:', tab);
  };

  return (
    <BrowserRouter>
      <Shell onOpenSettings={handleOpenSettings}>
        <Routes>
          <Route path="/" element={<ChatPage sidecarStatus={sidecarStatus} />} />
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/tasks" element={<TasksPage port={sidecarStatus.port} />} />
          <Route path="/memory" element={<MemoryPage />} />
          <Route path="/logs" element={<LogsPage />} />
        </Routes>
      </Shell>
    </BrowserRouter>
  );
}
