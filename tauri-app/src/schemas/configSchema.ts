/**
 * 配置 Schema 定义
 * 基于 config.template.toml 生成的配置结构
 */

import {
  Bot,
  Cpu,
  Key,
  Shield,
  Brain,
  Minimize2,
  Activity,
  Wrench,
  Users,
  MessageSquare,
  Server,
} from 'lucide-react'
import type { ConfigGroupSchema, ConfigFieldSchema } from '@/types/config'

/**
 * Agent 配置分组
 */
const agentFields: ConfigFieldSchema[] = [
  {
    key: 'agent.name',
    type: 'string',
    label: 'config.agent.name',
    description: 'config.agent.nameDesc',
    default: 'AnyClaw',
    group: 'agent',
  },
  {
    key: 'agent.workspace',
    type: 'string',
    label: 'config.agent.workspace',
    description: 'config.agent.workspaceDesc',
    default: '~/.anyclaw/workspace',
    group: 'agent',
    placeholder: 'config.agent.workspacePlaceholder',
  },
]

/**
 * LLM 配置分组
 */
const llmFields: ConfigFieldSchema[] = [
  {
    key: 'llm.provider',
    type: 'enum',
    label: 'config.llm.provider',
    description: 'config.llm.providerDesc',
    default: 'zai',
    group: 'llm',
    validation: {
      enum: ['openai', 'anthropic', 'zai', 'deepseek', 'openrouter', 'ollama'],
    },
  },
  {
    key: 'llm.model',
    type: 'string',
    label: 'config.llm.model',
    description: 'config.llm.modelDesc',
    default: 'glm-4.7',
    group: 'llm',
    placeholder: 'config.llm.modelPlaceholder',
  },
  {
    key: 'llm.max_tokens',
    type: 'number',
    label: 'config.llm.maxTokens',
    description: 'config.llm.maxTokensDesc',
    default: 2000,
    group: 'llm',
    validation: { min: 1, max: 128000 },
  },
  {
    key: 'llm.temperature',
    type: 'number',
    label: 'config.llm.temperature',
    description: 'config.llm.temperatureDesc',
    default: 0.7,
    group: 'llm',
    validation: { min: 0, max: 2 },
  },
  {
    key: 'llm.context_window_tokens',
    type: 'number',
    label: 'config.llm.contextWindow',
    description: 'config.llm.contextWindowDesc',
    default: 128000,
    group: 'llm',
    advanced: true,
  },
]

/**
 * Providers 配置分组 (动态)
 * 每个 Provider 包含 api_key 和可选的 api_base
 */
const providerFields: ConfigFieldSchema[] = [
  // OpenAI
  {
    key: 'providers.openai.api_key',
    type: 'string',
    label: 'config.providers.openaiApiKey',
    default: '',
    group: 'providers',
    sensitive: true,
    condition: { field: 'llm.provider', value: 'openai', operator: 'eq' },
  },
  {
    key: 'providers.openai.api_base',
    type: 'string',
    label: 'config.providers.apiBase',
    default: '',
    group: 'providers',
    advanced: true,
    placeholder: 'config.providers.apiBasePlaceholder',
    condition: { field: 'llm.provider', value: 'openai', operator: 'eq' },
  },
  // Anthropic
  {
    key: 'providers.anthropic.api_key',
    type: 'string',
    label: 'config.providers.anthropicApiKey',
    default: '',
    group: 'providers',
    sensitive: true,
    condition: { field: 'llm.provider', value: 'anthropic', operator: 'eq' },
  },
  // ZAI
  {
    key: 'providers.zai.api_key',
    type: 'string',
    label: 'config.providers.zaiApiKey',
    default: '',
    group: 'providers',
    sensitive: true,
    condition: { field: 'llm.provider', value: 'zai', operator: 'eq' },
  },
  {
    key: 'providers.zai.api_base',
    type: 'string',
    label: 'config.providers.apiBase',
    default: 'https://open.bigmodel.cn/api/coding/paas/v4',
    group: 'providers',
    advanced: true,
    condition: { field: 'llm.provider', value: 'zai', operator: 'eq' },
  },
  // DeepSeek
  {
    key: 'providers.deepseek.api_key',
    type: 'string',
    label: 'config.providers.deepseekApiKey',
    default: '',
    group: 'providers',
    sensitive: true,
    condition: { field: 'llm.provider', value: 'deepseek', operator: 'eq' },
  },
  // OpenRouter
  {
    key: 'providers.openrouter.api_key',
    type: 'string',
    label: 'config.providers.openrouterApiKey',
    default: '',
    group: 'providers',
    sensitive: true,
    condition: { field: 'llm.provider', value: 'openrouter', operator: 'eq' },
  },
  // Ollama
  {
    key: 'providers.ollama.api_base',
    type: 'string',
    label: 'config.providers.apiBase',
    default: 'http://localhost:11434/v1',
    group: 'providers',
    condition: { field: 'llm.provider', value: 'ollama', operator: 'eq' },
  },
]

