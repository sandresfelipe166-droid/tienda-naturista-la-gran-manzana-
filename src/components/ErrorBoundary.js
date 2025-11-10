import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Error Boundary para capturar errores en React
 *
 * Previene que errores en componentes hijos rompan toda la aplicación.
 * Muestra UI de fallback amigable y loggea errores para debugging.
 */
import { Component } from 'react';
import './ErrorBoundary.css';
export class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        Object.defineProperty(this, "handleReset", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: () => {
                this.setState({
                    hasError: false,
                    error: null,
                    errorInfo: null,
                });
            }
        });
        Object.defineProperty(this, "handleReload", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: () => {
                window.location.reload();
            }
        });
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
        };
    }
    static getDerivedStateFromError(error) {
        return {
            hasError: true,
            error,
            errorInfo: null,
        };
    }
    componentDidCatch(error, errorInfo) {
        console.error('Error capturado por ErrorBoundary:', error, errorInfo);
        this.setState({
            error,
            errorInfo,
        });
        // Callback personalizado
        this.props.onError?.(error, errorInfo);
        // Enviar a servicio de logging (Sentry, LogRocket, etc.)
        this.logErrorToService(error, errorInfo);
    }
    logErrorToService(error, errorInfo) {
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
                console.error('Failed to log error:', err);
            });
        }
        catch (err) {
            console.error('Error logging failed:', err);
        }
    }
    render() {
        if (this.state.hasError) {
            // Usar fallback personalizado si se proporciona
            if (this.props.fallback) {
                return this.props.fallback;
            }
            // UI de error por defecto
            return (_jsx("div", { className: "error-boundary", children: _jsxs("div", { className: "error-boundary-content", children: [_jsx("div", { className: "error-icon", children: "\u26A0\uFE0F" }), _jsx("h1", { children: "Algo sali\u00F3 mal" }), _jsx("p", { className: "error-message", children: "Ha ocurrido un error inesperado. Nuestro equipo ha sido notificado." }), process.env.NODE_ENV === 'development' && this.state.error && (_jsxs("details", { className: "error-details", children: [_jsx("summary", { children: "Detalles del error (solo desarrollo)" }), _jsxs("div", { className: "error-stack", children: [_jsx("h3", { children: this.state.error.toString() }), _jsx("pre", { children: this.state.error.stack }), this.state.errorInfo && (_jsxs(_Fragment, { children: [_jsx("h3", { children: "Component Stack:" }), _jsx("pre", { children: this.state.errorInfo.componentStack })] }))] })] })), _jsxs("div", { className: "error-actions", children: [_jsx("button", { onClick: this.handleReset, className: "btn btn-primary", children: "Intentar de nuevo" }), _jsx("button", { onClick: this.handleReload, className: "btn btn-secondary", children: "Recargar p\u00E1gina" })] })] }) }));
        }
        return this.props.children;
    }
}
// Hook para reportar errores manualmente
export function useErrorReporter() {
    return (error, context) => {
        console.error('Manual error report:', error, context);
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
            console.error('Failed to report error:', err);
        });
    };
}
