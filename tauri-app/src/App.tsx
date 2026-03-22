import { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { Shell } from './components/layout';
import { TasksPage } from './components/tasks';
import { SettingsDialog } from './components/settings';
import { Agents } from './pages/Agents';
import { Memory } from './pages/Memory';
import { Logs } from './pages/Logs';
import { Chat } from './pages/Chat';
import { useI18n } from './i18n';
import type { SidecarStatus } from './types';
import { AlertCircle, RefreshCw, Loader2 } from 'lucide-react';

// 聊天页面包装器
function ChatPage({
  sidecarStatus,
  onStartSidecar,
  isStarting,
  startError
}: {
  sidecarStatus: SidecarStatus;
  onStartSidecar: () => void;
  isStarting: boolean;
  startError: string | null;
}) {
  const { t } = useI18n();

  // 显示错误状态
  if (sidecarStatus.status === 'Error' || startError) {
    return (
      <div className="h-full flex items-center justify-center p-4">
        <div className="text-center space-y-4 max-w-md">
          <div className="mx-auto w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center">
            <AlertCircle className="h-6 w-6 text-destructive" />
          </div>
          <div className="space-y-2">
            <p className="text-lg font-medium text-foreground">后端启动失败</p>
            <p className="text-sm text-muted-foreground">
              {startError || sidecarStatus.message || '未知错误'}
            </p>
          </div>
          <button
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
            onClick={onStartSidecar}
            disabled={isStarting}
          >
            {isStarting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                重试中...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4" />
                重试启动
              </>
            )}
          </button>
        </div>
      </div>
    );
  }

  // 显示启动中状态
  if (sidecarStatus.status === 'Starting' || isStarting) {
    return (
      <div className="h-full flex items-center justify-center p-4">
        <div className="text-center space-y-4">
          <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
            <Loader2 className="h-6 w-6 text-primary animate-spin" />
          </div>
          <div className="space-y-1">
            <p className="text-lg font-medium text-foreground">正在启动后端...</p>
            <p className="text-sm text-muted-foreground">首次启动可能需要几秒钟</p>
          </div>
        </div>
      </div>
    );
  }

  // 显示未运行状态
  if (sidecarStatus.status !== 'Running') {
    return (
      <div className="h-full flex items-center justify-center p-4">
        <div className="text-center space-y-4">
          <p className="text-lg text-muted-foreground">{t.common.backendNotRunning}</p>
          <button
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
            onClick={onStartSidecar}
            disabled={isStarting}
          >
            {isStarting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                启动中...
              </>
            ) : (
              t.common.startBackend
            )}
          </button>
        </div>
      </div>
    );
  }

  return (
    <Chat sidecarStatus={sidecarStatus} />
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
  const [isStarting, setIsStarting] = useState(false);
  const [startError, setStartError] = useState<string | null>(null);
  const [hasAutoStarted, setHasAutoStarted] = useState(false);

  // 监听 sidecar 状态变化
  useEffect(() => {
    let unlisten: (() => void) | null = null;

    const setupListener = async () => {
      try {
        unlisten = await listen<SidecarStatus>('sidecar-status', (event) => {
          setSidecarStatus(event.payload);
          // 如果状态变为 Running 或 Error，清除启动中状态
          if (event.payload.status === 'Running') {
            setIsStarting(false);
            setStartError(null);
          } else if (event.payload.status === 'Error') {
            setIsStarting(false);
            setStartError(event.payload.message);
          }
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

  // 自动启动 sidecar
  useEffect(() => {
    const autoStart = async () => {
      if (hasAutoStarted) return;

      // 获取当前状态
      try {
        const status = await invoke<SidecarStatus>('get_sidecar_status');
        setSidecarStatus(status);

        // 如果后端未运行，自动启动
        if (status.status === 'Stopped') {
          setHasAutoStarted(true);
          setIsStarting(true);
          setStartError(null);
          await invoke('start_sidecar');
        }
      } catch (error) {
        console.error('Auto-start sidecar failed:', error);
        setStartError(String(error));
        setIsStarting(false);
      }
    };

    // 延迟一点启动，确保 Tauri 完全初始化
    const timer = setTimeout(autoStart, 500);
    return () => clearTimeout(timer);
  }, [hasAutoStarted]);

  // 手动启动 sidecar
  const handleStartSidecar = useCallback(async () => {
    setIsStarting(true);
    setStartError(null);
    try {
      await invoke('start_sidecar');
    } catch (error) {
      console.error('Failed to start sidecar:', error);
      setStartError(String(error));
      setIsStarting(false);
    }
  }, []);

  const handleOpenSettings = (tab?: string) => {
    setSettingsTab(tab);
    setSettingsOpen(true);
  };

  return (
    <BrowserRouter>
      <Shell onOpenSettings={handleOpenSettings}>
        <Routes>
          <Route path="/" element={
            <ChatPage
              sidecarStatus={sidecarStatus}
              onStartSidecar={handleStartSidecar}
              isStarting={isStarting}
              startError={startError}
            />
          } />
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
