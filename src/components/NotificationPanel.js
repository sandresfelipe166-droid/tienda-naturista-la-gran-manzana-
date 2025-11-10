import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Componente de notificaciones en tiempo real
 *
 * Muestra alertas del inventario con diseño toast moderno.
 */
import { useInventoryNotifications } from '@/hooks/useInventoryNotifications';
import { WebSocketStatus } from '@/hooks/useWebSocket';
import './NotificationPanel.css';
export function NotificationPanel({ onClose }) {
    const { notifications, unreadCount, status, isConnected, markAsRead, markAllAsRead, clearNotification, clearAll, } = useInventoryNotifications();
    const getSeverityColor = (severity) => {
        switch (severity) {
            case 'critical':
                return '#dc2626'; // red-600
            case 'error':
                return '#ea580c'; // orange-600
            case 'warning':
                return '#f59e0b'; // amber-500
            case 'info':
            default:
                return '#3b82f6'; // blue-500
        }
    };
    const getSeverityIcon = (severity) => {
        switch (severity) {
            case 'critical':
                return '🔴';
            case 'error':
                return '⚠️';
            case 'warning':
                return '⚡';
            case 'info':
            default:
                return 'ℹ️';
        }
    };
    const getAlertTypeLabel = (alertType) => {
        const labels = {
            stock_bajo: 'Stock Bajo',
            producto_expirado: 'Producto Expirado',
            producto_proximo_vencer: 'Próximo a Vencer',
            inventory_update: 'Actualización',
        };
        return labels[alertType] || alertType;
    };
    return (_jsxs("div", { className: "notification-panel", children: [_jsxs("div", { className: "notification-header", children: [_jsxs("div", { className: "notification-title", children: [_jsx("span", { className: "notification-icon", children: "\uD83D\uDD14" }), _jsx("h3", { children: "Notificaciones" }), unreadCount > 0 && (_jsx("span", { className: "notification-badge", children: unreadCount }))] }), _jsxs("div", { className: "notification-header-actions", children: [_jsxs("div", { className: "notification-status", children: [_jsx("span", { className: `status-indicator ${isConnected ? 'connected' : 'disconnected'}`, title: isConnected ? 'Conectado' : 'Desconectado' }), _jsxs("span", { className: "status-text", children: [status === WebSocketStatus.CONNECTING && 'Conectando...', status === WebSocketStatus.CONNECTED && 'En línea', status === WebSocketStatus.DISCONNECTED && 'Desconectado', status === WebSocketStatus.RECONNECTING && 'Reconectando...', status === WebSocketStatus.ERROR && 'Error'] })] }), onClose && (_jsx("button", { className: "notification-panel-close", onClick: onClose, title: "Cerrar panel", style: {
                                    background: 'none',
                                    border: 'none',
                                    fontSize: '1.5rem',
                                    cursor: 'pointer',
                                    padding: '0 8px',
                                    color: '#666',
                                    marginLeft: '12px'
                                }, children: "\u2715" }))] })] }), notifications.length > 0 && (_jsxs("div", { className: "notification-actions", children: [_jsx("button", { className: "btn-text", onClick: markAllAsRead, disabled: unreadCount === 0, children: "Marcar todas como le\u00EDdas" }), _jsx("button", { className: "btn-text btn-danger", onClick: clearAll, children: "Limpiar todas" })] })), _jsx("div", { className: "notification-list", children: notifications.length === 0 ? (_jsxs("div", { className: "notification-empty", children: [_jsx("span", { className: "empty-icon", children: "\uD83D\uDCED" }), _jsx("p", { children: "No hay notificaciones" })] })) : (notifications.map((notification) => (_jsxs("div", { className: `notification-item ${notification.read ? 'read' : 'unread'}`, onClick: () => markAsRead(notification.id), style: {
                        borderLeftColor: getSeverityColor(notification.severity),
                    }, children: [_jsxs("div", { className: "notification-content", children: [_jsxs("div", { className: "notification-item-header", children: [_jsx("span", { className: "notification-severity-icon", children: getSeverityIcon(notification.severity) }), _jsx("span", { className: "notification-type", children: getAlertTypeLabel(notification.alert_type) }), _jsx("span", { className: "notification-time", children: formatTimeAgo(notification.createdAt) })] }), _jsx("h4", { className: "notification-item-title", children: notification.title }), _jsx("p", { className: "notification-item-message", children: notification.message }), notification.data && Object.keys(notification.data).length > 0 && (_jsxs("div", { className: "notification-data", children: [notification.data.producto_nombre && (_jsxs("span", { className: "data-tag", children: ["\uD83D\uDCE6 ", notification.data.producto_nombre] })), notification.data.stock_actual !== undefined && (_jsxs("span", { className: "data-tag", children: ["\uD83D\uDCCA Stock: ", notification.data.stock_actual] })), notification.data.dias_restantes !== undefined && (_jsxs("span", { className: "data-tag", children: ["\u23F0 ", notification.data.dias_restantes, " d\u00EDas"] }))] }))] }), _jsx("button", { className: "notification-close", onClick: (e) => {
                                e.stopPropagation();
                                clearNotification(notification.id);
                            }, title: "Eliminar", children: "\u00D7" })] }, notification.id)))) })] }));
}
function formatTimeAgo(date) {
    const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000);
    if (seconds < 60)
        return 'Ahora';
    if (seconds < 3600)
        return `Hace ${Math.floor(seconds / 60)}m`;
    if (seconds < 86400)
        return `Hace ${Math.floor(seconds / 3600)}h`;
    return `Hace ${Math.floor(seconds / 86400)}d`;
}
