/**
 * useMemory Hook
 *
 * Provides memory management functionality:
 * - List memories (global + agent-level)
 * - Load/save memory content
 * - Daily logs management
 * - Search across memories
 */

import { useState, useCallback, useEffect } from 'react';
import { getApiClient } from '../lib/api';
import type { MemoryInfo, DailyLogInfo, MemoryStats, SearchResponse } from '../types';

export interface UseMemoryReturn {
  // State
  memories: MemoryInfo[];
  selectedMemory: MemoryInfo | null;
  content: string;
  dailyLogs: DailyLogInfo[];
  stats: MemoryStats | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;

  // Actions
  selectMemory: (memoryId: string) => Promise<void>;
  loadContent: () => Promise<void>;
  saveContent: (content: string) => Promise<boolean>;
  loadDailyLogs: (days?: number) => Promise<void>;
  loadStats: () => Promise<void>;
  search: (keyword: string, memoryId?: string) => Promise<SearchResponse>;
  refresh: () => Promise<void>;
}

export function useMemory(port?: number): UseMemoryReturn {
  const [memories, setMemories] = useState<MemoryInfo[]>([]);
  const [selectedMemory, setSelectedMemory] = useState<MemoryInfo | null>(null);
  const [content, setContent] = useState('');
  const [dailyLogs, setDailyLogs] = useState<DailyLogInfo[]>([]);
  const [stats, setStats] = useState<MemoryStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load memory list
  const loadMemories = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const api = getApiClient(port);
      const data = await api.listMemories();
      setMemories(data);

      // Auto-select global memory if no memory selected
      if (!selectedMemory && data.length > 0) {
        const globalMemory = data.find((m: MemoryInfo) => m.is_global);
        if (globalMemory) {
          setSelectedMemory(globalMemory);
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load memories';
      setError(errorMessage);
      console.error('Failed to load memories:', err);
    } finally {
      setIsLoading(false);
    }
  }, [port, selectedMemory]);

  // Select a memory
  const selectMemory = useCallback(async (memoryId: string) => {
    const memory = memories.find((m) => m.id === memoryId);
    if (memory) {
      setSelectedMemory(memory);
      setContent('');
      setDailyLogs([]);
      setStats(null);
    }
  }, [memories]);

  // Load memory content
  const loadContent = useCallback(async () => {
    if (!selectedMemory) return;

    setIsLoading(true);
    setError(null);

    try {
      const api = getApiClient(port);
      const data = await api.getMemory(selectedMemory.id);
      setContent(data.content);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load memory content';
      setError(errorMessage);
      console.error('Failed to load memory content:', err);
    } finally {
      setIsLoading(false);
    }
  }, [port, selectedMemory]);

  // Save memory content
  const saveContent = useCallback(async (newContent: string): Promise<boolean> => {
    if (!selectedMemory) return false;

    setIsSaving(true);
    setError(null);

    try {
      const api = getApiClient(port);
      await api.updateMemory(selectedMemory.id, newContent);
      setContent(newContent);

      // Update memory info with new char count
      setMemories((prev) =>
        prev.map((m) =>
          m.id === selectedMemory.id
            ? { ...m, char_count: newContent.length, exists: true }
            : m
        )
      );

      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save memory';
      setError(errorMessage);
      console.error('Failed to save memory:', err);
      return false;
    } finally {
      setIsSaving(false);
    }
  }, [port, selectedMemory]);

  // Load daily logs
  const loadDailyLogs = useCallback(async (days: number = 7) => {
    if (!selectedMemory) return;

    try {
      const api = getApiClient(port);
      const data = await api.getDailyLogs(selectedMemory.id, days);
      setDailyLogs(data);
    } catch (err) {
      console.error('Failed to load daily logs:', err);
      setDailyLogs([]);
    }
  }, [port, selectedMemory]);

  // Load stats
  const loadStats = useCallback(async () => {
    if (!selectedMemory) return;

    try {
      const api = getApiClient(port);
      const data = await api.getMemoryStats(selectedMemory.id);
      setStats(data);
    } catch (err) {
      console.error('Failed to load memory stats:', err);
    }
  }, [port, selectedMemory]);

  // Search memories
  const search = useCallback(
    async (keyword: string, memoryId?: string): Promise<SearchResponse> => {
      const api = getApiClient(port);
      return api.searchMemory(keyword, memoryId);
    },
    [port]
  );

  // Refresh all data
  const refresh = useCallback(async () => {
    await loadMemories();
    if (selectedMemory) {
      await loadContent();
      await loadDailyLogs();
      await loadStats();
    }
  }, [loadMemories, selectedMemory, loadContent, loadDailyLogs, loadStats]);

  // Initial load
  useEffect(() => {
    loadMemories();
  }, [loadMemories]);

  // Load content when memory is selected
  useEffect(() => {
    if (selectedMemory) {
      loadContent();
      loadDailyLogs();
      loadStats();
    }
  }, [selectedMemory, loadContent, loadDailyLogs, loadStats]);

  return {
    memories,
    selectedMemory,
    content,
    dailyLogs,
    stats,
    isLoading,
    isSaving,
    error,
    selectMemory,
    loadContent,
    saveContent,
    loadDailyLogs,
    loadStats,
    search,
    refresh,
  };
}

export default useMemory;
