import { useState, useEffect } from 'react';
import {
  Bot,
  Settings,
  Plus,
  Wrench,
  Clock,
  MessageSquare,
  Menu,
  X,
} from 'lucide-react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { Button } from './components/ui';
import { ScrollArea } from './components/ui';
import { cn } from './lib/utils';

// Page components
import { ChatWindow } from './components/chat';
import { SettingsPage } from './components/settings';
import { SkillsPage } from './components/skills';
import { TasksPage } from './components/tasks';

// Types
import type { SidecarStatus } from './types';

type Page = 'chat' | 'settings' | 'skills' | 'tasks';

interface NavItem {
  id: Page;
  label: string;
  icon: typeof MessageSquare;
}

const NAV_ITEMS: NavItem[] = [
  { id: 'chat', label: '聊天', icon: MessageSquare },
  { id: 'skills', label: '技能', icon: Wrench },
  { id: 'tasks', label: '任务', icon: Clock },
  { id: 'settings', label: '设置', icon: Settings },
];

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentPage, setCurrentPage] = useState<Page>('chat');
  const [selectedAgent, setSelectedAgent] = useState('default');

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

  const renderPage = () => {
    switch (currentPage) {
      case 'chat':
        return (
          <ChatWindow
            agentId={selectedAgent}
            sidecarStatus={sidecarStatus}
          />
        );
      case 'settings':
        return (
          <SettingsPage port={sidecarStatus.port} />
        );
      case 'skills':
        return (
          <SkillsPage port={sidecarStatus.port} />
        );
      case 'tasks':
        return (
          <TasksPage port={sidecarStatus.port} />
        );
      default:
        return null;
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
                onClick={() => {
                  setSelectedAgent('default');
                  setCurrentPage('chat');
                }}
                className={cn(
                  'w-full text-left px-3 py-2 rounded-lg hover:bg-accent transition-colors',
                  selectedAgent === 'default' && currentPage === 'chat' && 'bg-accent'
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

          {/* 导航菜单 */}
          <div className="p-2 border-t">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={cn(
                    'w-full text-left px-3 py-2 rounded-lg hover:bg-accent transition-colors flex items-center gap-2',
                    currentPage === item.id && 'bg-accent'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span className="text-sm">{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* 底部状态 */}
          <div className="p-4 border-t space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">后端状态</span>
              <span
                className={cn(
                  'text-sm px-2 py-0.5 rounded-full',
                  sidecarStatus.status === 'Running'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
                    : sidecarStatus.status === 'Error'
                    ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100'
                    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
                )}
              >
                {sidecarStatus.status}
              </span>
            </div>

            {sidecarStatus.status === 'Running' && (
              <div className="text-xs text-muted-foreground">
                PID: {sidecarStatus.pid} | Port: {sidecarStatus.port}
              </div>
            )}

            <div className="flex gap-2">
              {sidecarStatus.status !== 'Running' ? (
                <Button size="sm" className="flex-1" onClick={handleStart}>
                  启动
                </Button>
              ) : (
                <Button
                  size="sm"
                  variant="outline"
                  className="flex-1"
                  onClick={handleStop}
                >
                  停止
                </Button>
              )}
            </div>
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
              {sidebarOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </Button>
            <div>
              <h2 className="font-semibold">
                {NAV_ITEMS.find((item) => item.id === currentPage)?.label || 'AnyClaw'}
              </h2>
            </div>
          </div>

          {!sidebarOpen && (
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  'text-sm px-2 py-1 rounded-full',
                  sidecarStatus.status === 'Running'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
                    : sidecarStatus.status === 'Error'
                    ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100'
                    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
                )}
              >
                {sidecarStatus.status}
              </span>
            </div>
          )}
        </div>

        {/* 页面内容 */}
        <div className="flex-1 overflow-hidden">
          {sidecarStatus.status !== 'Running' && currentPage !== 'settings' ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center space-y-4">
                <div className="h-16 w-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white">
                  <Bot className="h-8 w-8" />
                </div>
                <p className="text-lg text-muted-foreground">后端服务未运行</p>
                <Button onClick={handleStart}>启动后端</Button>
              </div>
            </div>
          ) : (
            renderPage()
          )}
        </div>
      </main>
    </div>
  );
}
