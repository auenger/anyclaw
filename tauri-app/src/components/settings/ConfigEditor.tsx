/**
 * ConfigEditor Component
 *
 * 配置文件编辑器，支持表单模式和高级（TOML）模式切换
 */

import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import {
  Save,
  RotateCcw,
  Check,
  AlertCircle,
  Loader2,
  FileText,
  RefreshCw,
  Settings,
  Code,
} from 'lucide-react'
import { Button } from '../ui/button'
import { Switch } from '../ui/switch'
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
import { useConfigForm } from '@/hooks/useConfigForm'
import { ConfigFormEditor } from './ConfigFormEditor'
import { getAllFields } from '@/schemas/configSchema'

interface ConfigEditorProps {
  onSaved?: () => void
  className?: string
}

export function ConfigEditor({ onSaved, className }: ConfigEditorProps) {
  const { t } = useI18n()
  const {
    isLoading,
    isSaving,
    isDirty,
    error,
    configPath,
    editorMode,
    tomlContent,
    values,
    showAdvanced,
    save,
    reset,
    refresh,
    switchMode,
    setTomlContent,
    setShowAdvanced,
    updateValue,
    getError,
    isGroupCollapsed,
    toggleGroupCollapse,
  } = useConfigForm({ onSaved })

  const [saveSuccess, setSaveSuccess] = useState(false)
  const [showRestartDialog, setShowRestartDialog] = useState(false)

  // 保存处理
  const handleSave = async () => {
    const success = await save()
    if (success) {
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)
      setShowRestartDialog(true)
    }
  }

  // 重置处理
  const handleReset = () => {
    reset()
  }

  // 刷新处理
  const handleRefresh = () => {
    if (isDirty) {
      if (!confirm(t.settings?.discardChanges || 'Discard unsaved changes?')) {
        return
      }
    }
    refresh()
  }

  // 重启服务
  const handleRestart = async () => {
    setShowRestartDialog(false)
    try {
      await invoke('restart_sidecar')
    } catch (e) {
      console.error('Failed to restart service:', e)
    }
  }

  // 模式切换
  const handleModeChange = async (advanced: boolean) => {
    const success = await switchMode(advanced ? 'advanced' : 'form')
    if (!success) {
      // 切换失败，保持在当前模式
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
            {t.settings?.configFile || 'Config File'}
          </h3>
          <p className="text-sm text-muted-foreground">{configPath}</p>
        </div>

        <div className="flex items-center gap-3">
          {/* 保存成功提示 */}
          {saveSuccess && (
            <span className="flex items-center text-sm text-green-600">
              <Check className="h-4 w-4 mr-1" />
              {t.settings?.saved || 'Saved'}
            </span>
          )}

          {/* 刷新按钮 */}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            title={t.settings?.refresh || 'Refresh'}
          >
            <RefreshCw className="h-4 w-4" />
          </Button>

          {/* 重置按钮 */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleReset}
            disabled={!isDirty || isSaving}
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            {t.common?.reset || 'Reset'}
          </Button>

          {/* 保存按钮 */}
          <Button
            size="sm"
            onClick={handleSave}
            disabled={!isDirty || isSaving}
          >
            {isSaving ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {t.common?.saving || 'Saving...'}
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                {t.common?.save || 'Save'}
              </>
            )}
          </Button>
        </div>
      </div>

      {/* 模式切换和高级选项 */}
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-4">
          {/* 表单/高级模式切换 */}
          <div className="flex items-center gap-2">
            <Settings className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">
              {t.config?.formMode || 'Form Mode'}
            </span>
            <Switch
              checked={editorMode === 'advanced'}
              onCheckedChange={handleModeChange}
            />
            <Code className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">
              {t.config?.advancedMode || 'Advanced'}
            </span>
          </div>
        </div>

        {/* 显示高级选项（仅在表单模式） */}
        {editorMode === 'form' && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {t.config?.showAdvanced || 'Show Advanced'}
            </span>
            <Switch
              checked={showAdvanced}
              onCheckedChange={setShowAdvanced}
            />
          </div>
        )}
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="flex items-center gap-2 p-3 bg-destructive/10 text-destructive rounded-lg">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* 未保存更改提示 */}
      {isDirty && (
        <div className="flex items-center gap-2 p-3 bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-200 rounded-lg">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span className="text-sm">
            {t.settings?.unsavedChanges || 'You have unsaved changes'}
          </span>
        </div>
      )}

      {/* 编辑器内容 */}
      {editorMode === 'form' ? (
        <ConfigFormEditor
          values={values}
          errors={Object.fromEntries(
            getAllFieldKeys().map((key) => [key, getError(key) ?? ''])
          )}
          onChange={updateValue}
          isGroupCollapsed={isGroupCollapsed}
          toggleGroupCollapse={toggleGroupCollapse}
          showAdvanced={showAdvanced}
        />
      ) : (
        <div className="relative">
          <textarea
            value={tomlContent}
            onChange={(e) => setTomlContent(e.target.value)}
            className={cn(
              'w-full h-[500px] p-4 font-mono text-sm',
              'bg-muted/50 border border-[var(--subtle-border)] rounded-lg',
              'focus:outline-none focus:ring-2 focus:ring-primary/50',
              'resize-y'
            )}
            spellCheck={false}
            placeholder="# AnyClaw Configuration File&#10;&#10;[llm]&#10;model = 'glm-4.7'&#10;..."
          />
        </div>
      )}

      {/* 状态栏 */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <div className="flex items-center gap-4">
          {editorMode === 'advanced' && (
            <>
              <span>
                {tomlContent.split('\n').length} {t.settings?.lines || 'lines'}
              </span>
              <span>
                {tomlContent.length} {t.settings?.characters || 'characters'}
              </span>
            </>
          )}
        </div>
        {isDirty && (
          <span className="text-yellow-600 dark:text-yellow-400">
            {t.settings?.unsavedChanges || 'Unsaved changes'}
          </span>
        )}
      </div>

      {/* 重启提示对话框 */}
      <AlertDialog open={showRestartDialog} onOpenChange={setShowRestartDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {t.settings?.configSaved || 'Configuration Saved'}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {t.settings?.restartPrompt ||
                'Configuration has been saved. Restart the service to apply changes?'}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t.settings?.later || 'Later'}</AlertDialogCancel>
            <AlertDialogAction onClick={handleRestart}>
              <RefreshCw className="h-4 w-4 mr-2" />
              {t.settings?.restartNow || 'Restart Now'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

// 辅助函数：获取所有字段 key
function getAllFieldKeys(): string[] {
  return getAllFields().map((f) => f.key)
}

export default ConfigEditor
