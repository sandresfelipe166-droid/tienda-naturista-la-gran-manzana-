# Inventario Frontend

Frontend React + TypeScript para el sistema de gestión de inventario.

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
npm install
```

### 2. Configurar variables de entorno

Edita `.env`:
```
VITE_API_URL=http://localhost:8000
VITE_API_V1=/api/v1
```

### 3. Iniciar servidor de desarrollo

```bash
npm run dev
```

Abre http://localhost:3000

### 4. Compilar para producción

```bash
npm run build
```

## 📁 Estructura del Proyecto

```
src/
├── pages/           # Páginas de la aplicación
├── components/      # Componentes reutilizables
├── hooks/           # Custom hooks
├── store/           # Estado global (Zustand)
├── api/             # Cliente HTTP
├── types/           # TypeScript types
├── styles/          # Estilos CSS
├── App.tsx          # Componente raíz
└── main.tsx         # Entry point
```

## 🔐 Autenticación

El sistema usa JWT tokens. El flujo es:

1. Usuario hace login
2. Backend retorna `access_token` y `refresh_token`
3. Frontend guarda en `localStorage`
4. Axios interceptor agrega token a cada request
5. Si token expira (401), usuario es redirigido a login

## 🎯 Características

- ✅ Autenticación con JWT
- ✅ Rutas protegidas
- ✅ Gestión de estado con Zustand
- ✅ Fetching de datos con React Query
- ✅ TypeScript strict mode
- ✅ Diseño responsive

## 🛠️ Tecnologías

- **React 18** - UI Framework
- **TypeScript** - Lenguaje tipado
- **Vite** - Build tool
- **React Router** - Routing
- **Zustand** - State management
- **React Query** - Server state
- **Axios** - HTTP client

## 📝 Variables de Entorno

```env
VITE_API_URL=http://localhost:8000          # URL del backend
VITE_API_V1=/api/v1                        # Ruta de la API
```

## 🚨 Troubleshooting

### npm no está reconocido
- Instala Node.js desde https://nodejs.org/

### Error: Cannot find module
- Ejecuta `npm install`

### El login no funciona
- Verifica que el backend esté corriendo en http://localhost:8000
- Revisa el .env con las URLs correctas
- Abre DevTools (F12) y revisa la pestaña Network

### CORS errors
- Verifica que el backend tenga CORS configurado
- Usa vite.config.ts con proxy

## 📞 Contacto

Para dudas sobre el backend, revisa `inventario-backend/README.md`

---

**Status:** ✅ Production-ready
