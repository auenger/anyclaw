/**
 * Provider Types
 *
 * Types for LLM provider configuration and management.
 */

export interface Provider {
  name: string
  display_name: string
  is_configured: boolean
  has_api_key: boolean
  base_url?: string
  is_default?: boolean
}

export interface ProviderDetail {
  name: string
  display_name: string
  api_key?: string // Masked for security
  base_url?: string
  is_configured: boolean
  has_api_key: boolean
  is_default?: boolean
}

export interface ProviderConfig {
  api_key?: string
  base_url?: string
}

export interface TestResult {
  success: boolean
  message: string
  latency_ms?: number
  error_code?: string
  models_count?: number
}
