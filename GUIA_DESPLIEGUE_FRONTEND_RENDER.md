# 🌐 Guía de Despliegue Frontend en Render

## 📋 Pre-requisitos

✅ Backend desplegado y funcionando en: `https://inventario-backend-o0gu.onrender.com`

---

## 🔧 Archivos Creados/Modificados

### 1. **`.env.production`** (NUEVO)
Configuración de variables de entorno para producción:
```bash
VITE_API_URL=https://inventario-backend-o0gu.onrender.com
VITE_API_V1=/api/v1
VITE_WS_URL=wss://inventario-backend-o0gu.onrender.com
VITE_ENV=production
```

---

## 🚀 Pasos para Desplegar el Frontend

### 1️⃣ Commit y Push los Cambios

```powershell
# En la carpeta inventario-frontend
cd C:\Users\cleiv\Desktop\inventario-frontend

git add .env.production
git commit -m "feat: Añadir configuración de producción para Render"
git push origin main
```

### 2️⃣ Crear Static Site en Render

1. **Ve a Render Dashboard:**
   - https://dashboard.render.com

2. **Click en "New" → "Static Site"**

3. **Conectar Repositorio:**
   - Selecciona tu repositorio: `inventario-tienda_naturista`
   - Branch: `main`
   - Root Directory: `inventario-frontend` (si es monorepo) o dejar vacío

4. **Configurar Build Settings:**
   ```
   Build Command: npm run build
   Publish Directory: dist
   ```

5. **Variables de Entorno (opcional en Static Site):**
   Las variables están en `.env.production` y se inyectan durante el build.

6. **Click en "Create Static Site"**

### 3️⃣ Esperar el Build

El proceso toma 2-4 minutos. Render ejecutará:
```bash
npm install
npm run build
# Publica el contenido de /dist
```

### 4️⃣ Obtener la URL del Frontend

Una vez desplegado, Render te dará una URL como:
```
https://inventario-frontend-XXXX.onrender.com
```

### 5️⃣ Actualizar CORS en el Backend

**IMPORTANTE:** Debes agregar la URL del frontend al CORS del backend.

**En Render Dashboard:**
- Ve a: inventario-backend-o0gu
- Settings → Environment
- Busca la variable `CORS_ORIGINS`
- Actualiza el valor a:
  ```
  https://inventario-frontend-XXXX.onrender.com,http://localhost:5173
  ```
- Guarda cambios
- Manual Deploy → Deploy latest commit

---

## 🔍 Verificación Post-Despliegue

### 1. Abrir el Frontend
```
https://inventario-frontend-XXXX.onrender.com
```

### 2. Verificar Console del Browser
Presiona `F12` → Console

**Debería NO haber errores de CORS:**
```
✅ API connected successfully
```

**Si ves errores de CORS:**
```
❌ Access to XMLHttpRequest at 'https://...' has been blocked by CORS policy
```
→ Verifica que hayas actualizado `CORS_ORIGINS` en el backend.

### 3. Probar Login
1. Ir a `/login`
2. Intentar iniciar sesión
3. Verificar que la autenticación funciona

---

## 📁 Estructura de Build

El comando `npm run build` genera:
```
dist/
  ├── index.html
  ├── assets/
  │   ├── index-[hash].js
  │   ├── index-[hash].css
  │   └── [otros archivos]
  └── ...
```

Render sirve estos archivos estáticos automáticamente.

---

## ⚙️ Configuración Avanzada (Opcional)

### Custom Domain
Si tienes un dominio propio:
1. Render Settings → Custom Domain
2. Añade tu dominio (ej: `inventario.tudominio.com`)
3. Configura los DNS records que Render te indica
4. Actualiza `CORS_ORIGINS` en el backend con tu dominio

### Redirects para SPA
Si usas React Router, crea `_redirects` en `public/`:
```
/*    /index.html   200
```

O `public/_headers`:
```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
```

### Build Hooks
Para re-deploys automáticos cuando cambia el backend:
1. Render Settings → Build & Deploy
2. Copy "Deploy Hook URL"
3. Úsalo en CI/CD o webhooks

---

## 🐛 Troubleshooting

### Error: "VITE_API_URL is not defined"
**Solución:** 
- Verifica que `.env.production` exista
- Las variables deben empezar con `VITE_`
- Rebuild el proyecto

### Error: CORS policy
**Solución:**
1. Verifica que el backend esté corriendo
2. Verifica `CORS_ORIGINS` en el backend incluye la URL del frontend
3. Redespliega el backend después de cambiar CORS
4. Limpia caché del browser: `Ctrl + Shift + R`

### Error 404 en rutas
**Solución:**
- Añade archivo `_redirects` en `public/`:
  ```
  /*    /index.html   200
  ```

### Build falla con errores de TypeScript
**Solución:**
```powershell
# Localmente, verifica que compila
npm run build

# Si hay errores, corríge los tipos
# Puedes temporalmente desactivar type check en build
# (no recomendado para producción)
```

### El sitio carga pero no hace requests al backend
**Solución:**
1. Abre DevTools → Network
2. Verifica que las requests van a `https://inventario-backend-o0gu.onrender.com`
3. Si van a `localhost:8000`, verifica `.env.production` se esté usando

---

## 📊 Métricas y Monitoreo

### Ver Logs de Build
Render Dashboard → Static Site → Events

### Analytics (opcional)
Si habilitaste `VITE_ENABLE_ANALYTICS=true`, configura tu servicio de analytics.

### Uptime Monitoring
Render Free tier incluye:
- SSL/TLS automático
- CDN global
- 100GB bandwidth/mes

---

## 🔄 Proceso de Actualización

Cuando hagas cambios al frontend:

```powershell
# 1. Hacer cambios
# 2. Commit y push
git add .
git commit -m "feat: Nueva funcionalidad"
git push origin main

# 3. Render detecta y redespliega automáticamente
# 4. Espera 2-3 minutos
# 5. Refresca el browser
```

---

## ✅ Checklist de Despliegue Frontend

- [ ] `.env.production` creado con URLs correctas
- [ ] Cambios commiteados y pusheados
- [ ] Static Site creado en Render
- [ ] Build exitoso sin errores
- [ ] URL del frontend obtenida
- [ ] `CORS_ORIGINS` actualizado en backend
- [ ] Backend redesplgado con nuevo CORS
- [ ] Frontend abre correctamente
- [ ] No hay errores de CORS en Console
- [ ] Login funciona correctamente
- [ ] WebSocket conecta (si aplica)

---

## 🎯 URLs Finales

| Servicio | URL |
|----------|-----|
| **Backend API** | https://inventario-backend-o0gu.onrender.com |
| **Backend Health** | https://inventario-backend-o0gu.onrender.com/api/v1/health |
| **Backend Docs** | https://inventario-backend-o0gu.onrender.com/docs |
| **Frontend** | https://inventario-frontend-XXXX.onrender.com (actualizar) |

---

## 📚 Referencias

- [Render Static Sites](https://render.com/docs/static-sites)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [React Router Browser History](https://reactrouter.com/en/main/routers/create-browser-router)

---

**Fecha de implementación:** 9 de noviembre de 2025
**Estado:** ✅ Listo para desplegar
**Prerequisito:** Backend funcionando correctamente
