import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/api/client';
export function useEntradasListado(params) {
    return useQuery({
        queryKey: ['entradas', 'list', params],
        queryFn: async () => {
            const res = await apiClient.get('/entradas', { params });
            return res.data;
        },
    });
}
export function useCrearEntrada() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (data) => {
            const res = await apiClient.post('/entradas', data);
            return res.data;
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ['entradas', 'list'] });
            qc.invalidateQueries({ queryKey: ['entradas', 'stats'] });
            qc.invalidateQueries({ queryKey: ['products'] });
        },
    });
}
export function useEntradasMes(mes, año, enabled = true) {
    return useQuery({
        queryKey: ['entradas', 'stats', 'mes', mes, año],
        queryFn: async () => {
            const res = await apiClient.get('/entradas/estadisticas/mes', { params: { mes, año } });
            return res.data;
        },
        enabled,
    });
}
export function useEntradasAnio(año, enabled = true) {
    return useQuery({
        queryKey: ['entradas', 'stats', 'año', año],
        queryFn: async () => {
            const res = await apiClient.get('/entradas/estadisticas/año', { params: { año } });
            return res.data;
        },
        enabled,
    });
}