/**
 * Security 配置分组
 */
const securityFields: ConfigFieldSchema[] = [
  {
    key: 'security.allow_all_access',
    type: 'boolean',
    label: 'config.security.allowAllAccess',
    description: 'config.security.allowAllAccessDesc',
    default: false,
    group: 'security',
  },
  {
    key: 'security.restrict_to_workspace',
    type: 'boolean',
    label: 'config.security.restrictToWorkspace',
    description: 'config.security.restrictToWorkspaceDesc',
    default: true,
    group: 'security',
  },
  {
    key: 'security.extra_allowed_dirs',
    type: 'array',
    label: 'config.security.extraAllowedDirs',
    description: 'config.security.extraAllowedDirsDesc',
    default: [],
    group: 'security',
    advanced: true,
  },
  {
    key: 'security.allow_symlinks',
    type: 'boolean',
    label: 'config.security.allowSymlinks',
    description: 'config.security.allowSymlinksDesc',
    default: true,
    group: 'security',
    advanced: true,
  },
  {
    key: 'security.ssrf_enabled',
    type: 'boolean',
    label: 'config.security.ssrfEnabled',
    description: 'config.security.ssrfEnabledDesc',
    default: true,
    group: 'security',
  },
  {
    key: 'security.ssrf_allowed_networks',
    type: 'array',
    label: 'config.security.ssrfAllowedNetworks',
    description: 'config.security.ssrfAllowedNetworksDesc',
    default: [],
    group: 'security',
    advanced: true,
  },
  {
    key: 'security.ssrf_allowed_domains',
    type: 'array',
    label: 'config.security.ssrfAllowedDomains',
    description: 'config.security.ssrfAllowedDomainsDesc',
    default: [],
    group: 'security',
    advanced: true,
  },
  {
    key: 'security.exec_deny_patterns',
    type: 'array',
    label: 'config.security.execDenyPatterns',
    description: 'config.security.execDenyPatternsDesc',
    default: [],
    group: 'security',
    advanced: true,
  },
  {
    key: 'security.exec_allow_patterns',
    type: 'array',
    label: 'config.security.execAllowPatterns',
    description: 'config.security.execAllowPatternsDesc',
    default: [],
    group: 'security',
    advanced: true,
  },
  {
    key: 'security.exec_unrestricted',
    type: 'boolean',
    label: 'config.security.execUnrestricted',
    description: 'config.security.execUnrestrictedDesc',
    default: false,
    group: 'security',
    advanced: true,
  },
  {
    key: 'security.search_allow_all_paths',
    type: 'boolean',
    label: 'config.security.searchAllowAllPaths',
    description: 'config.security.searchAllowAllPathsDesc',
    default: true,
    group: 'security',
    advanced: true,
  },
  {
    key: 'security.search_max_depth',
    type: 'number',
    label: 'config.security.searchMaxDepth',
    default: 4,
    group: 'security',
    validation: { min: 1, max: 20 },
    advanced: true,
  },
  {
    key: 'security.search_timeout',
    type: 'number',
    label: 'config.security.searchTimeout',
    default: 10.0,
    group: 'security',
    validation: { min: 1, max: 300 },
    advanced: true,
  },
]

/**
 * Memory 配置分组
 */
const memoryFields: ConfigFieldSchema[] = [
  {
    key: 'memory.enabled',
    type: 'boolean',
    label: 'config.memory.enabled',
    description: 'config.memory.enabledDesc',
    default: true,
    group: 'memory',
  },
  {
    key: 'memory.max_chars',
    type: 'number',
    label: 'config.memory.maxChars',
    description: 'config.memory.maxCharsDesc',
    default: 10000,
    group: 'memory',
    validation: { min: 1000, max: 100000 },
  },
  {
    key: 'memory.daily_load_days',
    type: 'number',
    label: 'config.memory.dailyLoadDays',
    description: 'config.memory.dailyLoadDaysDesc',
    default: 2,
    group: 'memory',
    validation: { min: 0, max: 30 },
  },
  {
    key: 'memory.auto_update',
    type: 'boolean',
    label: 'config.memory.autoUpdate',
    description: 'config.memory.autoUpdateDesc',
    default: false,
    group: 'memory',
  },
]

/**
 * Compression 配置分组
 */
