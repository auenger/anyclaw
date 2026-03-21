import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { Shell } from './components/layout';
import { ChatWindow } from './components/chat';
import { TasksPage } from './components/tasks';
import { SettingsDialog } from './components/settings';
import { Agents } from './pages/Agents';
import { Memory } from './pages/Memory';
import { Logs } from './pages/Logs';
import { useI18n } from './i18n';
import type { SidecarStatus } from './types';

// 聊天页面包装器
function ChatPage({ sidecarStatus }: { sidecarStatus: SidecarStatus }) {
  const { t } = useI18n();

  if (sidecarStatus.status !== 'Running') {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-lg text-muted-foreground">{t.common.backendNotRunning}</p>
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
            {t.common.startBackend}
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
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [settingsTab, setSettingsTab] = useState<string | undefined>(undefined);

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
    setSettingsTab(tab);
    setSettingsOpen(true);
  };

  return (
    <BrowserRouter>
      <Shell onOpenSettings={handleOpenSettings}>
        <Routes>
          <Route path="/" element={<ChatPage sidecarStatus={sidecarStatus} />} />
          <Route path="/agents" element={<Agents />} />
          <Route path="/tasks" element={<TasksPage port={sidecarStatus.port} />} />
          <Route path="/memory" element={<Memory />} />
          <Route path="/logs" element={<Logs />} />
        </Routes>
      </Shell>
      <SettingsDialog
        open={settingsOpen}
        onOpenChange={setSettingsOpen}
        initialTab={settingsTab as 'general' | 'models' | 'about' | undefined}
      />
    </BrowserRouter>
  );
}
