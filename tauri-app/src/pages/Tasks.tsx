/**
 * Tasks Page
 *
 * 定时任务管理页面，使用与 Agents 页面类似的左右分栏布局
 */

import { useState, useEffect } from 'react';
import { Plus, AlertCircle, Clock, Search } from 'lucide-react';
import { SidePanel } from '@/components/layout/SidePanel';
import { useCronJobs, useAgents } from '@/hooks';
import { useI18n } from '@/i18n';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import type { CronJob, CreateJobRequest, UpdateJobRequest, RunLog } from '@/types';

// ============ StatusBadge 组件 ============
function StatusBadge({ enabled }: { enabled: boolean }) {
  const { t } = useI18n();
  return (
    <Badge variant={enabled ? 'success' : 'secondary'} className="text-xs">
      {enabled ? t.tasks.statusActive : t.tasks.statusPaused}
    </Badge>
  );
}

// ============ ScheduleDisplay 组件 ============
function ScheduleDisplay({ schedule }: { schedule: CronJob['schedule'] }) {
  const { t } = useI18n();

  const formatSchedule = () => {
    if (schedule.type === 'every' && schedule.valueMs) {
      const minutes = Math.round(schedule.valueMs / 60000);
      return `${t.tasks.interval}: ${minutes} ${t.tasks.intervalMinutes}`;
    }
    if (schedule.type === 'cron' && schedule.expr) {
      return `${t.tasks.cron}: ${schedule.expr}`;
    }
    if (schedule.type === 'at' && schedule.atMs) {
      return `${t.tasks.once}: ${new Date(schedule.atMs).toLocaleString()}`;
    }
    return '-';
  };

  return (
    <span className="text-xs text-muted-foreground font-mono">
      {formatSchedule()}
    </span>
  );
}

// ============ TaskItem 组件 ============
interface TaskItemProps {
  job: CronJob;
  isSelected: boolean;
  onClick: () => void;
}

function TaskItem({ job, isSelected, onClick }: TaskItemProps) {
  const { t } = useI18n();

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full p-3 text-left border-b border-[var(--subtle-border)] transition-colors',
        'hover:bg-accent/50',
        isSelected && 'bg-accent'
      )}
    >
      <div className="flex items-center gap-2 mb-1">
        <Clock className="h-4 w-4 text-muted-foreground" />
        <span className="font-medium truncate flex-1">
          {job.name || t.tasks.noName}
        </span>
        <StatusBadge enabled={job.enabled} />
      </div>
      <ScheduleDisplay schedule={job.schedule} />
    </button>
  );
}

// ============ TaskList 组件 ============
interface TaskListProps {
  jobs: CronJob[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  isLoading: boolean;
}

function TaskList({ jobs, selectedId, onSelect, isLoading }: TaskListProps) {
  const { t } = useI18n();
  const [searchQuery, setSearchQuery] = useState('');

  const filteredJobs = jobs.filter((job) =>
    job.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    job.prompt.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-muted-foreground">{t.common.loading}</div>
      </div>
    );
  }

  return (
    <>
      {/* 搜索框 */}
      <div className="p-2 border-b border-[var(--subtle-border)]">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder={t.tasks.search}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 h-8"
          />
        </div>
      </div>

      {/* 任务列表 */}
      <ScrollArea className="flex-1">
        {filteredJobs.length === 0 ? (
          <div className="p-4 text-center text-muted-foreground">
            <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>{searchQuery ? t.common.noData : t.tasks.noTasks}</p>
            {!searchQuery && (
              <p className="text-xs mt-1">{t.tasks.noTasksHint}</p>
            )}
          </div>
        ) : (
          filteredJobs.map((job) => (
            <TaskItem
              key={job.id}
              job={job}
              isSelected={job.id === selectedId}
              onClick={() => onSelect(job.id)}
            />
          ))
        )}
      </ScrollArea>
    </>
  );
}

