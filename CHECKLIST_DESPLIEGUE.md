# 📋 LISTA DE CHEQUEO RÁPIDA - DESPLIEGUE

## 🎯 ANTES DE EMPEZAR

- [ ] Tienes cuenta de GitHub (con tu repositorio subido)
- [ ] Puedes acceder a tu correo (para confirmar cuentas)
- [ ] Tienes 40 minutos disponibles

---

## ✅ PASO 1: RAILWAY (Backend)

### Configuración inicial:
- [ ] Crear cuenta en https://railway.app con GitHub
- [ ] Click "New Project" → "Deploy from GitHub repo"
- [ ] Seleccionar repositorio: `tienda-naturista-la-gran-manzana-`
- [ ] Esperar a que Railway detecte el proyecto

### Base de datos:
- [ ] Click "New" → "Database" → "Add PostgreSQL"
- [ ] Esperar 1 minuto a que se cree la DB

### Configuración del servicio:
- [ ] Ir a Settings del servicio backend
- [ ] Cambiar "Root Directory" a: `inventario-backend`
- [ ] Guardar cambios

### Variables de entorno:
- [ ] Click en "Variables" en el servicio backend
- [ ] Ejecutar script: `.\generar-claves.ps1` para obtener claves
- [ ] Copiar estas variables (una por una):

```
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=${{PORT}}
DATABASE_URL=${{DATABASE_URL}}
LOG_LEVEL=INFO
HEALTH_CHECK_ENABLED=true
DB_HEALTH_CHECK_ENABLED=true
REDIS_HEALTH_CHECK_ENABLED=false
SCHEDULER_ENABLED=false
PROMETHEUS_ENABLED=false
METRICS_ENABLED=false
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_USE_REDIS=false
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256
```

- [ ] Agregar SECRET_KEY (del script generar-claves.ps1)
- [ ] Agregar CSRF_SECRET (del script generar-claves.ps1)
- [ ] Agregar CORS_ORIGINS (temporalmente: `*` - lo cambiaremos después)
- [ ] Agregar TRUSTED_HOSTS (temporalmente: `*` - lo cambiaremos después)

### Verificar despliegue:
- [ ] Esperar 3-5 minutos a que despliegue (ver logs)
- [ ] Cuando aparezca verde, click en el dominio generado
- [ ] **COPIAR esta URL** (algo como: `https://inventario-backend-production-xxxx.up.railway.app`)
- [ ] Agregar `/api/v1/health` al final y abrir en navegador
- [ ] Deberías ver: `{"status":"healthy",...}`

### ⚠️ Si hay error:
- [ ] Ver los logs en Railway
- [ ] Verificar que Root Directory sea `inventario-backend`
- [ ] Verificar que todas las variables estén copiadas

---

## ✅ PASO 2: VERCEL (Frontend)

### Configuración inicial:
- [ ] Crear cuenta en https://vercel.com con GitHub
- [ ] Click "Add New..." → "Project"
- [ ] Seleccionar repositorio: `tienda-naturista-la-gran-manzana-`
- [ ] Click "Import"

### Configuración del proyecto:
- [ ] Framework Preset: `Vite`
- [ ] Root Directory: Click "Edit" → escribir: `inventario-frontend`
- [ ] Build Command: `npm run build`
- [ ] Output Directory: `dist`
- [ ] Install Command: dejar en blanco (usa npm ci automáticamente)

### Variables de entorno:
- [ ] Click "Environment Variables"
- [ ] Agregar TODAS estas (reemplaza la URL del backend con la de Railway):

```
VITE_API_URL=https://TU-BACKEND-RAILWAY.up.railway.app
VITE_API_V1=/api/v1
VITE_USE_PROXY=false
VITE_ENV=production
VITE_ENABLE_PWA=true
VITE_ENABLE_OFFLINE_MODE=true
VITE_ENABLE_NOTIFICATIONS=true
VITE_ENABLE_ANALYTICS=false
```

- [ ] Click "Deploy"

### Verificar despliegue:
- [ ] Esperar 2-3 minutos (ver el progreso del build)
- [ ] Cuando termine, click en "Visit" o en el dominio generado
- [ ] **COPIAR esta URL** (algo como: `https://inventario-frontend.vercel.app`)
- [ ] Deberías ver la página de login

