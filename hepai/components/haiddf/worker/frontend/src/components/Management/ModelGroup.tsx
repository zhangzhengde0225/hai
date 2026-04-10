import { Card, Switch, Space, Button, List, Typography, Tag } from 'antd'
import type { ModelItem } from '../../api/models'

const { Text } = Typography

interface Props {
  provider: string
  models: ModelItem[]
  pendingChanges: Record<string, boolean>
  onToggle: (modelName: string, enabled: boolean) => void
  onEnableAll: (provider: string) => void
  onDisableAll: (provider: string) => void
  filterEnabled: boolean
}

export default function ModelGroup({
  provider,
  models,
  pendingChanges,
  onToggle,
  onEnableAll,
  onDisableAll,
  filterEnabled,
}: Props) {
  const displayModels = filterEnabled
    ? models.filter((m) => (pendingChanges[m.name] ?? m.enabled))
    : models

  const enabledCount = models.filter((m) => (pendingChanges[m.name] ?? m.enabled)).length

  return (
    <Card
      size="small"
      style={{ marginBottom: 12 }}
      title={
        <Space>
          <Text strong>{provider}</Text>
          <Tag color="blue">{enabledCount}/{models.length} 启用</Tag>
        </Space>
      }
      extra={
        <Space size={8}>
          <Button size="small" onClick={() => onEnableAll(provider)}>全部启用</Button>
          <Button size="small" danger onClick={() => onDisableAll(provider)}>全部禁用</Button>
        </Space>
      }
    >
      <List
        size="small"
        dataSource={displayModels}
        renderItem={(model) => {
          const currentEnabled = pendingChanges[model.name] ?? model.enabled
          const isDirty = model.name in pendingChanges && pendingChanges[model.name] !== model.enabled

          return (
            <List.Item
              style={{
                padding: '6px 0',
                background: isDirty ? '#fffbe6' : undefined,
                borderRadius: 4,
                paddingLeft: isDirty ? 8 : 0,
              }}
              actions={[
                <Switch
                  key="switch"
                  size="small"
                  checked={currentEnabled}
                  onChange={(checked) => onToggle(model.name, checked)}
                />,
              ]}
            >
              <Space>
                <code style={{ fontSize: 12 }}>{model.name}</code>
                {isDirty && (
                  <Tag color="orange" style={{ fontSize: 11 }}>
                    {currentEnabled ? '待启用' : '待禁用'}
                  </Tag>
                )}
              </Space>
            </List.Item>
          )
        }}
      />
    </Card>
  )
}
