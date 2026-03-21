import { type ReactNode } from 'react'
import { en } from './en'
import { zh } from './zh'
import type { Translations } from './types'
import { I18nContext, type Locale } from './ctx'
import { useAppStore } from '@/stores/app'

const locales: Record<Locale, Translations> = { en, zh }

export function I18nProvider({ children }: { children: ReactNode }) {
  const locale = useAppStore((s) => s.locale)
  const setLocale = useAppStore((s) => s.setLocale)

  return (
    <I18nContext.Provider value={{ locale, t: locales[locale], setLocale }}>
      {children}
    </I18nContext.Provider>
  )
}
