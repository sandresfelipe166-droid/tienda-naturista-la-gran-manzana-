import { useState, useEffect } from 'react';
import apiClient from '@/api/client';
export const useSecciones = () => {
    const [secciones, setSecciones] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const fetchSecciones = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiClient.get('/secciones?page=1&size=100');
            if (response.data.success) {
                setSecciones(response.data.data);
            }
        }
        catch (err) {
            setError(err.response?.data?.detail || 'Error al cargar secciones');
            console.error('Error fetching secciones:', err);
        }
        finally {
            setLoading(false);
        }
    };
    const crearSeccion = async (data) => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiClient.post('/secciones', data);
            if (response.data.success) {
                await fetchSecciones(); // Recargar lista
                return true;
            }
            return false;
        }
        catch (err) {
            setError(err.response?.data?.detail || 'Error al crear sección');
            console.error('Error creating seccion:', err);
            return false;
        }
        finally {
            setLoading(false);
        }
    };
    const actualizarSeccion = async (id, data) => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiClient.put(`/secciones/${id}`, data);
            if (response.data.success) {
                await fetchSecciones(); // Recargar lista
                return true;
            }
            return false;
        }
        catch (err) {
            setError(err.response?.data?.detail || 'Error al actualizar sección');
            console.error('Error updating seccion:', err);
            return false;
        }
        finally {
            setLoading(false);
        }
    };
    const eliminarSeccion = async (id, modo = 'logico') => {
        setLoading(true);
        setError(null);
        try {
            const response = await apiClient.delete(`/secciones/${id}?modo=${modo}`);
            if (response.data.success) {
                await fetchSecciones(); // Recargar lista
                return true;
            }
            return false;
        }
        catch (err) {
            setError(err.response?.data?.detail || 'Error al eliminar sección');
            console.error('Error deleting seccion:', err);
            return false;
        }
        finally {
            setLoading(false);
        }
    };
    useEffect(() => {
        fetchSecciones();
    }, []);
    return {
        secciones,
        loading,
        error,
        fetchSecciones,
        crearSeccion,
        actualizarSeccion,
        eliminarSeccion
    };
};
