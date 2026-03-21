import { ExternalLink } from 'lucide-react'
import { useI18n } from '@/i18n'

export function AboutPanel() {
  const { t } = useI18n()

  return (
    <div className="space-y-6">
      <div className="text-center py-6">
        <h2 className="text-2xl font-bold">{t.about.appName}</h2>
        <p className="text-muted-foreground mt-2">{t.about.description}</p>
      </div>

      <div className="space-y-4">
        <div className="flex justify-between items-center py-3 border-b border-[var(--subtle-border)]">
          <span className="text-muted-foreground">{t.about.version}</span>
          <span className="font-mono">0.1.0</span>
        </div>

        <div className="flex justify-between items-center py-3 border-b border-[var(--subtle-border)]">
          <span className="text-muted-foreground">{t.about.framework}</span>
          <span>{t.about.frameworkDesc}</span>
        </div>

        <div className="flex justify-between items-center py-3 border-b border-[var(--subtle-border)]">
          <span className="text-muted-foreground">{t.about.license}</span>
          <span>{t.about.licenseType}</span>
        </div>

        <div className="flex justify-between items-center py-3">
          <span className="text-muted-foreground">{t.about.github}</span>
          <a
            href="https://github.com/user/anyclaw"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-primary hover:underline"
          >
            github.com/user/anyclaw
            <ExternalLink size={14} />
          </a>
        </div>
      </div>
    </div>
  )
}
