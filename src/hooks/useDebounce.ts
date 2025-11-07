/**
 * Hook personalizado para debounce con feedback visual
 * Proporciona estado de loading durante el debounce
 * 
 * @param value - Valor a debounce
 * @param delay - Delay en milisegundos (default: 350ms)
 * @returns { debouncedValue, isDebouncing }
 */
import { useState, useEffect } from 'react'

export function useDebounceWithLoading<T>(value: T, delay: number = 350) {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)
  const [isDebouncing, setIsDebouncing] = useState(false)

  useEffect(() => {
    // Si el valor cambió, empezar a debounce
    if (value !== debouncedValue) {
      setIsDebouncing(true)
    }

    const handler = setTimeout(() => {
      setDebouncedValue(value)
      setIsDebouncing(false)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay, debouncedValue])

  return { debouncedValue, isDebouncing }
}

/**
 * Hook para estado de loading con timeout automático
 * Previene estados de loading infinitos
 * 
 * @param timeout - Timeout máximo en milisegundos (default: 30s)
 */
export function useSafeLoading(timeout: number = 30000) {
  const [isLoading, setIsLoading] = useState(false)

  const startLoading = () => {
    setIsLoading(true)
    
    // Timeout de seguridad
    const timer = setTimeout(() => {
      console.warn('Loading timeout alcanzado')
      setIsLoading(false)
    }, timeout)

    return () => clearTimeout(timer)
  }

  const stopLoading = () => {
    setIsLoading(false)
  }

  return { isLoading, startLoading, stopLoading }
}
