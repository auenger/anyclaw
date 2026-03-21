import { useState } from 'react'
import { Plus, Check, Trash2, Edit } from 'lucide-react'
import { useI18n } from '@/i18n'
import { cn } from '@/lib/utils'

interface CustomModel {
  id: string
  name: string
  modelId: string
  baseUrl?: string
  isDefault?: boolean
}

const mockModels: CustomModel[] = [
  { id: '1', name: 'GLM-4.7', modelId: 'glm-4.7', isDefault: true },
  { id: '2', name: 'Claude Sonnet', modelId: 'claude-sonnet-4-6', baseUrl: 'https://api.anthropic.com' },
]

export function ModelsPanel() {
  const { t } = useI18n()
  const [models] = useState(mockModels)
  const [showAddForm, setShowAddForm] = useState(false)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">{t.settings.customModels}</h3>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 text-sm"
        >
          <Plus size={14} />
          {t.settings.addCustomModel}
        </button>
      </div>

      {showAddForm && (
        <div className="p-4 rounded-lg border border-[var(--subtle-border)] space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-muted-foreground">{t.settings.modelName}</label>
              <input
                type="text"
                placeholder={t.settings.modelNamePlaceholder}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-[var(--subtle-border)] bg-background"
              />
            </div>
            <div>
              <label className="text-sm text-muted-foreground">{t.settings.modelId}</label>
              <input
                type="text"
                placeholder={t.settings.modelIdPlaceholder}
                className="mt-1 w-full px-3 py-2 rounded-lg border border-[var(--subtle-border)] bg-background"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <button
              onClick={() => setShowAddForm(false)}
              className="px-3 py-1.5 rounded-lg border border-[var(--subtle-border)] hover:bg-accent text-sm"
            >
              {t.common.cancel}
            </button>
            <button
              onClick={() => setShowAddForm(false)}
              className="px-3 py-1.5 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 text-sm"
            >
              {t.common.save}
            </button>
          </div>
        </div>
      )}

      <div className="space-y-2">
        {models.map((model) => (
          <div
            key={model.id}
            className={cn(
              "flex items-center justify-between p-4 rounded-lg border transition-colors",
              model.isDefault
                ? "border-primary/50 bg-primary/5"
                : "border-[var(--subtle-border)] hover:border-primary/30"
            )}
          >
            <div className="flex items-center gap-3">
              {model.isDefault && (
                <div className="w-5 h-5 rounded-full bg-primary flex items-center justify-center">
                  <Check size={12} className="text-primary-foreground" />
                </div>
              )}
              <div>
                <div className="font-medium">{model.name}</div>
                <div className="text-sm text-muted-foreground font-mono">{model.modelId}</div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {!model.isDefault && (
                <>
                  <button
                    className="p-2 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground"
                    title={t.settings.setDefault}
                  >
                    <Check size={14} />
                  </button>
                  <button
                    className="p-2 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground"
                    title={t.common.edit}
                  >
                    <Edit size={14} />
                  </button>
                  <button
                    className="p-2 rounded-lg hover:bg-accent text-red-500"
                    title={t.common.delete}
                  >
                    <Trash2 size={14} />
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
