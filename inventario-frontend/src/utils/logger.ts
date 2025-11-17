/**
 * Sistema de Logging Profesional para Frontend
 * 
 * Funcionalidades:
 * - Logging condicional basado en entorno (DEV vs PROD)
 * - Sanitización automática de datos sensibles
 * - Integración con Sentry (futuro)
 * - Formateo consistente de mensajes
 * 
 * Uso:
 * ```typescript
 * import logger from '@/utils/logger'
 * 
 * logger.info('Usuario autenticado', { userId: 123 })
 * logger.error('Error en request', error)
 * logger.debug('Estado del componente', { state })
 * ```
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error'

interface LogContext {
  [key: string]: any
}

class Logger {
  private isDevelopment: boolean
  private enabledLevels: Set<LogLevel>

  constructor() {
    this.isDevelopment = import.meta.env.DEV
    
    // En producción, solo errores críticos
    this.enabledLevels = this.isDevelopment 
      ? new Set(['debug', 'info', 'warn', 'error'])
      : new Set(['error'])
  }

  /**
   * Sanitiza datos sensibles antes de loguear
   */
  private sanitize(data: any): any {
    if (!data || typeof data !== 'object') {
      return data
    }

    const sensitiveKeys = [
      'password', 
      'token', 
      'authorization', 
      'secret', 
      'apiKey',
      'jwt',
      'refreshToken',
      'accessToken'
    ]

    const sanitized = Array.isArray(data) ? [...data] : { ...data }

    for (const key in sanitized) {
      const lowerKey = key.toLowerCase()
      
      // Redactar campos sensibles
      if (sensitiveKeys.some(sensitive => lowerKey.includes(sensitive))) {
        sanitized[key] = '[REDACTED]'
      } 
      // Recursión para objetos anidados
      else if (typeof sanitized[key] === 'object' && sanitized[key] !== null) {
        sanitized[key] = this.sanitize(sanitized[key])
      }
    }

    return sanitized
  }

  /**
   * Formatea el mensaje con timestamp y contexto
   */
  private formatMessage(level: LogLevel, message: string, context?: LogContext): string {
    const timestamp = new Date().toISOString()
    const prefix = `[${timestamp}] [${level.toUpperCase()}]`
    
    if (!context || Object.keys(context).length === 0) {
      return `${prefix} ${message}`
    }

    const sanitizedContext = this.sanitize(context)
    return `${prefix} ${message} | Context: ${JSON.stringify(sanitizedContext)}`
  }

  /**
   * Logging de debug (solo en desarrollo)
   */
  debug(message: string, context?: LogContext): void {
    if (!this.enabledLevels.has('debug')) return

    const formatted = this.formatMessage('debug', message, context)
    console.log(`🔍 ${formatted}`)
  }

  /**
   * Logging de información general
   */
  info(message: string, context?: LogContext): void {
    if (!this.enabledLevels.has('info')) return

    const formatted = this.formatMessage('info', message, context)
    console.log(`ℹ️ ${formatted}`)
  }

  /**
   * Logging de advertencias
   */
  warn(message: string, context?: LogContext): void {
    if (!this.enabledLevels.has('warn')) return

    const formatted = this.formatMessage('warn', message, context)
    console.warn(`⚠️ ${formatted}`)
  }

  /**
   * Logging de errores (siempre activo, incluso en producción)
   */
  error(message: string, error?: Error | unknown, context?: LogContext): void {
    if (!this.enabledLevels.has('error')) return

    let errorDetails: any = {}

    if (error instanceof Error) {
      errorDetails = {
        name: error.name,
        message: error.message,
        stack: this.isDevelopment ? error.stack : undefined,
      }
    } else if (error) {
      errorDetails = { error }
    }

    const fullContext = { ...context, ...errorDetails }
    const formatted = this.formatMessage('error', message, fullContext)

    if (this.isDevelopment) {
      console.error(`❌ ${formatted}`, error)
    } else {
      // En producción, no exponemos stack traces completos
      console.error(`❌ [ERROR] ${message}`)
      
      // TODO: Enviar a Sentry cuando esté configurado
      // if (window.Sentry) {
      //   window.Sentry.captureException(error, { extra: context })
      // }
    }
  }

  /**
   * Logging de eventos de negocio importantes
   */
  event(eventName: string, data?: LogContext): void {
    if (!this.enabledLevels.has('info')) return

    this.info(`Event: ${eventName}`, data)
    
    // TODO: Enviar a analytics cuando esté configurado
    // if (window.analytics) {
    //   window.analytics.track(eventName, data)
    // }
  }

  /**
   * Logging de performance (timings)
   */
  perf(label: string, duration: number): void {
    if (!this.enabledLevels.has('debug')) return

    const formatted = `⏱️ Performance: ${label} completed in ${duration.toFixed(2)}ms`
    console.log(formatted)
  }

  /**
   * Helper para medir performance de funciones
   */
  async measure<T>(label: string, fn: () => T | Promise<T>): Promise<T> {
    const start = performance.now()
    try {
      const result = await fn()
      const duration = performance.now() - start
      this.perf(label, duration)
      return result
    } catch (error) {
      const duration = performance.now() - start
      this.error(`${label} failed after ${duration.toFixed(2)}ms`, error)
      throw error
    }
  }
}

// Exportar instancia singleton
const logger = new Logger()

export default logger

// Exportar tipos para uso en otros archivos
export type { LogLevel, LogContext }
