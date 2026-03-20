/**
 * SubAgentList Component
 *
 * SubAgent 任务列表组件
 */

import { Clock, CheckCircle, XCircle, Loader2, X, AlertCircle } from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Card, CardContent } from '../ui/card';
import { cn } from '../../lib/utils';
import type { SubAgent, TaskStatus } from '../../types';

export interface SubAgentListProps {
  subAgents: SubAgent[];
  onCancel?: (id: string) => void;
  className?: string;
}

const statusConfig: Record<TaskStatus, { icon: typeof Clock; color: string; label: string }> = {
  pending: { icon: Clock, color: 'text-yellow-500', label: '等待中' },
  running: { icon: Loader2, color: 'text-blue-500', label: '运行中' },
  completed: { icon: CheckCircle, color: 'text-green-500', label: '已完成' },
  failed: { icon: XCircle, color: 'text-red-500', label: '失败' },
  cancelled: { icon: AlertCircle, color: 'text-gray-500', label: '已取消' },
};

export function SubAgentList({ subAgents, onCancel, className }: SubAgentListProps) {
  if (subAgents.length === 0) {
    return (
      <div className={cn('text-center py-12', className)}>
        <Clock className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
        <p className="text-lg font-medium">没有运行中的任务</p>
        <p className="text-muted-foreground">SubAgent 任务将显示在这里</p>
      </div>
    );
  }

  return (
    <div className={cn('space-y-3', className)}>
      {subAgents.map((agent) => (
        <SubAgentItem
          key={agent.id}
          subAgent={agent}
          onCancel={onCancel}
        />
      ))}
    </div>
  );
}

interface SubAgentItemProps {
  subAgent: SubAgent;
  onCancel?: (id: string) => void;
}

function SubAgentItem({ subAgent, onCancel }: SubAgentItemProps) {
  const config = statusConfig[subAgent.status];
  const StatusIcon = config.icon;
  const isRunning = subAgent.status === 'running';

  const formatTime = (time: string) => {
    return new Date(time).toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <StatusIcon
                className={cn(
                  'h-4 w-4',
                  config.color,
                  isRunning && 'animate-spin'
                )}
              />
              <span className="font-medium truncate">{subAgent.name}</span>
              <Badge variant="outline" className="text-xs">
                {config.label}
              </Badge>
            </div>

            <div className="text-sm text-muted-foreground space-y-1">
              <p className="font-mono text-xs">ID: {subAgent.id}</p>

              {subAgent.started_at && (
                <p>开始时间: {formatTime(subAgent.started_at)}</p>
              )}

              {subAgent.completed_at && (
                <p>完成时间: {formatTime(subAgent.completed_at)}</p>
              )}

              {subAgent.progress !== undefined && (
                <div className="flex items-center gap-2">
                  <span>进度:</span>
                  <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary transition-all"
                      style={{ width: `${subAgent.progress}%` }}
                    />
                  </div>
                  <span className="text-xs">{subAgent.progress}%</span>
                </div>
              )}

              {subAgent.output && (
                <p className="truncate" title={subAgent.output}>
                  输出: {subAgent.output}
                </p>
              )}

              {subAgent.error && (
                <p className="text-destructive truncate" title={subAgent.error}>
                  错误: {subAgent.error}
                </p>
              )}
            </div>
          </div>

          {isRunning && onCancel && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => onCancel(subAgent.id)}
              title="取消任务"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default SubAgentList;
