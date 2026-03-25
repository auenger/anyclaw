/**
 * useCronJobs Hook
 *
 * Cron 任务管理的 React Hook
 */

import { useState, useEffect, useCallback } from 'react';
import { getApiClient } from '../lib/api';
import type { CronJob, CreateJobRequest, UpdateJobRequest, RunLog } from '../types';

export interface UseCronJobsResult {
  jobs: CronJob[];
  isLoading: boolean;
  error: string | null;
  loadJobs: () => Promise<void>;
  createJob: (data: CreateJobRequest) => Promise<CronJob | null>;
  updateJob: (id: string, data: UpdateJobRequest) => Promise<CronJob | null>;
  deleteJob: (id: string) => Promise<boolean>;
  cloneJob: (id: string) => Promise<CronJob | null>;
  runJob: (id: string) => Promise<boolean>;
  getJobLogs: (id: string, limit?: number) => Promise<RunLog[]>;
  toggleJob: (id: string, enabled: boolean) => Promise<CronJob | null>;
  startPolling: (intervalMs?: number) => void;
  stopPolling: () => void;
}

export function useCronJobs(port?: number): UseCronJobsResult {
  const [jobs, setJobs] = useState<CronJob[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pollingTimer, setPollingTimer] = useState<ReturnType<typeof setInterval> | null>(null);

  // 加载任务列表
  const loadJobs = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const client = getApiClient(port);
      const data = await client.getCronJobs();
      setJobs(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load cron jobs';
      setError(message);
      console.error('Failed to load cron jobs:', err);
    } finally {
      setIsLoading(false);
    }
  }, [port]);

  // 创建任务
  const createJob = useCallback(async (data: CreateJobRequest): Promise<CronJob | null> => {
    setError(null);
    try {
      const client = getApiClient(port);
      const job = await client.createCronJob(data);
      await loadJobs(); // 刷新列表
      return job;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create job';
      setError(message);
      console.error('Failed to create job:', err);
      return null;
    }
  }, [port, loadJobs]);

  // 更新任务
  const updateJob = useCallback(async (id: string, data: UpdateJobRequest): Promise<CronJob | null> => {
    setError(null);
    try {
      const client = getApiClient(port);
      const job = await client.updateCronJob(id, data);
      await loadJobs(); // 刷新列表
      return job;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update job';
      setError(message);
      console.error('Failed to update job:', err);
      return null;
    }
  }, [port, loadJobs]);

  // 删除任务
  const deleteJob = useCallback(async (id: string): Promise<boolean> => {
    setError(null);
    try {
      const client = getApiClient(port);
      await client.deleteCronJob(id);
      await loadJobs(); // 刷新列表
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete job';
      setError(message);
      console.error('Failed to delete job:', err);
      return false;
    }
  }, [port, loadJobs]);

  // 克隆任务
  const cloneJob = useCallback(async (id: string): Promise<CronJob | null> => {
    setError(null);
    try {
      const client = getApiClient(port);
      const job = await client.cloneCronJob(id);
      await loadJobs(); // 刷新列表
      return job;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to clone job';
      setError(message);
      console.error('Failed to clone job:', err);
      return null;
    }
  }, [port, loadJobs]);

  // 手动运行任务
  const runJob = useCallback(async (id: string): Promise<boolean> => {
    setError(null);
    try {
      const client = getApiClient(port);
      const result = await client.runCronJob(id);
      await loadJobs(); // 刷新列表以更新状态
      return result.success;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to run job';
      setError(message);
      console.error('Failed to run job:', err);
      return false;
    }
  }, [port, loadJobs]);

  // 获取任务执行日志
  const getJobLogs = useCallback(async (id: string, limit: number = 50): Promise<RunLog[]> => {
    try {
      const client = getApiClient(port);
      return await client.getCronJobLogs(id, limit);
    } catch (err) {
      console.error('Failed to get job logs:', err);
      return [];
    }
  }, [port]);

  // 切换任务启用状态
  const toggleJob = useCallback(async (id: string, enabled: boolean): Promise<CronJob | null> => {
    return updateJob(id, { enabled });
  }, [updateJob]);

  // 开始轮询
  const startPolling = useCallback((intervalMs: number = 5000) => {
    if (pollingTimer) {
      clearInterval(pollingTimer);
    }
    const timer = setInterval(loadJobs, intervalMs);
    setPollingTimer(timer);
  }, [loadJobs, pollingTimer]);

  // 停止轮询
  const stopPolling = useCallback(() => {
    if (pollingTimer) {
      clearInterval(pollingTimer);
      setPollingTimer(null);
    }
  }, [pollingTimer]);

  // 初始加载
  useEffect(() => {
    loadJobs();
  }, [loadJobs]);

  // 清理
  useEffect(() => {
    return () => {
      if (pollingTimer) {
        clearInterval(pollingTimer);
      }
    };
  }, [pollingTimer]);

  return {
    jobs,
    isLoading,
    error,
    loadJobs,
    createJob,
    updateJob,
    deleteJob,
    cloneJob,
    runJob,
    getJobLogs,
    toggleJob,
    startPolling,
    stopPolling,
  };
}

export default useCronJobs;
