import { useQuery } from '@tanstack/react-query';
import apiClient from '@/api/client';
export function useLotes(id_producto) {
    return useQuery({
        queryKey: ['lotes', id_producto],
        queryFn: async () => {
            if (!id_producto)
                return [];
            const res = await apiClient.get(`/inventory/lotes`, { params: { id_producto } });
            return res.data;
        },
        enabled: !!id_producto,
    });
}
