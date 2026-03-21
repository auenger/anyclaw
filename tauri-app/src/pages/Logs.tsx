import { useState, useRef, useEffect } from 'react'
import { Calendar, Search, ChevronDown, Radio } from 'lucide-react'
import { useI18n } from '@/i18n'
import { cn } from '@/lib/utils'

type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR'
type LogCategory = 'agent' | 'tool' | 'task' | 'system'

interface LogEntry {
  time: string
  level: LogLevel
  category: LogCategory
  agent?: string
  message: string
  details?: Record<string, unknown>
}

const mockLogs: LogEntry[] = [
  { time: '10:30:45', level: 'INFO', category: 'agent', agent: 'default', message: 'Agent started processing request' },
  { time: '10:30:46', level: 'DEBUG', category: 'tool', agent: 'default', message: 'Executing tool: ReadFileTool', details: { path: '/src/App.tsx' } },
  { time: '10:30:47', level: 'INFO', category: 'tool', agent: 'default', message: 'Tool completed successfully' },
  { time: '10:30:50', level: 'WARN', category: 'system', message: 'Memory usage high: 85%' },
  { time: '10:31:00', level: 'ERROR', category: 'agent', agent: 'researcher', message: 'Failed to connect to API', details: { error: 'Connection timeout' } },
  { time: '10:31:05', level: 'INFO', category: 'task', message: 'Cron job "daily_report" started' },
]

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
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])
  const [category, setCategory] = useState<LogCategory | 'all'>('all')
  const [level, setLevel] = useState<LogLevel | 'all'>('all')
  const [search, setSearch] = useState('')
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null)
  const [showDatePicker, setShowDatePicker] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  const isToday = selectedDate === new Date().toISOString().split('T')[0]

  const filteredLogs = mockLogs.filter((log) => {
    if (category !== 'all' && log.category !== category) return false
    if (level !== 'all' && log.level !== level) return false
    if (search && !log.message.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  // Auto-scroll to bottom when live
  useEffect(() => {
    if (isToday && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [filteredLogs.length, isToday])

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-[var(--subtle-border)] space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-semibold">{t.logs.title}</h1>
            {isToday && (
              <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-500/20 text-green-400 text-xs font-medium">
                <Radio size={10} className="animate-pulse" />
                {t.logs.live}
              </span>
            )}
          </div>
          <span className="text-sm text-muted-foreground">
            {filteredLogs.length} {t.logs.totalEntries}
          </span>
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

          {/* Category Buttons */}
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

          {/* Level Filter */}
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

      {/* Log Content */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 bg-[var(--surface-ground)]"
      >
        {filteredLogs.length === 0 ? (
          <div className="text-center py-12 text-muted-foreground">
            {t.logs.noLogs}
          </div>
        ) : (
          <div className="font-mono text-sm space-y-0.5">
            {filteredLogs.map((log, idx) => (
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
        )}
      </div>
    </div>
  )
}
