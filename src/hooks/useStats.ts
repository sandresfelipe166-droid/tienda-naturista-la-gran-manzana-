import { useQuery } from '@tanstack/react-query'
import apiClient from '@/api/client'
import { VentaEstadisticasMes, VentaEstadisticasAnio, GastoEstadisticasMes, GastoEstadisticasAnio } from '@/types'

const statsKeys = {
  ventasMes: (mes: number, anio: number) => ['stats', 'ventas', 'mes', mes, anio],
  ventasAnio: (anio: number) => ['stats', 'ventas', 'anio', anio],
  gastosMes: (mes: number, anio: number) => ['stats', 'gastos', 'mes', mes, anio],
  gastosAnio: (anio: number) => ['stats', 'gastos', 'anio', anio],
}

export function useVentasMes(mes: number, anio: number, enabled = true) {
  return useQuery({
    queryKey: statsKeys.ventasMes(mes, anio),
    queryFn: async () => {
      const res = await apiClient.get<VentaEstadisticasMes>(`/ventas/estadisticas/mes`, {
        params: { mes, año: anio },
      })
      return res.data
    },
    enabled,
  })
}

export function useVentasAnio(anio: number, enabled = true) {
  return useQuery({
    queryKey: statsKeys.ventasAnio(anio),
    queryFn: async () => {
      const res = await apiClient.get<VentaEstadisticasAnio>(`/ventas/estadisticas/año`, {
        params: { año: anio },
      })
      return res.data
    },
    enabled,
  })
}

export function useGastosMes(mes: number, anio: number, enabled = true) {
  return useQuery({
    queryKey: statsKeys.gastosMes(mes, anio),
    queryFn: async () => {
      const res = await apiClient.get<GastoEstadisticasMes>(`/gastos/estadisticas/mes`, {
        params: { mes, año: anio },
      })
      return res.data
    },
    enabled,
  })
}

export function useGastosAnio(anio: number, enabled = true) {
  return useQuery({
    queryKey: statsKeys.gastosAnio(anio),
    queryFn: async () => {
      const res = await apiClient.get<GastoEstadisticasAnio>(`/gastos/estadisticas/año`, {
        params: { año: anio },
      })
      return res.data
    },
    enabled,
  })
}
