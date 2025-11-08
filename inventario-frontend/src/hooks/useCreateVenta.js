import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/api/client';
export function useCreateVenta() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (data) => {
            const res = await apiClient.post('/ventas', data);
            return res.data;
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ['ventas', 'list'] });
            qc.invalidateQueries({ queryKey: ['stats', 'ventas'] });
        },
    });
}
