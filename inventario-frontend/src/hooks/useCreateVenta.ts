import { useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/api/client'

export interface CrearVentaDetalleInput {
  id_lote: number
  cantidad: number
  precio_unitario: number
}

export interface CrearVentaInput {
  id_cliente: number
  metodo_pago: string
  descuento?: number
  impuestos?: number
  detalles: CrearVentaDetalleInput[]
}

export function useCreateVenta() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: CrearVentaInput) => {
      const res = await apiClient.post('/ventas', data)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['ventas', 'list'] })
      qc.invalidateQueries({ queryKey: ['stats', 'ventas'] })
    },
  })
}