### ⚠️ Si hay error en build:
- [ ] Verificar que Root Directory sea `inventario-frontend`
- [ ] Verificar que todas las variables estén correctas
- [ ] Ver los logs del build
- [ ] Si falla, click "Redeploy"

---

## ✅ PASO 3: CONECTAR TODO

### Actualizar CORS en Railway:
- [ ] Volver a Railway → Tu backend → Variables
- [ ] Buscar `CORS_ORIGINS`
- [ ] Cambiar de `*` a tu URL de Vercel exacta (sin barra final):
  ```
  https://inventario-frontend.vercel.app
  ```
- [ ] Buscar `TRUSTED_HOSTS`
- [ ] Cambiar a (separados por coma sin espacios):
  ```
  inventario-backend-production-xxxx.up.railway.app,inventario-frontend.vercel.app
  ```
- [ ] Guardar y esperar 1-2 min a que redespliegue

### Verificar Vercel:
- [ ] En Vercel → Settings → Environment Variables
- [ ] Verificar que `VITE_API_URL` tenga la URL correcta de Railway
- [ ] Si la cambiaste, ir a Deployments → último deploy → "Redeploy"

---

## ✅ PASO 4: PROBAR

### En computadora:
- [ ] Abrir la URL de Vercel en navegador
- [ ] Intentar iniciar sesión
- [ ] Si no tienes usuario, crear uno
- [ ] Verificar que puedes navegar por la app

### En celular:
- [ ] Abrir navegador (Chrome/Safari)
- [ ] Escribir la URL de Vercel
- [ ] Iniciar sesión
- [ ] Probar navegación, agregar producto, etc.

### Instalar como app (opcional):
- [ ] Android: Menú → "Agregar a pantalla de inicio"
- [ ] iPhone: Compartir → "Agregar a pantalla de inicio"

---

## 🎉 COMPLETADO

Si todos los pasos están marcados, tu aplicación está lista!

### URLs finales:
```
Frontend (para usuarios): https://[tu-proyecto].vercel.app
Backend (API): https://[tu-backend].up.railway.app
Documentación API: https://[tu-backend].up.railway.app/docs
```

### Para compartir:
Solo comparte la URL del frontend con tus usuarios.

---

## 🆘 PROBLEMAS COMUNES

### Error: "Failed to fetch" o "Network Error"
1. [ ] Verificar que backend esté corriendo (verde en Railway)
2. [ ] Abrir `[backend-url]/api/v1/health` en navegador
3. [ ] Si no carga, ver logs en Railway
4. [ ] Verificar variables CORS en Railway

### Error: "CORS policy"
1. [ ] Ir a Railway → Variables
2. [ ] Verificar `CORS_ORIGINS` tenga URL exacta de Vercel
3. [ ] Sin espacios, sin barra final
4. [ ] Esperar a que redespliegue (1-2 min)

### Login no funciona
1. [ ] Abrir consola del navegador (F12)
2. [ ] Ver si hay errores rojos
3. [ ] Si dice "401" → credenciales incorrectas
4. [ ] Si dice "CORS" → ver solución arriba
5. [ ] Si dice "Network" → backend no responde

### Build de Vercel falla
1. [ ] Verificar Root Directory: `inventario-frontend`
2. [ ] Verificar que todas las variables estén puestas
3. [ ] Ver los logs del error
4. [ ] Si falla en TypeScript, puede ser error de tipado (ignorable en emergencia)

---

## 💾 GUARDAR INFORMACIÓN

Anota estas URLs en un lugar seguro:

```
Frontend: _______________________________
Backend:  _______________________________
Fecha despliegue: ________________________
Usuario admin: ___________________________
```

---

## 🔄 ACTUALIZACIONES FUTURAS

Cada vez que hagas cambios en GitHub:
- Railway redespliegue automáticamente el backend
- Vercel redespliegue automáticamente el frontend

Si no es automático:
- Railway: Click "Deploy" manualmente
- Vercel: Deployments → "Redeploy"

---

✅ **¡LISTO PARA TU ENTREGA DEL MARTES!**
