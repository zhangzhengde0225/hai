import { useState } from 'react'
import {
  Drawer, Form, Input, InputNumber, Select, Switch, Checkbox, Button,
  Space, Divider, message,
} from 'antd'
import { addModel } from '../../api/models'

const API_TYPE_OPTIONS = [
  'openai-completions',
  'openai-embeddings',
  'openai-responses',
  'anthropic-messages',
].map((v) => ({ label: v, value: v }))

interface Props {
  open: boolean
  providerName: string
  token: string
  onClose: () => void
  onSaved: () => void
}

export default function AddModelDrawer({ open, providerName, token, onClose, onSaved }: Props) {
  const [form] = Form.useForm()
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    let values: Record<string, unknown>
    try {
      values = await form.validateFields()
    } catch {
      return
    }

    const model: Record<string, unknown> = {
      id: values.id,
    }
    if (values.engine) model.engine = values.engine
    if ((values.api as string[] | undefined)?.length) model.api = values.api
    if (values.proxy) model.proxy = values.proxy
    if (values.endpoint_version) model.endpoint_version = values.endpoint_version
    if (values.reasoning != null) model.reasoning = values.reasoning
    if ((values.input as string[] | undefined)?.length) model.input = values.input
    if (values.contextWindow != null) model.contextWindow = values.contextWindow
    if (values.maxTokens != null) model.maxTokens = values.maxTokens
    model.enabled = values.enabled ?? true
    const costInput = values.cost_input as number | undefined
    const costOutput = values.cost_output as number | undefined
    if (costInput != null || costOutput != null) {
      model.cost = {
        input: costInput ?? 0,
        output: costOutput ?? 0,
        cacheRead: values.cost_cacheRead,
        cacheWrite: values.cost_cacheWrite,
      }
    }

    setSaving(true)
    try {
      await addModel(providerName, model as { id: string }, token)
      message.success('模型已添加')
      form.resetFields()
      onSaved()
      onClose()
    } catch (e: unknown) {
      message.error(`添加失败: ${e instanceof Error ? e.message : String(e)}`)
    } finally {
      setSaving(false)
    }
  }

  const handleClose = () => {
    form.resetFields()
    onClose()
  }

  return (
    <Drawer
      title={`添加模型 — ${providerName}`}
      open={open}
      onClose={handleClose}
      width={480}
      extra={
        <Space>
          <Button onClick={handleClose}>取消</Button>
          <Button type="primary" loading={saving} onClick={handleSave}>添加</Button>
        </Space>
      }
    >
      <Form form={form} layout="vertical" size="small" initialValues={{ enabled: true, reasoning: false }}>
        <Form.Item label="模型 ID" name="id" rules={[{ required: true, message: '必填' }]}>
          <Input placeholder="openai/gpt-5" />
        </Form.Item>

        <Form.Item label="Engine" name="engine" extra="留空则与 ID 相同">
          <Input placeholder="gpt-5" />
        </Form.Item>

        <Form.Item label="启用" name="enabled" valuePropName="checked">
          <Switch />
        </Form.Item>

        <Divider orientation="left" plain>接口</Divider>

        <Form.Item label="API 类型 (api)" name="api" extra="留空则继承 Provider 设置">
          <Select
            mode="tags"
            style={{ width: '100%' }}
            placeholder="留空则继承 Provider"
            options={API_TYPE_OPTIONS}
            tokenSeparators={[',']}
          />
        </Form.Item>

        <Form.Item label="Proxy" name="proxy">
          <Input placeholder="http://localhost:4250（留空则继承）" allowClear />
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
