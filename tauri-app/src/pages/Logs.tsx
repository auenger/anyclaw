import { useState, useRef, useEffect } from 'react'
import { Calendar, Search, ChevronDown, ChevronRight, Radio, ArrowLeft, Loader2 } from 'lucide-react'
import { useI18n } from '@/i18n'
import { cn } from '@/lib/utils'
import { useLogs } from '@/hooks/useLogs'
import type { LogCategory, LogLevel, SessionLogInfo, SessionRecord } from '@/types'

type TabType = 'sessions' | 'system'

const levelColors: Record<LogLevel, string> = {
  DEBUG: 'text-blue-500',
  INFO: 'text-green-500',
  WARN: 'text-yellow-500',
  ERROR: 'text-red-500',
}

const categoryColors: Record<LogCategory, string> = {
  agent: 'bg-purple-500/20 text-purple-400',
  tool: 'bg-blue-500/20 text-blue-400',
  task: 'bg-orange-500/20 text-orange-400',
  system: 'bg-gray-500/20 text-gray-400',
}

export function Logs() {
  const { t } = useI18n()
  const {
    sessionLogs,
    systemLogs,
    selectedSession,
    stats,
    isLoading,
    isLive,
    loadSessionLogs,
    loadSessionDetail,
    loadSystemLogs,
    clearSelection,
    toggleLive,
  } = useLogs()

  const [activeTab, setActiveTab] = useState<TabType>('sessions')
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])
  const [category, setCategory] = useState<LogCategory | 'all'>('all')
  const [level, setLevel] = useState<LogLevel | 'all'>('all')
  const [search, setSearch] = useState('')
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null)
  const [showDatePicker, setShowDatePicker] = useState(false)
  const [expandedSessionRecord, setExpandedSessionRecord] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  const isToday = selectedDate === new Date().toISOString().split('T')[0]

  // Load data when tab or date changes
  useEffect(() => {
    if (activeTab === 'sessions') {
      loadSessionLogs(selectedDate)
    } else {
      loadSystemLogs(level, category, selectedDate, search || undefined)
    }
  }, [activeTab, selectedDate, level, category, search, loadSessionLogs, loadSystemLogs])

  // Auto-scroll to bottom when live
  useEffect(() => {
    if (isLive && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [systemLogs.length, isLive])

  // Handle session click
  const handleSessionClick = async (session: SessionLogInfo) => {
    await loadSessionDetail(session.session_id)
  }

  // Handle back to list
  const handleBackToList = () => {
    clearSelection()
  }

  // Filter system logs locally for search
  const filteredSystemLogs = systemLogs.filter((log) => {
    if (category !== 'all' && log.category !== category) return false
    if (level !== 'all' && log.level !== level) return false
    if (search && !log.message.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  // Render record type badge
  const getRecordBadge = (record: SessionRecord) => {
    const typeStyles: Record<string, string> = {
      user_message: 'bg-blue-500/20 text-blue-400',
      assistant_message: 'bg-green-500/20 text-green-400',
      tool_call: 'bg-purple-500/20 text-purple-400',
      tool_result: 'bg-gray-500/20 text-gray-400',
      skill_call: 'bg-orange-500/20 text-orange-400',
      skill_result: 'bg-gray-500/20 text-gray-400',
      thinking: 'bg-cyan-500/20 text-cyan-400',
      error: 'bg-red-500/20 text-red-400',
    }
    return typeStyles[record.type] || 'bg-gray-500/20 text-gray-400'
  }

  // Render session detail view
  if (selectedSession) {
    return (
      <div className="h-full flex flex-col">
        <div className="p-4 border-b border-[var(--subtle-border)]">
          <div className="flex items-center gap-2">
            <button
              onClick={handleBackToList}
              className="p-1.5 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground"
            >
              <ArrowLeft size={16} />
            </button>
            <div>
              <h2 className="font-medium">{t.logs.title} - {t.logs.sessionDetail || 'Session Detail'}</h2>
              <p className="text-xs text-muted-foreground">{selectedSession.session_id.slice(0, 8)}...</p>
            </div>
          </div>
        </div>

        <div className="p-4 border-b border-[var(--subtle-border)] bg-muted/30">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Project: </span>
              <span className="font-mono">{selectedSession.project_id}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Channel: </span>
              <span>{selectedSession.channel}</span>
            </div>
            <div>
              <span className="text-muted-foreground">Messages: </span>
              <span>{selectedSession.message_count}</span>
            </div>
            {selectedSession.git_branch && (
              <div>
                <span className="text-muted-foreground">Branch: </span>
                <span>{selectedSession.git_branch}</span>
              </div>
            )}
            {selectedSession.duration_seconds && (
              <div>
                <span className="text-muted-foreground">Duration: </span>
                <span>{selectedSession.duration_seconds.toFixed(1)}s</span>
              </div>
            )}
            <div>
              <span className="text-muted-foreground">Tools: </span>
              <span>{selectedSession.tool_call_count}</span>
            </div>
          </div>
        </div>

        <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 bg-[var(--surface-ground)]">
          {selectedSession.records.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              {t.common.noData}
            </div>
          ) : (
            <div className="space-y-2">
              {selectedSession.records.map((record, idx) => (
                <div key={record.uuid || idx} className="border border-[var(--subtle-border)] rounded-lg">
                  <button
                    onClick={() => setExpandedSessionRecord(
                      expandedSessionRecord === (record.uuid || String(idx))
                        ? null
                        : (record.uuid || String(idx))
                    )}
                    className="w-full text-left p-3 hover:bg-accent/30 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <ChevronRight
                        size={14}
                        className={cn(
                          "transition-transform",
                          expandedSessionRecord === (record.uuid || String(idx)) && "rotate-90"
                        )}
                      />
                      <span className={cn("px-1.5 py-0.5 rounded text-xs", getRecordBadge(record))}>
                        {record.type}
                      </span>
                      {record.timestamp && (
                        <span className="text-xs text-muted-foreground">
                          {new Date(record.timestamp).toLocaleTimeString()}
                        </span>
                      )}
                      {record.tool_name && (
                        <span className="text-sm font-mono">{record.tool_name}</span>
                      )}
                      {record.content && (
                        <span className="text-sm truncate flex-1">
                          {record.content.slice(0, 100)}
                          {record.content.length > 100 && '...'}
                        </span>
                      )}
                    </div>
                  </button>
                  {expandedSessionRecord === (record.uuid || String(idx)) && (
                    <div className="px-3 pb-3 pt-0 border-t border-[var(--subtle-border)]">
                      <pre className="text-xs text-muted-foreground overflow-x-auto whitespace-pre-wrap bg-black/20 p-2 rounded">
                        {JSON.stringify(record, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-[var(--subtle-border)] space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-semibold">{t.logs.title}</h1>
            {isToday && activeTab === 'system' && (
              <button
                onClick={toggleLive}
                className={cn(
                  "flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium transition-colors",
                  isLive
                    ? "bg-green-500/20 text-green-400"
                    : "bg-gray-500/20 text-gray-400 hover:bg-green-500/20 hover:text-green-400"
                )}
              >
                <Radio size={10} className={isLive ? "animate-pulse" : ""} />
                {t.logs.live}
              </button>
            )}
          </div>
          <span className="text-sm text-muted-foreground">
            {activeTab === 'sessions'
              ? `${sessionLogs.length} ${t.logs.totalEntries}`
              : `${filteredSystemLogs.length} ${t.logs.totalEntries}`}
          </span>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-2 p-1 rounded-lg bg-muted/30 w-fit">
          <button
            onClick={() => setActiveTab('sessions')}
            className={cn(
              "px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
              activeTab === 'sessions'
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            {t.logs.sessionArchives || 'Sessions'}
          </button>
          <button
            onClick={() => setActiveTab('system')}
            className={cn(
              "px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
              activeTab === 'system'
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            {t.logs.systemLogs || 'System Logs'}
          </button>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Date Picker */}
          <div className="relative">
            <button
              onClick={() => setShowDatePicker(!showDatePicker)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[var(--subtle-border)] hover:bg-accent text-sm"
            >
              <Calendar size={14} />
              {selectedDate}
              <ChevronDown size={14} />
            </button>
            {showDatePicker && (
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => {
                  setSelectedDate(e.target.value)
                  setShowDatePicker(false)
                }}
                className="absolute top-full left-0 mt-1 z-10 rounded-lg border border-[var(--subtle-border)] bg-background p-2"
              />
            )}
          </div>

          {/* Category Buttons (System tab only) */}
          {activeTab === 'system' && (
            <div className="flex items-center gap-1 p-1 rounded-lg bg-muted/30">
              {(['all', 'agent', 'tool', 'task', 'system'] as const).map((cat) => (
                <button
                  key={cat}
                  onClick={() => setCategory(cat)}
                  className={cn(
                    "px-2.5 py-1 rounded-md text-xs font-medium transition-colors",
                    category === cat
                      ? "bg-background text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {cat === 'all' ? t.logs.allCategories : t.logs[`category${cat.charAt(0).toUpperCase() + cat.slice(1)}` as keyof typeof t.logs] as string}
                </button>
              ))}
            </div>
          )}

          {/* Level Filter (System tab only) */}
          {activeTab === 'system' && (
            <select
              value={level}
              onChange={(e) => setLevel(e.target.value as LogLevel | 'all')}
              className="px-3 py-1.5 rounded-lg border border-[var(--subtle-border)] bg-background text-sm"
            >
              <option value="all">{t.logs.allLevels}</option>
              <option value="DEBUG">DEBUG</option>
              <option value="INFO">INFO</option>
              <option value="WARN">WARN</option>
              <option value="ERROR">ERROR</option>
            </select>
          )}

          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={t.logs.searchLogs}
              className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-[var(--subtle-border)] bg-background text-sm"
            />
          </div>
        </div>
      </div>

      {/* Content */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 bg-[var(--surface-ground)]"
      >
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : activeTab === 'sessions' ? (
          // Session Logs
          sessionLogs.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              {t.logs.noLogs}
            </div>
          ) : (
            <div className="space-y-2">
              {sessionLogs.map((session) => (
                <button
                  key={session.session_id}
                  onClick={() => handleSessionClick(session)}
                  className="w-full text-left p-3 rounded-lg border border-[var(--subtle-border)] hover:bg-accent/30 transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono text-sm">
                      {session.session_id.slice(0, 8)}...
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {session.started_at && new Date(session.started_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="px-1.5 py-0.5 rounded bg-muted">
                      {session.channel}
                    </span>
                    <span>{session.project_id}</span>
                    {session.git_branch && (
                      <span className="text-cyan-400">{session.git_branch}</span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )
        ) : (
          // System Logs
          filteredSystemLogs.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              {t.logs.noLogs}
            </div>
          ) : (
            <div className="font-mono text-sm space-y-0.5">
              {filteredSystemLogs.map((log, idx) => (
                <div key={idx}>
                  <button
                    onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
                    className="w-full text-left py-1 px-2 rounded hover:bg-accent/30 transition-colors group"
                  >
                    <span className="text-muted-foreground mr-2">{log.time}</span>
                    <span className={cn("font-medium mr-2", levelColors[log.level])}>
                      [{log.level}]
                    </span>
                    <span className={cn(
                      "px-1.5 py-0.5 rounded text-xs mr-2",
                      categoryColors[log.category]
                    )}>
                      {log.category}
                    </span>
                    {log.agent && (
                      <span className="text-cyan-400 mr-2">{log.agent}</span>
                    )}
                    <span className="text-foreground">{log.message}</span>
                  </button>
                  {expandedIdx === idx && log.details && (
                    <div className="ml-20 p-2 bg-black/30 rounded text-xs text-muted-foreground overflow-x-auto">
                      <pre>{JSON.stringify(log.details, null, 2)}</pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )
        )}
      </div>

      {/* Stats Footer */}
      {stats && (
        <div className="p-2 border-t border-[var(--subtle-border)] text-xs text-muted-foreground bg-muted/30">
          <div className="flex justify-between">
            <span>Sessions today: {stats.sessions_today}</span>
            <span>System logs: {stats.system_logs_total}</span>
          </div>
        </div>
      )}
    </div>
  )
}
