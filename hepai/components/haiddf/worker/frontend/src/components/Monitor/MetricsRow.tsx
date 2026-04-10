import { Card, Row, Col, Statistic } from 'antd'
import {
  ThunderboltOutlined,
  ClockCircleOutlined,
  BarChartOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'
import type { MonitorStatus } from '../../api/worker'

interface Props {
  data: MonitorStatus
}

export default function MetricsRow({ data }: Props) {
  const utilization =
    data.total_limit > 0
      ? Math.round((data.total_active / data.total_limit) * 100)
      : 0

  return (
    <Row gutter={16} style={{ marginBottom: 16 }}>
      <Col span={6}>
        <Card size="small">
          <Statistic
            title="正在处理"
            value={data.total_active}
            prefix={<ThunderboltOutlined style={{ color: '#1677ff' }} />}
            suffix={`/ ${data.total_limit}`}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card size="small">
          <Statistic
            title="等待队列"
            value={data.total_queue}
            prefix={<ClockCircleOutlined style={{ color: '#faad14' }} />}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card size="small">
          <Statistic
            title="利用率"
            value={utilization}
            suffix="%"
            prefix={<BarChartOutlined style={{ color: utilization > 80 ? '#ff4d4f' : '#52c41a' }} />}
          />
        </Card>
      </Col>
      <Col span={6}>
        <Card size="small">
          <Statistic
            title="总请求数"
            value={data.global_counter}
            prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
          />
        </Card>
      </Col>
    </Row>
  )
}
