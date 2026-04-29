import { useState } from 'react'
import { Modal, Input, Alert, Space, Typography } from 'antd'
import { LockOutlined } from '@ant-design/icons'
import { verifyAdminPassword } from '../../api/models'
import { useAuthStore } from '../../store/authStore'

const { Text } = Typography

interface Props {
  open: boolean
  onSuccess: () => void
  onClose: () => void
}

export default function AuthModal({ open, onSuccess, onClose }: Props) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const setToken = useAuthStore((s) => s.setToken)

  const handleOk = async () => {
    if (!password.trim()) return
    setLoading(true)
    setError('')
    try {
      await verifyAdminPassword(password.trim())
      setToken(password.trim())
      onSuccess()
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      if (msg === 'UNAUTHORIZED' || msg === 'FORBIDDEN') {
        setError('Admin Key 错误，请重试')
      } else {
        setError(`连接失败: ${msg}`)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      title={
        <Space>
          <LockOutlined />
          管理员认证 (Admin Key)
        </Space>
      }
      open={open}
      onOk={handleOk}
      onCancel={onClose}
      okText="验证"
      cancelText="取消"
      closable={true}
      confirmLoading={loading}
      maskClosable={true}
    >
      <Space direction="vertical" style={{ width: '100%', marginTop: 8 }}>
        <Text type="secondary" style={{ fontSize: 13 }}>
          请输入 Admin Key（Worker 启动日志中可查看）
        </Text>
        <Input.Password
          prefix={<LockOutlined />}
          placeholder="xxxxxxxx"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onPressEnter={handleOk}
          autoFocus
        />
        {error && <Alert type="error" message={error} showIcon />}
      </Space>
    </Modal>
  )
}
