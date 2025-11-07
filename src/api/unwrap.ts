import type { ApiResponse } from '@/types'

export function unwrapApi<T>(payload: ApiResponse<T> | T): T {
  const maybe = payload as ApiResponse<T>
  if (typeof maybe === 'object' && maybe !== null && 'success' in maybe) {
    // It's an ApiResponse
    if (maybe.success && typeof maybe.data !== 'undefined') return maybe.data
    // If backend returned plain T in data, or directly T, fallback
    return (maybe.data as T) ?? (maybe as unknown as T)
  }
  return payload as T
}
