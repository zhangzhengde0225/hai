import { useEffect, useState } from 'react'
import {
  Drawer, Form, Input, Select, Switch, Button, Space, Spin, message,
} from 'antd'
import { useQuery } from '@tanstack/react-query'
import type { ProviderConfig } from '../../api/models'
import { fetchProviderConfigs, updateProviderConfig } from '../../api/models'

const API_TYPE_OPTIONS = [
  'openai-completions',
  'openai-embeddings',
  'openai-responses',
  'anthropic-messages',
].map((v) => ({ label: v, value: v }))

function toApiArray(api: string | string[] | undefined): string[] {
  if (!api) return []
  return Array.isArray(api) ? api : [api]
}

interface Props {
  open: boolean
  providerName: string
  token: string
  onClose: () => void
  onSaved: () => void
}

export default function ProviderConfigDrawer({
  open, providerName, token, onClose, onSaved,
}: Props) {
  const [form] = Form.useForm()
  const [saving, setSaving] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['providerConfigs', token],
    queryFn: () => fetchProviderConfigs(token),
    enabled: open && !!token,
    staleTime: 0,
  })

  const config: ProviderConfig | undefined = data?.data?.[providerName]

  useEffect(() => {
    if (open && config) {
      form.setFieldsValue({
        baseUrl: config.baseUrl ?? '',
        apiKey: config.apiKey ?? '',
        api: toApiArray(config.api),
        proxy: config.proxy ?? '',
        needExternalApiKey: config.needExternalApiKey ?? false,
        appendAnthropicPath: config.appendAnthropicPath ?? true,
      })
    }
  }, [open, config, form])

  const handleSave = async () => {
    const values = form.getFieldsValue()
    const updates: ProviderConfig = {
      baseUrl: values.baseUrl || undefined,
      apiKey: values.apiKey || undefined,
      api: (values.api as string[]).length > 0 ? values.api : undefined,
      proxy: values.proxy || null,
      needExternalApiKey: values.needExternalApiKey,
      appendAnthropicPath: values.appendAnthropicPath,
    }
    setSaving(true)
    try {
      await updateProviderConfig(providerName, updates, token)
      message.success(`Provider "${providerName}" 配置已保存`)
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
      title={`Provider 配置 — ${providerName}`}
      open={open}
      onClose={onClose}
      width={440}
      extra={
        <Space>
          <Button onClick={onClose}>取消</Button>
          <Button type="primary" loading={saving} onClick={handleSave}>保存</Button>
        </Space>
      }
    >
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 48 }}>
          <Spin tip="加载配置..." />
        </div>
      ) : (
        <Form form={form} layout="vertical" size="small">
          <Form.Item label="Base URL" name="baseUrl">
            <Input placeholder="https://openrouter.ai/api/" />
          </Form.Item>

          <Form.Item label="API Key" name="apiKey" extra="支持 os.environ/ENV_VAR_NAME 格式">
            <Input placeholder="os.environ/OPENROUTER_API_KEY" />
          </Form.Item>

          <Form.Item label="API 类型 (api)" name="api" extra="可添加多个，支持自定义类型">
            <Select
              mode="tags"
              style={{ width: '100%' }}
              placeholder="选择或输入 API 类型..."
              options={API_TYPE_OPTIONS}
              tokenSeparators={[',']}
            />
          </Form.Item>

          <Form.Item label="Proxy" name="proxy" extra="留空则清除代理">
            <Input placeholder="http://localhost:4250" allowClear />
          </Form.Item>

          <Form.Item label="需要外部 API Key (needExternalApiKey)" name="needExternalApiKey" valuePropName="checked">
            <Switch />
          </Form.Item>

          <Form.Item
            label="追加 /anthropic 路径 (appendAnthropicPath)"
            name="appendAnthropicPath"
            valuePropName="checked"
            extra="使用 anthropic-messages API 时是否自动在 Base URL 末尾追加 /anthropic"
          >
            <Switch />
          </Form.Item>
        </Form>
      )}
    </Drawer>
  )
}
