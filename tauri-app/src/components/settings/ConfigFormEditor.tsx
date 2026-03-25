/**
 * 配置表单编辑器组件
 * 分组卡片布局，支持折叠
 */

import { ChevronDown, ChevronRight } from 'lucide-react'
import { useI18n } from '@/i18n'
import { configGroups } from '@/schemas/configSchema'
import { ConfigField } from './ConfigField'
import type { ConfigData, ConfigValue, ConfigGroupSchema } from '@/types/config'

interface ConfigFormEditorProps {
  values: ConfigData
  errors: Record<string, string>
  onChange: (key: string, value: ConfigValue) => void
  isGroupCollapsed: (groupId: string) => boolean
  toggleGroupCollapse: (groupId: string) => void
  showAdvanced: boolean
  disabled?: boolean
}

export function ConfigFormEditor({
  values,
  errors,
  onChange,
  isGroupCollapsed,
  toggleGroupCollapse,
  showAdvanced,
  disabled,
}: ConfigFormEditorProps) {
  const { t } = useI18n()

  // 获取分组标签 - 使用类型安全的方式
  const getGroupLabel = (group: ConfigGroupSchema): string => {
    const config = t.config as Record<string, string>
    return config[group.label] || group.label
  }

  // 获取分组描述
  const getGroupDescription = (group: ConfigGroupSchema): string | undefined => {
    if (!group.description) return undefined
    const config = t.config as Record<string, string>
    return config[group.description] || group.description
  }

  // 计算分组中已配置的字段数量
  const getConfiguredCount = (group: ConfigGroupSchema): number => {
    return group.fields.filter((field) => {
      const value = getNestedValue(values, field.key)
      return value !== null && value !== undefined && value !== ''
    }).length
  }

  // 过滤字段（高级选项）
  const getVisibleFields = (group: ConfigGroupSchema) => {
    if (showAdvanced) return group.fields
    return group.fields.filter((f) => !f.advanced)
  }

  return (
    <div className="space-y-4">
      {configGroups.map((group) => {
        const collapsed = isGroupCollapsed(group.id)
        const Icon = group.icon
        const visibleFields = getVisibleFields(group)
        const configuredCount = getConfiguredCount(group)

        // 如果没有可见字段，跳过
        if (visibleFields.length === 0) return null

        return (
          <div
            key={group.id}
            className="border border-[var(--subtle-border)] rounded-xl overflow-hidden"
          >
            {/* 分组头部 */}
            <button
              type="button"
              onClick={() => toggleGroupCollapse(group.id)}
              className="w-full flex items-center gap-3 px-4 py-3 bg-muted/30 hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary/10">
                <Icon className="h-4 w-4 text-primary" />
              </div>

              <div className="flex-1 text-left">
                <h4 className="font-medium">{getGroupLabel(group)}</h4>
                {getGroupDescription(group) && (
                  <p className="text-xs text-muted-foreground">
                    {getGroupDescription(group)}
                  </p>
                )}
              </div>

              <div className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground">
                  {configuredCount}/{visibleFields.length} configured
                </span>
                {collapsed ? (
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-muted-foreground" />
                )}
              </div>
            </button>

            {/* 分组内容 */}
            {!collapsed && (
              <div className="p-4 space-y-4">
                {visibleFields.map((field) => (
                  <ConfigField
                    key={field.key}
                    field={field}
                    value={getNestedValue(values, field.key)}
                    error={errors[field.key]}
                    onChange={(value) => onChange(field.key, value)}
                    disabled={disabled}
                    allValues={values}
                  />
                ))}
              </div>
            )}
          </div>
        )
      })}
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
