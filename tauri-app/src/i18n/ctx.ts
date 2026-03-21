import { createContext } from 'react'
import { en } from './en'
import type { Translations } from './types'

export type Locale = 'en' | 'zh'

export interface I18nContextType {
  locale: Locale
  t: Translations
  setLocale: (locale: Locale) => void
}

export const I18nContext = createContext<I18nContextType>({
  locale: 'en',
  t: en,
  setLocale: () => {},
})
