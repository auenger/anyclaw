/**
 * LLMSettings Component
 *
 * LLM 配置组件：模型选择、Temperature、Max Tokens
 */

import { useState, useEffect } from 'react';
import { Slider } from '../ui/slider';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { cn } from '../../lib/utils';
import type { LLMSettings as LLMSettingsType } from '../../types';

export interface LLMSettingsProps {
  settings: LLMSettingsType;
  onChange: (settings: Partial<LLMSettingsType>) => void;
  disabled?: boolean;
  className?: string;
}

// 常用模型列表
const MODELS = [
  { value: 'gpt-4o', label: 'GPT-4o' },
  { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
  { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
  { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
  { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet' },
  { value: 'claude-3-opus-20240229', label: 'Claude 3 Opus' },
  { value: 'claude-3-haiku-20240307', label: 'Claude 3 Haiku' },
  { value: 'glm-4-plus', label: 'GLM-4 Plus' },
  { value: 'glm-4-flash', label: 'GLM-4 Flash' },
];

export function LLMSettings({
  settings,
  onChange,
  disabled = false,
  className,
}: LLMSettingsProps) {
  const [localSettings, setLocalSettings] = useState(settings);

  // 同步外部 settings
  useEffect(() => {
    setLocalSettings(settings);
  }, [settings]);

  const handleModelChange = (value: string) => {
    const newSettings = { ...localSettings, model: value };
    setLocalSettings(newSettings);
    onChange({ model: value });
  };

  const handleTemperatureChange = (value: number[]) => {
    const temp = value[0];
    const newSettings = { ...localSettings, temperature: temp };
    setLocalSettings(newSettings);
    onChange({ temperature: temp });
  };

  const handleMaxTokensChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value > 0) {
      const newSettings = { ...localSettings, max_tokens: value };
      setLocalSettings(newSettings);
      onChange({ max_tokens: value });
    }
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* 模型选择 */}
      <div className="space-y-2">
        <Label htmlFor="model">模型</Label>
        <Select
          value={localSettings.model}
          onValueChange={handleModelChange}
          disabled={disabled}
        >
          <SelectTrigger id="model">
            <SelectValue placeholder="选择模型" />
          </SelectTrigger>
          <SelectContent>
            {MODELS.map((model) => (
              <SelectItem key={model.value} value={model.value}>
                {model.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Temperature 滑块 */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="temperature">Temperature</Label>
          <span className="text-sm text-muted-foreground">
            {localSettings.temperature.toFixed(2)}
          </span>
        </div>
        <Slider
          id="temperature"
          min={0}
          max={2}
          step={0.1}
          value={[localSettings.temperature]}
          onValueChange={handleTemperatureChange}
          disabled={disabled}
        />
        <p className="text-xs text-muted-foreground">
          较低的值产生更一致的输出，较高的值产生更有创意的输出
        </p>
      </div>

      {/* Max Tokens */}
      <div className="space-y-2">
        <Label htmlFor="max-tokens">最大 Token 数</Label>
        <Input
          id="max-tokens"
          type="number"
          min={1}
          max={128000}
          value={localSettings.max_tokens}
          onChange={handleMaxTokensChange}
          disabled={disabled}
        />
        <p className="text-xs text-muted-foreground">
          限制生成的最大 token 数量
        </p>
      </div>
    </div>
  );
}

export default LLMSettings;
