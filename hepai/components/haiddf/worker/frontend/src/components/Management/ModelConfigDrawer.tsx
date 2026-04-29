import { useEffect, useState } from 'react'
import {
  Drawer, Form, Input, InputNumber, Select, Switch, Checkbox, Button,
  Space, Divider, Typography, message,
} from 'antd'
import type { ModelConfig } from '../../api/models'
import { updateModelConfig } from '../../api/models'

const { Text } = Typography

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
  model: ModelConfig | null
  token: string
  onClose: () => void
  onSaved: () => void
}

export default function ModelConfigDrawer({ open, model, token, onClose, onSaved }: Props) {
  const [form] = Form.useForm()
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (model && open) {
      form.setFieldsValue({
        enabled: model.enabled,
        engine: model.engine ?? '',
        api: toApiArray(model.api),
        appendAnthropicPath: model.appendAnthropicPath,   // undefined = 继承 provider
        proxy: model.proxy ?? '',
        reasoning: model.reasoning ?? false,
        input: model.input ?? [],
        contextWindow: model.contextWindow,
        maxTokens: model.maxTokens,
        endpoint_version: model.endpoint_version ?? '',
        cost_input: model.cost?.input,
        cost_output: model.cost?.output,
        cost_cacheRead: model.cost?.cacheRead,
        cost_cacheWrite: model.cost?.cacheWrite,
      })
    }
  }, [model, open, form])

  const handleSave = async () => {
    const values = form.getFieldsValue()
    const updates: Partial<ModelConfig> = {
      enabled: values.enabled,
      engine: values.engine || undefined,
      api: (values.api as string[]).length > 0 ? values.api : undefined,
      appendAnthropicPath: values.appendAnthropicPath,
      proxy: values.proxy || null,
      reasoning: values.reasoning,
      input: values.input,
      contextWindow: values.contextWindow,
      maxTokens: values.maxTokens,
      endpoint_version: values.endpoint_version || undefined,
      cost: {
        input: values.cost_input ?? 0,
        output: values.cost_output ?? 0,
        cacheRead: values.cost_cacheRead,
        cacheWrite: values.cost_cacheWrite,
      },
    }
    setSaving(true)
    try {
      await updateModelConfig(model!.id, updates, token)
      message.success('已保存')
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
      title={
        <Space direction="vertical" size={0}>
          <Text strong>编辑模型配置</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>{model?.id}</Text>
        </Space>
      }
      open={open}
      onClose={onClose}
      width={480}
      extra={
        <Space>
          <Button onClick={onClose}>取消</Button>
          <Button type="primary" loading={saving} onClick={handleSave}>保存</Button>
        </Space>
      }
    >
      <Form form={form} layout="vertical" size="small">
        <Form.Item label="启用" name="enabled" valuePropName="checked">
          <Switch />
        </Form.Item>

        <Divider orientation="left" plain>基本信息</Divider>

        <Form.Item label="Engine" name="engine">
          <Input placeholder="模型引擎名称" />
        </Form.Item>

        <Form.Item label="API 类型 (api)" name="api" extra="覆盖 Provider 的 API 类型，可添加多个">
          <Select
            mode="tags"
            style={{ width: '100%' }}
            placeholder="留空则继承 Provider 设置"
            options={API_TYPE_OPTIONS}
            tokenSeparators={[',']}
          />
        </Form.Item>

        <Form.Item
          label="追加 /anthropic 路径 (appendAnthropicPath)"
          name="appendAnthropicPath"
          valuePropName="checked"
          extra="留空时继承 Provider 设置；关闭则直接使用 Base URL"
        >
          <Switch />
        </Form.Item>

        <Form.Item label="Proxy" name="proxy">
          <Input placeholder="http://localhost:4250（留空则不使用）" allowClear />
        </Form.Item>

        <Form.Item label="Endpoint Version" name="endpoint_version">
          <Input placeholder="可选" allowClear />
        </Form.Item>

        <Form.Item label="支持推理 (Reasoning)" name="reasoning" valuePropName="checked">
          <Switch />
        </Form.Item>

        <Form.Item label="支持输入类型" name="input">
          <Checkbox.Group options={[
            { label: 'text', value: 'text' },
            { label: 'image', value: 'image' },
          ]} />
        </Form.Item>

        <Divider orientation="left" plain>上下文</Divider>

        <Form.Item label="Context Window (tokens)" name="contextWindow">
          <InputNumber style={{ width: '100%' }} min={0} />
        </Form.Item>

        <Form.Item label="Max Output Tokens" name="maxTokens">
          <InputNumber style={{ width: '100%' }} min={0} />
        </Form.Item>

        <Divider orientation="left" plain>成本（每百万 token）</Divider>

        <Form.Item label="Input 成本" name="cost_input">
          <InputNumber style={{ width: '100%' }} min={0} step={0.1} />
        </Form.Item>

        <Form.Item label="Output 成本" name="cost_output">
          <InputNumber style={{ width: '100%' }} min={0} step={0.1} />
        </Form.Item>

        <Form.Item label="Cache Read 成本" name="cost_cacheRead">
          <InputNumber style={{ width: '100%' }} min={0} step={0.1} />
        </Form.Item>

        <Form.Item label="Cache Write 成本" name="cost_cacheWrite">
          <InputNumber style={{ width: '100%' }} min={0} step={0.1} />
        </Form.Item>
      </Form>
    </Drawer>
  )
}
