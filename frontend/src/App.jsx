import { useEffect, useState } from "react";
import { BrowserRouter, Navigate, Outlet, Route, Routes } from "react-router-dom";

import AppShell from "./components/layout/AppShell";
import KaryaLoader from "./components/loading/KaryaLoading";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Landing from "./pages/landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Overview from "./pages/Overview";
import AgentsPage from "./pages/AgentsPage";
import TasksPage from "./pages/TasksPage";
import WorkflowsPage from "./pages/WorkflowsPage";
import KnowledgePage from "./pages/KnowledgePage";
import IntegrationsPage from "./pages/IntegrationsPage";
import ActivityPage from "./pages/ActivityPage";
import ApprovalsPage from "./pages/ApprovalsPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import SettingsPage from "./pages/SettingsPage";

function ProtectedRoute() {
  const { isAuthenticated, authReady } = useAuth();

  if (!authReady) {
    return <KaryaLoader />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <AppShell />;
}

function PublicRoute() {
  const { isAuthenticated, authReady } = useAuth();

  if (!authReady) {
    return <KaryaLoader />;
  }

  if (isAuthenticated) {
    return <Navigate to="/app" replace />;
  }

  return <Outlet />;
}

function AppRoutes() {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsReady(true), 1200);
    return () => clearTimeout(timer);
  }, []);

  if (!isReady) {
    return <KaryaLoader />;
  }

  return (
    <Routes>
      <Route element={<PublicRoute />}>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route path="/app" element={<Overview />} />
        <Route path="/app/agents" element={<AgentsPage />} />
        <Route path="/app/tasks" element={<TasksPage />} />
        <Route path="/app/workflows" element={<WorkflowsPage />} />
        <Route path="/app/knowledge" element={<KnowledgePage />} />
        <Route path="/app/integrations" element={<IntegrationsPage />} />
        <Route path="/app/activity" element={<ActivityPage />} />
        <Route path="/app/approvals" element={<ApprovalsPage />} />
        <Route path="/app/analytics" element={<AnalyticsPage />} />
        <Route path="/app/settings" element={<SettingsPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}