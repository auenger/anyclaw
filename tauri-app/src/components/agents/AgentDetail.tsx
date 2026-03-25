/**
 * AgentDetail Component
 *
 * 显示 Agent 详情，包含编辑/删除/激活/禁用按钮
 */

import { Bot, Edit, Trash2, Power, PowerOff } from 'lucide-react';
import { useI18n } from '@/i18n';
import type { Agent } from '@/types';

interface AgentDetailProps {
  agent: Agent | null;
  isLoading: boolean;
  onEdit: () => void;
  onDelete: () => void;
  onActivate: () => void;
  onDeactivate: () => void;
}

export function AgentDetail({
  agent,
  isLoading,
  onEdit,
  onDelete,
  onActivate,
  onDeactivate,
}: AgentDetailProps) {
  const { t } = useI18n();

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-muted-foreground">{t.common.loading}</div>
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center space-y-2">
          <Bot size={48} className="mx-auto text-muted-foreground/50" />
          <p className="text-muted-foreground">{t.agents.selectAgent}</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Header */}
      <div className="p-4 border-b border-[var(--subtle-border)]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{agent.emoji || '🤖'}</span>
            <h3 className="font-semibold">{agent.name}</h3>
            {!agent.enabled && (
              <span className="text-xs bg-muted px-2 py-0.5 rounded">
                {t.agents.status}: Disabled
              </span>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={onEdit}
              className="px-3 py-1.5 text-sm rounded-lg border border-[var(--subtle-border)] hover:bg-accent flex items-center gap-1"
            >
              <Edit size={14} />
              {t.common.edit}
            </button>
            <button
              onClick={onDelete}
              disabled={agent.id === 'default'}
              className="px-3 py-1.5 text-sm rounded-lg border border-[var(--subtle-border)] hover:bg-accent text-red-500 flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Trash2 size={14} />
              {t.common.delete}
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-4">
          <div>
            <label className="text-xs text-muted-foreground uppercase tracking-wide">
              {t.agents.id}
            </label>
            <p className="mt-1 font-mono text-sm">{agent.id}</p>
          </div>

          <div>
            <label className="text-xs text-muted-foreground uppercase tracking-wide">
              {t.agents.workspace}
            </label>
            <p className="mt-1 text-sm font-mono truncate" title={agent.workspace}>
              {agent.workspace || '-'}
            </p>
          </div>

          <div>
            <label className="text-xs text-muted-foreground uppercase tracking-wide">
              Sessions
            </label>
            <p className="mt-1 text-sm">{agent.sessionCount}</p>
          </div>

          <div>
            <label className="text-xs text-muted-foreground uppercase tracking-wide">
              {t.agents.skills}
            </label>
            <p className="mt-1 text-sm text-muted-foreground">
              {t.agents.skillsAll}
            </p>
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="p-4 border-t border-[var(--subtle-border)]">
        <div className="flex gap-2">
          {agent.enabled ? (
            <button
              onClick={onDeactivate}
              className="flex-1 px-3 py-2 text-sm rounded-lg border border-[var(--subtle-border)] hover:bg-accent flex items-center justify-center gap-2"
            >
              <PowerOff size={16} />
              Deactivate
            </button>
          ) : (
            <button
              onClick={onActivate}
              className="flex-1 px-3 py-2 text-sm rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 flex items-center justify-center gap-2"
            >
              <Power size={16} />
              Activate
            </button>
          )}
        </div>
      </div>
    </>
  );
}
