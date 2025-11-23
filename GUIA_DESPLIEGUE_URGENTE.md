# 🚀 GUÍA DE DESPLIEGUE URGENTE - VERCEL + RAILWAY

## ⏱️ Tiempo estimado: 30-40 minutos

---

## 📱 PASO 1: DESPLEGAR BACKEND EN RAILWAY (15 min)

### 1.1 Crear cuenta en Railway
1. Ve a: https://railway.app
2. Haz clic en "Start a New Project"
3. Conecta tu cuenta de GitHub

### 1.2 Crear el Backend
1. Click en "New Project" → "Deploy from GitHub repo"
2. Selecciona tu repositorio: `tienda-naturista-la-gran-manzana-`
3. Railway detectará automáticamente Python/FastAPI

### 1.3 Configurar Variables de Entorno
En Railway Dashboard → Tu proyecto → Backend service → Variables:

**Copia y pega estas variables:**

```env
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=${{PORT}}

# Security - IMPORTANTE: Cambia estos valores
SECRET_KEY=cambiar-por-secreto-super-seguro-minimo-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

CSRF_SECRET=cambiar-por-csrf-secret-super-seguro
CSRF_TOKEN_EXPIRE_MINUTES=60

# Database (Railway lo auto-configura)
DATABASE_URL=${{DATABASE_URL}}

# CORS - Actualizaremos después
CORS_ORIGINS=https://tu-frontend.vercel.app
TRUSTED_HOSTS=localhost,127.0.0.1

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
RATE_LIMIT_USE_REDIS=false

# Logging
LOG_LEVEL=INFO
LOG_JSON_FORMAT=true

# Health Checks
HEALTH_CHECK_ENABLED=true
DB_HEALTH_CHECK_ENABLED=true
REDIS_HEALTH_CHECK_ENABLED=false

# Scheduler y Metrics (desactivar)
SCHEDULER_ENABLED=false
PROMETHEUS_ENABLED=false
METRICS_ENABLED=false
```

### 1.4 Agregar Base de Datos PostgreSQL
1. En Railway Dashboard → Click en "New" → "Database" → "Add PostgreSQL"
2. Railway conectará automáticamente la base de datos
3. **GUARDA la URL del backend** que Railway te da (algo como: `https://tu-backend.up.railway.app`)

### 1.5 Configurar el root directory
1. En Settings → busca "Root Directory"
2. Cambia a: `inventario-backend`
3. Railway redesplegará automáticamente

---

## 🌐 PASO 2: DESPLEGAR FRONTEND EN VERCEL (10 min)

### 2.1 Crear cuenta en Vercel
1. Ve a: https://vercel.com
2. Click en "Sign Up" → usa tu cuenta de GitHub
3. Autoriza Vercel

### 2.2 Importar el proyecto
1. Click en "Add New..." → "Project"
2. Busca y selecciona: `tienda-naturista-la-gran-manzana-`
3. Click en "Import"

### 2.3 Configurar el proyecto
En la pantalla de configuración:

- **Framework Preset**: Vite
- **Root Directory**: `inventario-frontend` ← ¡IMPORTANTE!
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### 2.4 Agregar Variables de Entorno
Click en "Environment Variables" y agrega:

**IMPORTANTE: Usa la URL del backend de Railway aquí:**

```env
VITE_API_URL=https://tu-backend-railway.up.railway.app
VITE_API_V1=/api/v1
VITE_USE_PROXY=false
VITE_ENV=production
VITE_ENABLE_PWA=true
VITE_ENABLE_OFFLINE_MODE=true
VITE_ENABLE_NOTIFICATIONS=true
```

### 2.5 Desplegar
1. Click en "Deploy"
2. Espera 2-3 minutos
3. **GUARDA la URL del frontend** (algo como: `https://tu-proyecto.vercel.app`)

---

## 🔗 PASO 3: CONECTAR FRONTEND Y BACKEND (5 min)

### 3.1 Actualizar CORS en Railway
1. Ve a Railway → Tu backend → Variables
2. Actualiza estas variables con las URLs reales:

```env
CORS_ORIGINS=https://tu-proyecto.vercel.app
TRUSTED_HOSTS=tu-backend.up.railway.app,tu-proyecto.vercel.app
```

3. Railway redesplegará automáticamente

### 3.2 Verificar Frontend en Vercel
1. Ve a Vercel → Settings → Environment Variables
2. Verifica que `VITE_API_URL` tenga la URL correcta del backend de Railway
3. Si necesitas cambiarla:
   - Actualiza la variable
   - Ve a Deployments → Click en el último deploy → "Redeploy"

---

## 📱 PASO 4: PROBAR EN TELÉFONO (5 min)

### 4.1 Abrir en el navegador del celular
1. En tu celular, abre el navegador (Chrome, Safari, etc.)
2. Ve a tu URL de Vercel: `https://tu-proyecto.vercel.app`
3. Inicia sesión con tus credenciales

