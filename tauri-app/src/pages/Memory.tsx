import { useState, useEffect } from 'react'
import { Globe, FileText, ChevronRight, PanelRightClose, PanelRightOpen, Loader2, Search } from 'lucide-react'
import { SidePanel } from '@/components/layout/SidePanel'
import { useI18n } from '@/i18n'
import { cn } from '@/lib/utils'
import { useMemory } from '@/hooks/useMemory'
import type { MemoryInfo } from '@/types'

type PanelTab = 'logs' | 'search'

export function Memory() {
  const { t } = useI18n()
  const {
    memories,
    selectedMemory,
    content,
    dailyLogs,
    stats,
    isLoading,
    isSaving,
    error,
    selectMemory,
    saveContent,
    loadDailyLogs,
    search,
  } = useMemory()

  const [isEditing, setIsEditing] = useState(false)
  const [editedContent, setEditedContent] = useState('')
  const [panelOpen, setPanelOpen] = useState(true)
  const [panelTab, setPanelTab] = useState<PanelTab>('logs')
  const [expandedLog, setExpandedLog] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<{ source: string; matches: string[] }[]>([])
  const [isSearching, setIsSearching] = useState(false)

  // Sync edited content with loaded content
  useEffect(() => {
    if (content !== undefined) {
      setEditedContent(content)
    }
  }, [content])

  // Reset editing state when memory changes
  useEffect(() => {
    setIsEditing(false)
  }, [selectedMemory?.id])

  const handleSelectMemory = async (memory: MemoryInfo) => {
    await selectMemory(memory.id)
  }

  const handleSave = async () => {
    const success = await saveContent(editedContent)
    if (success) {
      setIsEditing(false)
    }
  }

  const handleCancel = () => {
    setEditedContent(content || '')
    setIsEditing(false)
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setIsSearching(true)
    try {
      const results = await search(searchQuery, selectedMemory?.id)
      setSearchResults(results.results)
    } catch (err) {
      console.error('Search failed:', err)
    } finally {
      setIsSearching(false)
    }
  }

  const handleLoadMoreLogs = async () => {
    await loadDailyLogs(30) // Load 30 days of logs
  }

  return (
    <div className="h-full flex">
      {/* Left Panel: Memory List */}
      <SidePanel>
        <div className="p-4 border-b border-[var(--subtle-border)]">
          <h2 className="text-sm font-medium">{t.memory.title}</h2>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {isLoading && memories.length === 0 ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          ) : memories.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">{t.common.noData}</p>
          ) : (
            memories.map((memory) => (
              <button
                key={memory.id}
                onClick={() => handleSelectMemory(memory)}
                className={cn(
                  "w-full text-left p-3 rounded-lg mb-1 transition-colors",
                  selectedMemory?.id === memory.id
                    ? "bg-accent text-foreground"
                    : "hover:bg-accent/50 text-muted-foreground"
                )}
              >
                <div className="flex items-center gap-2">
                  {memory.is_global ? <Globe size={16} /> : <FileText size={16} />}
                  <div className="flex-1 min-w-0">
                    <span className="font-medium truncate block">{memory.name}</span>
                    {memory.char_count > 0 && (
                      <span className="text-xs text-muted-foreground">
                        {memory.char_count.toLocaleString()} {t.settings.characters}
                      </span>
                    )}
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      </SidePanel>

      {/* Center Panel: Memory Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="p-4 border-b border-[var(--subtle-border)] flex items-center justify-between">
          <div className="flex items-center gap-2">
            {selectedMemory && (
              <>
                {selectedMemory.is_global ? <Globe size={16} /> : <FileText size={16} />}
                <span className="font-medium">
                  {selectedMemory.is_global ? t.memory.globalMemory : selectedMemory.name}
                </span>
                {stats && (
                  <span className="text-xs text-muted-foreground">
                    ({stats.long_term_chars.toLocaleString()} {t.settings.characters})
                  </span>
                )}
              </>
            )}
          </div>
          <div className="flex items-center gap-2">
            {error && (
              <span className="text-sm text-destructive">{error}</span>
            )}
            {isEditing ? (
              <>
                <button
                  onClick={handleCancel}
                  disabled={isSaving}
                  className="px-3 py-1.5 text-sm rounded-lg border border-[var(--subtle-border)] hover:bg-accent disabled:opacity-50"
                >
                  {t.common.cancel}
                </button>
                <button
                  onClick={handleSave}
                  disabled={isSaving}
                  className="px-3 py-1.5 text-sm rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 flex items-center gap-1.5"
                >
                  {isSaving && <Loader2 className="h-3 w-3 animate-spin" />}
                  {isSaving ? t.common.saving : t.common.save}
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
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : isEditing ? (
            <textarea
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              placeholder={t.memory.writePlaceholder}
              className="w-full h-full p-4 rounded-lg border border-[var(--subtle-border)] bg-background resize-none focus:outline-none focus:ring-2 focus:ring-primary/50 font-mono text-sm"
            />
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap">
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
              onClick={() => setPanelTab('search')}
              className={cn(
                "flex-1 px-3 py-1.5 text-sm rounded-lg transition-colors",
                panelTab === 'search' ? "bg-accent text-foreground" : "hover:bg-accent/50 text-muted-foreground"
              )}
            >
              {t.memory.search}
            </button>
          </div>

          <div className="flex-1 overflow-y-auto">
            {panelTab === 'logs' && (
              <div className="p-2">
                {dailyLogs.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">{t.memory.noLogs}</p>
                ) : (
                  <>
                    {dailyLogs.map((log) => (
                      <div key={log.date} className="mb-1">
                        <button
                          onClick={() => setExpandedLog(expandedLog === log.date ? null : log.date)}
                          className="w-full text-left p-2 rounded-lg hover:bg-accent/50 transition-colors"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">{log.date}</span>
                            <div className="flex items-center gap-2">
                              {log.char_count > 0 && (
                                <span className="text-xs text-muted-foreground">
                                  {log.char_count}
                                </span>
                              )}
                              <ChevronRight
                                size={14}
                                className={cn(
                                  "transition-transform",
                                  expandedLog === log.date && "rotate-90"
                                )}
                              />
                            </div>
                          </div>
                        </button>
                        {expandedLog === log.date && (
                          <div className="px-2 py-1 text-sm text-muted-foreground whitespace-pre-wrap max-h-[200px] overflow-y-auto">
                            {log.content || <span className="italic">{t.common.noData}</span>}
                          </div>
                        )}
                      </div>
                    ))}
                    {stats && stats.daily_logs_count > dailyLogs.length && (
                      <button
                        onClick={handleLoadMoreLogs}
                        className="w-full p-2 text-sm text-center text-muted-foreground hover:text-foreground hover:bg-accent/50 rounded-lg transition-colors"
                      >
                        {t.logs.loadMore}
                      </button>
                    )}
                  </>
                )}
              </div>
            )}

            {panelTab === 'search' && (
              <div className="p-2">
                <div className="flex gap-1 mb-2">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder={t.memory.searchPlaceholder}
                    className="flex-1 px-3 py-1.5 text-sm rounded-lg border border-[var(--subtle-border)] bg-background focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                  <button
                    onClick={handleSearch}
                    disabled={isSearching || !searchQuery.trim()}
                    className="p-1.5 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                  >
                    {isSearching ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Search className="h-4 w-4" />
                    )}
                  </button>
                </div>

                {searchResults.length > 0 ? (
                  <div className="space-y-2">
                    {searchResults.map((result, index) => (
                      <div key={index} className="p-2 rounded-lg bg-accent/50">
                        <div className="text-sm font-medium mb-1">{result.source}</div>
                        <div className="space-y-1">
                          {result.matches.slice(0, 3).map((match, matchIndex) => (
                            <div
                              key={matchIndex}
                              className="text-xs text-muted-foreground line-clamp-2"
                            >
                              {match}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : searchQuery && !isSearching ? (
                  <p className="text-center text-muted-foreground py-8">{t.memory.noResults}</p>
                ) : null}
              </div>
            )}
          </div>

          {/* Stats Footer */}
          {stats && (
            <div className="p-2 border-t border-[var(--subtle-border)] text-xs text-muted-foreground">
              <div className="flex justify-between">
                <span>{t.memory.dailyLogs}:</span>
                <span>{stats.daily_logs_count}</span>
              </div>
              {stats.oldest_log && (
                <div className="flex justify-between">
                  <span>Oldest:</span>
                  <span>{stats.oldest_log}</span>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
