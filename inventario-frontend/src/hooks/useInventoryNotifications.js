/**
 * Hook para notificaciones en tiempo real del inventario
 *
 * Integra WebSocket con sistema de notificaciones del navegador.
 * Muestra alertas de stock bajo, productos vencidos, etc.
 */
import { useEffect, useState, useCallback } from 'react';
import { useWebSocket } from './useWebSocket';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
export function useInventoryNotifications() {
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const handleAlert = useCallback((alert) => {
        const notification = {
            ...alert,
            id: `${Date.now()}-${Math.random()}`,
            read: false,
            createdAt: new Date(),
        };
        setNotifications(prev => [notification, ...prev].slice(0, 50)); // Keep last 50
        setUnreadCount(prev => prev + 1);
        // Mostrar notificación del navegador
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(alert.title, {
                body: alert.message,
                icon: '/logo.png',
                badge: '/badge.png',
                tag: alert.alert_type,
                requireInteraction: alert.severity === 'critical',
            });
        }
        // Reproducir sonido para alertas críticas
        if (alert.severity === 'critical' || alert.severity === 'error') {
            playNotificationSound();
        }
    }, []);
    const { status, isConnected } = useWebSocket({
        url: `${WS_BASE_URL}/api/v1/ws/alerts`,
        autoConnect: true,
        onAlert: handleAlert,
    });
    const markAsRead = useCallback((id) => {
        setNotifications(prev => prev.map(n => (n.id === id ? { ...n, read: true } : n)));
        setUnreadCount(prev => Math.max(0, prev - 1));
    }, []);
    const markAllAsRead = useCallback(() => {
        setNotifications(prev => prev.map(n => ({ ...n, read: true })));
        setUnreadCount(0);
    }, []);
    const clearNotification = useCallback((id) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
        setUnreadCount(prev => {
            const notification = notifications.find(n => n.id === id);
            return notification && !notification.read ? prev - 1 : prev;
        });
    }, [notifications]);
    const clearAll = useCallback(() => {
        setNotifications([]);
        setUnreadCount(0);
    }, []);
    // Solicitar permiso de notificaciones
    useEffect(() => {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }, []);
    return {
        notifications,
        unreadCount,
        status,
        isConnected,
        markAsRead,
        markAllAsRead,
        clearNotification,
        clearAll,
    };
}
function playNotificationSound() {
    try {
        const audio = new Audio('/notification.mp3');
        audio.volume = 0.5;
        audio.play().catch(err => {
            console.warn('Could not play notification sound:', err);
        });
    }
    catch (error) {
        console.warn('Notification sound not available:', error);
    }
}
// Hook para solicitar permiso de notificaciones
export function useNotificationPermission() {
    const [permission, setPermission] = useState('Notification' in window ? Notification.permission : 'denied');
    const requestPermission = useCallback(async () => {
        if ('Notification' in window) {
            const result = await Notification.requestPermission();
            setPermission(result);
            return result;
        }
        return 'denied';
    }, []);
    return { permission, requestPermission };
}
