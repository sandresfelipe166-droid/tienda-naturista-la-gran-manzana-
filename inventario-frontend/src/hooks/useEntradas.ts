import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/api/client'

export interface EntradaItemUI {
  id_entrada: number
  id_lote: number
  cantidad: number
  fecha_entrada: string
  precio_compra_unitario: number
  precio_compra_total: number
  proveedor?: string
  numero_factura_compra?: string
  observaciones?: string
}

export interface EntradasListParams {
  id_lote?: number
  mes?: number
  año?: number
  skip?: number
  limit?: number
}

export function useEntradasListado(params?: EntradasListParams) {
  return useQuery({
    queryKey: ['entradas', 'list', params],
    queryFn: async () => {
      const res = await apiClient.get('/entradas', { params })
      return (res.data as any[]) as EntradaItemUI[]
    },
  })
}

export interface CrearEntradaInput {
  id_lote: number
  cantidad: number
  precio_compra_unitario: number
  fecha_entrada?: string
  numero_factura_compra?: string
  proveedor?: string
  observaciones?: string
}

export function useCrearEntrada() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: CrearEntradaInput) => {
      const res = await apiClient.post('/entradas', data)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['entradas', 'list'] })
      qc.invalidateQueries({ queryKey: ['entradas', 'stats'] })
      qc.invalidateQueries({ queryKey: ['products'] })
    },
  })
}

export interface EntradasEstadisticasMes {
  mes: number
  año: number
  cantidad_entradas: number
  total_compras: number
  promedio_entrada: number
  total_unidades: number
}

export interface EntradasEstadisticasAnio {
  año: number
  cantidad_entradas: number
  total_compras: number
  promedio_entrada: number
  total_unidades: number
}

export function useEntradasMes(mes: number, año: number, enabled = true) {
  return useQuery({
    queryKey: ['entradas', 'stats', 'mes', mes, año],
    queryFn: async () => {
      const res = await apiClient.get('/entradas/estadisticas/mes', { params: { mes, año } })
      return res.data as EntradasEstadisticasMes
    },
    enabled,
  })
}

export function useEntradasAnio(año: number, enabled = true) {
  return useQuery({
    queryKey: ['entradas', 'stats', 'año', año],
    queryFn: async () => {
      const res = await apiClient.get('/entradas/estadisticas/año', { params: { año } })
      return res.data as EntradasEstadisticasAnio
    },
    enabled,
  })
}
