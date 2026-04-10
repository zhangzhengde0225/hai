const PREFIX = '/apiv2'

async function get<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

async function post<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

// ── Types ─────────────────────────────────────────────────────────────────

export interface NetworkInfo {
  host: string
  port: number
  route_prefix: string
  host_name: string
  worker_address: string
}

export interface ModelResourceInfo {
  model_name: string
  model_type: string
  model_version: string
  model_description: string
  model_functions: string[]
  id: string
  created: number
  object: string
  owned_by: string
}

export interface StatusInfo {
  speed: number
  queue_length: number
  status: 'idle' | 'ready' | 'busy' | 'error'
  start_time: number | null
}

export interface WorkerInfo {
  id: string
  type: string
  network_info: NetworkInfo
  resource_info: ModelResourceInfo[]
  status_info: StatusInfo
  check_heartbeat: boolean
  last_heartbeat: number
  version: string
  metadata: {
    uptime: number
    limit_model_concurrency: number
    description: string
    author: string
    permissions: { groups: string[]; users: string[]; owner: string | null }
    worker_name?: string | null
  }
}

export interface ModelConcurrencyStatus {
  active: number
  queue: number
  available: number
  limit: number
}

export interface MonitorStatus {
  timestamp: number
  total_active: number
  total_queue: number
  total_limit: number
  model_status: Record<string, ModelConcurrencyStatus>
  worker_id: string
  model_count: number
  global_counter: number
}

// ── API calls ─────────────────────────────────────────────────────────────

export const fetchWorkerInfo = () =>
  post<WorkerInfo>(`${PREFIX}/worker/get_worker_info`, {})

export const fetchMonitorStatus = () =>
  get<MonitorStatus>(`${PREFIX}/worker/monitor_status`)
