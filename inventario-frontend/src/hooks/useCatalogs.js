import { useQuery } from '@tanstack/react-query';
import apiClient from '@/api/client';
export const useSecciones = () => {
    return useQuery({
        queryKey: ['secciones', { page: 1, size: 100, estado: 'Activo' }],
        queryFn: async () => {
            const resp = await apiClient.get('/secciones', {
                params: { page: 1, size: 100, estado: 'Activo' },
            });
            return resp.data.data || [];
        },
    });
};
export const useLaboratorios = () => {
    return useQuery({
        queryKey: ['laboratorios', { page: 1, size: 100, estado: 'Activo' }],
        queryFn: async () => {
            const resp = await apiClient.get('/laboratorios', {
                params: { page: 1, size: 100, estado: 'Activo' },
            });
            return resp.data.data || [];
        },
    });
};
