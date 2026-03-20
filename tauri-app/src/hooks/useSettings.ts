/**
 * useSettings Hook
 *
 * 提供配置加载、保存和状态管理
 */

import { useState, useCallback, useEffect } from 'react';
import { getApiClient } from '../lib/api';
import type { Settings, LLMSettings, ProviderSettings } from '../types';

export interface UseSettingsReturn {
  settings: Settings | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  loadSettings: () => Promise<void>;
  saveSettings: (settings: Partial<Settings>) => Promise<boolean>;
  updateLLMSettings: (llm: Partial<LLMSettings>) => Promise<boolean>;
  updateProviderSettings: (name: string, provider: Partial<ProviderSettings>) => Promise<boolean>;
  resetToDefaults: () => Promise<void>;
}

const DEFAULT_SETTINGS: Settings = {
  llm: {
    model: 'gpt-4o',
    temperature: 0.7,
    max_tokens: 4096,
    stream: true,
  },
  providers: {},
};

export function useSettings(port?: number): UseSettingsReturn {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 加载配置
  const loadSettings = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const api = getApiClient(port);
      const data = await api.getConfig();
      setSettings(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '加载配置失败';
      setError(errorMessage);
      console.error('Failed to load settings:', err);
    } finally {
      setIsLoading(false);
    }
  }, [port]);

  // 保存配置
  const saveSettings = useCallback(
    async (newSettings: Partial<Settings>): Promise<boolean> => {
      setIsSaving(true);
      setError(null);

      try {
        const api = getApiClient(port);
        await api.updateConfig(newSettings);

        // 更新本地状态
        setSettings((prev) => ({
          ...prev,
          ...newSettings,
        } as Settings));

        return true;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '保存配置失败';
        setError(errorMessage);
        console.error('Failed to save settings:', err);
        return false;
      } finally {
        setIsSaving(false);
      }
    },
    [port]
  );

  // 更新 LLM 配置
  const updateLLMSettings = useCallback(
    async (llm: Partial<LLMSettings>): Promise<boolean> => {
      return saveSettings({
        llm: {
          ...settings?.llm,
          ...llm,
        } as LLMSettings,
      });
    },
    [saveSettings, settings?.llm]
  );

  // 更新 Provider 配置
  const updateProviderSettings = useCallback(
    async (name: string, provider: Partial<ProviderSettings>): Promise<boolean> => {
      const existingProvider = settings?.providers?.[name];
      const newProvider: ProviderSettings = {
        name,
        ...existingProvider,
        ...provider,
      };
      return saveSettings({
        providers: {
          ...settings?.providers,
          [name]: newProvider,
        },
      });
    },
    [saveSettings, settings?.providers]
  );

  // 重置为默认值
  const resetToDefaults = useCallback(async () => {
    setSettings(DEFAULT_SETTINGS);
    await saveSettings(DEFAULT_SETTINGS);
  }, [saveSettings]);

  // 初始加载
  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  return {
    settings,
    isLoading,
    isSaving,
    error,
    loadSettings,
    saveSettings,
    updateLLMSettings,
    updateProviderSettings,
    resetToDefaults,
  };
}

export default useSettings;
