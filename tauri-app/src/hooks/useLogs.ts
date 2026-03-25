/**
 * useLogs Hook
 *
 * Provides log management functionality:
 * - Session logs (from SessionArchiveManager)
 * - System logs (from SystemLogCollector)
 * - Real-time log streaming via SSE
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { getApiClient } from '../lib/api';
import type {
  SystemLogEntry,
  SessionLogInfo,
  SessionLogDetail,
  LogSearchResult,
  LogStats,
  LogCategory,
  LogLevel,
} from '../types';

export interface UseLogsReturn {
  // State
  sessionLogs: SessionLogInfo[];
  systemLogs: SystemLogEntry[];
  selectedSession: SessionLogDetail | null;
  stats: LogStats | null;
  isLoading: boolean;
  error: string | null;
  isLive: boolean;

  // Actions
  loadSessionLogs: (date?: string, project?: string, channel?: string) => Promise<void>;
  loadSessionDetail: (sessionId: string) => Promise<void>;
  loadSystemLogs: (level?: LogLevel | 'all', category?: LogCategory | 'all', date?: string, search?: string) => Promise<void>;
  searchSessions: (query: string, tool?: string) => Promise<LogSearchResult[]>;
  loadStats: () => Promise<void>;
  toggleLive: () => void;
  clearSelection: () => void;
  refresh: () => Promise<void>;
}

export function useLogs(port?: number): UseLogsReturn {
  const [sessionLogs, setSessionLogs] = useState<SessionLogInfo[]>([]);
  const [systemLogs, setSystemLogs] = useState<SystemLogEntry[]>([]);
  const [selectedSession, setSelectedSession] = useState<SessionLogDetail | null>(null);
  const [stats, setStats] = useState<LogStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLive, setIsLive] = useState(false);

  const eventSourceRef = useRef<EventSource | null>(null);

  // Load session logs
  const loadSessionLogs = useCallback(async (
    date?: string,
    project?: string,
    channel?: string
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const api = getApiClient(port);
      const data = await api.getSessionLogs(date, project, channel);
      setSessionLogs(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load session logs';
      setError(errorMessage);
      console.error('Failed to load session logs:', err);
    } finally {
      setIsLoading(false);
    }
  }, [port]);

  // Load session detail
  const loadSessionDetail = useCallback(async (sessionId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const api = getApiClient(port);
      const data = await api.getSessionDetail(sessionId);
      setSelectedSession(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load session detail';
      setError(errorMessage);
      console.error('Failed to load session detail:', err);
    } finally {
      setIsLoading(false);
    }
  }, [port]);

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

  // Search sessions
  const searchSessions = useCallback(async (
    query: string,
    tool?: string
  ): Promise<LogSearchResult[]> => {
    try {
      const api = getApiClient(port);
      return api.searchSessionLogs(query, tool);
    } catch (err) {
      console.error('Failed to search sessions:', err);
      return [];
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

  // Clear selection
  const clearSelection = useCallback(() => {
    setSelectedSession(null);
  }, []);

  // Refresh all data
  const refresh = useCallback(async () => {
    await Promise.all([
      loadStats(),
    ]);
  }, [loadStats]);

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
  }, [loadStats]);

  return {
    sessionLogs,
    systemLogs,
    selectedSession,
    stats,
    isLoading,
    error,
    isLive,
    loadSessionLogs,
    loadSessionDetail,
    loadSystemLogs,
    searchSessions,
    loadStats,
    toggleLive,
    clearSelection,
    refresh,
  };
}

export default useLogs;
