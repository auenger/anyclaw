/**
 * ServiceControl Component
 *
 * Sidecar 服务控制面板：显示服务状态，提供启动/停止/重启按钮
 */

import { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { listen } from '@tauri-apps/api/event'
import {
  Play,
  Square,
  RefreshCw,
  Activity,
  Loader2,
  CheckCircle2,
  XCircle,
} from 'lucide-react'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { cn } from '@/lib/utils'
import { useI18n } from '@/i18n'

type SidecarStatus = 'Stopped' | 'Starting' | 'Running' | 'Stopping' | 'Error'

interface SidecarInfo {
  status: SidecarStatus
  port: number
  message: string
}

interface ServiceControlProps {
  className?: string
}

// 状态颜色和图标映射
const statusConfig: Record<SidecarStatus, { color: string; bgColor: string; icon: typeof Activity }> = {
  Running: { color: 'text-green-600', bgColor: 'bg-green-100 dark:bg-green-900/20', icon: CheckCircle2 },
  Stopped: { color: 'text-gray-500', bgColor: 'bg-gray-100 dark:bg-gray-800', icon: Square },
  Starting: { color: 'text-blue-600', bgColor: 'bg-blue-100 dark:bg-blue-900/20', icon: Loader2 },
  Stopping: { color: 'text-orange-600', bgColor: 'bg-orange-100 dark:bg-orange-900/20', icon: Loader2 },
  Error: { color: 'text-red-600', bgColor: 'bg-red-100 dark:bg-red-900/20', icon: XCircle },
}

export function ServiceControl({ className }: ServiceControlProps) {
  const { t } = useI18n()
  const [status, setStatus] = useState<SidecarInfo>({
    status: 'Stopped',
    port: 62601,
    message: '',
  })
  const [isOperating, setIsOperating] = useState(false)

  // 加载状态
  useEffect(() => {
    loadStatus()
  }, [])

  // 监听状态变化
  useEffect(() => {
    const unlisten = listen<SidecarInfo>('sidecar-status', (event) => {
      setStatus(event.payload)
      setIsOperating(false)
    })

    return () => {
      unlisten.then((fn) => fn())
    }
  }, [])

  const loadStatus = async () => {
    try {
      const info = await invoke<SidecarInfo>('get_sidecar_status')
      setStatus(info)
    } catch (e) {
      console.error('Failed to load sidecar status:', e)
    }
  }

  const handleStart = async () => {
    setIsOperating(true)
    try {
      await invoke('start_sidecar')
    } catch (e) {
      console.error('Failed to start sidecar:', e)
      setIsOperating(false)
    }
  }

  const handleStop = async () => {
    setIsOperating(true)
    try {
      await invoke('stop_sidecar')
    } catch (e) {
      console.error('Failed to stop sidecar:', e)
      setIsOperating(false)
    }
  }

  const handleRestart = async () => {
    setIsOperating(true)
    try {
      await invoke('restart_sidecar')
    } catch (e) {
      console.error('Failed to restart sidecar:', e)
      setIsOperating(false)
    }
  }

  const config = statusConfig[status.status]
  const StatusIcon = config.icon
  const isRunning = status.status === 'Running'
  const isStopped = status.status === 'Stopped'
  const isTransitioning = status.status === 'Starting' || status.status === 'Stopping'

  return (
    <div className={cn('space-y-4', className)}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            {t.settings.serviceControl || 'Service Control'}
          </CardTitle>
          <CardDescription>
            {t.settings.serviceControlDesc || 'Manage the AnyClaw backend service'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 状态显示 */}
          <div className={cn('flex items-center gap-3 p-4 rounded-lg', config.bgColor)}>
            <StatusIcon
              className={cn(
                'h-6 w-6',
                config.color,
                isTransitioning && 'animate-spin'
              )}
            />
            <div className="flex-1">
              <div className={cn('font-medium', config.color)}>
                {status.status === 'Running' ? t.settings.serviceRunning :
                 status.status === 'Stopped' ? t.settings.serviceStopped :
                 status.status === 'Starting' ? t.settings.starting :
                 status.status === 'Stopping' ? t.settings.stopping :
                 status.status === 'Error' ? t.settings.serviceError :
                 status.status}
              </div>
              <div className="text-sm text-muted-foreground">
                {status.message || (isRunning ? t.settings.serviceRunning : t.settings.serviceStopped)}
              </div>
            </div>
          </div>

          {/* 详细信息 */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <div className="text-sm text-muted-foreground">{t.settings.port || 'Port'}</div>
              <div className="font-mono">{status.port}</div>
            </div>

            <div className="space-y-1">
              <div className="text-sm text-muted-foreground">{t.settings.apiUrl || 'API URL'}</div>
              <div className="font-mono text-xs">
                http://127.0.0.1:{status.port}
              </div>
            </div>
          </div>

          {/* 控制按钮 */}
          <div className="flex items-center gap-2 pt-2">
            {isStopped ? (
              <Button
                onClick={handleStart}
                disabled={isOperating || isTransitioning}
                className="flex-1"
              >
                {isOperating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    {t.settings.starting || 'Starting...'}
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    {t.settings.startService || 'Start Service'}
                  </>
                )}
              </Button>
            ) : (
              <>
                <Button
                  variant="outline"
                  onClick={handleStop}
                  disabled={isOperating || isTransitioning || isStopped}
                  className="flex-1"
                >
                  {status.status === 'Stopping' ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      {t.settings.stopping || 'Stopping...'}
                    </>
                  ) : (
                    <>
                      <Square className="h-4 w-4 mr-2" />
                      {t.settings.stopService || 'Stop'}
                    </>
                  )}
                </Button>

                <Button
                  onClick={handleRestart}
                  disabled={isOperating || isTransitioning || isStopped}
                  className="flex-1"
                >
                  {isOperating ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      {t.settings.restarting || 'Restarting...'}
                    </>
                  ) : (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2" />
                      {t.settings.restartService || 'Restart'}
                    </>
                  )}
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default ServiceControl
