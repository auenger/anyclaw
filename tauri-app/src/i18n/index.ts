import { useContext } from 'react'
import { I18nContext } from './ctx'

export { I18nProvider } from './context'
export type { Locale, I18nContextType } from './ctx'
export type { Translations } from './types'

export function useI18n() {
  const ctx = useContext(I18nContext)
  if (!ctx) {
    throw new Error('useI18n must be used within an I18nProvider')
  }
  return ctx
}
