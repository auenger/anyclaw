/**
 * ConfigEditor Component
 *
 * TOML 配置文件编辑器，支持读取、编辑、保存和验证配置文件
 */

import { useState, useEffect, useCallback } from 'react'
import { invoke } from '@tauri-apps/api/core'
import {
  Save,
  RotateCcw,
  Check,
  AlertCircle,
  Loader2,
  FileText,
  RefreshCw,
} from 'lucide-react'
import { Button } from '../ui/button'
import { cn } from '@/lib/utils'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../ui/alert-dialog'
import { useI18n } from '@/i18n'

interface ConfigEditorProps {
  onSaved?: () => void
  className?: string
}

export function ConfigEditor({ onSaved, className }: ConfigEditorProps) {
  const { t } = useI18n()
  const [content, setContent] = useState('')
  const [originalContent, setOriginalContent] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [warning, setWarning] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [configPath, setConfigPath] = useState<string>('')

  // 重启提示对话框
  const [showRestartDialog, setShowRestartDialog] = useState(false)

  // 加载配置文件
  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    setIsLoading(true)
    setError(null)

    try {
      // 获取配置文件路径
      const path = await invoke<string>('get_config_path_string')
      setConfigPath(path)

      // 读取配置文件内容
      const configContent = await invoke<string>('read_config_file')
      setContent(configContent)
      setOriginalContent(configContent)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsLoading(false)
    }
  }

  // 检查是否有未保存的更改
  const hasChanges = content !== originalContent

  // 验证 TOML 格式
  const validateContent = useCallback(async (value: string): Promise<string | null> => {
    try {
      await invoke('validate_toml', { content: value })
      return null
    } catch (e) {
      return String(e)
    }
  }, [])

  // 内容变更处理
  const handleContentChange = async (value: string) => {
    setContent(value)
    setSaveSuccess(false)

    // 实时验证（防抖）
    if (value.trim()) {
      const validationError = await validateContent(value)
      setWarning(validationError)
    } else {
      setWarning(null)
    }
  }

  // 保存配置
  const handleSave = async () => {
    if (!hasChanges) return

    // 先验证
    const validationError = await validateContent(content)
    if (validationError) {
      setError(validationError)
      return
    }

    setIsSaving(true)
    setError(null)

    try {
      await invoke('write_config_file', { content })
      setOriginalContent(content)
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)

      // 显示重启提示
      setShowRestartDialog(true)

      onSaved?.()
    } catch (e) {
      setError(String(e))
    } finally {
      setIsSaving(false)
    }
  }

  // 重置到原始内容
  const handleReset = () => {
    setContent(originalContent)
    setError(null)
    setWarning(null)
    setSaveSuccess(false)
  }

  // 刷新配置
  const handleRefresh = () => {
    if (hasChanges) {
      if (!confirm(t.settings.discardChanges || 'Discard unsaved changes?')) {
        return
      }
    }
    loadConfig()
  }

  // 重启服务
  const handleRestart = async () => {
    setShowRestartDialog(false)
    try {
      await invoke('restart_sidecar')
    } catch (e) {
      setError(`Failed to restart service: ${e}`)
    }
  }

  if (isLoading) {
    return (
      <div className={cn('flex items-center justify-center h-64', className)}>
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* 头部 */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <FileText className="h-5 w-5" />
            {t.settings.configFile || 'Config File'}
          </h3>
          <p className="text-sm text-muted-foreground">
            {configPath}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {saveSuccess && (
            <span className="flex items-center text-sm text-green-600">
              <Check className="h-4 w-4 mr-1" />
              {t.settings.saved || 'Saved'}
            </span>
          )}

          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            title={t.settings.refresh || 'Refresh'}
          >
            <RefreshCw className="h-4 w-4" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={handleReset}
            disabled={!hasChanges || isSaving}
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            {t.common.reset || 'Reset'}
          </Button>

          <Button
            size="sm"
            onClick={handleSave}
            disabled={!hasChanges || isSaving || !!warning}
          >
            {isSaving ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {t.common.saving || 'Saving...'}
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                {t.common.save || 'Save'}
              </>
            )}
          </Button>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="flex items-center gap-2 p-3 bg-destructive/10 text-destructive rounded-lg">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* 警告提示 */}
      {warning && (
        <div className="flex items-center gap-2 p-3 bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-200 rounded-lg">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span className="text-sm">{warning}</span>
        </div>
      )}

      {/* 编辑器 */}
      <div className="relative">
        <textarea
          value={content}
          onChange={(e) => handleContentChange(e.target.value)}
          className={cn(
            'w-full h-[500px] p-4 font-mono text-sm',
            'bg-muted/50 border border-[var(--subtle-border)] rounded-lg',
            'focus:outline-none focus:ring-2 focus:ring-primary/50',
            'resize-y',
            warning && 'border-yellow-500'
          )}
          spellCheck={false}
          placeholder="# AnyClaw Configuration File&#10;&#10;[llm]&#10;model = 'glm-4.7'&#10;..."
        />
      </div>

      {/* 状态栏 */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <div className="flex items-center gap-4">
          <span>
            {content.split('\n').length} {t.settings.lines || 'lines'}
          </span>
          <span>
            {content.length} {t.settings.characters || 'characters'}
          </span>
        </div>
        {hasChanges && (
          <span className="text-yellow-600 dark:text-yellow-400">
            {t.settings.unsavedChanges || 'Unsaved changes'}
          </span>
        )}
      </div>

      {/* 重启提示对话框 */}
      <AlertDialog open={showRestartDialog} onOpenChange={setShowRestartDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {t.settings.configSaved || 'Configuration Saved'}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {t.settings.restartPrompt || 'Configuration has been saved. Restart the service to apply changes?'}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>
              {t.settings.later || 'Later'}
            </AlertDialogCancel>
            <AlertDialogAction onClick={handleRestart}>
              <RefreshCw className="h-4 w-4 mr-2" />
              {t.settings.restartNow || 'Restart Now'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

export default ConfigEditor
