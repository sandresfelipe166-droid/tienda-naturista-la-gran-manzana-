import { useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/api/client';
export function useCreateGasto() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (data) => {
            const res = await apiClient.post('/gastos', data);
            return res.data;
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ['gastos', 'list'] });
            qc.invalidateQueries({ queryKey: ['stats', 'gastos'] });
        },
    });
}
