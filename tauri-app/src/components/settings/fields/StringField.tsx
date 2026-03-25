/**
 * 字符串字段组件
 */

import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import type { ConfigFieldSchema } from '@/types/config'

interface StringFieldProps {
  field: ConfigFieldSchema
  value: string
  error?: string
  onChange: (value: string) => void
  disabled?: boolean
}

export function StringField({ field, value, error, onChange, disabled }: StringFieldProps) {
  return (
    <div className="space-y-1.5">
      <Input
        type={field.sensitive ? 'password' : 'text'}
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value)}
        placeholder={field.placeholder}
        disabled={disabled || field.disabled}
        className={cn(error && 'border-destructive')}
      />
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  )
}
