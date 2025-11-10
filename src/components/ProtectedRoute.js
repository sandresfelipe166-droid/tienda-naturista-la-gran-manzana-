import { jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
/**
 * Componente que protege rutas según autenticación y rol
 */
export const ProtectedRoute = ({ children, requiredRole, requireAuth = true }) => {
    const { user } = useAuthStore();
    // Si requiere autenticación y no hay usuario
    if (requireAuth && !user) {
        return _jsx(Navigate, { to: "/login", replace: true });
    }
    // Si requiere rol específico
    if (requiredRole && user) {
        const userRoleName = typeof user.rol === 'string'
            ? user.rol.toLowerCase()
            : user.rol?.nombre_rol?.toLowerCase();
        if (userRoleName !== requiredRole.toLowerCase()) {
            return _jsx(Navigate, { to: "/dashboard", replace: true });
        }
    }
    return _jsx(_Fragment, { children: children });
};
