// Service Worker para Progressive Web App
const CACHE_NAME = 'inventario-v1.1'
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/manifest.json',
  // Core shell assets (agregar según build)
  '/vite.svg'
]

// Instalar Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('📦 Service Worker: Cache abierto')
      // No fallar si algún asset no se encuentra
      return Promise.allSettled(
        ASSETS_TO_CACHE.map(url => 
          cache.add(url).catch(err => console.warn(`⚠️ No se pudo cachear: ${url}`, err))
        )
      )
    })
  )
  self.skipWaiting()
})

// Activar Service Worker
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('🗑️  Service Worker: Limpiando cache antiguo:', cacheName)
            return caches.delete(cacheName)
          }
        })
      )
    })
  )
  self.clients.claim()
})

// Estrategia: Network first, fallback to cache
self.addEventListener('fetch', (event) => {
  // Solo cachear requests GET
  if (event.request.method !== 'GET') {
    return
  }

  // Ignorar chrome-extension y otras URLs no HTTP(S)
  if (!event.request.url.startsWith('http')) {
    return
  }

  // Para API, usar network first
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Cachear respuestas exitosas GET
          if (response.status === 200) {
            const responseToCache = response.clone()
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache)
            })
          }
          return response
        })
        .catch(() => {
          // Volver a cache si falla
          return caches.match(event.request).then((response) => {
            return response || new Response(
              JSON.stringify({ error: 'Sin conexión', offline: true }), 
              { 
                status: 503, 
                headers: { 'Content-Type': 'application/json' } 
              }
            )
          })
        })
    )
    return
  }

  // Para assets, usar cache first
  event.respondWith(
    caches.match(event.request).then((response) => {
      return (
        response ||
        fetch(event.request).then((response) => {
          // Cachear assets nuevos
          if (response.status === 200) {
            const responseToCache = response.clone()
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache)
            })
          }
          return response
        }).catch(() => {
          // Si es navegación, devolver index.html del cache
          if (event.request.mode === 'navigate') {
            return caches.match('/index.html')
          }
          return new Response('', { status: 404 })
        })
      )
    })
  )
})

// Mensaje desde cliente
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }
})
