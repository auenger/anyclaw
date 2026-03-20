/**
 * useTasks Hook
 *
 * 提供任务加载、实时更新和操作处理
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { getApiClient } from '../lib/api';
import type { SubAgent, CronTask } from '../types';

export interface UseTasksReturn {
  subAgents: SubAgent[];
  crons: CronTask[];
  isLoading: boolean;
  error: string | null;
  loadTasks: () => Promise<void>;
  cancelSubAgent: (id: string) => Promise<boolean>;
  toggleCron: (id: string, enabled: boolean) => Promise<boolean>;
  startPolling: (interval?: number) => void;
  stopPolling: () => void;
}

export function useTasks(port?: number): UseTasksReturn {
  const [subAgents, setSubAgents] = useState<SubAgent[]>([]);
  const [crons, setCrons] = useState<CronTask[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pollingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // 加载任务列表
  const loadTasks = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const api = getApiClient(port);
      const data = await api.listTasks();
      setSubAgents(data.subagents || []);
      setCrons(data.crons || []);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '加载任务失败';
      setError(errorMessage);
      console.error('Failed to load tasks:', err);
    } finally {
      setIsLoading(false);
    }
  }, [port]);

  // 取消 SubAgent
  const cancelSubAgent = useCallback(
    async (id: string): Promise<boolean> => {
      try {
        const api = getApiClient(port);
        await api.cancelSubAgent(id);
        await loadTasks(); // 重新加载
        return true;
      } catch (err) {
        console.error('Failed to cancel subagent:', err);
        return false;
      }
    },
    [port, loadTasks]
  );

  // 切换 Cron 状态
  const toggleCron = useCallback(
    async (id: string, enabled: boolean): Promise<boolean> => {
      try {
        const api = getApiClient(port);
        await api.toggleCron(id, enabled);
        await loadTasks(); // 重新加载
        return true;
      } catch (err) {
        console.error('Failed to toggle cron:', err);
        return false;
      }
    },
    [port, loadTasks]
  );

  // 开始轮询
  const startPolling = useCallback(
    (interval = 5000) => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }

      pollingIntervalRef.current = setInterval(() => {
        loadTasks();
      }, interval);
    },
    [loadTasks]
  );

  // 停止轮询
  const stopPolling = useCallback(() => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  }, []);

  // 初始加载
  useEffect(() => {
    loadTasks();

    return () => {
      stopPolling();
    };
  }, [loadTasks, stopPolling]);

  return {
    subAgents,
    crons,
    isLoading,
    error,
    loadTasks,
    cancelSubAgent,
    toggleCron,
    startPolling,
    stopPolling,
  };
}

export default useTasks;
