/**
 * ModelsPanel Component
 *
 * Provider configuration and model management panel.
 * Connects to backend API for provider CRUD operations.
 */

import { useState } from 'react'
import { Eye, EyeOff, Check, X, Loader2, RefreshCw, Star } from 'lucide-react'
import { useI18n } from '@/i18n'
import { cn } from '@/lib/utils'
import { useProviders, useUpdateProvider, useTestProvider, useSetDefaultProvider } from '@/hooks/useProviders'
import type { Provider } from '@/types/providers'

interface ProviderCardProps {
  provider: Provider
  onRefresh: () => void
  port?: number
}

function ProviderCard({ provider, onRefresh, port }: ProviderCardProps) {
  const { t } = useI18n()
  const [showApiKey, setShowApiKey] = useState(false)
  const [apiKey, setApiKey] = useState('')
  const [baseUrl, setBaseUrl] = useState(provider.base_url || '')
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)

  const { updateProvider, isSaving } = useUpdateProvider(port)
  const { testProvider, isTesting } = useTestProvider(port)
  const { setDefaultProvider, isSetting } = useSetDefaultProvider(port)

  const handleSave = async () => {
    const success = await updateProvider(provider.name, {
      api_key: apiKey || undefined,
      base_url: baseUrl || undefined,
    })
    if (success) {
      setApiKey('')
      onRefresh()
    }
  }

  const handleTest = async () => {
    const result = await testProvider(provider.name, {
      api_key: apiKey || undefined,
      base_url: baseUrl || undefined,
    })
    setTestResult({ success: result.success, message: result.message })
  }

  const handleSetDefault = async () => {
    const success = await setDefaultProvider(provider.name)
    if (success) {
      onRefresh()
    }
  }

  const isOllama = provider.name === 'ollama'
  const canTest = isOllama || provider.has_api_key || apiKey.length > 0

  return (
    <div className={cn(
      "p-4 rounded-lg border transition-colors",
      provider.is_configured
        ? "border-primary/30 bg-primary/5"
        : "border-[var(--subtle-border)] hover:border-primary/20"
    )}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h4 className="font-medium">{provider.display_name}</h4>
          {provider.is_default && (
            <span className="flex items-center text-xs text-green-600 dark:text-green-400">
              <Check size={12} className="mr-1" />
              {t.settings.currentSelection}
            </span>
          )}
        </div>
        {provider.is_default && (
          <button
            onClick={handleSetDefault}
            disabled={isSetting}
            className="flex items-center gap-1 px-2 py-1 text-xs rounded hover:bg-accent"
            title={t.settings.setDefault}
          >
            {isSetting ? (
              <Loader2 size={12} className="animate-spin" />
            ) : (
              <Star size={12} />
            )}
          </button>
        )}
      </div>

      {/* API Key (not for Ollama) */}
      {!isOllama && (
        <div className="space-y-2 mb-3">
          <label className="text-sm text-muted-foreground">API Key</label>
          <div className="relative">
            <input
              type={showApiKey ? 'text' : 'password'}
              value={apiKey}
              onChange={(e) => {
                setApiKey(e.target.value)
                setTestResult(null)
              }}
              placeholder={provider.has_api_key ? t.settings.apiKeyEditPlaceholder : t.settings.apiKeyPlaceholder}
              className="w-full px-3 py-2 pr-10 rounded-lg border border-[var(--subtle-border)] bg-background text-sm"
            />
            <button
              type="button"
              onClick={() => setShowApiKey(!showApiKey)}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              {showApiKey ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>
      )}

      {/* Base URL */}
      <div className="space-y-2 mb-4">
        <label className="text-sm text-muted-foreground">
          Base URL <span className="text-muted-foreground/60">(可选)</span>
        </label>
        <input
          type="url"
          value={baseUrl}
          onChange={(e) => {
            setBaseUrl(e.target.value)
            setTestResult(null)
          }}
          placeholder={t.settings.baseUrlPlaceholder}
          className="w-full px-3 py-2 rounded-lg border border-[var(--subtle-border)] bg-background text-sm"
        />
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={handleTest}
          disabled={isTesting || !canTest}
          className={cn(
            "flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg border border-[var(--subtle-border)] hover:bg-accent",
            (isTesting || !canTest) && "opacity-50 cursor-not-allowed"
          )}
        >
          {isTesting ? (
            <>
              <Loader2 size={14} className="animate-spin" />
              {t.common.loading}
            </>
          ) : (
            t.settings.testConnection || 'Test Connection'
          )}
        </button>

        <button
          onClick={handleSave}
          disabled={isSaving}
          className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg bg-primary text-primary-foreground hover:bg-primary/90"
        >
          {isSaving ? (
            <>
              <Loader2 size={14} className="animate-spin" />
              {t.common.saving}
            </>
          ) : (
            t.common.save
          )}
        </button>
      </div>

      {/* Test Result */}
      {testResult && (
        <div className={cn(
          "mt-3 flex items-center gap-2 text-sm",
          testResult.success ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
        )}>
          {testResult.success ? <Check size={14} /> : <X size={14} />}
          {testResult.message}
        </div>
      )}
    </div>
  )
}

interface ModelsPanelProps {
  port?: number
}

export function ModelsPanel({ port }: ModelsPanelProps) {
  const { t } = useI18n()
  const { providers, isLoading, error, refetch } = useProviders(port)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 size={24} className="animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500 mb-4">{error}</p>
        <button
          onClick={refetch}
          className="flex items-center gap-2 px-4 py-2 mx-auto rounded-lg border hover:bg-accent"
        >
          <RefreshCw size={16} />
          {t.common.retry}
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">{t.settings.models}</h3>
        <button
          onClick={refetch}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[var(--subtle-border)] hover:bg-accent text-sm"
        >
          <RefreshCw size={14} />
          {t.settings.refresh}
        </button>
      </div>

      <div className="space-y-3">
        {providers.map((provider) => (
          <ProviderCard
            key={provider.name}
            provider={provider}
            onRefresh={refetch}
            port={port}
          />
        ))}
      </div>

      {providers.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          {t.common.noData}
        </div>
      )}
    </div>
  )
}

export default ModelsPanel
