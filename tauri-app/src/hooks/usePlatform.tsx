import { createContext, useContext, useState, useEffect } from 'react'
import { isTauri } from '@/lib/utils'

export type PlatformContextValue = {
  platform: string
  isMac: boolean
  isWin: boolean
  isDesktop: boolean
}

export const PlatformContext = createContext<PlatformContextValue>({
  platform: '',
  isMac: false,
  isWin: false,
  isDesktop: false,
})

export const usePlatform = () => useContext(PlatformContext)

/**
 * 获取平台信息的 Hook
 */
export function usePlatformInfo() {
  const [platform, setPlatform] = useState('')

  useEffect(() => {
    if (!isTauri) return
    import('@tauri-apps/api/core').then(({ invoke }) => {
      invoke<string>('get_platform').then(setPlatform)
    })
  }, [])

  return {
    platform,
    isMac: platform === 'macos',
    isWin: platform === 'windows',
    isDesktop: isTauri,
  }
}
