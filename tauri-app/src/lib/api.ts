/**
 * API Client for AnyClaw Sidecar
 */

import type {
  Settings, Skill, SubAgent, CronTask, Agent,
  CreateAgentRequest, UpdateAgentRequest,
  MemoryInfo, MemoryContent, DailyLogInfo, MemoryStats, SearchResponse,
  SystemLogEntry, LogStats,
  LogCategory, LogLevel, Provider, ProviderDetail, ProviderConfig, TestResult,
  CronJob, CreateJobRequest, UpdateJobRequest, RunLog, RunResult
} from '../types';
import type { ChatItem } from './chat-utils';

const DEFAULT_PORT = 62601;

export function getApiUrl(port: number = DEFAULT_PORT): string {
  return `http://127.0.0.1:${port}`;
}

export class ApiClient {
  private baseUrl: string;

  constructor(port: number = DEFAULT_PORT) {
    this.baseUrl = `http://127.0.0.1:${port}`;
  }

  setPort(port: number): void {
    this.baseUrl = `http://127.0.0.1:${port}`;
  }

  // ============ Health ============
  async health(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseUrl}/api/health`);
    return response.json();
  }

  // ============ Chats ============
  async getChats(): Promise<ChatItem[]> {
    const response = await fetch(`${this.baseUrl}/api/chats`);
    return response.json();
  }

  async getChat(chatId: string): Promise<{
    chat_id: string
    messages: Array<{
      id: string
      role: 'user' | 'assistant' | 'tool'
      content: string
      timestamp: string
      tool_calls?: Array<{
        id: string
        type: 'function'
        function: { name: string; arguments: string }
      }>
      tool_call_id?: string
      name?: string
    }>
  }> {
    const response = await fetch(`${this.baseUrl}/api/chats/${chatId}`);
    return response.json();
  }

  async deleteChat(chatId: string): Promise<{ success: boolean }> {
    const response = await fetch(`${this.baseUrl}/api/chats/${chatId}`, {
      method: 'DELETE',
    });
    return response.json();
  }

  async updateChat(chatId: string, data: { name?: string; avatar?: string }): Promise<{ success: boolean }> {
    const response = await fetch(`${this.baseUrl}/api/chats/${chatId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  }

  // ============ Agents ============
  async listAgents(includeDisabled: boolean = false): Promise<Agent[]> {
    const params = includeDisabled ? '?include_disabled=true' : '';
    const response = await fetch(`${this.baseUrl}/api/agents${params}`);
    return response.json();
  }

  async getAgent(agentId: string): Promise<Agent> {
    const response = await fetch(`${this.baseUrl}/api/agents/${agentId}`);
    return response.json();
  }

