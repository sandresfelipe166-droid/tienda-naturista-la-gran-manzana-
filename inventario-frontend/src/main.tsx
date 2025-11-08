import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClientProvider, QueryClient } from '@tanstack/react-query'
import App from './App'
import './index.css'
// breakpoints integrados en styles/mobile-optimized.css (consolidación)
import './styles/mobile-optimized.css'
// Registro PWA (vite-plugin-pwa auto inyectará, pero añadimos flush de outbox al volver online)
import { flush, hasPending } from '@/offline/outbox'
import { useAuthStore } from '@/store/authStore'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 1,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
)

// Intento de flush cuando vuelve la conexión
window.addEventListener('online', () => {
  if (hasPending()) {
    const { token } = useAuthStore.getState()
    flush(token || undefined)
  }
})
