# 🚀 Guía Completa de Despliegue en Render

Esta guía te llevará paso a paso para desplegar correctamente el backend (API) y el frontend (React) de tu sistema de inventario en Render.

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Preparación del Repositorio](#preparación-del-repositorio)
3. [Despliegue del Backend](#despliegue-del-backend)
4. [Despliegue del Frontend](#despliegue-del-frontend)
5. [Configuración Post-Despliegue](#configuración-post-despliegue)
6. [Verificación y Pruebas](#verificación-y-pruebas)
7. [Solución de Problemas](#solución-de-problemas)

---

## 📦 Requisitos Previos

Antes de comenzar, asegúrate de tener:

- ✅ Cuenta en [Render.com](https://render.com) (puedes usar GitHub para registrarte)
- ✅ Repositorio en GitHub con el código actualizado
- ✅ Git instalado localmente
- ✅ Acceso a tu terminal/PowerShell

---

## 🔧 Preparación del Repositorio

### Paso 1: Verificar la Estructura del Proyecto

Tu repositorio debe tener esta estructura:

```
tienda-naturista-la-gran-manzana-/
├── inventario-backend/
│   ├── app/
│   ├── alembic/
│   ├── main.py
│   ├── requirements.txt
│   ├── runtime.txt
│   ├── start.sh
│   └── render.yaml
└── inventario-frontend/
    ├── src/
    ├── public/
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── build.sh
    └── render.yaml
```

### Paso 2: Subir los Cambios a GitHub

Abre tu terminal de PowerShell y ejecuta:

```powershell
# Navegar al directorio del backend
cd C:\Users\cleiv\Desktop\inventario-backend

# Verificar el estado de Git
git status

# Añadir todos los archivos modificados
git add .

# Hacer commit con un mensaje descriptivo
git commit -m "feat: configuración completa para despliegue en Render"

# Subir los cambios a GitHub
git push origin main

# Repetir para el frontend
cd C:\Users\cleiv\Desktop\inventario-frontend
git add .
git commit -m "feat: configuración completa para despliegue en Render"
git push origin main
```

---

## 🖥️ Despliegue del Backend

### Paso 1: Crear el Servicio de Base de Datos

1. **Inicia sesión en Render**: Ve a [dashboard.render.com](https://dashboard.render.com)

2. **Crear nueva base de datos**:
   - Click en **"New +"** → **"PostgreSQL"**
   - Configuración:
     - **Name**: `inventario-db`
     - **Database**: `inventario`
     - **User**: `inventario_user`
     - **Region**: `Oregon (US West)`
     - **Plan**: `Free`
   - Click en **"Create Database"**

3. **Guardar la URL de conexión**:
   - Una vez creada, copia la **Internal Database URL**
   - La necesitarás en el siguiente paso

### Paso 2: Crear el Servicio Web del Backend

1. **Crear nuevo servicio web**:
   - Click en **"New +"** → **"Web Service"**
   - Selecciona **"Build and deploy from a Git repository"**
   - Click **"Next"**

2. **Conectar tu repositorio**:
   - Busca y selecciona: `sandresfelipe166-droid/tienda-naturista-la-gran-manzana-`
   - Click **"Connect"**

3. **Configurar el servicio**:
   - **Name**: `inventario-backend`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Root Directory**: Dejar en blanco o usar `.` (punto)
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     ./start.sh
     ```
   - **Plan**: `Free`

4. **Configurar variables de entorno** (en la sección "Environment"):

   Click en **"Add Environment Variable"** para cada una de estas:

   ```
   PYTHON_VERSION=3.11.0
   ENVIRONMENT=production
   DEBUG=false
   HOST=0.0.0.0
   PORT=10000
   
   # Database (usa la URL que copiaste antes)
   DATABASE_URL=postgresql://inventario_user:XXXX@XXXX.oregon-postgres.render.com/inventario
   DB_POOL_SIZE=10
   DB_MAX_OVERFLOW=20
   DB_POOL_TIMEOUT=30
   DB_POOL_RECYCLE=3600
   CREATE_SCHEMA_ON_STARTUP=false
   
   # Security - JWT (Render puede auto-generar estas)
   SECRET_KEY=[Auto-generar: click en "Generate"]
   JWT_ALG=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   
   # Security - CSRF
   CSRF_SECRET=[Auto-generar: click en "Generate"]
   
   # CORS - IMPORTANTE: Actualizarás esto después
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173
   TRUSTED_HOSTS=*.onrender.com,localhost,127.0.0.1
   ALLOW_ALL_HOSTS_DEV=false
   
   # Rate Limiting
   RATE_LIMIT_REQUESTS=100
   RATE_LIMIT_WINDOW=60
   
   # Logging
   LOG_LEVEL=INFO
   LOG_JSON_FORMAT=true
   
   # Features
   SCHEDULER_ENABLED=false
   HEALTH_CHECK_ENABLED=true
   DB_HEALTH_CHECK_ENABLED=true
   METRICS_ENABLED=false
   PROMETHEUS_ENABLED=false
   SSL_ENABLED=false
   
   # Session
   SESSION_COOKIE_SECURE=true
   SESSION_COOKIE_HTTPONLY=true
   SESSION_COOKIE_SAMESITE=lax
   
   # Password Policy
   MIN_PASSWORD_LENGTH=8
   REQUIRE_SPECIAL_CHARS=true
   REQUIRE_UPPERCASE=true
   REQUIRE_NUMBERS=true
   PASSWORD_RESET_EXPIRE_MINUTES=15
   ```

5. **Configurar Health Check**:
   - En la sección **"Health Check"**, configura:
     - **Health Check Path**: `/api/v1/health`

6. **Crear el servicio**:
   - Click en **"Create Web Service"**
   - Render comenzará a construir y desplegar tu backend
   - Esto tomará unos 5-10 minutos

7. **Esperar a que termine el despliegue**:
   - Observa los logs en tiempo real
   - Verás mensajes como:
     ```
     📦 Ejecutando migraciones de base de datos...
     ✓ Migraciones aplicadas exitosamente
     🌐 Iniciando servidor Uvicorn...
     ```
   - Cuando veas "Your service is live 🎉", ¡el backend está listo!

8. **Obtener la URL del backend**:
   - En la parte superior verás algo como: `https://inventario-backend-xxxx.onrender.com`
   - **COPIA ESTA URL**, la necesitarás para el frontend

---

## 🎨 Despliegue del Frontend

### Paso 1: Actualizar Variables de Entorno

Antes de desplegar el frontend, necesitas actualizar la URL del backend.

1. **Editar archivo `.env.production`**:
   
   En tu computadora local, abre:
   `C:\Users\cleiv\Desktop\inventario-frontend\.env.production`
   
   Actualiza con la URL real de tu backend:
   ```bash
   # API Configuration - PRODUCCIÓN RENDER
   VITE_API_URL=https://inventario-backend-xxxx.onrender.com
   VITE_API_V1=/api/v1
   
   # WebSocket Configuration
   VITE_WS_URL=wss://inventario-backend-xxxx.onrender.com
   
   # Environment
   VITE_ENV=production
   
   # Features
   VITE_ENABLE_NOTIFICATIONS=true
   VITE_ENABLE_ANALYTICS=false
   ```

2. **Guardar y subir los cambios**:
   ```powershell
   cd C:\Users\cleiv\Desktop\inventario-frontend
   git add .env.production
   git commit -m "update: configurar URL del backend en producción"
   git push origin main
   ```

### Paso 2: Crear el Servicio Web del Frontend

1. **Crear nuevo servicio**:
   - En el dashboard de Render, click en **"New +"** → **"Static Site"**
   - Selecciona tu repositorio: `sandresfelipe166-droid/tienda-naturista-la-gran-manzana-`
   - Click **"Connect"**

2. **Configurar el servicio**:
   - **Name**: `inventario-frontend`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Root Directory**: `inventario-frontend`
   - **Build Command**: 
     ```bash
     npm ci --legacy-peer-deps && npm run build
     ```
   - **Publish Directory**: `dist`

3. **Configurar variables de entorno**:

   Click en **"Advanced"** → **"Add Environment Variable"**:

   ```
   NODE_VERSION=18.17.0
   VITE_API_URL=https://inventario-backend-xxxx.onrender.com
   VITE_API_V1=/api/v1
   VITE_WS_URL=wss://inventario-backend-xxxx.onrender.com
   VITE_ENV=production
   VITE_ENABLE_NOTIFICATIONS=true
   VITE_ENABLE_ANALYTICS=false
   ```

   **⚠️ IMPORTANTE**: Reemplaza `inventario-backend-xxxx` con la URL real de tu backend.

4. **Configurar redirecciones** (para React Router):
   - En **"Redirects/Rewrites"**, agrega:
     - **Source**: `/*`
     - **Destination**: `/index.html`
     - **Action**: `Rewrite`

5. **Crear el sitio**:
   - Click en **"Create Static Site"**
   - El despliegue tomará unos 3-5 minutos

6. **Obtener la URL del frontend**:
   - Una vez desplegado, verás: `https://inventario-frontend-xxxx.onrender.com`
   - **GUARDA ESTA URL**

---

## 🔄 Configuración Post-Despliegue

### Paso 1: Actualizar CORS en el Backend

Ahora que tienes la URL del frontend, debes permitirla en el backend:

1. **Volver al servicio del backend** en Render
2. **Ir a "Environment"**
3. **Editar la variable `CORS_ORIGINS`**:
   ```
   CORS_ORIGINS=https://inventario-frontend-xxxx.onrender.com,http://localhost:3000,http://localhost:5173
   ```
4. **Guardar los cambios**
5. El servicio se reiniciará automáticamente

### Paso 2: Verificar Trusted Hosts

También verifica que `TRUSTED_HOSTS` incluya Render:
```
TRUSTED_HOSTS=*.onrender.com,localhost,127.0.0.1
```

---

## ✅ Verificación y Pruebas

### 1. Probar el Backend

Abre en tu navegador:
```
https://inventario-backend-xxxx.onrender.com/api/v1/health
```

Deberías ver una respuesta JSON como:
```json
{
  "status": "healthy",
  "timestamp": "2024-11-11T10:00:00Z",
  "version": "1.0.0"
}
```

### 2. Probar el Frontend

Abre en tu navegador:
```
https://inventario-frontend-xxxx.onrender.com
```

Deberías ver:
- ✅ La página de login del sistema
- ✅ Sin errores en la consola del navegador (F12)
- ✅ Posibilidad de iniciar sesión

### 3. Prueba de Integración Completa

1. **Intenta iniciar sesión** con las credenciales por defecto o crea un usuario
2. **Navega por las diferentes secciones** del sistema
3. **Realiza operaciones básicas**: 
   - Agregar un producto
   - Editar un producto
   - Ver el inventario

### 4. Verificar Logs

Si algo falla:

**Backend:**
- En Render → Tu servicio backend → pestaña "Logs"
- Busca mensajes de error en rojo

**Frontend:**
- F12 en tu navegador → pestaña "Console"
- Busca errores de red o JavaScript

---

## 🔧 Solución de Problemas Comunes

### Problema 1: Error 502 Bad Gateway

**Síntoma**: El backend no responde.

**Solución**:
1. Verifica que `start.sh` tenga permisos de ejecución
2. Revisa los logs del backend en Render
3. Verifica que `DATABASE_URL` esté correctamente configurada
4. Asegúrate de que las migraciones se ejecutaron correctamente

### Problema 2: CORS Error en el Frontend

**Síntoma**: Error en consola: "CORS policy: No 'Access-Control-Allow-Origin'"

**Solución**:
1. Verifica que `CORS_ORIGINS` en el backend incluya la URL completa del frontend
2. No uses trailing slash en las URLs
3. Reinicia el servicio del backend después de cambiar CORS

### Problema 3: Frontend No Carga o Muestra Página Blanca

**Síntoma**: Página en blanco o errores 404.

**Solución**:
1. Verifica que `dist` sea el directorio de publicación
2. Asegúrate de que las redirecciones estén configuradas (`/* → /index.html`)
3. Revisa los logs de build en Render
4. Verifica que todas las variables `VITE_*` estén configuradas

### Problema 4: Base de Datos No Se Conecta

**Síntoma**: Errores de conexión a PostgreSQL.

**Solución**:
1. Verifica que `DATABASE_URL` esté correctamente copiada
2. Asegúrate de usar la **Internal Database URL**, no la External
3. Verifica que la base de datos esté en el mismo plan (Free)

### Problema 5: Build Falla

**Síntoma**: El build del frontend o backend falla.

**Solución Backend**:
```bash
# Verifica requirements.txt
# Asegúrate de que todas las dependencias estén listadas
```

**Solución Frontend**:
```bash
# Usa --legacy-peer-deps si hay conflictos
npm ci --legacy-peer-deps
```

---

## 📝 Comandos Útiles para Actualizar

### Actualizar Backend

```powershell
cd C:\Users\cleiv\Desktop\inventario-backend
git add .
git commit -m "update: descripción de los cambios"
git push origin main
```

Render detectará automáticamente el cambio y re-desplegará.

### Actualizar Frontend

```powershell
cd C:\Users\cleiv\Desktop\inventario-frontend
git add .
git commit -m "update: descripción de los cambios"
git push origin main
```

Render re-construirá y desplegará automáticamente.

### Forzar Re-despliegue

Si necesitas forzar un re-despliegue sin cambios:

1. Ve a tu servicio en Render
2. Click en **"Manual Deploy"** → **"Deploy latest commit"**

---

## 🎉 ¡Felicidades!

Si has seguido todos los pasos correctamente, ahora tienes:

- ✅ Backend API desplegado y funcionando
- ✅ Base de datos PostgreSQL configurada
- ✅ Frontend React desplegado
- ✅ Integración completa entre frontend y backend
- ✅ URLs públicas para acceder a tu aplicación

### URLs Finales

- **Backend API**: `https://inventario-backend-xxxx.onrender.com`
- **Frontend App**: `https://inventario-frontend-xxxx.onrender.com`
- **API Docs**: `https://inventario-backend-xxxx.onrender.com/docs`
- **Health Check**: `https://inventario-backend-xxxx.onrender.com/api/v1/health`

---

## 📚 Recursos Adicionales

- [Documentación de Render](https://render.com/docs)
- [Render Status](https://status.render.com/)
- [Render Community](https://community.render.com/)

---

## 🆘 Soporte

Si encuentras problemas adicionales:

1. **Revisa los logs detalladamente** en Render
2. **Verifica las variables de entorno** dos veces
3. **Asegúrate de que GitHub tenga los últimos cambios**
4. **Consulta la documentación de Render** para tu caso específico

---

**Última actualización**: 11 de noviembre de 2025  
**Versión**: 1.0.0
