import { useQuery } from '@tanstack/react-query';
import apiClient from '@/api/client';
export function useVentasListado(params) {
    return useQuery({
        queryKey: ['ventas', 'list', params],
        queryFn: async () => {
            const res = await apiClient.get('/ventas', { params });
            // Backend retorna lista de ventas (VentaResponse[])
            const data = res.data;
            const items = (data || []).map((v) => ({
                id_venta: v.id_venta,
                fecha_venta: v.fecha_venta,
                cliente: typeof v.cliente === 'object' && v.cliente ? `${v.cliente?.nombre_cliente ?? ''}` : `${v.id_cliente}`,
                total: v.total ?? 0,
                estado: v.estado ?? 'Activo',
            }));
            return items;
        },
    });
}
