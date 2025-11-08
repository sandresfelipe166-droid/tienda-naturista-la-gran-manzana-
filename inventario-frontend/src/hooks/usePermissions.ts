/**
 * Hook usePermissions - Sistema de permisos por rol
 * 
 * Define qué puede hacer cada rol en el sistema:
 * - admin: Acceso total (crear, editar, eliminar todo)
 * - vendedor: Puede vender, crear entradas, ver reportes
 * - viewer: Solo puede ver (sin modificar nada)
 */

import { useAuthStore } from '@/store/authStore'

// Tipos de recursos en el sistema
type Resource = 
  | 'productos' 
  | 'ventas' 
  | 'entradas' 
  | 'gastos' 
  | 'cotizaciones'
  | 'laboratorios'
  | 'secciones'
  | 'usuarios'
  | 'configuracion'
  | 'logs'

// Tipos de acciones
type Action = 'read' | 'create' | 'update' | 'delete'

// Permisos de cada rol
const ROLE_PERMISSIONS = {
  admin: {
    productos: { read: true, create: true, update: true, delete: true },
    ventas: { read: true, create: true, update: true, delete: true },
    entradas: { read: true, create: true, update: true, delete: true },
    gastos: { read: true, create: true, update: true, delete: true },
    cotizaciones: { read: true, create: true, update: true, delete: true },
    laboratorios: { read: true, create: true, update: true, delete: true },
    secciones: { read: true, create: true, update: true, delete: true },
    usuarios: { read: true, create: true, update: true, delete: true },
    configuracion: { read: true, update: true },
    logs: { read: true }
  },
  vendedor: {
    productos: { read: true, create: false, update: true, delete: false },
    ventas: { read: true, create: true, update: true, delete: false },
    entradas: { read: true, create: true, update: false, delete: false },
    gastos: { read: true, create: true, update: false, delete: false },
    cotizaciones: { read: true, create: true, update: true, delete: false },
    laboratorios: { read: true, create: false, update: false, delete: false },
    secciones: { read: true, create: false, update: false, delete: false },
    usuarios: { read: false, create: false, update: false, delete: false },
    configuracion: { read: false, update: false },
    logs: { read: false }
  },
  viewer: {
    productos: { read: true, create: false, update: false, delete: false },
    ventas: { read: true, create: false, update: false, delete: false },
    entradas: { read: true, create: false, update: false, delete: false },
    gastos: { read: true, create: false, update: false, delete: false },
    cotizaciones: { read: true, create: false, update: false, delete: false },
    laboratorios: { read: true, create: false, update: false, delete: false },
    secciones: { read: true, create: false, update: false, delete: false },
    usuarios: { read: false, create: false, update: false, delete: false },
    configuracion: { read: false, update: false },
    logs: { read: false }
  }
} as const

/**
 * Hook principal de permisos
 * 
 * @example
 * const { can, isAdmin, isVendedor } = usePermissions()
 * 
 * // Verificar si puede crear productos
 * if (can('productos', 'create')) {
 *   // Mostrar botón
 * }
 * 
 * // Verificar si es admin
 * if (isAdmin()) {
 *   // Mostrar panel de administración
 * }
 */
export function usePermissions() {
  const { user } = useAuthStore()

  /**
   * Verifica si el usuario tiene permiso para una acción en un recurso
   * 
   * @param resource - El recurso a verificar (productos, ventas, etc.)
   * @param action - La acción a verificar (read, create, update, delete)
   * @returns true si tiene permiso, false si no
   */
  const can = (resource: Resource, action: Action): boolean => {
    if (!user || !user.rol) return false
    
    // El rol puede ser string o objeto
    const roleName = typeof user.rol === 'string' 
      ? user.rol.toLowerCase()
      : user.rol.nombre_rol?.toLowerCase()
    
    if (!roleName) return false

    const permissions = ROLE_PERMISSIONS[roleName as keyof typeof ROLE_PERMISSIONS]
    if (!permissions) return false

    const resourcePerms = permissions[resource]
    if (!resourcePerms) return false

    return (resourcePerms as any)[action] === true
  }

  /**
   * Verifica si el usuario es administrador
   */
  const isAdmin = (): boolean => {
    if (!user || !user.rol) return false
    const roleName = typeof user.rol === 'string' 
      ? user.rol.toLowerCase()
      : user.rol.nombre_rol?.toLowerCase()
    return roleName === 'admin'
  }

  /**
   * Verifica si el usuario es gestor de inventario
   */
  const isGestor = (): boolean => {
    if (!user || !user.rol) return false
    const roleName = typeof user.rol === 'string' 
      ? user.rol.toLowerCase()
      : user.rol.nombre_rol?.toLowerCase()
    return roleName === 'gestor'
  }

  /**
   * Verifica si el usuario es viewer (solo lectura)
   */
  const isViewer = (): boolean => {
    if (!user || !user.rol) return false
    const roleName = typeof user.rol === 'string' 
      ? user.rol.toLowerCase()
      : user.rol.nombre_rol?.toLowerCase()
    return roleName === 'viewer'
  }

  /**
   * Obtiene todos los permisos del usuario actual
   */
  const getPermissions = () => {
    if (!user || !user.rol) return null
    
    const roleName = typeof user.rol === 'string' 
      ? user.rol.toLowerCase()
      : user.rol.nombre_rol?.toLowerCase()
    
    if (!roleName) return null

    return ROLE_PERMISSIONS[roleName as keyof typeof ROLE_PERMISSIONS] || null
  }

  /**
   * Obtiene el nombre del rol del usuario
   */
  const getRoleName = (): string => {
    if (!user || !user.rol) return 'Sin rol'
    return typeof user.rol === 'string' 
      ? user.rol
      : user.rol.nombre_rol || 'Sin rol'
  }

  return {
    can,
    isAdmin,
    isGestor,
    isViewer,
    getPermissions,
    getRoleName,
    user
  }
}

/**
 * Tipo para el store de autenticación
 * Asegura que el usuario tiene la estructura correcta
 */
export interface User {
  id_usuario: number
  nombre_usuario: string
  nombre_completo?: string
  email?: string
  rol?: {
    id_rol: number
    nombre_rol: string
    descripcion?: string
  }
}
