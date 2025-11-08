import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/api/client';
import { unwrapApi } from '@/api/unwrap';
// Query keys
export const productKeys = {
    all: ['products'],
    lists: () => [...productKeys.all, 'list'],
    list: (filters) => [...productKeys.lists(), filters],
    details: () => [...productKeys.all, 'detail'],
    detail: (id) => [...productKeys.details(), id],
};
// Get all products
export const useProducts = (filters) => {
    return useQuery({
        queryKey: productKeys.list(filters),
        queryFn: async () => {
            const response = await apiClient.get('/productos', {
                params: filters,
            });
            // Backend retorna ProductoPaginatedResponse con data: ProductoBase[]
            const payload = response.data;
            if (payload && payload.success && Array.isArray(payload.data)) {
                // Adaptar a ProductListResponse esperado por el UI
                const items = payload.data.map((p) => ({
                    id: p.id_producto,
                    nombre: p.nombre_producto,
                    descripcion: p.descripcion ?? '',
                    cantidad: p.stock_actual ?? 0,
                    precio: p.precio_compra ?? 0,
                    sku: p.codigo_barras ?? '',
                    categoria: p.forma_farmaceutica ?? '',
                    id_seccion: p.id_seccion,
                    id_laboratorio: p.id_laboratorio,
                    estado: (p.estado?.toLowerCase?.() === 'activo' ? 'activo' : 'inactivo'),
                    created_at: '',
                    updated_at: '',
                }));
                const pagination = payload.pagination || { page: 1, size: items.length, total: items.length, pages: 1 };
                return { items, total: pagination.total, page: pagination.page, per_page: pagination.size, pages: pagination.pages };
            }
            return unwrapApi(payload);
        },
    });
};
// Get single product
export const useProductDetail = (id) => {
    return useQuery({
        queryKey: productKeys.detail(id),
        queryFn: async () => {
            const response = await apiClient.get(`/productos/${id}`);
            return unwrapApi(response.data);
        },
        enabled: !!id,
    });
};
// Create product
export const useCreateProduct = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (data) => {
            // Mapear a ProductoCreate del backend
            const payload = {
                id_seccion: data.id_seccion,
                id_laboratorio: data.id_laboratorio,
                nombre_producto: data.nombre,
                descripcion: data.descripcion,
                precio_compra: data.precio,
                stock_actual: data.cantidad,
                stock_minimo: Math.min(5, data.cantidad ?? 5),
                codigo_barras: data.sku,
                forma_farmaceutica: data.categoria,
                estado: 'Activo',
            };
            const response = await apiClient.post('/productos', payload);
            const p = response.data.data;
            // Adaptar a Producto UI
            const created = {
                id: p.id_producto,
                nombre: p.nombre_producto,
                descripcion: p.descripcion ?? '',
                cantidad: p.stock_actual ?? 0,
                precio: p.precio_compra ?? 0,
                sku: p.codigo_barras ?? '',
                categoria: p.forma_farmaceutica ?? '',
                estado: (p.estado?.toLowerCase?.() === 'activo' ? 'activo' : 'inactivo'),
                created_at: '',
                updated_at: '',
            };
            return created;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: productKeys.lists() });
        },
    });
};
// Update product
export const useUpdateProduct = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ id, data }) => {
            const payload = {
                id_seccion: data.id_seccion,
                id_laboratorio: data.id_laboratorio,
                nombre_producto: data.nombre,
                descripcion: data.descripcion,
                precio_compra: data.precio,
                stock_actual: data.cantidad,
                codigo_barras: data.sku,
                forma_farmaceutica: data.categoria,
            };
            const response = await apiClient.put(`/productos/${id}`, payload);
            const p = response.data.data;
            const updated = {
                id: p.id_producto,
                nombre: p.nombre_producto,
                descripcion: p.descripcion ?? '',
                cantidad: p.stock_actual ?? 0,
                precio: p.precio_compra ?? 0,
                sku: p.codigo_barras ?? '',
                categoria: p.forma_farmaceutica ?? '',
                estado: (p.estado?.toLowerCase?.() === 'activo' ? 'activo' : 'inactivo'),
                created_at: '',
                updated_at: '',
            };
            return updated;
        },
        onSuccess: (_, { id }) => {
            queryClient.invalidateQueries({ queryKey: productKeys.detail(id) });
            queryClient.invalidateQueries({ queryKey: productKeys.lists() });
        },
    });
};
// Delete product
export const useDeleteProduct = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (id) => {
            await apiClient.delete(`/productos/${id}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: productKeys.lists() });
        },
    });
};
