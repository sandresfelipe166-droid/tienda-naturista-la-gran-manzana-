/**
 * Componente de notificaciones en tiempo real
 * 
 * Muestra alertas del inventario con diseño toast moderno.
 */
import { useInventoryNotifications } from '@/hooks/useInventoryNotifications'
import { WebSocketStatus } from '@/hooks/useWebSocket'
import './NotificationPanel.css'

interface NotificationPanelProps {
  onClose?: () => void
}

export function NotificationPanel({ onClose }: NotificationPanelProps) {
  const {
    notifications,
    unreadCount,
    status,
    isConnected,
    markAsRead,
    markAllAsRead,
    clearNotification,
    clearAll,
  } = useInventoryNotifications()

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '#dc2626' // red-600
      case 'error':
        return '#ea580c' // orange-600
      case 'warning':
        return '#f59e0b' // amber-500
      case 'info':
      default:
        return '#3b82f6' // blue-500
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '🔴'
      case 'error':
        return '⚠️'
      case 'warning':
        return '⚡'
      case 'info':
      default:
        return 'ℹ️'
    }
  }

  const getAlertTypeLabel = (alertType: string) => {
    const labels: Record<string, string> = {
      stock_bajo: 'Stock Bajo',
      producto_expirado: 'Producto Expirado',
      producto_proximo_vencer: 'Próximo a Vencer',
      inventory_update: 'Actualización',
    }
    return labels[alertType] || alertType
  }

  return (
    <div className="notification-panel">
      <div className="notification-header">
        <div className="notification-title">
          <span className="notification-icon">🔔</span>
          <h3>Notificaciones</h3>
          {unreadCount > 0 && (
            <span className="notification-badge">{unreadCount}</span>
          )}
        </div>
        
        <div className="notification-header-actions">
          <div className="notification-status">
            <span
              className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}
              title={isConnected ? 'Conectado' : 'Desconectado'}
            />
            <span className="status-text">
              {status === WebSocketStatus.CONNECTING && 'Conectando...'}
              {status === WebSocketStatus.CONNECTED && 'En línea'}
              {status === WebSocketStatus.DISCONNECTED && 'Desconectado'}
              {status === WebSocketStatus.RECONNECTING && 'Reconectando...'}
              {status === WebSocketStatus.ERROR && 'Error'}
            </span>
          </div>
          
          {onClose && (
            <button
              className="notification-panel-close"
              onClick={onClose}
              title="Cerrar panel"
              style={{
                background: 'none',
                border: 'none',
                fontSize: '1.5rem',
                cursor: 'pointer',
                padding: '0 8px',
                color: '#666',
                marginLeft: '12px'
              }}
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {notifications.length > 0 && (
        <div className="notification-actions">
          <button
            className="btn-text"
            onClick={markAllAsRead}
            disabled={unreadCount === 0}
          >
            Marcar todas como leídas
          </button>
          <button className="btn-text btn-danger" onClick={clearAll}>
            Limpiar todas
          </button>
        </div>
      )}

      <div className="notification-list">
        {notifications.length === 0 ? (
          <div className="notification-empty">
            <span className="empty-icon">📭</span>
            <p>No hay notificaciones</p>
          </div>
        ) : (
          notifications.map((notification) => (
            <div
              key={notification.id}
              className={`notification-item ${notification.read ? 'read' : 'unread'}`}
              onClick={() => markAsRead(notification.id)}
              style={{
                borderLeftColor: getSeverityColor(notification.severity),
              }}
            >
              <div className="notification-content">
                <div className="notification-item-header">
                  <span className="notification-severity-icon">
                    {getSeverityIcon(notification.severity)}
                  </span>
                  <span className="notification-type">
                    {getAlertTypeLabel(notification.alert_type)}
                  </span>
                  <span className="notification-time">
                    {formatTimeAgo(notification.createdAt)}
                  </span>
                </div>
                
                <h4 className="notification-item-title">
                  {notification.title}
                </h4>
                
                <p className="notification-item-message">
                  {notification.message}
                </p>

                {notification.data && Object.keys(notification.data).length > 0 && (
                  <div className="notification-data">
                    {notification.data.producto_nombre && (
                      <span className="data-tag">
                        📦 {notification.data.producto_nombre}
                      </span>
                    )}
                    {notification.data.stock_actual !== undefined && (
                      <span className="data-tag">
                        📊 Stock: {notification.data.stock_actual}
                      </span>
                    )}
                    {notification.data.dias_restantes !== undefined && (
                      <span className="data-tag">
                        ⏰ {notification.data.dias_restantes} días
                      </span>
                    )}
                  </div>
                )}
              </div>

              <button
                className="notification-close"
                onClick={(e) => {
                  e.stopPropagation()
                  clearNotification(notification.id)
                }}
                title="Eliminar"
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

function formatTimeAgo(date: Date): string {
  const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000)

  if (seconds < 60) return 'Ahora'
  if (seconds < 3600) return `Hace ${Math.floor(seconds / 60)}m`
  if (seconds < 86400) return `Hace ${Math.floor(seconds / 3600)}h`
  return `Hace ${Math.floor(seconds / 86400)}d`
}
