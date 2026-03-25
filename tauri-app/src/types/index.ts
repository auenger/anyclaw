// AnyClaw Desktop Types

// ============ Message Types ============
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
}

// ============ Sidecar Status ============
export interface SidecarStatus {
  status: 'Stopped' | 'Starting' | 'Running' | 'Stopping' | 'Error';
  port: number;
  pid: number | null;
  uptime_seconds: number;
  message: string;
}

// ============ SSE Event Types ============
export type SSEEventType =
  | 'message_start'
  | 'content_delta'
  | 'message_end'
  | 'message:outbound'
  | 'agent:thinking'
  | 'tool:start'
  | 'tool:complete'
  | 'error'
  | 'connected';

export interface SSEEvent {
  type: SSEEventType;
  data: {
    content?: string;
    delta?: string;
    message_id?: string;
    error?: string;
    timestamp?: number;
    payload?: any;
  };
}

export interface SSEState {
  connected: boolean;
  reconnecting: boolean;
  error: string | null;
}

// ============ Settings Types ============
export interface LLMSettings {
  model: string;
  temperature: number;
  max_tokens: number;
  stream: boolean;
}

export interface ProviderSettings {
  name: string;
  api_key?: string;
  base_url?: string;
}

export interface Settings {
  llm: LLMSettings;
  providers: Record<string, ProviderSettings>;
}

// ============ Skill Types ============
export interface SkillParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  description?: string;
  required?: boolean;
  default?: any;
}

export interface Skill {
  id: string;
  name: string;
  description: string;
  version?: string;
  author?: string;
  tags?: string[];
  enabled: boolean;
  parameters?: SkillParameter[];
  examples?: string[];
  source?: string;
}

// ============ Task Types ============
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface SubAgent {
  id: string;
  name: string;
  status: TaskStatus;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  progress?: number;
  output?: string;
  error?: string;
}

export type CronStatus = 'enabled' | 'disabled';

export interface CronTask {
  id: string;
  name: string;
  schedule: string;
  status: CronStatus;
  next_run?: string;
  last_run?: string;
  last_result?: string;
}

// ============ Agent Types ============
export interface Agent {
  id: string;
  name: string;
  emoji: string;
  avatar: string;
  enabled: boolean;
  workspace?: string;
  sessionCount: number;
}

export interface CreateAgentRequest {
  name: string;
  creature?: string;
  vibe?: string;
  emoji?: string;
  avatar?: string;
  workspace?: string;
}

export interface UpdateAgentRequest {
  name?: string;
  emoji?: string;
  avatar?: string;
  enabled?: boolean;
}

// ============ Memory Types ============
export interface MemoryInfo {
  id: string;
  name: string;
  is_global: boolean;
  agent_id?: string;
  exists: boolean;
  char_count: number;
}

export interface MemoryContent {
  id: string;
  content: string;
  exists: boolean;
}

export interface DailyLogInfo {
  date: string;
  content: string;
  char_count: number;
}

export interface MemoryStats {
  long_term_exists: boolean;
  long_term_chars: number;
  daily_logs_count: number;
  oldest_log?: string;
  newest_log?: string;
}

export interface SearchMatch {
  source: string;
  matches: string[];
}

export interface SearchResponse {
  results: SearchMatch[];
}

// ============ Log Types ============
export type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';
export type LogCategory = 'agent' | 'tool' | 'task' | 'system';

export interface SystemLogEntry {
  time: string;
  level: LogLevel;
  category: LogCategory;
  agent?: string;
  message: string;
  details?: Record<string, unknown>;
  timestamp: string;
}

export interface SessionLogInfo {
  session_id: string;
  project_id: string;
  channel: string;
  cwd?: string;
  git_branch?: string;
  started_at?: string;
  ended_at?: string;
  message_count: number;
  tool_call_count: number;
  duration_seconds?: number;
  path: string;
}

export interface SessionLogDetail extends SessionLogInfo {
  records: SessionRecord[];
}

export interface SessionRecord {
  type: string;
  uuid?: string;
  parent_uuid?: string;
  timestamp?: string;
  content?: string;
  tool_name?: string;
  tool_input?: Record<string, unknown>;
  tool_call_id?: string;
  output?: string;
  success?: boolean;
  duration_ms?: number;
  [key: string]: unknown;
}

export interface LogSearchResult {
  session_id: string;
  path: string;
  type: string;
  timestamp?: string;
  content: Record<string, unknown>;
}

export interface LogStats {
  sessions_total: number;
  sessions_today: number;
  system_logs_total: number;
  by_level: Record<string, number>;
  by_category: Record<string, number>;
}

// ============ Provider Types ============
export type { Provider, ProviderDetail, ProviderConfig, TestResult } from './providers';

// Re-export for convenience
export type { Provider as ProviderInfo } from './providers';

// ============ Cron Job Types ============
export type ScheduleType = 'interval' | 'cron' | 'once';
export type JobStatus = 'active' | 'paused' | 'completed';
export type RunStatus = 'success' | 'error';

export interface CronSchedule {
  type: 'every' | 'cron' | 'at';
  valueMs?: number;
  expr?: string;
  tz?: string;
  atMs?: number;
}

export interface CronJobState {
  nextRunAtMs: number | null;
  lastRunAtMs: number | null;
  lastStatus?: 'ok' | 'error' | 'skipped';
  lastError?: string;
  consecutiveFailures: number;
}

export interface CronJob {
  id: string;
  name: string;
  description?: string;
  agentId: string;
  chatId: string;
  prompt: string;
  enabled: boolean;
  schedule: CronSchedule;
  state: CronJobState;
  createdAtMs: number;
  updatedAtMs: number;
}

export interface CreateJobRequest {
  name: string;
  description?: string;
  agent_id: string;
  chat_id: string;
  prompt: string;
  schedule: {
    type: ScheduleType;
    value_ms?: number;
    expr?: string;
    tz?: string;
    at_ms?: number;
  };
}

export interface UpdateJobRequest {
  name?: string;
  description?: string;
  prompt?: string;
  schedule?: {
    type: ScheduleType;
    value_ms?: number;
    expr?: string;
    tz?: string;
    at_ms?: number;
  };
  enabled?: boolean;
}

export interface RunLog {
  id: number;
  jobId: string;
  runAtMs: number;
  durationMs: number;
  status: RunStatus;
  result?: string;
  error?: string;
}

export interface RunResult {
  success: boolean;
  message: string;
}
