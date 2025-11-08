import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

interface ProtectedRouteProps {
  children: ReactNode
  requiredRole?: 'admin' | 'gestor' | 'viewer'
  requireAuth?: boolean
}

/**
 * Componente que protege rutas según autenticación y rol
 */
export const ProtectedRoute = ({ 
  children, 
  requiredRole,
  requireAuth = true 
}: ProtectedRouteProps) => {
  const { user } = useAuthStore()

  // Si requiere autenticación y no hay usuario
  if (requireAuth && !user) {
    return <Navigate to="/login" replace />
  }

  // Si requiere rol específico
  if (requiredRole && user) {
    const userRoleName = typeof user.rol === 'string' 
      ? user.rol.toLowerCase()
      : user.rol?.nombre_rol?.toLowerCase()

    if (userRoleName !== requiredRole.toLowerCase()) {
      return <Navigate to="/dashboard" replace />
    }
  }

  return <>{children}</>
}
