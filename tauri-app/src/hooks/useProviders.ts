/**
 * useProviders Hook
 *
 * React hooks for provider management.
 */

import { useState, useEffect, useCallback } from 'react'
import { getApiUrl } from '@/lib/api'
import type { Provider, ProviderDetail, ProviderConfig, TestResult } from '@/types/providers'

export function useProviders() {
  const [providers, setProviders] = useState<Provider[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchProviders = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`${getApiUrl()}/providers`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      setProviders(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load providers')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchProviders()
  }, [fetchProviders])

  return { providers, isLoading, error, refetch: fetchProviders }
}

export function useProvider(name: string) {
  const [provider, setProvider] = useState<ProviderDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchProvider = useCallback(async () => {
    if (!name) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`${getApiUrl()}/providers/${name}`)
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const data = await response.json()
      setProvider(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load provider')
    } finally {
      setIsLoading(false)
    }
  }, [name])

  useEffect(() => {
    fetchProvider()
  }, [fetchProvider])

  return { provider, isLoading, error, refetch: fetchProvider }
}

export function useUpdateProvider() {
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const updateProvider = useCallback(async (name: string, config: ProviderConfig) => {
    setIsSaving(true)
    setError(null)

    try {
      const response = await fetch(`${getApiUrl()}/providers/${name}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || `HTTP ${response.status}`)
      }

      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update provider')
      return false
    } finally {
      setIsSaving(false)
    }
  }, [])

  return { updateProvider, isSaving, error }
}

export function useTestProvider() {
  const [isTesting, setIsTesting] = useState(false)
  const [result, setResult] = useState<TestResult | null>(null)

  const testProvider = useCallback(async (
    name: string,
    config?: ProviderConfig
  ) => {
    setIsTesting(true)
    setResult(null)

    try {
      const response = await fetch(`${getApiUrl()}/providers/${name}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config || {}),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || `HTTP ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
      return data as TestResult
    } catch (err) {
      const errorResult: TestResult = {
        success: false,
        message: err instanceof Error ? err.message : 'Test failed',
        error_code: 'TEST_ERROR',
      }
      setResult(errorResult)
      return errorResult
    } finally {
      setIsTesting(false)
    }
  }, [])

  return { testProvider, isTesting, result }
}

export function useSetDefaultProvider() {
  const [isSetting, setIsSetting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const setDefaultProvider = useCallback(async (name: string) => {
    setIsSetting(true)
    setError(null)

    try {
      const response = await fetch(`${getApiUrl()}/providers/${name}/set-default`, {
        method: 'POST',
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || `HTTP ${response.status}`)
      }

      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to set default provider')
      return false
    } finally {
      setIsSetting(false)
    }
  }, [])

  return { setDefaultProvider, isSetting, error }
}
