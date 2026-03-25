/**
 * useAgents Hook
 *
 * 提供 Agent CRUD 功能：列表、创建、更新、删除、激活、禁用
 */

import { useState, useCallback, useEffect } from 'react';
import { getApiClient } from '../lib/api';
import type { Agent, CreateAgentRequest, UpdateAgentRequest } from '../types';

export interface UseAgentsReturn {
  agents: Agent[];
  isLoading: boolean;
  error: string | null;
  loadAgents: () => Promise<void>;
  createAgent: (data: CreateAgentRequest) => Promise<Agent | null>;
  updateAgent: (id: string, data: UpdateAgentRequest) => Promise<Agent | null>;
  deleteAgent: (id: string) => Promise<boolean>;
  activateAgent: (id: string) => Promise<boolean>;
  deactivateAgent: (id: string) => Promise<boolean>;
}

export function useAgents(port?: number): UseAgentsReturn {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 加载 Agent 列表
  const loadAgents = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const api = getApiClient(port);
      const data = await api.listAgents(true); // 包含禁用的 agent
      setAgents(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '加载 Agent 失败';
      setError(errorMessage);
      console.error('Failed to load agents:', err);
    } finally {
      setIsLoading(false);
    }
  }, [port]);

  // 创建 Agent
  const createAgent = useCallback(
    async (data: CreateAgentRequest): Promise<Agent | null> => {
      try {
        const api = getApiClient(port);
        const agent = await api.createAgent(data);
        await loadAgents(); // 刷新列表
        return agent;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '创建 Agent 失败';
        setError(errorMessage);
        console.error('Failed to create agent:', err);
        return null;
      }
    },
    [port, loadAgents]
  );

  // 更新 Agent
  const updateAgent = useCallback(
    async (id: string, data: UpdateAgentRequest): Promise<Agent | null> => {
      try {
        const api = getApiClient(port);
        const agent = await api.updateAgent(id, data);
        await loadAgents(); // 刷新列表
        return agent;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '更新 Agent 失败';
        setError(errorMessage);
        console.error('Failed to update agent:', err);
        return null;
      }
    },
    [port, loadAgents]
  );

  // 删除 Agent
  const deleteAgent = useCallback(
    async (id: string): Promise<boolean> => {
      try {
        const api = getApiClient(port);
        await api.deleteAgent(id);
        await loadAgents(); // 刷新列表
        return true;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '删除 Agent 失败';
        setError(errorMessage);
        console.error('Failed to delete agent:', err);
        return false;
      }
    },
    [port, loadAgents]
  );

  // 激活 Agent (设为默认)
  const activateAgent = useCallback(
    async (id: string): Promise<boolean> => {
      try {
        const api = getApiClient(port);
        await api.activateAgent(id);
        await loadAgents(); // 刷新列表
        return true;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '激活 Agent 失败';
        setError(errorMessage);
        console.error('Failed to activate agent:', err);
        return false;
      }
    },
    [port, loadAgents]
  );

  // 禁用 Agent
  const deactivateAgent = useCallback(
    async (id: string): Promise<boolean> => {
      try {
        const api = getApiClient(port);
        await api.deactivateAgent(id);
        await loadAgents(); // 刷新列表
        return true;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '禁用 Agent 失败';
        setError(errorMessage);
        console.error('Failed to deactivate agent:', err);
        return false;
      }
    },
    [port, loadAgents]
  );

  // 初始加载
  useEffect(() => {
    loadAgents();
  }, [loadAgents]);

  return {
    agents,
    isLoading,
    error,
    loadAgents,
    createAgent,
    updateAgent,
    deleteAgent,
    activateAgent,
    deactivateAgent,
  };
}

export default useAgents;
