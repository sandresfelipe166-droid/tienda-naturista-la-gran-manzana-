/**
 * Hook para Optimistic Updates
 *
 * Actualiza la UI inmediatamente antes de que el servidor responda.
 * Si el servidor falla, revierte los cambios automáticamente.
 *
 * ROI: Mejora UX percibida en 10x (respuesta instantánea vs 200-500ms de latencia)
 */
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
/**
 * Hook para mutaciones con optimistic updates
 *
 * Ejemplo:
 * ```tsx
 * const updateProduct = useOptimisticUpdate({
 *   mutationFn: (data) => apiClient.put(`/productos/${data.id}`, data),
 *   queryKey: ['productos'],
 *   updateFn: (old, newData) => {
 *     return old?.map(p => p.id === newData.id ? {...p, ...newData} : p)
 *   },
 * })
 *
 * // La UI se actualiza inmediatamente
 * updateProduct.mutate({ id: 1, nombre: 'Nuevo nombre' })
 * ```
 */
export function useOptimisticUpdate(options) {
    const queryClient = useQueryClient();
    const mutation = useMutation({
        mutationFn: options.mutationFn,
        // Antes de la mutación
        onMutate: async (variables) => {
            // Cancelar queries en curso para evitar que sobrescriban el optimistic update
            await queryClient.cancelQueries({ queryKey: options.queryKey });
            // Snapshot del estado actual
            const previousData = queryClient.getQueryData(options.queryKey);
            // Actualizar optimísticamente
            queryClient.setQueryData(options.queryKey, (old) => options.updateFn(old, variables));
            // Retornar contexto con snapshot para rollback
            return { previousData };
        },
        // Si hay error, revertir
        onError: (error, variables, context) => {
            if (context?.previousData) {
                queryClient.setQueryData(options.queryKey, context.previousData);
            }
            options.onError?.(error, variables, context);
        },
        // Cuando la mutación es exitosa
        onSuccess: (data, variables) => {
            options.onSuccess?.(data, variables);
        },
        // Siempre refetch después de error o éxito
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: options.queryKey });
        },
    });
    return mutation;
}
/**
 * Hook para mutaciones con optimistic ADD (agregar item a lista)
 */
export function useOptimisticAdd(options) {
    return useOptimisticUpdate({
        ...options,
        updateFn: (old, variables) => {
            const tempId = options.generateTempId?.() || `temp-${Date.now()}`;
            const newItem = { ...variables, id: tempId };
            return [...(old || []), newItem];
        },
    });
}
/**
 * Hook para mutaciones con optimistic UPDATE (actualizar item en lista)
 */
export function useOptimisticUpdate_Item(options) {
    return useOptimisticUpdate({
        ...options,
        updateFn: (old, variables) => {
            if (!old)
                return [];
            return old.map(item => item.id === variables.id
                ? { ...item, ...variables }
                : item);
        },
    });
}
/**
 * Hook para mutaciones con optimistic DELETE (eliminar item de lista)
 */
export function useOptimisticDelete(options) {
    return useOptimisticUpdate({
        ...options,
        updateFn: (old, variables) => {
            if (!old)
                return [];
            return old.filter(item => item.id !== variables.id);
        },
    });
}
/**
 * Hook para loading states más sofisticados
 */
export function useLoadingState() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [progress, setProgress] = useState(0);
    const withLoading = async (promise, options) => {
        setIsLoading(true);
        setError(null);
        setProgress(0);
        try {
            // Simular progreso si no hay callback real
            const progressInterval = setInterval(() => {
                setProgress(prev => {
                    const next = prev + 10;
                    return next >= 90 ? 90 : next;
                });
            }, 200);
            const result = await (options?.timeout
                ? Promise.race([
                    promise,
                    new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), options.timeout))
                ])
                : promise);
            clearInterval(progressInterval);
            setProgress(100);
            return result;
        }
        catch (err) {
            setError(err);
            throw err;
        }
        finally {
            setIsLoading(false);
            setTimeout(() => setProgress(0), 500);
        }
    };
    return {
        isLoading,
        error,
        progress,
        withLoading,
    };
}
