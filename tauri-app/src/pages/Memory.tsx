import { useState } from 'react'
import { Globe, FileText, ChevronRight, PanelRightClose, PanelRightOpen } from 'lucide-react'
import { SidePanel } from '@/components/layout/SidePanel'
import { useI18n } from '@/i18n'
import { cn } from '@/lib/utils'

type PanelTab = 'logs' | 'archives' | 'search'

interface MemoryItem {
  id: string
  name: string
  isGlobal: boolean
}

const mockMemoryItems: MemoryItem[] = [
  { id: 'global', name: 'Global Memory', isGlobal: true },
  { id: 'agent-default', name: 'Default Agent', isGlobal: false },
]

interface DailyLog {
  date: string
  content: string
}

const mockDailyLogs: DailyLog[] = [
  { date: '2024-03-21', content: 'Worked on UI implementation...' },
  { date: '2024-03-20', content: 'Fixed API integration issues...' },
]

export function Memory() {
  const { t } = useI18n()
  const [selectedId, setSelectedId] = useState<string>('global')
  const [isEditing, setIsEditing] = useState(false)
  const [content, setContent] = useState('# Memory\n\nThis is the global memory content...')
  const [editedContent, setEditedContent] = useState(content)
  const [panelOpen, setPanelOpen] = useState(true)
  const [panelTab, setPanelTab] = useState<PanelTab>('logs')
  const [expandedLog, setExpandedLog] = useState<string | null>(null)

  const selectedItem = mockMemoryItems.find(m => m.id === selectedId)

  const handleSave = () => {
    setContent(editedContent)
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditedContent(content)
    setIsEditing(false)
  }

  return (
    <div className="h-full flex">
      {/* Left Panel: Memory List */}
      <SidePanel>
        <div className="p-4 border-b border-[var(--subtle-border)]">
          <h2 className="text-sm font-medium">{t.memory.title}</h2>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {mockMemoryItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setSelectedId(item.id)}
              className={cn(
                "w-full text-left p-3 rounded-lg mb-1 transition-colors",
                selectedId === item.id
                  ? "bg-accent text-foreground"
                  : "hover:bg-accent/50 text-muted-foreground"
              )}
            >
              <div className="flex items-center gap-2">
                {item.isGlobal ? <Globe size={16} /> : <FileText size={16} />}
                <span className="font-medium truncate">{item.name}</span>
              </div>
            </button>
          ))}
        </div>
      </SidePanel>

      {/* Center Panel: Memory Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="p-4 border-b border-[var(--subtle-border)] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="font-medium">
              {selectedItem?.isGlobal ? t.memory.globalMemory : t.memory.memoryFile}
            </span>
          </div>
          <div className="flex items-center gap-2">
            {isEditing ? (
              <>
                <button
                  onClick={handleCancel}
                  className="px-3 py-1.5 text-sm rounded-lg border border-[var(--subtle-border)] hover:bg-accent"
                >
                  {t.common.cancel}
                </button>
                <button
                  onClick={handleSave}
                  className="px-3 py-1.5 text-sm rounded-lg bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  {t.common.save}
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-3 py-1.5 text-sm rounded-lg border border-[var(--subtle-border)] hover:bg-accent"
                >
                  {t.common.edit}
                </button>
                <button
                  onClick={() => setPanelOpen(!panelOpen)}
                  className="p-1.5 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground"
                  title={t.memory.togglePanel}
                >
                  {panelOpen ? <PanelRightClose size={16} /> : <PanelRightOpen size={16} />}
                </button>
              </>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {isEditing ? (
            <textarea
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              placeholder={t.memory.writePlaceholder}
              className="w-full h-full p-4 rounded-lg border border-[var(--subtle-border)] bg-background resize-none focus:outline-none focus:ring-2 focus:ring-primary/50 font-mono text-sm"
            />
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              {content || <p className="text-muted-foreground">{t.memory.noContent}</p>}
            </div>
          )}
        </div>
      </div>

      {/* Right Panel */}
      {panelOpen && (
        <div className="w-[320px] shrink-0 border-l border-[var(--subtle-border)] flex flex-col">
          <div className="p-2 border-b border-[var(--subtle-border)] flex gap-1">
            <button
              onClick={() => setPanelTab('logs')}
              className={cn(
                "flex-1 px-3 py-1.5 text-sm rounded-lg transition-colors",
                panelTab === 'logs' ? "bg-accent text-foreground" : "hover:bg-accent/50 text-muted-foreground"
              )}
            >
              {t.memory.dailyLogs}
            </button>
            <button
              onClick={() => setPanelTab('archives')}
              className={cn(
                "flex-1 px-3 py-1.5 text-sm rounded-lg transition-colors",
                panelTab === 'archives' ? "bg-accent text-foreground" : "hover:bg-accent/50 text-muted-foreground"
              )}
            >
              {t.memory.archives}
            </button>
          </div>

          <div className="flex-1 overflow-y-auto">
            {panelTab === 'logs' && (
              <div className="p-2">
                {mockDailyLogs.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">{t.memory.noLogs}</p>
                ) : (
                  mockDailyLogs.map((log) => (
                    <div key={log.date} className="mb-1">
                      <button
                        onClick={() => setExpandedLog(expandedLog === log.date ? null : log.date)}
                        className="w-full text-left p-2 rounded-lg hover:bg-accent/50 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">{log.date}</span>
                          <ChevronRight
                            size={14}
                            className={cn(
                              "transition-transform",
                              expandedLog === log.date && "rotate-90"
                            )}
                          />
                        </div>
                      </button>
                      {expandedLog === log.date && (
                        <div className="px-2 py-1 text-sm text-muted-foreground">
                          {log.content}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}

            {panelTab === 'archives' && (
              <div className="p-4 text-center text-muted-foreground">
                {t.common.noData}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
