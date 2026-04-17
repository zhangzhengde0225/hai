import { useState } from 'react'
import { Card, Table, Switch, Space, Button, Typography, Tag, Popconfirm, message } from 'antd'
import { EditOutlined, SettingOutlined, PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { ModelConfig } from '../../api/models'
import { deleteModel } from '../../api/models'
import ModelConfigDrawer from './ModelConfigDrawer'
import ProviderConfigDrawer from './ProviderConfigDrawer'
import AddModelDrawer from './AddModelDrawer'

const { Text } = Typography

interface Props {
  provider: string
  models: ModelConfig[]
  token: string
  pendingChanges: Record<string, boolean>
  onToggle: (modelName: string, enabled: boolean) => void
  onEnableAll: (provider: string) => void
  onDisableAll: (provider: string) => void
  filterEnabled: boolean
  onRefresh: () => void
}

export default function ModelGroup({
  provider,
  models,
  token,
  pendingChanges,
  onToggle,
  onEnableAll,
  onDisableAll,
  filterEnabled,
  onRefresh,
}: Props) {
  const [editingModel, setEditingModel] = useState<ModelConfig | null>(null)
  const [providerDrawerOpen, setProviderDrawerOpen] = useState(false)
  const [addDrawerOpen, setAddDrawerOpen] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)

  const handleDelete = async (modelId: string) => {
    setDeleting(modelId)
    try {
      await deleteModel(modelId, provider, token)
      message.success(`已删除 ${modelId}`)
      onRefresh()
    } catch (e: unknown) {
      message.error(`删除失败: ${e instanceof Error ? e.message : String(e)}`)
    } finally {
      setDeleting(null)
    }
  }

  const displayModels = filterEnabled
    ? models.filter((m) => (pendingChanges[m.id] ?? m.enabled))
    : models

  const enabledCount = models.filter((m) => (pendingChanges[m.id] ?? m.enabled)).length

  const columns: ColumnsType<ModelConfig> = [
    {
      title: '模型 ID',
      dataIndex: 'id',
      key: 'id',
      render: (id: string, record) => {
        const isDirty = id in pendingChanges && pendingChanges[id] !== record.enabled
        return (
          <Space>
            <code style={{ fontSize: 12 }}>{id}</code>
            {isDirty && (
              <Tag color="orange" style={{ fontSize: 11 }}>
                {pendingChanges[id] ? '待启用' : '待禁用'}
              </Tag>
            )}
          </Space>
        )
      },
    },
    {
      title: 'Proxy',
      dataIndex: 'proxy',
      key: 'proxy',
      width: 180,
      render: (proxy: string | null) =>
        proxy ? (
          <Text type="secondary" style={{ fontSize: 11 }} ellipsis={{ tooltip: proxy }}>
            {proxy}
          </Text>
        ) : (
          <Text type="secondary" style={{ fontSize: 11 }}>—</Text>
        ),
    },
    {
      title: 'Max Tokens',
      dataIndex: 'maxTokens',
      key: 'maxTokens',
      width: 100,
      render: (v?: number) =>
        v != null ? <Text style={{ fontSize: 12 }}>{v.toLocaleString()}</Text> : <Text type="secondary" style={{ fontSize: 11 }}>—</Text>,
    },
    {
      title: '启用',
      key: 'enabled',
      width: 70,
      render: (_: unknown, record) => {
        const currentEnabled = pendingChanges[record.id] ?? record.enabled
        return (
          <Switch
            size="small"
            checked={currentEnabled}
            onChange={(checked) => onToggle(record.id, checked)}
          />
        )
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 130,
      render: (_: unknown, record) => (
        <Space size={4}>
          <Button
            size="small"
            icon={<EditOutlined />}
            onClick={() => setEditingModel(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title={`删除 ${record.id}？`}
            description="删除后不可恢复"
            okText="删除"
            okType="danger"
            cancelText="取消"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button
              size="small"
              danger
              icon={<DeleteOutlined />}
              loading={deleting === record.id}
            />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <>
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
            <Button size="small" icon={<SettingOutlined />} onClick={() => setProviderDrawerOpen(true)}>
              Provider 配置
            </Button>
            <Button size="small" icon={<PlusOutlined />} onClick={() => setAddDrawerOpen(true)}>
              添加模型
            </Button>
            <Button size="small" onClick={() => onEnableAll(provider)}>全部启用</Button>
            <Button size="small" danger onClick={() => onDisableAll(provider)}>全部禁用</Button>
          </Space>
        }
      >
        <Table
          size="small"
          dataSource={displayModels}
          columns={columns}
          rowKey="id"
          pagination={false}
          rowClassName={(record) =>
            record.id in pendingChanges && pendingChanges[record.id] !== record.enabled
              ? 'row-dirty'
              : ''
          }
        />
      </Card>

      <ModelConfigDrawer
        open={editingModel !== null}
        model={editingModel}
        token={token}
        onClose={() => setEditingModel(null)}
        onSaved={() => {
          setEditingModel(null)
          onRefresh()
        }}
      />

      <ProviderConfigDrawer
        open={providerDrawerOpen}
        providerName={provider}
        token={token}
        onClose={() => setProviderDrawerOpen(false)}
        onSaved={() => {
          setProviderDrawerOpen(false)
          onRefresh()
        }}
      />

      <AddModelDrawer
        open={addDrawerOpen}
        providerName={provider}
        token={token}
        onClose={() => setAddDrawerOpen(false)}
        onSaved={() => {
          setAddDrawerOpen(false)
          onRefresh()
        }}
      />
    </>
  )
}
