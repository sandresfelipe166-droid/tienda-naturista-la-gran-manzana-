import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/api/client'

export interface DetalleCotizacion {
  id_producto: number
  cantidad: number
  precio_unitario: number
  subtotal?: number
}

export interface CotizacionItem {
  id_cotizacion: number
  numero_cotizacion: string
  fecha_cotizacion: string
  id_cliente: number
  subtotal: number
  descuento: number
  impuestos: number
  total: number
  estado: string
  observaciones?: string
  detalles?: DetalleCotizacion[]
}

export interface CotizacionesListParams {
  skip?: number
  limit?: number
  estado?: string
}

export function useCotizacionesListado(params?: CotizacionesListParams) {
  return useQuery({
    queryKey: ['cotizaciones', 'list', params],
    queryFn: async () => {
      const res = await apiClient.get('/cotizaciones', { params })
      return (res.data as any[]) as CotizacionItem[]
    },
  })
}

export function useCotizacion(id: number, enabled = true) {
  return useQuery({
    queryKey: ['cotizaciones', 'detail', id],
    queryFn: async () => {
      const res = await apiClient.get(`/cotizaciones/${id}`)
      return res.data as CotizacionItem
    },
    enabled: enabled && id > 0,
  })
}

export interface CrearCotizacionInput {
  id_cliente: number
  fecha_cotizacion?: string
  descuento?: number
  impuestos?: number
  observaciones?: string
  detalles: DetalleCotizacion[]
}

export function useCrearCotizacion() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: CrearCotizacionInput) => {
      const res = await apiClient.post('/cotizaciones', data)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['cotizaciones', 'list'] })
    },
  })
}

export function useConvertirCotizacionAVenta() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id_cotizacion: number) => {
      const res = await apiClient.post(`/cotizaciones/${id_cotizacion}/convertir-a-venta`)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['cotizaciones', 'list'] })
      qc.invalidateQueries({ queryKey: ['ventas', 'list'] })
      qc.invalidateQueries({ queryKey: ['products'] })
    },
  })
}

export interface CotizacionEstadisticas {
  total_cotizaciones: number
  total_monto_cotizado: number
  cotizaciones_pendientes: number
  cotizaciones_aprobadas: number
  cotizaciones_rechazadas: number
  tasa_conversion: number
}

export function useCotizacionEstadisticas(enabled = true) {
  return useQuery({
    queryKey: ['cotizaciones', 'stats'],
    queryFn: async () => {
      const res = await apiClient.get('/cotizaciones/estadisticas')
      return res.data as CotizacionEstadisticas
    },
    enabled,
  })
}
