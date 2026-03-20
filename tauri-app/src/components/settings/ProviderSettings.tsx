/**
 * ProviderSettings Component
 *
 * Provider 配置组件：API Key、Endpoint、连接测试
 */

import { useState } from 'react';
import { Eye, EyeOff, Check, X, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';
import type { ProviderSettings as ProviderSettingsType } from '../../types';

export interface ProviderSettingsProps {
  name: string;
  settings: ProviderSettingsType;
  onChange: (settings: Partial<ProviderSettingsType>) => void;
  onTest?: () => Promise<boolean>;
  disabled?: boolean;
  className?: string;
}

export function ProviderSettings({
  name,
  settings,
  onChange,
  onTest,
  disabled = false,
  className,
}: ProviderSettingsProps) {
  const [showApiKey, setShowApiKey] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<'success' | 'error' | null>(null);

  const handleApiKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ api_key: e.target.value });
    setTestResult(null);
  };

  const handleBaseUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ base_url: e.target.value });
    setTestResult(null);
  };

  const handleTest = async () => {
    if (!onTest) return;

    setIsTesting(true);
    setTestResult(null);

    try {
      const success = await onTest();
      setTestResult(success ? 'success' : 'error');
    } catch {
      setTestResult('error');
    } finally {
      setIsTesting(false);
    }
  };

  const providerLabel = name.charAt(0).toUpperCase() + name.slice(1);

  return (
    <div className={cn('space-y-4 p-4 border rounded-lg', className)}>
      <div className="flex items-center justify-between">
        <h4 className="font-medium">{providerLabel}</h4>
        {settings.api_key && (
          <Badge variant="outline" className="text-xs">
            已配置
          </Badge>
        )}
      </div>

      {/* API Key */}
      <div className="space-y-2">
        <Label htmlFor={`${name}-api-key`}>API Key</Label>
        <div className="relative">
          <Input
            id={`${name}-api-key`}
            type={showApiKey ? 'text' : 'password'}
            value={settings.api_key || ''}
            onChange={handleApiKeyChange}
            placeholder={`输入 ${providerLabel} API Key`}
            disabled={disabled}
            className="pr-20"
          />
          <button
            type="button"
            onClick={() => setShowApiKey(!showApiKey)}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            {showApiKey ? (
              <EyeOff className="h-4 w-4" />
            ) : (
              <Eye className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>

      {/* Base URL (可选) */}
      <div className="space-y-2">
        <Label htmlFor={`${name}-base-url`}>
          Base URL <span className="text-muted-foreground">(可选)</span>
        </Label>
        <Input
          id={`${name}-base-url`}
          type="url"
          value={settings.base_url || ''}
          onChange={handleBaseUrlChange}
          placeholder="自定义 API 端点"
          disabled={disabled}
        />
      </div>

      {/* 测试按钮 */}
      {onTest && (
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleTest}
            disabled={disabled || isTesting || !settings.api_key}
          >
            {isTesting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                测试中...
              </>
            ) : (
              '测试连接'
            )}
          </Button>

          {testResult === 'success' && (
            <span className="flex items-center text-sm text-green-600">
              <Check className="h-4 w-4 mr-1" />
              连接成功
            </span>
          )}

          {testResult === 'error' && (
            <span className="flex items-center text-sm text-red-600">
              <X className="h-4 w-4 mr-1" />
              连接失败
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export default ProviderSettings;
