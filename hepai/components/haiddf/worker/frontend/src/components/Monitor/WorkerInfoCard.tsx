import { Card, Descriptions, Badge, Tag } from 'antd'
import type { WorkerInfo } from '../../api/worker'

interface Props {
  data: WorkerInfo
}

function formatUptime(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) return `${h}h ${m}m`
  if (m > 0) return `${m}m ${s}s`
  return `${s}s`
}

const statusConfig: Record<string, { color: 'success' | 'warning' | 'processing' | 'error'; text: string }> = {
  ready:   { color: 'success',    text: 'Ready' },
  busy:    { color: 'warning',    text: 'Busy' },
  idle:    { color: 'processing', text: 'Idle' },
  error:   { color: 'error',      text: 'Error' },
}

export default function WorkerInfoCard({ data }: Props) {
  const { id, type, network_info, status_info, metadata } = data
  const sc = statusConfig[status_info.status] ?? { color: 'default', text: status_info.status }

  return (
    <Card title="Worker 信息" size="small" style={{ marginBottom: 16 }}>
      <Descriptions size="small" column={3} bordered>
        <Descriptions.Item label="Worker ID">
          <code style={{ fontSize: 12 }}>{id}</code>
        </Descriptions.Item>
        <Descriptions.Item label="类型">
          <Tag color="blue">{type}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="状态">
          <Badge status={sc.color} text={sc.text} />
        </Descriptions.Item>

        <Descriptions.Item label="地址" span={2}>
          {network_info?.worker_address}
        </Descriptions.Item>
        <Descriptions.Item label="运行时长">
          {metadata?.uptime != null ? formatUptime(metadata.uptime) : '—'}
        </Descriptions.Item>

        <Descriptions.Item label="并发上限">
          {metadata?.limit_model_concurrency ?? '—'}
        </Descriptions.Item>
        <Descriptions.Item label="队列长度">
          {status_info.queue_length}
        </Descriptions.Item>
        <Descriptions.Item label="处理速度">
          {status_info.speed} req/s
        </Descriptions.Item>

        {metadata?.description && (
          <Descriptions.Item label="描述" span={3}>
            {metadata.description}
          </Descriptions.Item>
        )}
      </Descriptions>
    </Card>
  )
}
