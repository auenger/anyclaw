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
  model: string;
  description?: string;
  status: 'idle' | 'busy' | 'error';
}
