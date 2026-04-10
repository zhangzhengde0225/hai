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
