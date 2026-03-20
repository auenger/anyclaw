/**
 * SettingsPage Component
 *
 * 设置页面：LLM 配置、Provider 配置
 */

import { useState, useEffect } from 'react';
import { Save, RotateCcw, Check, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { LLMSettings } from './LLMSettings';
import { ProviderSettings } from './ProviderSettings';
import { useSettings } from '../../hooks/useSettings';
import { cn } from '../../lib/utils';
import type { LLMSettings as LLMSettingsType, ProviderSettings as ProviderSettingsType } from '../../types';

export interface SettingsPageProps {
  port?: number;
  className?: string;
}

export function SettingsPage({ port, className }: SettingsPageProps) {
  const {
    settings,
    isLoading,
    isSaving,
    error,
    saveSettings,
    resetToDefaults,
  } = useSettings(port);

  const [localLLM, setLocalLLM] = useState<LLMSettingsType | null>(null);
  const [localProviders, setLocalProviders] = useState<Record<string, ProviderSettingsType>>({});
  const [saveSuccess, setSaveSuccess] = useState(false);

  // 同步本地状态
  useEffect(() => {
    if (settings) {
      setLocalLLM(settings.llm);
      setLocalProviders(settings.providers || {});
    }
  }, [settings]);

  // 处理 LLM 配置变更
  const handleLLMChange = (llm: Partial<LLMSettingsType>) => {
    setLocalLLM((prev) => ({ ...prev, ...llm } as LLMSettingsType));
    setSaveSuccess(false);
  };

  // 处理 Provider 配置变更
  const handleProviderChange = (name: string, provider: Partial<ProviderSettingsType>) => {
    setLocalProviders((prev) => ({
      ...prev,
      [name]: { ...prev[name], ...provider } as ProviderSettingsType,
    }));
    setSaveSuccess(false);
  };

  // 保存所有配置
  const handleSave = async () => {
    if (!localLLM) return;

    const success = await saveSettings({
      llm: localLLM,
      providers: localProviders,
    });

    if (success) {
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    }
  };

  // 重置为默认值
  const handleReset = async () => {
    if (window.confirm('确定要重置所有设置为默认值吗？')) {
      await resetToDefaults();
      setSaveSuccess(false);
    }
  };

  // 测试 Provider 连接
  const testProviderConnection = async (_name: string): Promise<boolean> => {
    // TODO: 实现实际的连接测试
    // 目前只是模拟
    return new Promise((resolve) => {
      setTimeout(() => resolve(true), 1000);
    });
  };

  if (isLoading) {
    return (
      <div className={cn('flex items-center justify-center h-64', className)}>
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className={cn('p-6 max-w-4xl mx-auto', className)}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">设置</h1>
          <p className="text-muted-foreground">配置 LLM 和 Provider 设置</p>
        </div>

        <div className="flex items-center gap-2">
          {saveSuccess && (
            <span className="flex items-center text-sm text-green-600 mr-2">
              <Check className="h-4 w-4 mr-1" />
              已保存
            </span>
          )}

          {error && (
            <span className="flex items-center text-sm text-red-600 mr-2">
              <AlertCircle className="h-4 w-4 mr-1" />
              {error}
            </span>
          )}

          <Button variant="outline" onClick={handleReset} disabled={isSaving}>
            <RotateCcw className="h-4 w-4 mr-2" />
            重置
          </Button>

          <Button onClick={handleSave} disabled={isSaving || !localLLM}>
            {isSaving ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                保存中...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                保存
              </>
            )}
          </Button>
        </div>
      </div>

      <Tabs defaultValue="llm" className="space-y-4">
        <TabsList>
          <TabsTrigger value="llm">LLM 配置</TabsTrigger>
          <TabsTrigger value="providers">Provider 配置</TabsTrigger>
        </TabsList>

        <TabsContent value="llm">
          <Card>
            <CardHeader>
              <CardTitle>LLM 配置</CardTitle>
              <CardDescription>配置语言模型的参数</CardDescription>
            </CardHeader>
            <CardContent>
              {localLLM && (
                <LLMSettings
                  settings={localLLM}
                  onChange={handleLLMChange}
                  disabled={isSaving}
                />
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="providers">
          <div className="space-y-4">
            {Object.entries(localProviders).map(([name, provider]) => (
              <Card key={name}>
                <CardHeader>
                  <CardTitle className="text-lg">{name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <ProviderSettings
                    name={name}
                    settings={provider}
                    onChange={(p) => handleProviderChange(name, p)}
                    onTest={() => testProviderConnection(name)}
                    disabled={isSaving}
                  />
                </CardContent>
              </Card>
            ))}

            {/* 默认显示常用 Provider */}
            {!localProviders.openai && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">OpenAI</CardTitle>
                </CardHeader>
                <CardContent>
                  <ProviderSettings
                    name="openai"
                    settings={localProviders.openai || { name: 'openai' }}
                    onChange={(p) => handleProviderChange('openai', p)}
                    onTest={() => testProviderConnection('openai')}
                    disabled={isSaving}
                  />
                </CardContent>
              </Card>
            )}

            {!localProviders.anthropic && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Anthropic</CardTitle>
                </CardHeader>
                <CardContent>
                  <ProviderSettings
                    name="anthropic"
                    settings={localProviders.anthropic || { name: 'anthropic' }}
                    onChange={(p) => handleProviderChange('anthropic', p)}
                    onTest={() => testProviderConnection('anthropic')}
                    disabled={isSaving}
                  />
                </CardContent>
              </Card>
            )}

            {!localProviders.zai && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">ZAI/GLM</CardTitle>
                </CardHeader>
                <CardContent>
                  <ProviderSettings
                    name="zai"
                    settings={localProviders.zai || { name: 'zai' }}
                    onChange={(p) => handleProviderChange('zai', p)}
                    onTest={() => testProviderConnection('zai')}
                    disabled={isSaving}
                  />
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default SettingsPage;
