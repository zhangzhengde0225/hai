import { useEffect, useState } from 'react'
import {
  Drawer, Form, Input, InputNumber, Switch, Select, Button, Space, Typography, message,
} from 'antd'
import type { WorkerInfo, WorkerConfigUpdates } from '../../api/worker'
import { updateWorkerConfig } from '../../api/worker'
import { useAuthStore } from '../../store/authStore'

const { Text } = Typography

interface Props {
  open: boolean
  workerInfo: WorkerInfo | undefined
  onClose: () => void
  onSaved: () => void
}

export default function WorkerConfigDrawer({ open, workerInfo, onClose, onSaved }: Props) {
  const [form] = Form.useForm()
  const [saving, setSaving] = useState(false)
  const [owner, setOwner] = useState<string>('')
  const token = useAuthStore((s) => s.token)

  useEffect(() => {
    if (workerInfo && open) {
      const m = workerInfo.metadata
      const perms = m?.permissions as Record<string, unknown> | null | undefined
      const ownerVal = (perms?.owner as string | null | undefined) ?? ''
      setOwner(ownerVal)
      const usersVal = (perms?.users as string[] | undefined) ?? []
      const groupsVal = (perms?.groups as string[] | undefined) ?? []
      form.setFieldsValue({
        description: m?.description ?? '',
        limit_model_concurrency: m?.limit_model_concurrency,
        is_free: m?.is_free ?? false,
        users: usersVal,
        groups: groupsVal,
      })
    }
  }, [workerInfo, open, form])

  const handleSave = async () => {
    if (!token) {
      message.error('请先在模型配置页面完成 Admin Key 认证')
      return
    }
    const values = form.getFieldsValue()

    const users: string[] = values.users ?? []
    const groups: string[] = values.groups ?? []
    const parts: string[] = []
    if (users.length > 0) parts.push(`users: ${users.join(', ')}`)
    if (groups.length > 0) parts.push(`groups: ${groups.join(', ')}`)
    if (owner) parts.push(`owner: ${owner}`)
    const permsStr: string | null = parts.length > 0 ? parts.join('; ') : null

    const updates: WorkerConfigUpdates = {
      description: values.description || undefined,
      limit_model_concurrency: values.limit_model_concurrency,
      is_free: values.is_free,
      permissions: permsStr,
    }
    setSaving(true)
    try {
      await updateWorkerConfig(updates, token)
      message.success('Worker 配置已保存')
      onSaved()
      onClose()
    } catch (e: unknown) {
      message.error(`保存失败: ${e instanceof Error ? e.message : String(e)}`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Drawer
      title="编辑 Worker 配置"
      open={open}
      onClose={onClose}
      width={440}
      extra={
        <Space>
          <Button onClick={onClose}>关闭</Button>
          <Button type="primary" loading={saving} onClick={handleSave}>保存</Button>
        </Space>
      }
    >
      <Form form={form} layout="vertical" size="small">
        <Form.Item label="描述 (description)" name="description">
          <Input.TextArea rows={2} placeholder="Worker 描述信息" />
        </Form.Item>

        <Form.Item
          label="并发上限 (limit_model_concurrency)"
          name="limit_model_concurrency"
          extra="修改后需重启 Worker 才对并发信号量生效"
        >
          <InputNumber style={{ width: '100%' }} min={1} />
        </Form.Item>

        <Form.Item label="免费使用 (is_free)" name="is_free" valuePropName="checked">
          <Switch />
        </Form.Item>

        <Form.Item label="Owner（只读）">
          <Input value={owner || '（未设置）'} disabled style={{ color: '#888' }} />
        </Form.Item>

        <Form.Item label="Users" name="users" extra="输入用户名后按 Enter 或逗号添加，点击 × 删除">
          <Select
            mode="tags"
            style={{ width: '100%' }}
            placeholder="添加用户..."
            tokenSeparators={[',']}
          />
        </Form.Item>

        <Form.Item label="Groups" name="groups" extra="输入分组名后按 Enter 或逗号添加，点击 × 删除">
          <Select
            mode="tags"
            style={{ width: '100%' }}
            placeholder="添加分组..."
            tokenSeparators={[',']}
          />
        </Form.Item>
      </Form>
    </Drawer>
  )
}
