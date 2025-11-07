import { useState, useEffect } from 'react'
import apiClient from '@/api/client'

export interface Laboratorio {
  id_laboratorio: number
  nombre_laboratorio: string
  descripcion?: string
  estado: 'Activo' | 'Inactivo'
}

export interface LaboratorioCreate {
  nombre_laboratorio: string
  descripcion?: string
}

export interface LaboratorioUpdate {
  nombre_laboratorio?: string
  descripcion?: string
  estado?: 'Activo' | 'Inactivo'
}

export const useLaboratorios = () => {
  const [laboratorios, setLaboratorios] = useState<Laboratorio[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchLaboratorios = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.get('/laboratorios?page=1&size=100')
      if (response.data.success) {
        setLaboratorios(response.data.data)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar laboratorios')
      console.error('Error fetching laboratorios:', err)
    } finally {
      setLoading(false)
    }
  }

  const crearLaboratorio = async (data: LaboratorioCreate) => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.post('/laboratorios', data)
      if (response.data.success) {
        await fetchLaboratorios() // Recargar lista
        return true
      }
      return false
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear laboratorio')
      console.error('Error creating laboratorio:', err)
      return false
    } finally {
      setLoading(false)
    }
  }

  const actualizarLaboratorio = async (id: number, data: LaboratorioUpdate) => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.put(`/laboratorios/${id}`, data)
      if (response.data.success) {
        await fetchLaboratorios() // Recargar lista
        return true
      }
      return false
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al actualizar laboratorio')
      console.error('Error updating laboratorio:', err)
      return false
    } finally {
      setLoading(false)
    }
  }

  const eliminarLaboratorio = async (id: number, modo: 'logico' | 'fisico' = 'logico') => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.delete(`/laboratorios/${id}?modo=${modo}`)
      if (response.data.success) {
        await fetchLaboratorios() // Recargar lista
        return true
      }
      return false
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar laboratorio')
      console.error('Error deleting laboratorio:', err)
      return false
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLaboratorios()
  }, [])

  return {
    laboratorios,
    loading,
    error,
    fetchLaboratorios,
    crearLaboratorio,
    actualizarLaboratorio,
    eliminarLaboratorio
  }
}
