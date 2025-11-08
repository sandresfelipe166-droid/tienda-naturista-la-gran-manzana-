import { useQuery } from '@tanstack/react-query';
import apiClient from '@/api/client';
export function useGastosListado(params) {
    return useQuery({
        queryKey: ['gastos', 'list', params],
        queryFn: async () => {
            const res = await apiClient.get('/gastos', { params });
            const data = res.data;
            const items = (data || []).map((g) => ({
                id_gasto: g.id_gasto,
                fecha_gasto: g.fecha_gasto,
                concepto: g.concepto,
                categoria: g.categoria,
                monto: g.monto ?? 0,
                metodo_pago: g.metodo_pago ?? undefined,
                observaciones: g.observaciones ?? undefined,
            }));
            return items;
        },
    });
}
