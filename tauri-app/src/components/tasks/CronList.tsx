/**
 * CronList Component
 *
 * Cron 定时任务列表组件
 */

import { Clock, Play, CheckCircle } from 'lucide-react';
import { Switch } from '../ui/switch';
import { Badge } from '../ui/badge';
import { Card, CardContent } from '../ui/card';
import { cn } from '../../lib/utils';
import type { CronTask } from '../../types';

export interface CronListProps {
  crons: CronTask[];
  onToggle?: (id: string, enabled: boolean) => void;
  className?: string;
}

export function CronList({ crons, onToggle, className }: CronListProps) {
  if (crons.length === 0) {
    return (
      <div className={cn('text-center py-12', className)}>
        <Clock className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
        <p className="text-lg font-medium">没有定时任务</p>
        <p className="text-muted-foreground">Cron 定时任务将显示在这里</p>
      </div>
    );
  }

  return (
    <div className={cn('space-y-3', className)}>
      {crons.map((cron) => (
        <CronItem
          key={cron.id}
          cron={cron}
          onToggle={onToggle}
        />
      ))}
    </div>
  );
}

interface CronItemProps {
  cron: CronTask;
  onToggle?: (id: string, enabled: boolean) => void;
}

function CronItem({ cron, onToggle }: CronItemProps) {
  const formatTime = (time?: string) => {
    if (!time) return '-';
    return new Date(time).toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatSchedule = (schedule: string) => {
    // 简单的 cron 表达式解析
    // 实际项目中可以使用更完善的库
    return schedule;
  };

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium truncate">{cron.name}</span>
              <Badge
                variant={cron.status === 'enabled' ? 'success' : 'secondary'}
                className="text-xs"
              >
                {cron.status === 'enabled' ? '已启用' : '已禁用'}
              </Badge>
            </div>

            <div className="text-sm text-muted-foreground space-y-1">
              <p className="font-mono text-xs">ID: {cron.id}</p>

              <div className="flex items-center gap-2">
                <span>调度:</span>
                <code className="px-2 py-0.5 bg-muted rounded text-xs">
                  {formatSchedule(cron.schedule)}
                </code>
              </div>

              {cron.next_run && (
                <div className="flex items-center gap-2">
                  <Play className="h-3 w-3" />
                  <span>下次执行: {formatTime(cron.next_run)}</span>
                </div>
              )}

              {cron.last_run && (
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-3 w-3" />
                  <span>上次执行: {formatTime(cron.last_run)}</span>
                </div>
              )}

              {cron.last_result && (
                <p className="truncate" title={cron.last_result}>
                  结果: {cron.last_result}
                </p>
              )}
            </div>
          </div>

          {onToggle && (
            <div className="flex items-center gap-2">
              <Switch
                checked={cron.status === 'enabled'}
                onCheckedChange={(checked) => onToggle(cron.id, checked)}
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default CronList;
