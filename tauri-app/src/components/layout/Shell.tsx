import { type ReactNode, useState, useEffect } from 'react'
import { AppSidebar } from './AppSidebar'
import { PlatformContext } from '@/hooks/usePlatform'
import { isTauri } from '@/lib/utils'

interface ShellProps {
  children: ReactNode
  onOpenSettings?: (tab?: string) => void
}

export function Shell({ children, onOpenSettings }: ShellProps) {
  const [platform, setPlatform] = useState('')

  useEffect(() => {
    if (!isTauri) return
    import('@tauri-apps/api/core').then(({ invoke }) => {
      invoke<string>('get_platform').then(setPlatform)
    })
  }, [])

  const isWin = platform === 'windows'
  const isMac = platform === 'macos'
  const isDesktop = isTauri

  const platformCtx = { platform, isMac, isWin, isDesktop }

  return (
    <PlatformContext.Provider value={platformCtx}>
      <div className="h-screen flex flex-col bg-background text-foreground">
        <div className="flex-1 flex overflow-hidden">
          <AppSidebar onOpenSettings={onOpenSettings} />
          <main className="flex-1 overflow-hidden flex flex-col">
            {children}
          </main>
        </div>
      </div>
    </PlatformContext.Provider>
  )
}
