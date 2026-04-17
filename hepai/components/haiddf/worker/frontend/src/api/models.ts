const PREFIX = '/apiv2'

async function authGet<T>(url: string, token: string): Promise<T> {
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (res.status === 401) throw new Error('UNAUTHORIZED')
  if (res.status === 403) throw new Error('FORBIDDEN')
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

async function authPost<T>(url: string, body: unknown, token: string): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  })
  if (res.status === 401) throw new Error('UNAUTHORIZED')
  if (res.status === 403) throw new Error('FORBIDDEN')
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

async function authPut<T>(url: string, body: unknown, token: string): Promise<T> {
  const res = await fetch(url, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  })
  if (res.status === 401) throw new Error('UNAUTHORIZED')
  if (res.status === 403) throw new Error('FORBIDDEN')
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

// ── Types ─────────────────────────────────────────────────────────────────

export interface ModelItem {
  name: string
  enabled: boolean
}

export interface GroupedModels {
  success: boolean
  data: Record<string, ModelItem[]>
  timestamp: number
}

export interface ModelStatusMap {
  success: boolean
  models: Record<string, boolean>
  timestamp: number
}

export interface BatchUpdateItem {
  model_name: string
  enabled: boolean
}

export interface ModelCost {
  input: number
  output: number
  cacheRead?: number
  cacheWrite?: number
}

export interface ModelConfig {
  id: string
  name?: string
  engine?: string
  enabled: boolean
  api?: string | string[]
  appendAnthropicPath?: boolean
  reasoning?: boolean
  input?: string[]
  cost?: ModelCost
  contextWindow?: number
  maxTokens?: number
  proxy?: string | null
  endpoint_version?: string
}

export interface ModelConfigsResponse {
  success: boolean
  data: Record<string, ModelConfig[]>
  timestamp: number
}

export interface BatchUpdateResult {
  success: boolean
  results: Array<{
    model_name: string
    enabled?: boolean
    success: boolean
    error?: string
  }>
  count: number
}

// ── API calls ─────────────────────────────────────────────────────────────

export const verifyAdminPassword = (token: string) =>
  authGet<ModelStatusMap>(`${PREFIX}/models/status`, token)

export const fetchGroupedModels = (token: string) =>
  authGet<GroupedModels>(`${PREFIX}/models/grouped`, token)

export const batchUpdate = (updates: BatchUpdateItem[], token: string) =>
  authPost<BatchUpdateResult>(`${PREFIX}/models/batch_update`, { updates }, token)

export const fetchModelConfigs = (token: string) =>
  authGet<ModelConfigsResponse>(`${PREFIX}/models/configs`, token)

export const updateModelConfig = (
  modelId: string,
  updates: Partial<ModelConfig>,
  token: string
) => authPut<{ success: boolean }>(`${PREFIX}/models/config`, { model_id: modelId, updates }, token)

export interface ProviderConfig {
  baseUrl?: string
  apiKey?: string
  api?: string | string[]
  proxy?: string | null
  needExternalApiKey?: boolean
  appendAnthropicPath?: boolean
}

export interface ProviderConfigsResponse {
  success: boolean
  data: Record<string, ProviderConfig>
  timestamp: number
}

export const fetchProviderConfigs = (token: string) =>
  authGet<ProviderConfigsResponse>(`${PREFIX}/providers/configs`, token)

export const updateProviderConfig = (
  providerName: string,
  updates: ProviderConfig,
  token: string
) => authPut<{ success: boolean }>(`${PREFIX}/providers/config`, { provider_name: providerName, updates }, token)

async function authDelete<T>(url: string, body: unknown, token: string): Promise<T> {
  const res = await fetch(url, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  })
  if (res.status === 401) throw new Error('UNAUTHORIZED')
  if (res.status === 403) throw new Error('FORBIDDEN')
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export const addModel = (
  providerName: string,
  model: Partial<ModelConfig> & { id: string },
  token: string
) => authPost<{ success: boolean }>(`${PREFIX}/models/model`, { provider_name: providerName, model }, token)

export const deleteModel = (
  modelId: string,
  providerName: string,
  token: string
) => authDelete<{ success: boolean }>(`${PREFIX}/models/model`, { model_id: modelId, provider_name: providerName }, token)
