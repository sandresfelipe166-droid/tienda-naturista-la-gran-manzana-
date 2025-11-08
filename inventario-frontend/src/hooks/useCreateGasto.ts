import { useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/api/client'

export interface CrearGastoInput {
  fecha_gasto: string
  concepto: string
  categoria: string
  monto: number
  metodo_pago?: string
  numero_factura?: string
  proveedor?: string
  observaciones?: string
}

export function useCreateGasto() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: CrearGastoInput) => {
      const res = await apiClient.post('/gastos', data)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['gastos', 'list'] })
      qc.invalidateQueries({ queryKey: ['stats', 'gastos'] })
    },
  })
}
