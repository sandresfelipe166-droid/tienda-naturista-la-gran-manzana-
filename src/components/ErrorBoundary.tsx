/**
 * Error Boundary para capturar errores en React
 * 
 * Previene que errores en componentes hijos rompan toda la aplicación.
 * Muestra UI de fallback amigable y loggea errores para debugging.
 */
import { Component, ErrorInfo, ReactNode } from 'react'
import './ErrorBoundary.css'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error capturado por ErrorBoundary:', error, errorInfo)
    
    this.setState({
      error,
      errorInfo,
    })

    // Callback personalizado
    this.props.onError?.(error, errorInfo)

    // Enviar a servicio de logging (Sentry, LogRocket, etc.)
    this.logErrorToService(error, errorInfo)
  }

  logErrorToService(error: Error, errorInfo: ErrorInfo) {
    // Aquí puedes integrar Sentry, LogRocket, etc.
    // Ejemplo con fetch a tu backend:
    try {
      fetch('/api/v1/logs/client-error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          error: {
            message: error.message,
            stack: error.stack,
          },
          errorInfo: {
            componentStack: errorInfo.componentStack,
          },
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          url: window.location.href,
        }),
      }).catch(err => {
        console.error('Failed to log error:', err)
      })
    } catch (err) {
      console.error('Error logging failed:', err)
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  handleReload = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      // Usar fallback personalizado si se proporciona
      if (this.props.fallback) {
        return this.props.fallback
      }

      // UI de error por defecto
      return (
        <div className="error-boundary">
          <div className="error-boundary-content">
            <div className="error-icon">⚠️</div>
            <h1>Algo salió mal</h1>
            <p className="error-message">
              Ha ocurrido un error inesperado. Nuestro equipo ha sido notificado.
            </p>
            
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="error-details">
                <summary>Detalles del error (solo desarrollo)</summary>
                <div className="error-stack">
                  <h3>{this.state.error.toString()}</h3>
                  <pre>{this.state.error.stack}</pre>
                  {this.state.errorInfo && (
                    <>
                      <h3>Component Stack:</h3>
                      <pre>{this.state.errorInfo.componentStack}</pre>
                    </>
                  )}
                </div>
              </details>
            )}

            <div className="error-actions">
              <button onClick={this.handleReset} className="btn btn-primary">
                Intentar de nuevo
              </button>
              <button onClick={this.handleReload} className="btn btn-secondary">
                Recargar página
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Hook para reportar errores manualmente
export function useErrorReporter() {
  return (error: Error, context?: Record<string, any>) => {
    console.error('Manual error report:', error, context)
    
    // Enviar a servicio de logging
    fetch('/api/v1/logs/client-error', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        error: {
          message: error.message,
          stack: error.stack,
        },
        context,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      }),
    }).catch(err => {
      console.error('Failed to report error:', err)
    })
  }
}
