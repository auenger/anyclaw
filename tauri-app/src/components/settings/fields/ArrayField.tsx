/**
 * 数组字段组件
 */

import { useState } from 'react'
import { Plus, X } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { ConfigFieldSchema } from '@/types/config'

interface ArrayFieldProps {
  field: ConfigFieldSchema
  value: string[]
  error?: string
  onChange: (value: string[]) => void
  disabled?: boolean
}

export function ArrayField({ field, value, error, onChange, disabled }: ArrayFieldProps) {
  const [newValue, setNewValue] = useState('')
  const items = Array.isArray(value) ? value : []

  const handleAdd = () => {
    if (newValue.trim()) {
      onChange([...items, newValue.trim()])
      setNewValue('')
    }
  }

  const handleRemove = (index: number) => {
    const newItems = [...items]
    newItems.splice(index, 1)
    onChange(newItems)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAdd()
    }
  }

  return (
    <div className="space-y-2">
      {/* 已添加的项 */}
      {items.length > 0 && (
        <div className="space-y-1">
          {items.map((item, index) => (
            <div
              key={index}
              className="flex items-center gap-2 px-3 py-1.5 bg-muted/50 rounded-md"
            >
              <span className="flex-1 text-sm truncate">{item}</span>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0"
                onClick={() => handleRemove(index)}
                disabled={disabled || field.disabled}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {/* 添加新项 */}
      <div className="flex gap-2">
        <Input
          value={newValue}
          onChange={(e) => setNewValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={field.placeholder}
          disabled={disabled || field.disabled}
          className={cn(error && 'border-destructive')}
        />
        <Button
          variant="outline"
          size="sm"
          onClick={handleAdd}
          disabled={disabled || field.disabled || !newValue.trim()}
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  )
}
