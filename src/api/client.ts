import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/store/authStore'

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

// Response interceptor: Handle 401 and logout
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      const { logout } = useAuthStore.getState()
      logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
