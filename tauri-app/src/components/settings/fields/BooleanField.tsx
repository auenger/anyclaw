/**
 * 布尔字段组件
 */

import { Switch } from '@/components/ui/switch'
import type { ConfigFieldSchema } from '@/types/config'

interface BooleanFieldProps {
  field: ConfigFieldSchema
  value: boolean
  onChange: (value: boolean) => void
  disabled?: boolean
}

export function BooleanField({ field, value, onChange, disabled }: BooleanFieldProps) {
  return (
    <div className="flex items-center justify-between">
      <Switch
        checked={value ?? false}
        onCheckedChange={onChange}
        disabled={disabled || field.disabled}
      />
    </div>
  )
}
