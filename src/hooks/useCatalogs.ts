import { useQuery } from '@tanstack/react-query'
import apiClient from '@/api/client'

// Minimal types based on backend responses
export interface Seccion {
  id_seccion: number
  nombre_seccion: string
  estado?: string
}
export interface Laboratorio {
  id_laboratorio: number
  nombre_laboratorio: string
  estado?: string
}

interface PaginatedApiResponse<T> {
  success: boolean
  message?: string
  data: T
  pagination?: any
}

export const useSecciones = () => {
  return useQuery({
    queryKey: ['secciones', { page: 1, size: 100, estado: 'Activo' }],
    queryFn: async () => {
      const resp = await apiClient.get<PaginatedApiResponse<Seccion[]>>('/secciones', {
        params: { page: 1, size: 100, estado: 'Activo' },
      })
      return resp.data.data || []
    },
  })
}

export const useLaboratorios = () => {
  return useQuery({
    queryKey: ['laboratorios', { page: 1, size: 100, estado: 'Activo' }],
    queryFn: async () => {
      const resp = await apiClient.get<PaginatedApiResponse<Laboratorio[]>>('/laboratorios', {
        params: { page: 1, size: 100, estado: 'Activo' },
      })
      return resp.data.data || []
    },
  })
}
