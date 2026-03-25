/**
 * AgentList Component
 *
 * 显示 Agent 列表，支持选中高亮
 */

import { cn } from '@/lib/utils';
import type { Agent } from '@/types';

interface AgentListProps {
  agents: Agent[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function AgentList({ agents, selectedId, onSelect }: AgentListProps) {
  return (
    <div className="flex-1 overflow-y-auto p-2">
      {agents.length === 0 ? (
        <div className="text-center text-muted-foreground text-sm py-8">
          No agents found
        </div>
      ) : (
        agents.map((agent) => (
          <button
            key={agent.id}
            onClick={() => onSelect(agent.id)}
            className={cn(
              'w-full text-left p-3 rounded-lg mb-1 transition-colors',
              selectedId === agent.id
                ? 'bg-accent text-foreground'
                : 'hover:bg-accent/50 text-muted-foreground',
              !agent.enabled && 'opacity-50'
            )}
          >
            <div className="flex items-center gap-2">
              <span className="text-lg">{agent.emoji || '🤖'}</span>
              <span className="font-medium truncate">{agent.name}</span>
              {!agent.enabled && (
                <span className="text-xs bg-muted px-1.5 py-0.5 rounded">
                  Disabled
                </span>
              )}
            </div>
            {agent.workspace && (
              <p className="text-xs text-muted-foreground mt-1 truncate">
                {agent.workspace}
              </p>
            )}
          </button>
        ))
      )}
    </div>
  );
}
