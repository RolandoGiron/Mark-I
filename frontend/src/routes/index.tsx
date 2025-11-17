import { createBrowserRouter, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/shared/store/auth'
import { MainLayout } from '@/layouts/MainLayout'
import { LoginPage } from '@/features/auth/components/LoginPage'
import { DashboardPage } from '@/features/dashboard/components/DashboardPage'

// Protected Route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

// Public Route wrapper (redirect to dashboard if already authenticated)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: (
      <PublicRoute>
        <LoginPage />
      </PublicRoute>
    ),
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <MainLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'proyectos',
        element: <div className="p-6">Proyectos (próximamente)</div>,
      },
      {
        path: 'proyectos/:id',
        element: <div className="p-6">Detalle de Proyecto (próximamente)</div>,
      },
      {
        path: 'costos',
        element: <div className="p-6">Costos (próximamente)</div>,
      },
      {
        path: 'tareas',
        element: <div className="p-6">Tareas (próximamente)</div>,
      },
      {
        path: 'personal',
        element: <div className="p-6">Personal (próximamente)</div>,
      },
      {
        path: 'horas',
        element: <div className="p-6">Registro de Horas (próximamente)</div>,
      },
      {
        path: 'notificaciones',
        element: <div className="p-6">Notificaciones (próximamente)</div>,
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/dashboard" replace />,
  },
])
