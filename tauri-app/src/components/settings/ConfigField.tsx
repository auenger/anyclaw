/**
 * 配置字段渲染器
 * 根据字段类型动态渲染对应的组件
 */

import { HelpCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useI18n } from '@/i18n'
import type { ConfigFieldSchema, ConfigValue } from '@/types/config'
import { StringField } from './fields/StringField'
import { NumberField } from './fields/NumberField'
import { BooleanField } from './fields/BooleanField'
import { EnumField } from './fields/EnumField'
import { ArrayField } from './fields/ArrayField'

interface ConfigFieldProps {
  field: ConfigFieldSchema
  value: ConfigValue
  error?: string
  onChange: (value: ConfigValue) => void
  disabled?: boolean
  allValues?: Record<string, ConfigValue>
}

export function ConfigField({
  field,
  value,
  error,
  onChange,
  disabled,
  allValues,
}: ConfigFieldProps) {
  const { t } = useI18n()

  // 条件显示检查
  if (field.condition && allValues) {
    const { field: condField, value: condValue, operator = 'eq' } = field.condition
    const actualValue = getNestedValue(allValues, condField)

    let show = false
    switch (operator) {
      case 'eq':
        show = actualValue === condValue
        break
      case 'neq':
        show = actualValue !== condValue
        break
      case 'in':
        show = Array.isArray(condValue) && condValue.includes(actualValue)
        break
      case 'contains':
        show = String(actualValue).includes(String(condValue))
        break
    }

    if (!show) {
      return null
    }
  }

  // 获取标签和描述 - 使用类型安全的方式
  const config = t.config as Record<string, string>
  const label = config[field.label] || field.label
  const description = field.description ? (config[field.description] || field.description) : null

  // 渲染字段组件
  const renderFieldComponent = () => {
    switch (field.type) {
      case 'string':
        return (
          <StringField
            field={field}
            value={value as string}
            error={error}
            onChange={(v) => onChange(v)}
            disabled={disabled}
          />
        )

      case 'number':
        return (
          <NumberField
            field={field}
            value={value as number}
            error={error}
            onChange={(v) => onChange(v)}
            disabled={disabled}
          />
        )

      case 'boolean':
        return (
          <BooleanField
            field={field}
            value={value as boolean}
            onChange={(v) => onChange(v)}
            disabled={disabled}
          />
        )

      case 'enum':
        return (
          <EnumField
            field={field}
            value={value as string}
            error={error}
            onChange={(v) => onChange(v)}
            disabled={disabled}
          />
        )

      case 'array':
        return (
          <ArrayField
            field={field}
            value={value as string[]}
            error={error}
            onChange={(v) => onChange(v)}
            disabled={disabled}
          />
        )

      default:
        return (
          <StringField
            field={field}
            value={String(value ?? '')}
            error={error}
            onChange={(v) => onChange(v)}
            disabled={disabled}
          />
        )
    }
  }

  return (
    <div className={cn('space-y-1', field.advanced && 'opacity-75')}>
      {/* Label */}
      <div className="flex items-center gap-1.5">
        <label className="text-sm font-medium">{label}</label>
        {field.required && <span className="text-destructive">*</span>}
        {field.advanced && (
          <span className="text-xs text-muted-foreground">(Advanced)</span>
        )}
        {description && (
          <span className="relative group">
            <HelpCircle className="h-3.5 w-3.5 text-muted-foreground cursor-help" />
            <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-2 py-1 bg-popover text-popover-foreground text-xs rounded shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-10">
              {description}
            </div>
          </span>
        )}
      </div>

      {/* Field Component */}
      {renderFieldComponent()}
    </div>
  )
}

// 辅助函数：获取嵌套值
function getNestedValue(obj: Record<string, any>, path: string): any {
  const parts = path.split('.')
  let current = obj

  for (const part of parts) {
    if (current === null || current === undefined) return undefined
    current = current[part]
  }

  return current
}
