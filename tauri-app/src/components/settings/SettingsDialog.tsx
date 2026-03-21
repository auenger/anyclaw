import { useState } from 'react'
import { X, Palette, Cpu, Info } from 'lucide-react'
import { useI18n } from '@/i18n'
import { cn } from '@/lib/utils'
import { GeneralPanel } from './GeneralPanel'
import { ModelsPanel } from './ModelsPanel'
import { AboutPanel } from './AboutPanel'

type Tab = 'general' | 'models' | 'skills' | 'about'

interface SettingsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  initialTab?: Tab
}

export function SettingsDialog({ open, onOpenChange, initialTab = 'general' }: SettingsDialogProps) {
  const { t } = useI18n()
  const [currentTab, setCurrentTab] = useState<Tab>(initialTab)

  if (!open) return null

  const tabs = [
    { id: 'general' as const, label: t.settings.general, icon: Palette },
    { id: 'models' as const, label: t.settings.models, icon: Cpu },
    { id: 'about' as const, label: t.settings.about, icon: Info },
  ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => onOpenChange(false)}
      />

      {/* Dialog */}
      <div className="relative w-[90vw] max-w-4xl h-[80vh] bg-background rounded-xl shadow-2xl border border-[var(--subtle-border)] flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-[200px] shrink-0 border-r border-[var(--subtle-border)] p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">{t.settings.title}</h3>
            <button
              onClick={() => onOpenChange(false)}
              className="p-1 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground"
            >
              <X size={16} />
            </button>
          </div>

          <div className="space-y-0.5">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setCurrentTab(tab.id)}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-colors",
                  currentTab === tab.id
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-accent text-muted-foreground hover:text-foreground"
                )}
              >
                <tab.icon size={16} />
                <span className="text-sm">{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {currentTab === 'general' && <GeneralPanel />}
          {currentTab === 'models' && <ModelsPanel />}
          {currentTab === 'about' && <AboutPanel />}
        </div>
      </div>
    </div>
  )
}
