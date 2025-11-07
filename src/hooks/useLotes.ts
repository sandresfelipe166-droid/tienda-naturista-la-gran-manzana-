import { useQuery } from '@tanstack/react-query'
import apiClient from '@/api/client'

export interface LoteItem {
  id_lote: number
  id_producto: number
  numero_lote: string
  fecha_vencimiento: string
  cantidad_disponible: number
  precio_compra: number
}

export function useLotes(id_producto?: number) {
  return useQuery({
    queryKey: ['lotes', id_producto],
    queryFn: async () => {
      if (!id_producto) return []
      const res = await apiClient.get(`/inventory/lotes`, { params: { id_producto } })
      return (res.data as any[]) as LoteItem[]
    },
    enabled: !!id_producto,
  })
}
