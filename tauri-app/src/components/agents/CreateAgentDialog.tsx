/**
 * CreateAgentDialog Component
 *
 * 创建 Agent 的对话框表单
 */

import { useState } from 'react';
import { X } from 'lucide-react';
import { useI18n } from '@/i18n';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type { CreateAgentRequest, Agent } from '@/types';

// 常用 emoji 列表
const EMOJI_OPTIONS = [
  '🤖', '🧠', '🔬', '📝', '🎨', '🚀', '⚡', '🛡️', '🔮', '🎯',
  '💡', '🌟', '🎭', '📱', '🔧', '📊', '🎮', '🌈', '🦾', '🧪',
];

// Creature 选项
const CREATURE_OPTIONS = [
  { value: 'AI', label: 'AI' },
  { value: 'robot', label: 'Robot' },
  { value: 'ghost', label: 'Ghost' },
  { value: 'cat', label: 'Cat' },
  { value: 'dog', label: 'Dog' },
  { value: 'alien', label: 'Alien' },
];

// Vibe 选项
const VIBE_OPTIONS = [
  { value: 'helpful', label: 'Helpful' },
  { value: 'sharp', label: 'Sharp' },
  { value: 'warm', label: 'Warm' },
  { value: 'chaotic', label: 'Chaotic' },
  { value: 'calm', label: 'Calm' },
  { value: 'playful', label: 'Playful' },
];

interface CreateAgentDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (data: CreateAgentRequest) => Promise<Agent | null>;
}

export function CreateAgentDialog({ isOpen, onClose, onCreate }: CreateAgentDialogProps) {
  const { t } = useI18n();
  const [name, setName] = useState('');
  const [emoji, setEmoji] = useState('🤖');
  const [creature, setCreature] = useState('AI');
  const [vibe, setVibe] = useState('helpful');
  const [workspace, setWorkspace] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Name is required');
      return;
    }

    setIsCreating(true);
    setError(null);

    const result = await onCreate({
      name: name.trim(),
      emoji,
      creature,
      vibe,
      workspace: workspace.trim() || undefined,
    });

    setIsCreating(false);

    if (result) {
      // 重置表单
      setName('');
      setEmoji('🤖');
      setCreature('AI');
      setVibe('helpful');
      setWorkspace('');
      onClose();
    }
  };

  const handleClose = () => {
    if (!isCreating) {
      setError(null);
      onClose();
    }
  };

  if (!isOpen) return null;

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
          <h2 className="text-lg font-semibold">{t.agents.createTitle}</h2>
          <button
            onClick={handleClose}
            className="p-1 rounded hover:bg-accent"
            disabled={isCreating}
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
              disabled={isCreating}
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
                  disabled={isCreating}
                >
                  {e}
                </button>
              ))}
            </div>
          </div>

          {/* Creature */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Creature
            </label>
            <select
              value={creature}
              onChange={(e) => setCreature(e.target.value)}
              className="w-full h-9 px-3 rounded-md border border-input bg-background text-sm"
              disabled={isCreating}
            >
              {CREATURE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Vibe */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Vibe
            </label>
            <select
              value={vibe}
              onChange={(e) => setVibe(e.target.value)}
              className="w-full h-9 px-3 rounded-md border border-input bg-background text-sm"
              disabled={isCreating}
            >
              {VIBE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Workspace (optional) */}
          <div>
            <label className="block text-sm font-medium mb-1">
              {t.agents.workspace}
            </label>
            <Input
              value={workspace}
              onChange={(e) => setWorkspace(e.target.value)}
              placeholder={t.agents.workspacePlaceholder || "留空使用默认路径"}
              disabled={isCreating}
            />
            <p className="text-xs text-muted-foreground mt-1">
              {t.agents.workspaceDesc || "指定 Agent 的工作目录，留空则在默认位置创建"}
            </p>
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
              disabled={isCreating}
            >
              {t.common.cancel}
            </Button>
            <Button type="submit" disabled={isCreating}>
              {isCreating ? t.agents.creating : t.common.create}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
