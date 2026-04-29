import { Menu } from 'antd'
import { BarChartOutlined, AppstoreOutlined } from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'

const items = [
  { key: '/monitor', icon: <BarChartOutlined />, label: 'Worker配置' },
  { key: '/management', icon: <AppstoreOutlined />, label: '模型配置' },
]

export default function AppSidebar() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Menu
      mode="inline"
      selectedKeys={[location.pathname || '/monitor']}
      items={items}
      onClick={({ key }) => navigate(key)}
      style={{ height: '100%', borderRight: 0 }}
    />
  )
}
