/**
 * 配置类型定义
 * 用于配置表单编辑器的类型系统
 */

import type { LucideIcon } from 'lucide-react'

/** 字段类型 */
export type FieldType = 'string' | 'number' | 'boolean' | 'enum' | 'array' | 'object'

/** 验证规则 */
export interface FieldValidation {
  min?: number
  max?: number
  pattern?: string
  enum?: string[]
}

/** 条件显示配置 */
export interface FieldCondition {
  field: string
  value: any
  operator?: 'eq' | 'neq' | 'in' | 'contains'
}

/** 配置字段 Schema */
export interface ConfigFieldSchema {
  /** 配置键名 (如 "llm.model") */
  key: string
  /** 字段类型 */
  type: FieldType
  /** 显示标签 (i18n key) */
  label: string
  /** 字段描述 (i18n key) */
  description?: string
  /** 默认值 */
  default?: any
  /** 是否必填 */
  required?: boolean
  /** 是否为敏感字段 (如 API Key) */
  sensitive?: boolean
  /** 验证规则 */
  validation?: FieldValidation
  /** 所属分组 ID */
  group: string
  /** 条件显示 */
  condition?: FieldCondition
  /** 占位符 (i18n key) */
  placeholder?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 仅高级模式显示 */
  advanced?: boolean
}

/** 配置分组 Schema */
export interface ConfigGroupSchema {
  /** 分组 ID */
  id: string
  /** 显示标签 (i18n key) */
  label: string
  /** 分组描述 (i18n key) */
  description?: string
  /** 图标 */
  icon: LucideIcon
  /** 字段列表 */
  fields: ConfigFieldSchema[]
  /** 默认折叠状态 */
  defaultCollapsed?: boolean
  /** 分组顺序 */
  order?: number
}

/** 配置值类型 */
export type ConfigValue = string | number | boolean | string[] | Record<string, any> | null | undefined

/** 配置数据结构 */
export type ConfigData = Record<string, ConfigValue>

/** 表单字段状态 */
export interface FieldState {
  value: ConfigValue
  error?: string
  touched: boolean
  dirty: boolean
}

/** 表单状态 */
export interface FormState {
  values: ConfigData
  errors: Record<string, string>
  touched: Record<string, boolean>
  dirty: Record<string, boolean>
  isValid: boolean
  isDirty: boolean
  isSubmitting: boolean
}

/** 编辑模式 */
export type EditorMode = 'form' | 'advanced'

/** 折叠状态 */
export type CollapsedState = Record<string, boolean>
