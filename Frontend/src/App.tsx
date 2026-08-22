import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/layout/Layout';
import { LoginPage } from './features/auth/LoginPage';
import { AdminDashboard } from './features/dashboard/AdminDashboard';
import { StorekeeperDashboard } from './features/dashboard/StorekeeperDashboard';
import { SamplerDashboard } from './features/dashboard/SamplerDashboard';
import { AnalystDashboard } from './features/dashboard/AnalystDashboard';
import { QCSupervisorDashboard } from './features/dashboard/QCSupervisorDashboard';
import { ManagerDashboard } from './features/dashboard/ManagerDashboard';
import { ReceivingModule } from './features/receiving/ReceivingModule';
import { SamplingModule } from './features/sampling/SamplingModule';
import { AnalysisModule } from './features/analysis/AnalysisModule';
import { CertificatesModule } from './features/certificates/CertificatesModule';
import { AuditLogViewer } from './features/audit/AuditLogViewer';

const ProtectedRoute: React.FC<{ children: React.ReactNode; permission?: string }> = ({ children, permission }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="p-8">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (permission && !user.effective_permissions.includes(permission) && !user.roles.some(r => r.code === 'sysadmin')) {
    return <Navigate to="/dashboard" replace />;
  }
  return <>{children}</>;
};

const DashboardRouter: React.FC = () => {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  const role = user.roles[0]?.code;
  switch (role) {
    case 'sysadmin':
    case 'admin': return <AdminDashboard />;
    case 'storekeeper': return <StorekeeperDashboard />;
    case 'sampler': return <SamplerDashboard />;
    case 'qc_analyst': return <AnalystDashboard />;
    case 'qc_supervisor': return <QCSupervisorDashboard />;
    case 'manager': return <ManagerDashboard />;
    default: return <AdminDashboard />;
  }
};

const App: React.FC = () => (
  <AuthProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route path="dashboard" element={<DashboardRouter />} />
          <Route path="receiving" element={<ProtectedRoute permission="receiving.view"><ReceivingModule /></ProtectedRoute>} />
          <Route path="sampling" element={<ProtectedRoute permission="sampling.view"><SamplingModule /></ProtectedRoute>} />
          <Route path="analysis" element={<ProtectedRoute permission="analysis.view"><AnalysisModule /></ProtectedRoute>} />
          <Route path="certificates" element={<ProtectedRoute permission="certificate.view"><CertificatesModule /></ProtectedRoute>} />
          <Route path="audit" element={<ProtectedRoute permission="audit.view"><AuditLogViewer /></ProtectedRoute>} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  </AuthProvider>
);

export default App;