// ============ RunLogItem 组件 ============
function RunLogItem({ log }: { log: RunLog }) {
  const formatTime = (ms: number) => {
    return new Date(ms).toLocaleString();
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  return (
    <div className="p-2 border-b border-[var(--subtle-border)] text-sm">
      <div className="flex items-center gap-2">
        <Badge variant={log.status === 'success' ? 'success' : 'destructive'} className="text-xs">
          {log.status === 'success' ? 'OK' : 'ERR'}
        </Badge>
        <span className="text-xs text-muted-foreground">
          {formatTime(log.runAtMs)}
        </span>
        <span className="text-xs text-muted-foreground ml-auto">
          {formatDuration(log.durationMs)}
        </span>
      </div>
      {log.error && (
        <p className="mt-1 text-xs text-destructive truncate">{log.error}</p>
      )}
    </div>
  );
}

// ============ TaskDetail 组件 ============
interface TaskDetailProps {
  job: CronJob | null;
  isLoading: boolean;
  onEdit: () => void;
  onClone: () => void;
  onDelete: () => void;
  onToggle: (enabled: boolean) => void;
  onRun: () => void;
  logs: RunLog[];
  isLoadingLogs: boolean;
}

function TaskDetail({
  job,
  isLoading,
  onEdit,
  onClone,
  onDelete,
  onToggle,
  onRun,
  logs,
  isLoadingLogs,
}: TaskDetailProps) {
  const { t } = useI18n();

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-muted-foreground">{t.common.loading}</div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center text-muted-foreground">
          <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>{t.tasks.selectTask}</p>
        </div>
      </div>
    );
  }

  const formatTime = (ms: number | null | undefined) => {
    if (!ms) return '-';
    return new Date(ms).toLocaleString();
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* 头部 */}
      <div className="p-4 border-b border-[var(--subtle-border)]">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold">{job.name || t.tasks.noName}</h2>
          <StatusBadge enabled={job.enabled} />
        </div>
        {job.description && (
          <p className="text-sm text-muted-foreground">{job.description}</p>
        )}
      </div>

      {/* 操作按钮 */}
      <div className="p-4 border-b border-[var(--subtle-border)] flex flex-wrap gap-2">
        <Button size="sm" variant="outline" onClick={onEdit}>
          {t.common.edit}
        </Button>
        <Button size="sm" variant="outline" onClick={onClone}>
          {t.tasks.clone}
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => onToggle(!job.enabled)}
        >
          {job.enabled ? t.tasks.pause : t.tasks.resume}
        </Button>
        <Button size="sm" variant="outline" onClick={onRun}>
          {t.tasks.runNow}
        </Button>
        <Button size="sm" variant="destructive" onClick={onDelete}>
          {t.common.delete}
        </Button>
      </div>

      {/* 详情内容 */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {/* 基本信息 */}
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-muted-foreground">
              {t.tasks.taskId}
            </h3>
            <p className="font-mono text-xs">{job.id}</p>
          </div>

          <div className="space-y-2">
            <h3 className="text-sm font-medium text-muted-foreground">
              {t.tasks.schedule}
            </h3>
            <ScheduleDisplay schedule={job.schedule} />
          </div>

          {job.state.nextRunAtMs && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-muted-foreground">
                {t.tasks.nextRun}
              </h3>
              <p className="text-sm">{formatTime(job.state.nextRunAtMs)}</p>
            </div>
          )}

          {job.state.lastRunAtMs && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-muted-foreground">
                {t.tasks.lastRun}
              </h3>
              <p className="text-sm">{formatTime(job.state.lastRunAtMs)}</p>
            </div>
          )}

          <div className="space-y-2">
            <h3 className="text-sm font-medium text-muted-foreground">
              {t.tasks.created}
            </h3>
            <p className="text-sm">{formatTime(job.createdAtMs)}</p>
          </div>

          {/* Prompt */}
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-muted-foreground">
              {t.tasks.prompt}
            </h3>
            <pre className="p-3 bg-muted rounded-md text-xs overflow-x-auto whitespace-pre-wrap">
              {job.prompt}
            </pre>
          </div>

          {/* 执行历史 */}
          <div className="space-y-2">
            <h3 className="text-sm font-medium text-muted-foreground">
              {t.tasks.recentRuns}
            </h3>
            {isLoadingLogs ? (
              <p className="text-sm text-muted-foreground">{t.common.loading}</p>
            ) : logs.length === 0 ? (
              <p className="text-sm text-muted-foreground">{t.tasks.noRuns}</p>
            ) : (
              <div className="border border-[var(--subtle-border)] rounded-md">
                {logs.map((log) => (
                  <RunLogItem key={log.id} log={log} />
                ))}
              </div>
            )}
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}

