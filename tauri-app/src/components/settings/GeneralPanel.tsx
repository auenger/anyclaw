import { useI18n } from '@/i18n'
import { useAppStore, type Theme, type Locale } from '@/stores/app'
import { cn } from '@/lib/utils'
import { Sun, Moon, Monitor } from 'lucide-react'

export function GeneralPanel() {
  const { t } = useI18n()
  const theme = useAppStore((s) => s.theme)
  const setTheme = useAppStore((s) => s.setTheme)
  const locale = useAppStore((s) => s.locale)
  const setLocale = useAppStore((s) => s.setLocale)

  const themes: { id: Theme; label: string; desc: string; icon: typeof Sun }[] = [
    { id: 'light', label: t.settings.light, desc: t.settings.lightDesc, icon: Sun },
    { id: 'dark', label: t.settings.dark, desc: t.settings.darkDesc, icon: Moon },
    { id: 'system', label: t.settings.system, desc: t.settings.systemDesc, icon: Monitor },
  ]

  const locales: { id: Locale; label: string }[] = [
    { id: 'en', label: 'English' },
    { id: 'zh', label: '简体中文' },
  ]

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold mb-4">{t.settings.appearance}</h3>

        <div className="grid grid-cols-3 gap-3">
          {themes.map((item) => (
            <button
              key={item.id}
              onClick={() => setTheme(item.id)}
              className={cn(
                "flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-colors",
                theme === item.id
                  ? "border-primary bg-primary/5"
                  : "border-[var(--subtle-border)] hover:border-primary/50"
              )}
            >
              <item.icon size={24} className={theme === item.id ? "text-primary" : "text-muted-foreground"} />
              <span className="font-medium text-sm">{item.label}</span>
              <span className="text-xs text-muted-foreground text-center">{item.desc}</span>
            </button>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-4">{t.settings.language}</h3>

        <div className="flex gap-2">
          {locales.map((item) => (
            <button
              key={item.id}
              onClick={() => setLocale(item.id)}
              className={cn(
                "px-4 py-2 rounded-lg border transition-colors",
                locale === item.id
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-[var(--subtle-border)] hover:border-primary/50"
              )}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
