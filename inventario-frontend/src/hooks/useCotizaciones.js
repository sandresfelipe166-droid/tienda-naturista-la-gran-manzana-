import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/api/client';
export function useCotizacionesListado(params) {
    return useQuery({
        queryKey: ['cotizaciones', 'list', params],
        queryFn: async () => {
            const res = await apiClient.get('/cotizaciones', { params });
            return res.data;
        },
    });
}
export function useCotizacion(id, enabled = true) {
    return useQuery({
        queryKey: ['cotizaciones', 'detail', id],
        queryFn: async () => {
            const res = await apiClient.get(`/cotizaciones/${id}`);
            return res.data;
        },
        enabled: enabled && id > 0,
    });
}
export function useCrearCotizacion() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (data) => {
            const res = await apiClient.post('/cotizaciones', data);
            return res.data;
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ['cotizaciones', 'list'] });
        },
    });
}
export function useConvertirCotizacionAVenta() {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async (id_cotizacion) => {
            const res = await apiClient.post(`/cotizaciones/${id_cotizacion}/convertir-a-venta`);
            return res.data;
        },
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ['cotizaciones', 'list'] });
            qc.invalidateQueries({ queryKey: ['ventas', 'list'] });
            qc.invalidateQueries({ queryKey: ['products'] });
        },
    });
}
export function useCotizacionEstadisticas(enabled = true) {
    return useQuery({
        queryKey: ['cotizaciones', 'stats'],
        queryFn: async () => {
            const res = await apiClient.get('/cotizaciones/estadisticas');
            return res.data;
        },
        enabled,
    });
}