// ============ TaskForm 组件 ============
interface TaskFormProps {
  job?: CronJob | null;
  agents: { id: string; name: string }[];
  onSubmit: (data: CreateJobRequest | UpdateJobRequest) => Promise<boolean>;
  onCancel: () => void;
  isCreating: boolean;
}

function TaskForm({ job, agents, onSubmit, onCancel, isCreating }: TaskFormProps) {
  const { t } = useI18n();
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 表单状态
  const [name, setName] = useState(job?.name || '');
  const [description, setDescription] = useState(job?.description || '');
  const [agentId, setAgentId] = useState(job?.agentId || agents[0]?.id || '');
  const [prompt, setPrompt] = useState(job?.prompt || '');
  const [scheduleType, setScheduleType] = useState<'interval' | 'cron' | 'once'>(
    job?.schedule.type === 'every' ? 'interval' :
    job?.schedule.type === 'cron' ? 'cron' :
    job?.schedule.type === 'at' ? 'once' : 'interval'
  );
  const [intervalMinutes, setIntervalMinutes] = useState(
    job?.schedule.valueMs ? Math.round(job.schedule.valueMs / 60000) : 30
  );
  const [cronExpr, setCronExpr] = useState(job?.schedule.expr || '0 9 * * *');
  const [cronTz, setCronTz] = useState(job?.schedule.tz || 'Asia/Shanghai');
  const [onceDatetime, setOnceDatetime] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // 验证
    if (!prompt.trim()) {
      return;
    }

    if (scheduleType === 'interval' && intervalMinutes < 1) {
      return;
    }

    setIsSubmitting(true);

    try {
      // 构建调度配置
      let schedule: CreateJobRequest['schedule'];
      if (scheduleType === 'interval') {
        schedule = {
          type: 'interval',
          value_ms: intervalMinutes * 60000,
        };
      } else if (scheduleType === 'cron') {
        schedule = {
          type: 'cron',
          expr: cronExpr,
          tz: cronTz,
        };
      } else {
        const atMs = new Date(onceDatetime).getTime();
        schedule = {
          type: 'once',
          at_ms: atMs,
        };
      }

      if (isCreating) {
        await onSubmit({
          name: name || 'Untitled Task',
          description,
          agent_id: agentId,
          chat_id: `chat-${Date.now()}`, // 临时 chat_id
          prompt,
          schedule,
        } as CreateJobRequest);
      } else {
        await onSubmit({
          name: name || 'Untitled Task',
          description,
          prompt,
          schedule,
        } as UpdateJobRequest);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="p-4 border-b border-[var(--subtle-border)]">
        <h2 className="text-lg font-semibold">
          {isCreating ? t.tasks.createTitle : t.tasks.editTitle}
        </h2>
      </div>

      <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* 名称 */}
        <div className="space-y-2">
          <label className="text-sm font-medium">{t.tasks.name}</label>
          <Input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder={t.tasks.namePlaceholder}
          />
        </div>

        {/* 描述 */}
        <div className="space-y-2">
          <label className="text-sm font-medium">{t.tasks.description}</label>
          <Input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder={t.tasks.descriptionPlaceholder}
          />
        </div>

        {/* Agent 选择 (创建时可选，编辑时禁用) */}
        {isCreating && (
          <div className="space-y-2">
            <label className="text-sm font-medium">{t.tasks.agent}</label>
            <select
              value={agentId}
              onChange={(e) => setAgentId(e.target.value)}
              className="w-full px-3 py-2 border rounded-md bg-background"
            >
              {agents.map((agent) => (
                <option key={agent.id} value={agent.id}>
                  {agent.name}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Prompt */}
        <div className="space-y-2">
          <label className="text-sm font-medium">{t.tasks.prompt} *</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={t.tasks.promptPlaceholder}
            className="w-full min-h-[120px] px-3 py-2 border rounded-md bg-background resize-y"
            required
          />
        </div>

        {/* 调度类型 */}
        <div className="space-y-2">
          <label className="text-sm font-medium">{t.tasks.scheduleType}</label>
          <div className="flex gap-2">
            <Button
              type="button"
              size="sm"
              variant={scheduleType === 'interval' ? 'default' : 'outline'}
              onClick={() => setScheduleType('interval')}
            >
              {t.tasks.interval}
            </Button>
            <Button
              type="button"
              size="sm"
              variant={scheduleType === 'cron' ? 'default' : 'outline'}
              onClick={() => setScheduleType('cron')}
            >
              {t.tasks.cron}
            </Button>
            <Button
              type="button"
              size="sm"
              variant={scheduleType === 'once' ? 'default' : 'outline'}
              onClick={() => setScheduleType('once')}
            >
              {t.tasks.once}
            </Button>
          </div>
        </div>

        {/* 调度配置 */}
        {scheduleType === 'interval' && (
          <div className="space-y-2">
            <label className="text-sm font-medium">{t.tasks.intervalMinutes} *</label>
            <Input
              type="number"
              min={1}
              value={intervalMinutes}
              onChange={(e) => setIntervalMinutes(parseInt(e.target.value) || 1)}
              placeholder={t.tasks.intervalPlaceholder}
            />
          </div>
        )}

        {scheduleType === 'cron' && (
          <>
            <div className="space-y-2">
              <label className="text-sm font-medium">{t.tasks.cronExpression} *</label>
              <Input
                value={cronExpr}
                onChange={(e) => setCronExpr(e.target.value)}
                placeholder={t.tasks.cronPlaceholder}
              />
              <p className="text-xs text-muted-foreground">{t.tasks.cronHelp}</p>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Timezone</label>
              <Input
                value={cronTz}
                onChange={(e) => setCronTz(e.target.value)}
                placeholder="Asia/Shanghai"
              />
            </div>
          </>
        )}

        {scheduleType === 'once' && (
          <div className="space-y-2">
            <label className="text-sm font-medium">{t.tasks.runAt} *</label>
            <Input
              type="datetime-local"
              value={onceDatetime}
              onChange={(e) => setOnceDatetime(e.target.value)}
            />
          </div>
        )}

        {/* 提交按钮 */}
        <div className="flex justify-end gap-2 pt-4">
          <Button type="button" variant="outline" onClick={onCancel}>
            {t.common.cancel}
          </Button>
          <Button type="submit" disabled={isSubmitting || !prompt.trim()}>
            {isSubmitting ? t.common.saving : t.common.save}
          </Button>
        </div>
      </form>
    </div>
  );
}

// ============ Tasks 主组件 ============
export function Tasks() {
  const { t } = useI18n();
  const {
    jobs,
    isLoading,
    error,
    createJob,
    updateJob,
    deleteJob,
    cloneJob,
    runJob,
    getJobLogs,
    toggleJob,
  } = useCronJobs();

  const { agents } = useAgents();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [panelMode, setPanelMode] = useState<'detail' | 'create' | 'edit'>('detail');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [logs, setLogs] = useState<RunLog[]>([]);
  const [isLoadingLogs, setIsLoadingLogs] = useState(false);

  const selectedJob = jobs.find((j) => j.id === selectedId) || null;

  // 加载选中任务的日志
  useEffect(() => {
    if (selectedId && panelMode === 'detail') {
      setIsLoadingLogs(true);
      getJobLogs(selectedId, 20)
        .then(setLogs)
        .finally(() => setIsLoadingLogs(false));
    }
  }, [selectedId, panelMode, getJobLogs]);

  // 创建任务
  const handleCreate = async (data: CreateJobRequest | UpdateJobRequest): Promise<boolean> => {
    const job = await createJob(data as CreateJobRequest);
    if (job) {
      setSelectedId(job.id);
      setPanelMode('detail');
      return true;
    }
    return false;
  };

  // 更新任务
  const handleUpdate = async (data: CreateJobRequest | UpdateJobRequest): Promise<boolean> => {
    if (!selectedId) return false;
    const job = await updateJob(selectedId, data as UpdateJobRequest);
    if (job) {
      setPanelMode('detail');
      return true;
    }
    return false;
  };

  // 克隆任务
  const handleClone = async () => {
    if (!selectedId) return;
    const job = await cloneJob(selectedId);
    if (job) {
      setSelectedId(job.id);
    }
  };

  // 删除任务
  const handleDelete = async () => {
    if (!selectedId) return;
    const success = await deleteJob(selectedId);
    if (success) {
      setSelectedId(null);
      setShowDeleteConfirm(false);
    }
  };

  // 切换启用状态
  const handleToggle = async (enabled: boolean) => {
    if (!selectedId) return;
    await toggleJob(selectedId, enabled);
  };

  // 手动运行
  const handleRun = async () => {
    if (!selectedId) return;
    await runJob(selectedId);
    // 刷新日志
    setIsLoadingLogs(true);
    getJobLogs(selectedId, 20)
      .then(setLogs)
      .finally(() => setIsLoadingLogs(false));
  };

  // 新建按钮点击
  const handleNewClick = () => {
    setSelectedId(null);
    setPanelMode('create');
  };

  // 取消表单
  const handleCancelForm = () => {
    setPanelMode('detail');
  };

  return (
    <div className="h-full flex">
      {/* 左侧面板：任务列表 */}
      <SidePanel>
        <div className="p-4 border-b border-[var(--subtle-border)]">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium">{t.tasks.title}</h2>
            <button
              onClick={handleNewClick}
              className="p-1.5 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground"
              title={t.tasks.createTask}
            >
              <Plus size={16} />
            </button>
          </div>
        </div>

        <TaskList
          jobs={jobs}
          selectedId={selectedId}
          onSelect={(id) => {
            setSelectedId(id);
            setPanelMode('detail');
          }}
          isLoading={isLoading}
        />

        {/* 错误显示 */}
        {error && (
          <div className="p-2 border-t border-[var(--subtle-border)]">
            <div className="flex items-center gap-2 text-sm text-red-500">
              <AlertCircle size={14} />
              <span className="truncate">{error}</span>
            </div>
          </div>
        )}
      </SidePanel>

      {/* 右侧面板：详情或表单 */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {panelMode === 'create' ? (
          <TaskForm
            agents={agents}
            onSubmit={handleCreate}
            onCancel={handleCancelForm}
            isCreating={true}
          />
        ) : panelMode === 'edit' ? (
          <TaskForm
            job={selectedJob}
            agents={agents}
            onSubmit={handleUpdate}
            onCancel={handleCancelForm}
            isCreating={false}
          />
        ) : (
          <TaskDetail
            job={selectedJob}
            isLoading={isLoading}
            onEdit={() => setPanelMode('edit')}
            onClone={handleClone}
            onDelete={() => setShowDeleteConfirm(true)}
            onToggle={handleToggle}
            onRun={handleRun}
            logs={logs}
            isLoadingLogs={isLoadingLogs}
          />
        )}
      </div>

      {/* 删除确认对话框 */}
      <AlertDialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t.common.delete}</AlertDialogTitle>
            <AlertDialogDescription>
              {t.tasks.confirmDelete}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t.common.cancel}</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-red-500 hover:bg-red-600"
            >
              {t.common.delete}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

export default Tasks;