### 4.2 Compartir con otros
**Simplemente comparte la URL de Vercel:**
- `https://tu-proyecto.vercel.app`

Cualquier persona con WiFi o datos móviles puede:
1. Abrir ese link en su navegador
2. Crear una cuenta o usar las credenciales que les des
3. Usar la aplicación

### 4.3 Instalar como PWA (opcional)
En el navegador del celular:
- **Android (Chrome)**: Menú → "Agregar a pantalla de inicio"
- **iPhone (Safari)**: Compartir → "Agregar a pantalla de inicio"

---

## 🐛 SOLUCIÓN DE PROBLEMAS COMUNES

### ❌ Error: "Cannot connect to backend"
**Solución:**
1. Verifica que el backend de Railway esté desplegado (verde)
2. Abre `https://tu-backend.up.railway.app/api/v1/health` en el navegador
3. Si no funciona, revisa los logs en Railway
4. Verifica que `VITE_API_URL` en Vercel tenga la URL correcta

### ❌ Error: "CORS policy"
**Solución:**
1. Ve a Railway → Variables
2. Actualiza `CORS_ORIGINS` con la URL exacta de Vercel
3. Asegúrate de NO tener espacios extras
4. Railway redesplegará automáticamente

### ❌ Error: "Build failed" en Vercel
**Solución:**
1. Verifica que el Root Directory sea `inventario-frontend`
2. Verifica que todas las variables de entorno estén configuradas
3. Revisa los logs del build en Vercel

### ❌ Frontend carga pero no muestra datos
**Solución:**
1. Abre la consola del navegador (F12)
2. Si ves errores 401/403: verifica las credenciales
3. Si ves errores de red: verifica `VITE_API_URL`

---

## 🎯 CHECKLIST FINAL

Antes de compartir la aplicación, verifica:

- [ ] Backend en Railway está desplegado y verde
- [ ] Puedes abrir: `https://tu-backend.up.railway.app/api/v1/health`
- [ ] Frontend en Vercel está desplegado y verde
- [ ] Puedes abrir: `https://tu-proyecto.vercel.app`
- [ ] Puedes iniciar sesión en el frontend
- [ ] Las variables CORS están correctamente configuradas
- [ ] Has probado en tu celular con WiFi/datos

---

## 📞 URLs IMPORTANTES PARA COMPARTIR

Una vez desplegado, tendrás:

1. **URL de la aplicación (para usuarios):**
   - `https://tu-proyecto.vercel.app`

2. **URL del backend (para desarrollo):**
   - `https://tu-backend.up.railway.app`

3. **Documentación API:**
   - `https://tu-backend.up.railway.app/docs`

---

## 💰 COSTOS

- **Vercel**: GRATIS (100GB bandwidth/mes, suficiente para tu proyecto)
- **Railway**: $5 gratis de crédito (dura ~1 mes para proyectos pequeños)

**Después del mes gratis de Railway:**
- ~$5-10/mes dependiendo del uso
- O puedes usar el plan gratuito hobby con límites

---

## ⚡ ALTERNATIVA MÁS RÁPIDA (SI TIENES PRISA)

Si Railway también te da problemas, usa:

### Backend: **Render** (gratis pero más lento)
- https://render.com
- Sigue los mismos pasos pero con Render
- Tarda ~2 min en "despertar" cuando alguien accede

### Frontend: **Vercel** (igual, es el mejor para React)

---

## 🆘 ¿NECESITAS AYUDA?

Si algo no funciona:
1. Revisa los logs en Railway/Vercel
2. Verifica que todas las URLs estén correctas (sin espacios)
3. Prueba primero en modo incógnito del navegador
4. Asegúrate de que el backend esté corriendo antes de probar el frontend

---

## 📝 NOTAS IMPORTANTES

1. **Dominio personalizado (opcional):**
   - Vercel te permite agregar un dominio propio gratis
   - Railway también permite dominios personalizados

2. **Actualizaciones:**
   - Cada push a GitHub redesplegará automáticamente
   - Puedes configurar esto en Railway/Vercel settings

3. **Monitoreo:**
   - Railway y Vercel tienen dashboards para ver logs y métricas
   - Úsalos si algo falla

4. **Seguridad:**
   - Cambia SECRET_KEY y CSRF_SECRET por valores únicos
   - Nunca compartas estas variables de entorno

---

## ✅ ¡LISTO PARA ENTREGAR!

Una vez completados estos pasos:
1. Tu aplicación estará accesible desde cualquier dispositivo con internet
2. Puedes compartir la URL de Vercel con quien quieras
3. La aplicación funcionará en celulares, tablets y computadoras
4. Tendrás una aplicación profesional desplegada en la nube

**¡Éxito con tu entrega del martes!** 🎉
