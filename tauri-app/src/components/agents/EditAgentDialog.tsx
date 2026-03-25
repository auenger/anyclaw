/**
 * EditAgentDialog Component
 *
 * 编辑 Agent 的对话框表单
 */

import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { useI18n } from '@/i18n';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type { UpdateAgentRequest, Agent } from '@/types';

// 常用 emoji 列表
const EMOJI_OPTIONS = [
  '🤖', '🧠', '🔬', '📝', '🎨', '🚀', '⚡', '🛡️', '🔮', '🎯',
  '💡', '🌟', '🎭', '📱', '🔧', '📊', '🎮', '🌈', '🦾', '🧪',
];

interface EditAgentDialogProps {
  isOpen: boolean;
  agent: Agent | null;
  onClose: () => void;
  onUpdate: (id: string, data: UpdateAgentRequest) => Promise<Agent | null>;
}

export function EditAgentDialog({ isOpen, agent, onClose, onUpdate }: EditAgentDialogProps) {
  const { t } = useI18n();
  const [name, setName] = useState('');
  const [emoji, setEmoji] = useState('🤖');
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 当 agent 变化时更新表单
  useEffect(() => {
    if (agent) {
      setName(agent.name);
      setEmoji(agent.emoji || '🤖');
    }
  }, [agent]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!agent) return;

    if (!name.trim()) {
      setError('Name is required');
      return;
    }

    setIsSaving(true);
    setError(null);

    const result = await onUpdate(agent.id, {
      name: name.trim(),
      emoji,
    });

    setIsSaving(false);

    if (result) {
      onClose();
    }
  };

  const handleClose = () => {
    if (!isSaving) {
      setError(null);
      onClose();
    }
  };

  if (!isOpen || !agent) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={handleClose}
      />

      {/* Dialog */}
      <div className="relative bg-background border border-[var(--subtle-border)] rounded-lg shadow-lg w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[var(--subtle-border)]">
          <h2 className="text-lg font-semibold">{t.agents.editAgent || 'Edit Agent'}</h2>
          <button
            onClick={handleClose}
            className="p-1 rounded hover:bg-accent"
            disabled={isSaving}
          >
            <X size={18} />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium mb-1">
              {t.agents.agentName} *
            </label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t.agents.agentNamePlaceholder}
              disabled={isSaving}
              autoFocus
            />
          </div>

          {/* Emoji */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Emoji
            </label>
            <div className="flex flex-wrap gap-1">
              {EMOJI_OPTIONS.map((e) => (
                <button
                  key={e}
                  type="button"
                  onClick={() => setEmoji(e)}
                  className={`w-8 h-8 text-lg rounded border transition-colors ${
                    emoji === e
                      ? 'border-primary bg-primary/10'
                      : 'border-[var(--subtle-border)] hover:bg-accent'
                  }`}
                  disabled={isSaving}
                >
                  {e}
                </button>
              ))}
            </div>
          </div>

          {/* Error */}
          {error && (
            <p className="text-sm text-red-500">{error}</p>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isSaving}
            >
              {t.common.cancel}
            </Button>
            <Button type="submit" disabled={isSaving}>
              {isSaving ? t.agents.saving : t.common.save}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
