import { Card, Table, Progress, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import type { MonitorStatus, ModelConcurrencyStatus } from '../../api/worker'

interface Row extends ModelConcurrencyStatus {
  key: string
  modelName: string
  utilization: number
}

interface Props {
  monitor: MonitorStatus
}

const columns: ColumnsType<Row> = [
  {
    title: '模型名',
    dataIndex: 'modelName',
    key: 'modelName',
    render: (v: string) => <code style={{ fontSize: 12 }}>{v}</code>,
    ellipsis: true,
  },
  {
    title: '活跃',
    dataIndex: 'active',
    key: 'active',
    width: 70,
    align: 'center',
    render: (v: number) => <Tag color={v > 0 ? 'blue' : 'default'}>{v}</Tag>,
  },
  {
    title: '队列',
    dataIndex: 'queue',
    key: 'queue',
    width: 70,
    align: 'center',
    render: (v: number) => <Tag color={v > 0 ? 'orange' : 'default'}>{v}</Tag>,
  },
  {
    title: '可用',
    dataIndex: 'available',
    key: 'available',
    width: 70,
    align: 'center',
  },
  {
    title: '上限',
    dataIndex: 'limit',
    key: 'limit',
    width: 70,
    align: 'center',
  },
  {
    title: '利用率',
    dataIndex: 'utilization',
    key: 'utilization',
    width: 160,
    render: (v: number) => (
      <Progress
        percent={v}
        size="small"
        strokeColor={v > 80 ? '#ff4d4f' : v > 50 ? '#faad14' : '#52c41a'}
        style={{ marginBottom: 0 }}
      />
    ),
  },
]

export default function ModelTable({ monitor }: Props) {
  const rows: Row[] = Object.entries(monitor.model_status).map(([name, s]) => ({
    key: name,
    modelName: name,
    active: s.active,
    queue: s.queue,
    available: s.available,
    limit: s.limit,
    utilization: s.limit > 0 ? Math.round((s.active / s.limit) * 100) : 0,
  }))

  return (
    <Card
      title={`模型并发状态（${monitor.model_count} 个模型）`}
      size="small"
    >
      <Table
        columns={columns}
        dataSource={rows}
        pagination={false}
        size="small"
        scroll={{ x: true }}
      />
    </Card>
  )
}
