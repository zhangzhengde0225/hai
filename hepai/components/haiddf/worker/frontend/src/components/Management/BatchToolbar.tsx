import { Space, Button, Segmented, Badge, Tooltip } from 'antd'
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons'

interface Props {
  pendingCount: number
  filterEnabled: boolean
  saving: boolean
  onFilterChange: (v: boolean) => void
  onSave: () => void
  onRefresh: () => void
}

export default function BatchToolbar({
  pendingCount,
  filterEnabled,
  saving,
  onFilterChange,
  onSave,
  onRefresh,
}: Props) {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 16,
        padding: '10px 16px',
        background: '#fff',
        borderRadius: 8,
        border: '1px solid #f0f0f0',
      }}
    >
      <Segmented
        options={[
          { label: '显示全部', value: 'all' },
          { label: '仅启用', value: 'enabled' },
        ]}
        value={filterEnabled ? 'enabled' : 'all'}
        onChange={(v) => onFilterChange(v === 'enabled')}
      />

      <Space>
        <Tooltip title="重新加载配置">
          <Button icon={<ReloadOutlined />} onClick={onRefresh} size="middle">
            刷新
          </Button>
        </Tooltip>
        <Badge count={pendingCount} size="small" offset={[-4, 4]}>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            loading={saving}
            disabled={pendingCount === 0}
            onClick={onSave}
          >
            保存更改{pendingCount > 0 ? ` (${pendingCount})` : ''}
          </Button>
        </Badge>
      </Space>
    </div>
  )
}
