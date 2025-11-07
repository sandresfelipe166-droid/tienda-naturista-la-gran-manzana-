// API Response types
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: {
    code: string
    message: string
    details?: string[]
  }
  request_id?: string
  timestamp?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface ApiError {
  code: string
  message: string
  details?: string[]
}

// Auth types
export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token?: string
  token_type: string
  user: UserInfo
}

export interface UserInfo {
  id: number
  email: string
  nombre: string
  apellido: string
  rol: {
    id_rol: number
    nombre_rol: string
    descripcion?: string
    permisos?: string
  } | string  // Puede ser objeto o string por compatibilidad
  activo: boolean
}

// Backend UserResponse type (from FastAPI)
export interface UserResponse {
  id_usuario: number
  nombre_usuario: string
  email: string
  nombre_completo: string | null
  estado: string
  fecha_creacion: string | null
  ultima_acceso: string | null
  id_rol: number
}

export interface TokenPayload {
  sub: number
  email: string
  exp: number
}

export interface AuthState {
  user: UserInfo | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
}

// Product types
export interface Producto {
  id: number
  nombre: string
  descripcion: string
  cantidad: number
  precio: number
  sku: string
  categoria: string
  // IDs de catálogo para edición
  id_seccion?: number
  id_laboratorio?: number
  estado: 'activo' | 'inactivo'
  created_at: string
  updated_at: string
}

export interface CreateProductoRequest {
  nombre: string
  descripcion: string
  precio: number
  cantidad: number
  sku?: string
  categoria?: string
  // Backend-required ids for creation
  id_seccion?: number
  id_laboratorio?: number
}

export interface ProductListResponse extends PaginatedResponse<Producto> {}

// Alert types
export type AlertType = 'STOCK_BAJO' | 'VENCIMIENTO_PROXIMO' | 'PRODUCTO_FALTANTE'
export type AlertaSeverity = 'BAJA' | 'MEDIA' | 'ALTA' | 'CRITICA'
export type AlertaStatus = 'activa' | 'resuelta' | 'ignorada'

export interface Alerta {
  id: number
  tipo: AlertType
  severidad: AlertaSeverity
  estado: AlertaStatus
  producto_id: number
  mensaje: string
  created_at: string
  updated_at: string
}

// Tipos de estadísticas de Ventas y Gastos
export interface VentaEstadisticasMes {
  mes: number
  año: number
  total_ventas: number
  cantidad_ventas: number
  promedio_venta: number
}

export interface VentaEstadisticasAnio {
  año: number
  total_ventas: number
  cantidad_ventas: number
  meses: VentaEstadisticasMes[]
}

export interface GastoEstadisticasMes {
  mes: number
  año: number
  total_gastos: number
  cantidad_gastos: number
  por_categoria: Record<string, number>
}

export interface GastoEstadisticasAnio {
  año: number
  total_gastos: number
  cantidad_gastos: number
  meses: GastoEstadisticasMes[]
}
