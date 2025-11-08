import { useState, useEffect } from 'react'
import apiClient from '@/api/client'

export interface Rol {
  id_rol: number
  nombre_rol: string
  descripcion?: string
  permisos?: string
}

export interface Usuario {
  id_usuario: number
  nombre_usuario: string
  email: string
  nombre_completo?: string
  estado: 'Activo' | 'Inactivo' | 'Suspendido'
  fecha_creacion?: string
  ultima_acceso?: string
  id_rol: number
  rol?: Rol
}

export interface UsuarioUpdate {
  username?: string
  email?: string
  nombre_completo?: string
  estado?: 'Activo' | 'Inactivo' | 'Suspendido'
  password?: string
  id_rol?: number
}

export const useUsuarios = () => {
  const [usuarios, setUsuarios] = useState<Usuario[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchUsuarios = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.get('/users?limit=100&skip=0')
      // La respuesta es un array directo
      if (Array.isArray(response.data)) {
        setUsuarios(response.data)
      } else {
        setError('Formato de respuesta inválido')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar usuarios')
      console.error('Error fetching usuarios:', err)
    } finally {
      setLoading(false)
    }
  }

  const obtenerUsuario = async (id: number): Promise<Usuario | null> => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.get(`/users/${id}`)
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al obtener usuario')
      console.error('Error fetching usuario:', err)
      return null
    } finally {
      setLoading(false)
    }
  }

  const actualizarUsuario = async (id: number, data: UsuarioUpdate) => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.put(`/users/${id}`, data)
      if (response.data) {
        await fetchUsuarios() // Recargar lista
        return true
      }
      return false
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Error al actualizar usuario'
      setError(errorMsg)
      console.error('Error updating usuario:', err)
      
      // Re-lanzar el error para que el componente pueda manejarlo
      throw new Error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const eliminarUsuario = async (id: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.delete(`/users/${id}`)
      if (response.data?.message) {
        await fetchUsuarios() // Recargar lista
        return true
      }
      return false
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Error al eliminar usuario'
      setError(errorMsg)
      console.error('Error deleting usuario:', err)
      
      // Re-lanzar el error para que el componente pueda manejarlo
      throw new Error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  // Obtener lista de roles disponibles
  const fetchRoles = async (): Promise<Rol[]> => {
    try {
      // Asumiendo que existe un endpoint /roles
      const response = await apiClient.get('/roles')
      return Array.isArray(response.data) ? response.data : []
    } catch (err: any) {
      console.error('Error fetching roles:', err)
      return []
    }
  }

  useEffect(() => {
    fetchUsuarios()
  }, [])

  return {
    usuarios,
    loading,
    error,
    fetchUsuarios,
    obtenerUsuario,
    actualizarUsuario,
    eliminarUsuario,
    fetchRoles
  }
}
