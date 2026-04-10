import { useState } from 'react'
import { Alert, Spin, Button, Space, Typography, Checkbox } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { fetchWorkerInfo, fetchMonitorStatus } from '../api/worker'
import WorkerInfoCard from '../components/Monitor/WorkerInfoCard'
import MetricsRow from '../components/Monitor/MetricsRow'
import ModelTable from '../components/Monitor/ModelTable'

const { Text } = Typography

export default function MonitorPage() {
  const [autoRefresh, setAutoRefresh] = useState(true)

  const {
    data: workerInfo,
    isLoading: loadingInfo,
    error: errorInfo,
    refetch: refetchInfo,
  } = useQuery({
    queryKey: ['workerInfo'],
    queryFn: fetchWorkerInfo,
    refetchInterval: autoRefresh ? 10_000 : false,
  })

  const {
    data: monitorStatus,
    isLoading: loadingMonitor,
    error: errorMonitor,
    refetch: refetchMonitor,
    dataUpdatedAt,
  } = useQuery({
    queryKey: ['monitorStatus'],
    queryFn: fetchMonitorStatus,
    refetchInterval: autoRefresh ? 3_000 : false,
  })

  const handleRefresh = () => {
    refetchInfo()
    refetchMonitor()
  }

  const isLoading = loadingInfo || loadingMonitor

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>实时监控</Typography.Title>
        <Space>
          {dataUpdatedAt > 0 && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              更新于 {new Date(dataUpdatedAt).toLocaleTimeString()}
            </Text>
          )}
          <Checkbox
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
          >
            自动刷新
          </Checkbox>
          <Button icon={<ReloadOutlined />} onClick={handleRefresh} size="small">
            刷新
          </Button>
        </Space>
      </div>

      {(errorInfo || errorMonitor) && (
        <Alert
          type="error"
          message="无法连接到 Worker"
          description={(errorInfo as Error)?.message || (errorMonitor as Error)?.message}
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {isLoading && !workerInfo && !monitorStatus ? (
        <div style={{ textAlign: 'center', padding: 64 }}>
          <Spin size="large" tip="加载中..." />
        </div>
      ) : (
        <>
          {workerInfo && <WorkerInfoCard data={workerInfo} />}
          {monitorStatus && <MetricsRow data={monitorStatus} />}
          {monitorStatus && <ModelTable monitor={monitorStatus} />}
        </>
      )}
    </div>
  )
}
