/**
 * 数字字段组件
 */

import { Input } from '@/components/ui/input'
import { Slider } from '@/components/ui/slider'
import { cn } from '@/lib/utils'
import type { ConfigFieldSchema } from '@/types/config'

interface NumberFieldProps {
  field: ConfigFieldSchema
  value: number
  error?: string
  onChange: (value: number) => void
  disabled?: boolean
}

export function NumberField({ field, value, error, onChange, disabled }: NumberFieldProps) {
  const min = field.validation?.min ?? 0
  const max = field.validation?.max ?? 100
  const useSlider = max - min <= 100 && field.validation?.min !== undefined

  const handleChange = (newValue: number) => {
    if (field.validation) {
      newValue = Math.max(min, Math.min(max, newValue))
    }
    onChange(newValue)
  }

  if (useSlider) {
    return (
      <div className="space-y-2">
        <div className="flex items-center gap-4">
          <Slider
            value={[value ?? min]}
            min={min}
            max={max}
            step={max <= 10 ? 1 : max <= 100 ? 1 : 10}
            onValueChange={([v]) => handleChange(v)}
            disabled={disabled || field.disabled}
            className="flex-1"
          />
          <span className="w-12 text-sm text-right tabular-nums">{value ?? min}</span>
        </div>
        {error && <p className="text-xs text-destructive">{error}</p>}
      </div>
    )
  }

  return (
    <div className="space-y-1.5">
      <Input
        type="number"
        value={value ?? ''}
        onChange={(e) => handleChange(Number(e.target.value))}
        placeholder={field.placeholder}
        disabled={disabled || field.disabled}
        min={field.validation?.min}
        max={field.validation?.max}
        className={cn(error && 'border-destructive')}
      />
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  )
}
