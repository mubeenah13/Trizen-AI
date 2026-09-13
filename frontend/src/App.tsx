import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './pages/LoginPage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';
import { AdminEventDetailPage } from './pages/AdminEventDetailPage';
import { TeamDashboardPage } from './pages/TeamDashboardPage';
import { TeamEventDetailPage } from './pages/TeamEventDetailPage';
import { PublicGalleryPage } from './pages/PublicGalleryPage';
import type { UserRole } from './types';

const ProtectedRoute: React.FC<{ children: React.ReactNode; allowedRoles?: UserRole[] }> = ({
  children,
  allowedRoles,
}) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <p className="text-slate-400">Loading session...</p>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to={user.role === 'ADMIN' ? '/admin' : '/team'} replace />;
  }

  return <>{children}</>;
};

const RootRedirect: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();
  if (isLoading) return null;
  if (!isAuthenticated || !user) return <Navigate to="/login" replace />;
  return <Navigate to={user.role === 'ADMIN' ? '/admin' : '/team'} replace />;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          {/* Admin Routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <AdminDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/events/:eventId"
            element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <AdminEventDetailPage />
              </ProtectedRoute>
            }
          />

          {/* Team Member Routes */}
          <Route
            path="/team"
            element={
              <ProtectedRoute allowedRoles={['ADMIN', 'TEAM_MEMBER']}>
                <TeamDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/team/events/:eventId"
            element={
              <ProtectedRoute allowedRoles={['ADMIN', 'TEAM_MEMBER']}>
                <TeamEventDetailPage />
              </ProtectedRoute>
            }
          />

          {/* Public Customer Gallery Route (No Account Needed!) */}
          <Route path="/gallery/:slug" element={<PublicGalleryPage />} />

          {/* Root Fallback */}
          <Route path="*" element={<RootRedirect />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
