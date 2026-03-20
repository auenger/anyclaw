/**
 * useSkills Hook
 *
 * 提供技能加载、搜索和重载功能
 */

import { useState, useCallback, useEffect, useMemo } from 'react';
import { getApiClient } from '../lib/api';
import type { Skill } from '../types';

export interface UseSkillsReturn {
  skills: Skill[];
  filteredSkills: Skill[];
  isLoading: boolean;
  isReloading: boolean;
  error: string | null;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  loadSkills: () => Promise<void>;
  reloadSkill: (id: string) => Promise<boolean>;
  reloadAllSkills: () => Promise<boolean>;
}

export function useSkills(port?: number): UseSkillsReturn {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isReloading, setIsReloading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // 加载技能列表
  const loadSkills = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const api = getApiClient(port);
      const data = await api.listSkills();
      setSkills(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '加载技能失败';
      setError(errorMessage);
      console.error('Failed to load skills:', err);
    } finally {
      setIsLoading(false);
    }
  }, [port]);

  // 重载单个技能
  const reloadSkill = useCallback(
    async (id: string): Promise<boolean> => {
      setIsReloading(true);

      try {
        const api = getApiClient(port);
        await api.reloadSkill(id);
        await loadSkills(); // 重新加载列表
        return true;
      } catch (err) {
        console.error('Failed to reload skill:', err);
        return false;
      } finally {
        setIsReloading(false);
      }
    },
    [port, loadSkills]
  );

  // 重载所有技能
  const reloadAllSkills = useCallback(async (): Promise<boolean> => {
    setIsReloading(true);

    try {
      const api = getApiClient(port);
      await api.reloadAllSkills();
      await loadSkills(); // 重新加载列表
      return true;
    } catch (err) {
      console.error('Failed to reload all skills:', err);
      return false;
    } finally {
      setIsReloading(false);
    }
  }, [port, loadSkills]);

  // 过滤技能
  const filteredSkills = useMemo(() => {
    if (!searchQuery.trim()) {
      return skills;
    }

    const query = searchQuery.toLowerCase();
    return skills.filter(
      (skill) =>
        skill.name.toLowerCase().includes(query) ||
        skill.description.toLowerCase().includes(query) ||
        skill.tags?.some((tag) => tag.toLowerCase().includes(query))
    );
  }, [skills, searchQuery]);

  // 初始加载
  useEffect(() => {
    loadSkills();
  }, [loadSkills]);

  return {
    skills,
    filteredSkills,
    isLoading,
    isReloading,
    error,
    searchQuery,
    setSearchQuery,
    loadSkills,
    reloadSkill,
    reloadAllSkills,
  };
}

export default useSkills;