  async createAgent(data: CreateAgentRequest): Promise<Agent> {
    const response = await fetch(`${this.baseUrl}/api/agents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  }

  async updateAgent(agentId: string, data: UpdateAgentRequest): Promise<Agent> {
    const response = await fetch(`${this.baseUrl}/api/agents/${agentId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  }

  async deleteAgent(agentId: string): Promise<void> {
    await fetch(`${this.baseUrl}/api/agents/${agentId}`, {
      method: 'DELETE',
    });
  }

  async activateAgent(agentId: string): Promise<{ status: string; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/agents/${agentId}/activate`, {
      method: 'POST',
    });
    return response.json();
  }

  async deactivateAgent(agentId: string): Promise<{ status: string; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/agents/${agentId}/deactivate`, {
      method: 'POST',
    });
    return response.json();
  }

  async sendMessage(agentId: string, content: string, conversationId?: string): Promise<{ message_id: string }> {
    const response = await fetch(`${this.baseUrl}/api/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId, content, conversation_id: conversationId }),
    });
    return response.json();
  }

  // ============ Messages (Legacy) ============
  async postMessage(content: string, agentId: string = 'default'): Promise<{ success: boolean }> {
    const response = await fetch(`${this.baseUrl}/api/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId, content }),
    });
    return response.json();
  }

  // ============ Skills ============
  async listSkills(): Promise<Skill[]> {
    const response = await fetch(`${this.baseUrl}/api/skills`);
    return response.json();
  }

  async reloadSkill(skillId: string): Promise<{ success: boolean }> {
    const response = await fetch(`${this.baseUrl}/api/skills/${skillId}/reload`, {
      method: 'POST',
    });
    return response.json();
  }

  async reloadAllSkills(): Promise<{ success: boolean }> {
    const response = await fetch(`${this.baseUrl}/api/skills/reload`, {
      method: 'POST',
    });
    return response.json();
  }

  // ============ Tasks ============
  async listSubAgents(): Promise<SubAgent[]> {
    const response = await fetch(`${this.baseUrl}/api/tasks`);
    const data = await response.json();
    return data.subagents || [];
  }

  async listCrons(): Promise<CronTask[]> {
    const response = await fetch(`${this.baseUrl}/api/tasks`);
    const data = await response.json();
    return data.crons || [];
  }

  async listTasks(): Promise<{ subagents: SubAgent[]; crons: CronTask[] }> {
    const response = await fetch(`${this.baseUrl}/api/tasks`);
    return response.json();
  }

  async cancelSubAgent(id: string): Promise<{ success: boolean }> {
    const response = await fetch(`${this.baseUrl}/api/tasks/${id}/cancel`, {
      method: 'POST',
    });
    return response.json();
  }

  async toggleCron(id: string, enabled: boolean): Promise<{ success: boolean }> {
    const response = await fetch(`${this.baseUrl}/api/crons/${id}/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    });
    return response.json();
  }

  // ============ Config ============
  async getConfig(): Promise<Settings> {
    const response = await fetch(`${this.baseUrl}/api/config`);
    return response.json();
  }

  async updateConfig(config: Partial<Settings>): Promise<{ success: boolean }> {
    const response = await fetch(`${this.baseUrl}/api/config`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    return response.json();
  }

  // ============ Stream ============
  getStreamUrl(): string {
    return `${this.baseUrl}/api/stream`;
  }

  // ============ Memory ============
  async listMemories(): Promise<MemoryInfo[]> {
    const response = await fetch(`${this.baseUrl}/api/memory`);
    return response.json();
  }

  async getMemory(memoryId: string): Promise<MemoryContent> {
    const response = await fetch(`${this.baseUrl}/api/memory/${memoryId}`);
    return response.json();
  }

  async updateMemory(memoryId: string, content: string): Promise<{ status: string; message: string; char_count: number }> {
    const response = await fetch(`${this.baseUrl}/api/memory/${memoryId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    });
    return response.json();
  }

  async getDailyLogs(memoryId: string, days: number = 7): Promise<DailyLogInfo[]> {
    const response = await fetch(`${this.baseUrl}/api/memory/${memoryId}/daily-logs?days=${days}`);
    return response.json();
  }

  async getMemoryStats(memoryId: string): Promise<MemoryStats> {
    const response = await fetch(`${this.baseUrl}/api/memory/${memoryId}/stats`);
    return response.json();
  }

  async searchMemory(keyword: string, memoryId?: string): Promise<SearchResponse> {
    const response = await fetch(`${this.baseUrl}/api/memory/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ keyword, memory_id: memoryId }),
    });
    return response.json();
  }

  // ============ Logs ============
  async getLogStats(): Promise<LogStats> {
    const response = await fetch(`${this.baseUrl}/api/logs/stats`);
    return response.json();
  }

  async getAvailableDates(): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/logs/dates`);
      if (!response.ok) return [];
      const data = await response.json();
      return Array.isArray(data) ? data : [];
    } catch {
      return [];
    }
  }

  async getSystemLogs(
    level?: LogLevel | 'all',
    category?: LogCategory | 'all',
    date?: string,
    search?: string,
    limit: number = 100
  ): Promise<SystemLogEntry[]> {
    const params = new URLSearchParams();
    if (level && level !== 'all') params.append('level', level);
    if (category && category !== 'all') params.append('category', category);
    if (date) params.append('date', date);
    if (search) params.append('search', search);
    params.append('limit', String(limit));

    const response = await fetch(`${this.baseUrl}/api/logs/system?${params}`);
    return response.json();
  }

  getLogStreamUrl(category?: string): string {
    const params = category && category !== 'all' ? `?category=${category}` : '';
    return `${this.baseUrl}/api/logs/stream${params}`;
  }

  // ============ Providers ============
  async listProviders(): Promise<Provider[]> {
    const response = await fetch(`${this.baseUrl}/api/providers`);
    return response.json();
  }

  async getProvider(name: string): Promise<ProviderDetail> {
    const response = await fetch(`${this.baseUrl}/api/providers/${name}`);
    return response.json();
  }

  async updateProvider(name: string, config: ProviderConfig): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/providers/${name}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    return response.json();
  }

  async testProvider(name: string, config?: ProviderConfig): Promise<TestResult> {
    const response = await fetch(`${this.baseUrl}/api/providers/${name}/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config || {}),
    });
    return response.json();
  }

  async setDefaultProvider(name: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/providers/${name}/set-default`, {
      method: 'POST',
    });
    return response.json();
  }

  // ============ Cron Jobs ============
  async getCronJobs(enabled?: boolean): Promise<CronJob[]> {
    const params = enabled !== undefined ? `?enabled=${enabled}` : '';
    const response = await fetch(`${this.baseUrl}/api/cron/jobs${params}`);
    return response.json();
  }

  async getCronJob(id: string): Promise<CronJob> {
    const response = await fetch(`${this.baseUrl}/api/cron/jobs/${id}`);
    return response.json();
  }

  async createCronJob(data: CreateJobRequest): Promise<CronJob> {
    const response = await fetch(`${this.baseUrl}/api/cron/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  }

  async updateCronJob(id: string, data: UpdateJobRequest): Promise<CronJob> {
    const response = await fetch(`${this.baseUrl}/api/cron/jobs/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  }

  async deleteCronJob(id: string): Promise<{ status: string; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/cron/jobs/${id}`, {
      method: 'DELETE',
    });
    return response.json();
  }

  async cloneCronJob(id: string): Promise<CronJob> {
    const response = await fetch(`${this.baseUrl}/api/cron/jobs/${id}/clone`, {
      method: 'POST',
    });
    return response.json();
  }

  async runCronJob(id: string): Promise<RunResult> {
    const response = await fetch(`${this.baseUrl}/api/cron/jobs/${id}/run`, {
      method: 'POST',
    });
    return response.json();
  }

  async getCronJobLogs(id: string, limit: number = 50): Promise<RunLog[]> {
    const response = await fetch(`${this.baseUrl}/api/cron/jobs/${id}/logs?limit=${limit}`);
    return response.json();
  }
}

// 单例实例
let apiClient: ApiClient | null = null;

export function getApiClient(port?: number): ApiClient {
  if (!apiClient) {
    apiClient = new ApiClient(port);
  } else if (port !== undefined) {
    apiClient.setPort(port);
  }
  return apiClient;
}

export function resetApiClient(): void {
  apiClient = null;
}
