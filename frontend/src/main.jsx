import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'
import AppShell from './components/layout/AppShell.jsx'
import ActivityPage from './pages/ActivityPage.jsx'
import AgentsPage from './pages/AgentsPage.jsx'
import AnalyticsPage from './pages/AnalyticsPage.jsx'
import ApprovalsPage from './pages/ApprovalsPage.jsx'
import Desktop from './pages/Desktop.jsx'
import IntegrationsPage from './pages/IntegrationsPage.jsx'
import KnowledgePage from './pages/KnowledgePage.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import SettingsPage from './pages/SettingsPage.jsx'
import TasksPage from './pages/TasksPage.jsx'
import WorkflowsPage from './pages/WorkflowsPage.jsx'

function RequireAuth({ children }) {
  const { authReady, isAuthenticated } = useAuth()

  if (!authReady) return null
  if (!isAuthenticated) return <Navigate to="/login" replace />

  return children
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/app"
            element={
              <RequireAuth>
                <AppShell />
              </RequireAuth>
            }
          >
            <Route index element={<Desktop />} />
            <Route path="agents" element={<AgentsPage />} />
            <Route path="workflows" element={<WorkflowsPage />} />
            <Route path="tasks" element={<TasksPage />} />
            <Route path="knowledge" element={<KnowledgePage />} />
            <Route path="integrations" element={<IntegrationsPage />} />
            <Route path="activity" element={<ActivityPage />} />
            <Route path="approvals" element={<ApprovalsPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
