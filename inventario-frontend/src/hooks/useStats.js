import { useQuery } from '@tanstack/react-query';
import apiClient from '@/api/client';
const statsKeys = {
    ventasMes: (mes, anio) => ['stats', 'ventas', 'mes', mes, anio],
    ventasAnio: (anio) => ['stats', 'ventas', 'anio', anio],
    gastosMes: (mes, anio) => ['stats', 'gastos', 'mes', mes, anio],
    gastosAnio: (anio) => ['stats', 'gastos', 'anio', anio],
};
export function useVentasMes(mes, anio, enabled = true) {
    return useQuery({
        queryKey: statsKeys.ventasMes(mes, anio),
        queryFn: async () => {
            const res = await apiClient.get(`/ventas/estadisticas/mes`, {
                params: { mes, año: anio },
            });
            return res.data;
        },
        enabled,
    });
}
export function useVentasAnio(anio, enabled = true) {
    return useQuery({
        queryKey: statsKeys.ventasAnio(anio),
        queryFn: async () => {
            const res = await apiClient.get(`/ventas/estadisticas/año`, {
                params: { año: anio },
            });
            return res.data;
        },
        enabled,
    });
}
export function useGastosMes(mes, anio, enabled = true) {
    return useQuery({
        queryKey: statsKeys.gastosMes(mes, anio),
        queryFn: async () => {
            const res = await apiClient.get(`/gastos/estadisticas/mes`, {
                params: { mes, año: anio },
            });
            return res.data;
        },
        enabled,
    });
}
export function useGastosAnio(anio, enabled = true) {
    return useQuery({
        queryKey: statsKeys.gastosAnio(anio),
        queryFn: async () => {
            const res = await apiClient.get(`/gastos/estadisticas/año`, {
                params: { año: anio },
            });
            return res.data;
        },
        enabled,
    });
}
