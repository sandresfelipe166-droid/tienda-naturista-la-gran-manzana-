import { useQuery } from '@tanstack/react-query'
import apiClient from '@/api/client'

export interface GastoItemUI {
  id_gasto: number
  fecha_gasto: string
  concepto: string
  categoria: string
  monto: number
  metodo_pago?: string
  observaciones?: string
}

export function useGastosListado(params?: { mes?: number; año?: number; categoria?: string; skip?: number; limit?: number }) {
  return useQuery({
    queryKey: ['gastos', 'list', params],
    queryFn: async () => {
      const res = await apiClient.get('/gastos', { params })
      const data = res.data as any[]
      const items: GastoItemUI[] = (data || []).map((g: any) => ({
        id_gasto: g.id_gasto,
        fecha_gasto: g.fecha_gasto,
        concepto: g.concepto,
        categoria: g.categoria,
        monto: g.monto ?? 0,
        metodo_pago: g.metodo_pago ?? undefined,
        observaciones: g.observaciones ?? undefined,
      }))
      return items
    },
  })
}
