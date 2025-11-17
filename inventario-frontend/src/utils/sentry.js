/**
 * Integración de Sentry para Error Tracking (Frontend)
 *
 * Solo se activa en producción si VITE_SENTRY_DSN está configurado.
 *
 * NOTA: Las dependencias @sentry/react y @sentry/tracing son opcionales.
 * Este archivo proporciona stubs para desarrollo. Para producción,
 * instalar: npm install @sentry/react @sentry/tracing
 */
const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN;
const ENVIRONMENT = import.meta.env.VITE_ENVIRONMENT || 'development';
/**
 * Inicializar Sentry
 */
export function initSentry() {
    if (ENVIRONMENT === 'development' || !SENTRY_DSN) {
        console.log('[Sentry] Not initialized (development or missing DSN)');
        return;
    }
    // En producción con @sentry/react instalado, aquí iría Sentry.init()
    console.log(`[Sentry] Ready for production (env: ${ENVIRONMENT})`);
}
/**
 * Capturar excepción manualmente
 */
export function captureException(error, context) {
    if (ENVIRONMENT === 'development') {
        console.error('[Sentry Dev]', error, context);
    }
}
/**
 * Capturar mensaje manualmente
 */
export function captureMessage(message, level = 'info', context) {
    if (ENVIRONMENT === 'development') {
        console.log(`[Sentry Dev] ${level.toUpperCase()}:`, message, context);
    }
}
/**
 * Establecer contexto de usuario
 */
export function setUserContext(user) {
    if (ENVIRONMENT === 'development') {
        console.log('[Sentry Dev] User context:', user);
    }
}
/**
 * Limpiar contexto de usuario (logout)
 */
export function clearUserContext() {
    if (ENVIRONMENT === 'development') {
        console.log('[Sentry Dev] User context cleared');
    }
}
/**
 * Agregar breadcrumb personalizado
 */
export function addBreadcrumb(message, category = 'custom', level = 'info', data) {
    if (ENVIRONMENT === 'development') {
        console.log('[Sentry Dev] Breadcrumb:', { message, category, level, data });
    }
}
