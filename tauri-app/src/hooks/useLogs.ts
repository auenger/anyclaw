/**
 * useLogs Hook
 *
 * Provides system log management functionality:
 * - System logs (from SystemLogCollector)
 * - Available dates for historical log viewing
 * - Real-time log streaming via SSE
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { getApiClient } from '../lib/api';
import type {
  SystemLogEntry,
  LogStats,
  LogCategory,
  LogLevel,
} from '../types';

export interface UseLogsReturn {
  // State
  systemLogs: SystemLogEntry[];
  availableDates: string[];
  stats: LogStats | null;
  isLoading: boolean;
  error: string | null;
  isLive: boolean;

  // Actions
  loadSystemLogs: (level?: LogLevel | 'all', category?: LogCategory | 'all', date?: string, search?: string) => Promise<void>;
  loadAvailableDates: () => Promise<void>;
  loadStats: () => Promise<void>;
  toggleLive: () => void;
  refresh: () => Promise<void>;
}

export function useLogs(port?: number): UseLogsReturn {
  const [systemLogs, setSystemLogs] = useState<SystemLogEntry[]>([]);
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [stats, setStats] = useState<LogStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLive, setIsLive] = useState(false);

  const eventSourceRef = useRef<EventSource | null>(null);

  // Load system logs
  const loadSystemLogs = useCallback(async (
    level?: LogLevel | 'all',
    category?: LogCategory | 'all',
    date?: string,
    search?: string
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const api = getApiClient(port);
      const data = await api.getSystemLogs(level, category, date, search);
      setSystemLogs(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load system logs';
      setError(errorMessage);
      console.error('Failed to load system logs:', err);
    } finally {
      setIsLoading(false);
    }
  }, [port]);

  // Load available dates
  const loadAvailableDates = useCallback(async () => {
    try {
      const api = getApiClient(port);
      const data = await api.getAvailableDates();
      setAvailableDates(data);
    } catch (err) {
      console.error('Failed to load available dates:', err);
    }
  }, [port]);

  // Load stats
  const loadStats = useCallback(async () => {
    try {
      const api = getApiClient(port);
      const data = await api.getLogStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load log stats:', err);
    }
  }, [port]);

  // Toggle live mode
  const toggleLive = useCallback(() => {
    setIsLive((prev) => !prev);
  }, []);

  // Refresh all data
  const refresh = useCallback(async () => {
    await Promise.all([
      loadStats(),
      loadAvailableDates(),
    ]);
  }, [loadStats, loadAvailableDates]);

  // Handle SSE connection for live logs
  useEffect(() => {
    if (isLive) {
      const api = getApiClient(port);
      const url = api.getLogStreamUrl();

      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onmessage = (event) => {
        try {
          const entry: SystemLogEntry = JSON.parse(event.data);
          setSystemLogs((prev) => {
            // Keep last 200 entries
            const newLogs = [...prev, entry];
            return newLogs.slice(-200);
          });
        } catch {
          // Ignore parse errors
        }
      };

      eventSource.onerror = () => {
        console.error('SSE connection error');
        eventSource.close();
        setIsLive(false);
      };

      return () => {
        eventSource.close();
        eventSourceRef.current = null;
      };
    } else if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, [isLive, port]);

  // Initial load
  useEffect(() => {
    loadStats();
    loadAvailableDates();
  }, [loadStats, loadAvailableDates]);

  return {
    systemLogs,
    availableDates,
    stats,
    isLoading,
    error,
    isLive,
    loadSystemLogs,
    loadAvailableDates,
    loadStats,
    toggleLive,
    refresh,
  };
}

export default useLogs;
