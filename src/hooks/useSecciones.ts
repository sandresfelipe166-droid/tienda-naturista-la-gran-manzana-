import { useState, useEffect } from 'react'
import apiClient from '@/api/client'

export interface Seccion {
  id_seccion: number
  nombre_seccion: string
  descripcion?: string
  estado: 'Activo' | 'Inactivo'
}

export interface SeccionCreate {
  nombre_seccion: string
  descripcion?: string
}

export interface SeccionUpdate {
  nombre_seccion?: string
  descripcion?: string
  estado?: 'Activo' | 'Inactivo'
}

export const useSecciones = () => {
  const [secciones, setSecciones] = useState<Seccion[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchSecciones = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.get('/secciones?page=1&size=100')
      if (response.data.success) {
        setSecciones(response.data.data)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar secciones')
      console.error('Error fetching secciones:', err)
    } finally {
      setLoading(false)
    }
  }

  const crearSeccion = async (data: SeccionCreate) => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.post('/secciones', data)
      if (response.data.success) {
        await fetchSecciones() // Recargar lista
        return true
      }
      return false
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear sección')
      console.error('Error creating seccion:', err)
      return false
    } finally {
      setLoading(false)
    }
  }

  const actualizarSeccion = async (id: number, data: SeccionUpdate) => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.put(`/secciones/${id}`, data)
      if (response.data.success) {
        await fetchSecciones() // Recargar lista
        return true
      }
      return false
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al actualizar sección')
      console.error('Error updating seccion:', err)
      return false
    } finally {
      setLoading(false)
    }
  }

  const eliminarSeccion = async (id: number, modo: 'logico' | 'fisico' = 'logico') => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.delete(`/secciones/${id}?modo=${modo}`)
      if (response.data.success) {
        await fetchSecciones() // Recargar lista
        return true
      }
      return false
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar sección')
      console.error('Error deleting seccion:', err)
      return false
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSecciones()
  }, [])

  return {
    secciones,
    loading,
    error,
    fetchSecciones,
    crearSeccion,
    actualizarSeccion,
    eliminarSeccion
  }
}
