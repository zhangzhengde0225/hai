import { useState, useCallback, useEffect } from 'react'
import { Alert, Spin, Typography, message } from 'antd'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  fetchModelConfigs, batchUpdate,
  type BatchUpdateItem, type ModelConfigsResponse,
} from '../api/models'
import { useAuthStore } from '../store/authStore'
import AuthModal from '../components/Management/AuthModal'
import BatchToolbar from '../components/Management/BatchToolbar'
import ModelGroup from '../components/Management/ModelGroup'

export default function ManagementPage() {
  const token = useAuthStore((s) => s.token)
  const clearToken = useAuthStore((s) => s.clearToken)
  const [authOpen, setAuthOpen] = useState(!token)
  const [pendingChanges, setPendingChanges] = useState<Record<string, boolean>>({})
  const [filterEnabled, setFilterEnabled] = useState(false)
  const [msgApi, contextHolder] = message.useMessage()
  const queryClient = useQueryClient()

  const {
    data: configs,
    isLoading,
    error,
    refetch,
  } = useQuery<ModelConfigsResponse, Error>({
    queryKey: ['modelConfigs', token],
    queryFn: () => fetchModelConfigs(token!),
    enabled: !!token,
    retry: false,
  })

useEffect(() => {
    if (error?.message === 'UNAUTHORIZED' || error?.message === 'FORBIDDEN') {
      clearToken()
      setAuthOpen(true)
    }
  }, [error, clearToken])

  const { mutate: save, isPending: saving } = useMutation({
    mutationFn: (updates: BatchUpdateItem[]) => batchUpdate(updates, token!),
    onSuccess: (result) => {
      const failed = result.results.filter((r) => !r.success)
      if (failed.length > 0) {
        msgApi.warning(`${result.count - failed.length} 项成功，${failed.length} 项失败`)
      } else {
        msgApi.success(`已保存 ${result.count} 项更改`)
      }
      setPendingChanges({})
      queryClient.invalidateQueries({ queryKey: ['modelConfigs'] })
    },
    onError: (e: Error) => {
      msgApi.error(`保存失败: ${e.message}`)
    },
  })

  const handleToggle = useCallback((modelName: string, enabled: boolean) => {
    setPendingChanges((prev) => ({ ...prev, [modelName]: enabled }))
  }, [])

  const handleEnableAll = useCallback((provider: string) => {
    const models = configs?.data?.[provider]
    if (!models) return
    const updates: Record<string, boolean> = {}
    models.forEach((m) => { updates[m.id] = true })
    setPendingChanges((prev) => ({ ...prev, ...updates }))
  }, [configs])

  const handleDisableAll = useCallback((provider: string) => {
    const models = configs?.data?.[provider]
    if (!models) return
    const updates: Record<string, boolean> = {}
    models.forEach((m) => { updates[m.id] = false })
    setPendingChanges((prev) => ({ ...prev, ...updates }))
  }, [configs])

  const handleSave = () => {
    const updates: BatchUpdateItem[] = Object.entries(pendingChanges).map(
      ([model_name, enabled]) => ({ model_name, enabled })
    )
    save(updates)
  }

  const handleRefresh = () => {
    setPendingChanges({})
    refetch()
  }

  const pendingCount = Object.keys(pendingChanges).length

  return (
    <div>
      {contextHolder}

      <AuthModal
        open={authOpen}
        onSuccess={() => setAuthOpen(false)}
        onClose={() => setAuthOpen(false)}
      />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Typography.Title level={4} style={{ margin: 0 }}>模型配置</Typography.Title>
      </div>

      {error && error.message !== 'UNAUTHORIZED' && error.message !== 'FORBIDDEN' && (
        <Alert
          type="error"
          message="加载失败"
          description={error.message}
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {token && (
        <BatchToolbar
          pendingCount={pendingCount}
          filterEnabled={filterEnabled}
          saving={saving}
          onFilterChange={setFilterEnabled}
          onSave={handleSave}
          onRefresh={handleRefresh}
        />
      )}

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: 64 }}>
          <Spin size="large" tip="加载模型配置..." />
        </div>
      ) : (
        configs?.data &&
        Object.entries(configs.data).map(([provider, models]) => (
          <ModelGroup
            key={provider}
            provider={provider}
            models={models}
            token={token!}
            pendingChanges={pendingChanges}
            onToggle={handleToggle}
            onEnableAll={handleEnableAll}
            onDisableAll={handleDisableAll}
            filterEnabled={filterEnabled}
            onRefresh={handleRefresh}
          />
        ))
      )}
    </div>
  )
}
