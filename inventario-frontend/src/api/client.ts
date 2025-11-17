import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/store/authStore'
import { enqueue } from '@/offline/outbox'
import logger from '@/utils/logger'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_V1 = import.meta.env.VITE_API_V1 || '/api/v1'

const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}${API_V1}`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: Add token to requests
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { token } = useAuthStore.getState()
    if (token) {
      const headers = (config.headers ?? {}) as any
      if (typeof headers.set === 'function') {
        headers.set('Authorization', `Bearer ${token}`)
      } else {
        headers['Authorization'] = `Bearer ${token}`
      }
      config.headers = headers
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor: Handle 401 and offline encolado básico
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    // Si es 401 token inválido
    if (status === 401) {
      const { logout } = useAuthStore.getState()
      logout()
      window.location.href = '/login'
    }
    // Si no hay conexión y es un método de mutación, encolar
    if (!navigator.onLine) {
      const original = error.config
      const method = (original?.method || 'get').toUpperCase()
      if (['POST','PUT','PATCH','DELETE'].includes(method) && original?.url) {
        try {
          enqueue(method as any, `${original.baseURL || ''}${original.url}`.replace(/\/+/,'/'), original.data ? JSON.parse(original.data) : undefined)
          logger.info('Operación encolada para sincronización offline', { method, url: original.url })
        } catch (e) {
          logger.warn('No se pudo encolar mutación offline', e as Error)
        }
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
