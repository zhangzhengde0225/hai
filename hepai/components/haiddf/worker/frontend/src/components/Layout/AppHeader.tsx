import { Badge, Space, Typography, Button, Tooltip } from 'antd'
import { LogoutOutlined } from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { fetchWorkerInfo } from '../../api/worker'
import { useAuthStore } from '../../store/authStore'
import logo from '../../assets/hepai.png'

const { Text } = Typography

export default function AppHeader() {
  const { data } = useQuery({
    queryKey: ['workerInfo'],
    queryFn: fetchWorkerInfo,
    refetchInterval: 10_000,
  })

  const token = useAuthStore((s) => s.token)
  const clearToken = useAuthStore((s) => s.clearToken)

  const status = data?.status_info?.status ?? 'idle'
  const statusColor: Record<string, string> = {
    ready: 'green',
    busy: 'yellow',
    idle: 'blue',
    error: 'red',
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '100%',
        padding: '0 24px',
      }}
    >
      <Space size={12}>
        <img src={logo} alt="HepAI" style={{ height: 28, verticalAlign: 'middle' }} />
        <span style={{ fontSize: 20, fontWeight: 700, color: '#fff', letterSpacing: 1 }}>
          HepAI Worker
        </span>
        {data?.metadata?.worker_name && (
          <span style={{
            fontSize: 13,
            color: 'rgba(255,255,255,0.65)',
            background: 'rgba(255,255,255,0.1)',
            padding: '2px 10px',
            borderRadius: 12,
          }}>
            {data.metadata.worker_name}
          </span>
        )}
      </Space>

      <Space size={16}>
        {data && (
          <>
            <Badge color={statusColor[status] ?? 'default'} text={
              <Text style={{ color: 'rgba(255,255,255,0.85)' }}>
                {data.id}
              </Text>
            } />
            <Text style={{ color: 'rgba(255,255,255,0.55)', fontSize: 12 }}>
              {data.network_info?.worker_address}
            </Text>
            <Text style={{ color: 'rgba(255,255,255,0.55)', fontSize: 12 }}>
              v{data.version}
            </Text>
          </>
        )}
        {token && (
          <Tooltip title="退出登录，清空凭据">
            <Button
              type="text"
              icon={<LogoutOutlined />}
              onClick={clearToken}
              style={{ color: 'rgba(255,255,255,0.65)' }}
            />
          </Tooltip>
        )}
      </Space>
    </div>
  )
}