const compressionFields: ConfigFieldSchema[] = [
  {
    key: 'compression.enabled',
    type: 'boolean',
    label: 'config.compression.enabled',
    description: 'config.compression.enabledDesc',
    default: true,
    group: 'compression',
  },
  {
    key: 'compression.threshold',
    type: 'number',
    label: 'config.compression.threshold',
    description: 'config.compression.thresholdDesc',
    default: 10,
    group: 'compression',
    validation: { min: 1, max: 100 },
  },
  {
    key: 'compression.keep_recent',
    type: 'number',
    label: 'config.compression.keepRecent',
    description: 'config.compression.keepRecentDesc',
    default: 5,
    group: 'compression',
    validation: { min: 1, max: 50 },
  },
  {
    key: 'compression.strategy',
    type: 'enum',
    label: 'config.compression.strategy',
    description: 'config.compression.strategyDesc',
    default: 'truncate',
    group: 'compression',
    validation: {
      enum: ['summary', 'truncate', 'key_points'],
    },
  },
]

/**
 * Streaming 配置分组
 */
const streamingFields: ConfigFieldSchema[] = [
  {
    key: 'streaming.enabled',
    type: 'boolean',
    label: 'config.streaming.enabled',
    description: 'config.streaming.enabledDesc',
    default: true,
    group: 'streaming',
  },
  {
    key: 'streaming.buffer_size',
    type: 'number',
    label: 'config.streaming.bufferSize',
    description: 'config.streaming.bufferSizeDesc',
    default: 10,
    group: 'streaming',
    validation: { min: 1, max: 100 },
    advanced: true,
  },
]

/**
 * Tools 配置分组
 */
const toolsFields: ConfigFieldSchema[] = [
  {
    key: 'tools.timeout',
    type: 'number',
    label: 'config.tools.timeout',
    description: 'config.tools.timeoutDesc',
    default: 60,
    group: 'tools',
    validation: { min: 1, max: 3600 },
  },
  {
    key: 'tools.max_iterations',
    type: 'number',
    label: 'config.tools.maxIterations',
    description: 'config.tools.maxIterationsDesc',
    default: 10,
    group: 'tools',
    validation: { min: 1, max: 100 },
  },
]

/**
 * Session 配置分组
 */
const sessionFields: ConfigFieldSchema[] = [
  {
    key: 'session.max_concurrent_sessions',
    type: 'number',
    label: 'config.session.maxConcurrent',
    description: 'config.session.maxConcurrentDesc',
    default: 3,
    group: 'session',
    validation: { min: 1, max: 50 },
  },
]

/**
 * Channels 配置分组
 */
const channelsFields: ConfigFieldSchema[] = [
  // CLI Channel
  {
    key: 'channels.cli.enabled',
    type: 'boolean',
    label: 'config.channels.cliEnabled',
    description: 'config.channels.cliEnabledDesc',
    default: true,
    group: 'channels',
  },
  {
    key: 'channels.cli.prompt',
    type: 'string',
    label: 'config.channels.cliPrompt',
    default: 'You: ',
    group: 'channels',
    advanced: true,
  },
  {
    key: 'channels.cli.agent_name',
    type: 'string',
    label: 'config.channels.cliAgentName',
    default: 'AnyClaw',
    group: 'channels',
    advanced: true,
  },
  // Feishu Channel
  {
    key: 'channels.feishu.enabled',
    type: 'boolean',
    label: 'config.channels.feishuEnabled',
    description: 'config.channels.feishuEnabledDesc',
    default: false,
    group: 'channels',
  },
  {
    key: 'channels.feishu.app_id',
    type: 'string',
    label: 'config.channels.feishuAppId',
    default: '',
    group: 'channels',
    condition: { field: 'channels.feishu.enabled', value: true, operator: 'eq' },
  },
  {
    key: 'channels.feishu.app_secret',
    type: 'string',
    label: 'config.channels.feishuAppSecret',
    default: '',
    group: 'channels',
    sensitive: true,
    condition: { field: 'channels.feishu.enabled', value: true, operator: 'eq' },
  },
  {
    key: 'channels.feishu.encrypt_key',
    type: 'string',
    label: 'config.channels.feishuEncryptKey',
    default: '',
    group: 'channels',
    advanced: true,
    condition: { field: 'channels.feishu.enabled', value: true, operator: 'eq' },
  },
  {
    key: 'channels.feishu.verification_token',
    type: 'string',
    label: 'config.channels.feishuVerificationToken',
    default: '',
    group: 'channels',
    advanced: true,
    condition: { field: 'channels.feishu.enabled', value: true, operator: 'eq' },
  },
  // Discord Channel
  {
    key: 'channels.discord.enabled',
    type: 'boolean',
    label: 'config.channels.discordEnabled',
    description: 'config.channels.discordEnabledDesc',
    default: false,
    group: 'channels',
  },
  {
    key: 'channels.discord.token',
    type: 'string',
    label: 'config.channels.discordToken',
    default: '',
    group: 'channels',
    sensitive: true,
    condition: { field: 'channels.discord.enabled', value: true, operator: 'eq' },
  },
  {
    key: 'channels.discord.group_policy',
    type: 'enum',
    label: 'config.channels.discordGroupPolicy',
    default: 'mention',
    group: 'channels',
    validation: { enum: ['mention', 'open'] },
    condition: { field: 'channels.discord.enabled', value: true, operator: 'eq' },
  },
]

