/**
 * 枚举字段组件
 */

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { cn } from '@/lib/utils'
import type { ConfigFieldSchema } from '@/types/config'

interface EnumFieldProps {
  field: ConfigFieldSchema
  value: string
  error?: string
  onChange: (value: string) => void
  disabled?: boolean
}

export function EnumField({ field, value, error, onChange, disabled }: EnumFieldProps) {
  const options = field.validation?.enum ?? []

  return (
    <div className="space-y-1.5">
      <Select
        value={value ?? ''}
        onValueChange={onChange}
        disabled={disabled || field.disabled}
      >
        <SelectTrigger className={cn(error && 'border-destructive')}>
          <SelectValue placeholder={field.placeholder} />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => (
            <SelectItem key={option} value={option}>
              {option}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  )
}
