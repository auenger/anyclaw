/**
 * TasksPage Component
 *
 * 任务管理页面：Tab 切换 (SubAgent / Cron)
 */

import { useState, useEffect } from 'react';
import { RefreshCw, Loader2, Bot, Clock } from 'lucide-react';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { SubAgentList } from './SubAgentList';
import { CronList } from './CronList';
import { useTasks } from '../../hooks/useTasks';
import { cn } from '../../lib/utils';

export interface TasksPageProps {
  port?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
  className?: string;
}

export function TasksPage({
  port,
  autoRefresh = true,
  refreshInterval = 5000,
  className,
}: TasksPageProps) {
  const [activeTab, setActiveTab] = useState('subagents');

  const {
    subAgents,
    crons,
    isLoading,
    error,
    loadTasks,
    cancelSubAgent,
    toggleCron,
    startPolling,
    stopPolling,
  } = useTasks(port);

  // 自动刷新
  useEffect(() => {
    if (autoRefresh) {
      startPolling(refreshInterval);
    }

    return () => {
      stopPolling();
    };
  }, [autoRefresh, refreshInterval, startPolling, stopPolling]);

  const handleRefresh = () => {
    loadTasks();
  };

  const runningCount = subAgents.filter((s) => s.status === 'running').length;
  const enabledCronCount = crons.filter((c) => c.status === 'enabled').length;

  return (
    <div className={cn('flex flex-col h-full', className)}>
      {/* 工具栏 */}
      <div className="p-4 border-b flex items-center justify-between">
        <h2 className="text-lg font-semibold">任务管理</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={isLoading}
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4 mr-2" />
          )}
          刷新
        </Button>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="p-4 bg-destructive/10 text-destructive">
          {error}
        </div>
      )}

      {/* Tab 内容 */}
      <div className="flex-1 overflow-hidden">
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="h-full flex flex-col"
        >
          <div className="px-4 pt-2">
            <TabsList>
              <TabsTrigger value="subagents" className="flex items-center gap-2">
                <Bot className="h-4 w-4" />
                SubAgent
                {runningCount > 0 && (
                  <span className="ml-1 px-1.5 py-0.5 text-xs bg-primary text-primary-foreground rounded-full">
                    {runningCount}
                  </span>
                )}
              </TabsTrigger>
              <TabsTrigger value="crons" className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Cron
                {enabledCronCount > 0 && (
                  <span className="ml-1 px-1.5 py-0.5 text-xs bg-secondary text-secondary-foreground rounded-full">
                    {enabledCronCount}
                  </span>
                )}
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="subagents" className="flex-1 overflow-y-auto p-4">
            <SubAgentList
              subAgents={subAgents}
              onCancel={cancelSubAgent}
            />
          </TabsContent>

          <TabsContent value="crons" className="flex-1 overflow-y-auto p-4">
            <CronList
              crons={crons}
              onToggle={toggleCron}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default TasksPage;