/**
 * MCP Servers 配置分组 (仅显示说明，实际配置通过 Advanced 模式编辑)
 * 由于 mcp_servers 是动态字典结构，表单模式只显示基本说明
 */
const mcpServerFields: ConfigFieldSchema[] = [
  {
    key: '_mcp_servers_note',
    type: 'string',
    label: 'config.mcpServers.note',
    description: 'config.mcpServers.noteDesc',
    default: '',
    group: 'mcp_servers',
    placeholder: 'config.mcpServers.notePlaceholder',
  },
]

/**
 * 配置分组定义
 */
export const configGroups: ConfigGroupSchema[] = [
  {
    id: 'agent',
    label: 'config.groups.agent',
    description: 'config.groups.agentDesc',
    icon: Bot,
    fields: agentFields,
    order: 1,
  },
  {
    id: 'llm',
    label: 'config.groups.llm',
    description: 'config.groups.llmDesc',
    icon: Cpu,
    fields: llmFields,
    order: 2,
  },
  {
    id: 'providers',
    label: 'config.groups.providers',
    description: 'config.groups.providersDesc',
    icon: Key,
    fields: providerFields,
    order: 3,
  },
  {
    id: 'channels',
    label: 'config.groups.channels',
    description: 'config.groups.channelsDesc',
    icon: MessageSquare,
    fields: channelsFields,
    order: 4,
    defaultCollapsed: true,
  },
  {
    id: 'mcp_servers',
    label: 'config.groups.mcpServers',
    description: 'config.groups.mcpServersDesc',
    icon: Server,
    fields: mcpServerFields,
    order: 5,
    defaultCollapsed: true,
  },
  {
    id: 'security',
    label: 'config.groups.security',
    description: 'config.groups.securityDesc',
    icon: Shield,
    fields: securityFields,
    order: 6,
    defaultCollapsed: true,
  },
  {
    id: 'memory',
    label: 'config.groups.memory',
    description: 'config.groups.memoryDesc',
    icon: Brain,
    fields: memoryFields,
    order: 7,
  },
  {
    id: 'compression',
    label: 'config.groups.compression',
    description: 'config.groups.compressionDesc',
    icon: Minimize2,
    fields: compressionFields,
    order: 8,
    defaultCollapsed: true,
  },
  {
    id: 'streaming',
    label: 'config.groups.streaming',
    description: 'config.groups.streamingDesc',
    icon: Activity,
    fields: streamingFields,
    order: 9,
    defaultCollapsed: true,
  },
  {
    id: 'tools',
    label: 'config.groups.tools',
    description: 'config.groups.toolsDesc',
    icon: Wrench,
    fields: toolsFields,
    order: 10,
    defaultCollapsed: true,
  },
  {
    id: 'session',
    label: 'config.groups.session',
    description: 'config.groups.sessionDesc',
    icon: Users,
    fields: sessionFields,
    order: 11,
    defaultCollapsed: true,
  },
]

/**
 * 获取所有字段（扁平化）
 */
export function getAllFields(): ConfigFieldSchema[] {
  return configGroups.flatMap((group) => group.fields)
}

/**
 * 根据 key 获取字段 Schema
 */
export function getFieldSchema(key: string): ConfigFieldSchema | undefined {
  return getAllFields().find((field) => field.key === key)
}

/**
 * 获取字段的默认值
 */
export function getFieldDefaults(): Record<string, any> {
  const defaults: Record<string, any> = {}
  for (const field of getAllFields()) {
    const parts = field.key.split('.')
    let current = defaults
    for (let i = 0; i < parts.length - 1; i++) {
      if (!current[parts[i]]) {
        current[parts[i]] = {}
      }
      current = current[parts[i]]
    }
    current[parts[parts.length - 1]] = field.default
  }
  return defaults
}

/**
 * 根据分组 ID 获取分组
 */
export function getGroupById(id: string): ConfigGroupSchema | undefined {
  return configGroups.find((group) => group.id === id)
}
