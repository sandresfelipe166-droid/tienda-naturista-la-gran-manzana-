import { useQuery } from '@tanstack/react-query'
import apiClient from '@/api/client'

export interface VentaItemUI {
  id_venta: number
  fecha_venta: string
  cliente: string
  total: number
  estado: string
}

export function useVentasListado(params?: { mes?: number; año?: number; id_cliente?: number; skip?: number; limit?: number }) {
  return useQuery({
    queryKey: ['ventas', 'list', params],
    queryFn: async () => {
      const res = await apiClient.get('/ventas', { params })
      // Backend retorna lista de ventas (VentaResponse[])
      const data = res.data as any[]
      const items: VentaItemUI[] = (data || []).map((v: any) => ({
        id_venta: v.id_venta,
        fecha_venta: v.fecha_venta,
        cliente: typeof v.cliente === 'object' && v.cliente ? `${v.cliente?.nombre_cliente ?? ''}` : `${v.id_cliente}`,
        total: v.total ?? 0,
        estado: v.estado ?? 'Activo',
      }))
      return items
    },
  })
}
