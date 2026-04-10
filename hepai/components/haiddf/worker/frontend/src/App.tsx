import { Layout } from 'antd'
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import AppHeader from './components/Layout/AppHeader'
import AppSidebar from './components/Layout/AppSidebar'
import MonitorPage from './pages/MonitorPage'
import ManagementPage from './pages/ManagementPage'

const { Header, Sider, Content } = Layout

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, staleTime: 2_000 },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <HashRouter>
        <Layout style={{ height: '100vh' }}>
          <Header style={{ padding: 0, background: '#001529', position: 'sticky', top: 0, zIndex: 10 }}>
            <AppHeader />
          </Header>

          <Layout>
            <Sider width={200} style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}>
              <AppSidebar />
            </Sider>

            <Content style={{ padding: 24, overflowY: 'auto', background: '#f5f5f5' }}>
              <Routes>
                <Route path="/" element={<Navigate to="/monitor" replace />} />
                <Route path="/monitor" element={<MonitorPage />} />
                <Route path="/management" element={<ManagementPage />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </HashRouter>
    </QueryClientProvider>
  )
}
