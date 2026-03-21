import { useState } from 'react'
import { Plus, Bot } from 'lucide-react'
import { SidePanel } from '@/components/layout/SidePanel'
import { useI18n } from '@/i18n'
import { cn } from '@/lib/utils'

interface Agent {
  id: string
  name: string
  description?: string
  model?: string
}

// Mock data
const mockAgents: Agent[] = [
  { id: 'default', name: 'Default Agent', description: 'Default assistant agent', model: 'glm-4.7' },
  { id: 'researcher', name: 'Research Assistant', description: 'Helps with research tasks', model: 'glm-4.7' },
]

export function Agents() {
  const { t } = useI18n()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  // Future: Create agent form
  // const [showCreateForm, setShowCreateForm] = useState(false)

  const selectedAgent = mockAgents.find(a => a.id === selectedId)

  return (
    <div className="h-full flex">
      {/* Left Panel: Agent List */}
      <SidePanel>
        <div className="p-4 border-b border-[var(--subtle-border)]">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium">{t.agents.title}</h2>
            <button
              onClick={() => {/* TODO: Open create agent form */}}
              className="p-1.5 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground"
            >
              <Plus size={16} />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {mockAgents.map((agent) => (
            <button
              key={agent.id}
              onClick={() => setSelectedId(agent.id)}
              className={cn(
                "w-full text-left p-3 rounded-lg mb-1 transition-colors",
                selectedId === agent.id
                  ? "bg-accent text-foreground"
                  : "hover:bg-accent/50 text-muted-foreground"
              )}
            >
              <div className="flex items-center gap-2">
                <Bot size={16} />
                <span className="font-medium truncate">{agent.name}</span>
              </div>
              {agent.description && (
                <p className="text-xs text-muted-foreground mt-1 truncate">
                  {agent.description}
                </p>
              )}
            </button>
          ))}
        </div>
      </SidePanel>

      {/* Right Panel: Agent Details */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {selectedAgent ? (
          <>
            <div className="p-4 border-b border-[var(--subtle-border)]">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">{selectedAgent.name}</h3>
                <div className="flex gap-2">
                  <button className="px-3 py-1.5 text-sm rounded-lg border border-[var(--subtle-border)] hover:bg-accent">
                    {t.common.edit}
                  </button>
                  <button className="px-3 py-1.5 text-sm rounded-lg border border-[var(--subtle-border)] hover:bg-accent text-red-500">
                    {t.common.delete}
                  </button>
                </div>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              <div className="space-y-4">
                <div>
                  <label className="text-xs text-muted-foreground uppercase tracking-wide">
                    {t.agents.id}
                  </label>
                  <p className="mt-1 font-mono text-sm">{selectedAgent.id}</p>
                </div>

                <div>
                  <label className="text-xs text-muted-foreground uppercase tracking-wide">
                    {t.agents.model}
                  </label>
                  <p className="mt-1 text-sm">{selectedAgent.model || '-'}</p>
                </div>

                {selectedAgent.description && (
                  <div>
                    <label className="text-xs text-muted-foreground uppercase tracking-wide">
                      {t.tasks.description}
                    </label>
                    <p className="mt-1 text-sm">{selectedAgent.description}</p>
                  </div>
                )}

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
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-2">
              <Bot size={48} className="mx-auto text-muted-foreground/50" />
              <p className="text-muted-foreground">{t.agents.selectAgent}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
