# 🚀 GUÍA DE DESPLIEGUE EN RENDER - Paso a Paso

**Repositorio:** `sandresfelipe166-droid/tienda-naturista-la-gran-manzana-`  
**Fecha:** 9 de noviembre de 2025

---

## 📋 PRE-REQUISITOS

- [x] Cuenta en [Render.com](https://render.com)
- [x] Repositorio conectado a GitHub
- [x] Código pusheado a rama `main`

---

## 🗄️ PASO 1: Crear Base de Datos PostgreSQL

1. **Render Dashboard** → **New +** → **PostgreSQL**
2. Configuración:
   - **Name:** `inventario-db-naturista`
   - **Database:** `inventario`
   - **User:** (generado automático)
   - **Region:** `Oregon` (o tu región preferida)
   - **Plan:** `Starter` (gratis 90 días)
3. **Create Database**
4. ⚠️ **IMPORTANTE:** Copia la **Internal Database URL** (aparece en la pestaña "Info")
   - Formato: `postgresql://user:pass@host:port/dbname`
   - **NO uses la External URL** (más lenta y menos segura)

---

## 🐳 PASO 2: Crear Backend (Web Service Docker)

### 2.1 Crear Servicio

1. **Render Dashboard** → **New +** → **Web Service**
2. **Connect Repository:**
   - Busca: `tienda-naturista-la-gran-manzana-`
   - Click **Connect**
3. **Configuración inicial:**
   - **Name:** `inventario-backend-naturista` (o el que prefieras)
   - **Region:** `Oregon` (misma que la DB)
   - **Branch:** `main`
   - Click **Advanced** y configura:
     - **Root Directory:** `inventario-backend` ⚠️ (sin `/` al inicio ni final)
     - **Runtime:** `Docker`
   - **Plan:** `Starter` (gratis)
4. **Create Web Service** (NO agregues env vars aún)

### 2.2 Agregar Variables de Entorno

Una vez creado el servicio:
1. Ve a **Settings** → **Environment**
2. Click **Add Environment Variable** y agrega cada una:

```env
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
DATABASE_URL=<PEGA_AQUI_INTERNAL_DATABASE_URL>
SECRET_KEY=<GENERA_UNA_CLAVE_SEGURA_64_CARACTERES>
CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO
PROMETHEUS_ENABLED=true
METRICS_ENABLED=true
SCHEDULER_ENABLED=false
CREATE_SCHEMA_ON_STARTUP=false
```

**Generador SECRET_KEY:** Usa este comando en tu terminal local:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

3. **Save Changes**
4. Render iniciará el deploy automáticamente

### 2.3 Aplicar Migraciones

Cuando el deploy termine (status: **Live**):
1. Ve a tu servicio → **Shell** (botón arriba a la derecha)
2. Ejecuta **en orden**:

```bash
alembic upgrade head
python scripts/seed_roles.py
python scripts/seed_admin_user.py
```

3. Si hay errores, revisa que `DATABASE_URL` sea correcta
4. **Restart** el servicio si es necesario (Actions → Restart)

### 2.4 Verificar Backend

1. Copia la URL del servicio (ej: `https://inventario-backend-naturista.onrender.com`)
2. Abre en navegador:
   - `/` → Debe mostrar JSON con info del API
   - `/docs` → Swagger UI operativo
   - `/api/v1/health` → Status OK

---

## 🌐 PASO 3: Crear Frontend (Static Site)

### 3.1 Crear Servicio

1. **Render Dashboard** → **New +** → **Static Site**
2. **Connect Repository:** `tienda-naturista-la-gran-manzana-`
3. **Configuración:**
   - **Name:** `inventario-frontend-naturista`
   - **Region:** `Oregon` (misma región)
   - **Branch:** `main`
   - Click **Advanced**:
     - **Root Directory:** `inventario-frontend` ⚠️
   - **Build Command:** `npm ci && npm run build`
   - **Publish Directory:** `dist`
4. **Create Static Site**

### 3.2 Agregar Variable de Entorno

1. **Settings** → **Environment**
2. **Add Environment Variable:**

```env
VITE_API_URL=https://inventario-backend-naturista.onrender.com
```

⚠️ Reemplaza con la URL **real** de tu backend (paso 2.4)

3. **Save Changes** → Redeploy automático

### 3.3 Verificar Frontend

1. Copia URL del sitio (ej: `https://inventario-frontend-naturista.onrender.com`)
2. Abre en navegador
3. Intenta **Login:**
   - Si funciona: ✅ Todo correcto
   - Si error CORS: → Sigue al Paso 4

---

## 🔐 PASO 4: Ajustar CORS (Backend)

1. Ve al servicio **Backend** → **Settings** → **Environment**
2. Edita `CORS_ORIGINS`:

```env
CORS_ORIGINS=https://inventario-frontend-naturista.onrender.com,http://localhost:5173
```

⚠️ Reemplaza con la URL **real** de tu frontend (sin `/` al final)

3. **Save Changes**
4. El servicio se redesplega automáticamente
5. **Prueba de nuevo** el login desde el frontend

---

## 📱 PASO 5: Instalar PWA en Móvil

### Android (Chrome)

1. Abre la URL del frontend en **Chrome móvil**
2. Navega por varias páginas (precarga cache)
3. Menú (⋮) → **Añadir a pantalla de inicio**
4. Confirma instalación
5. Abre desde el icono instalado

### iOS (Safari)

1. Abre la URL en **Safari**
2. Navega por varias páginas
3. Botón **Compartir** (cuadrado con flecha)
4. **Añadir a pantalla de inicio**
5. Abre desde el icono

### Prueba Offline

1. **Activa modo avión**
2. Abre la app instalada
3. Las páginas visitadas deben cargar
4. Intenta hacer una venta/edición:
   - Se **encolará** automáticamente (ver consola: 🕓)
5. **Desactiva modo avión**
6. Refresca: las operaciones pendientes se sincronizan

---

## ✅ CHECKLIST FINAL

### Backend ✓
- [ ] Deploy exitoso (status: Live)
- [ ] Migraciones aplicadas (`alembic upgrade head`)
- [ ] Roles creados (seed_roles.py)
- [ ] Usuario admin creado (seed_admin_user.py)
- [ ] `/docs` accesible
- [ ] CORS configurado con URL frontend real

### Frontend ✓
- [ ] Deploy exitoso
- [ ] `VITE_API_URL` apunta a backend real
- [ ] Login funciona
- [ ] DevTools → Application → Manifest presente
- [ ] Service Worker registrado

### PWA ✓
- [ ] Instalable en móvil
- [ ] Icono aparece en pantalla inicio
- [ ] Funciona offline (páginas vistas)
- [ ] Operaciones se encolan offline
- [ ] Sincronización al reconectar

### Seguridad ✓
- [ ] `SECRET_KEY` >= 64 caracteres
- [ ] `DEBUG=false` en producción
- [ ] CORS sin wildcard `*` (solo dominios necesarios)
- [ ] Variables sensibles NO en código (solo env vars)

---

## 🐛 SOLUCIÓN DE PROBLEMAS COMUNES

### Error: "no se pudo leer dockerfile"
**Causa:** Root Directory incorrecto  
**Solución:** Verifica que sea exactamente `inventario-backend` (sin `/`)

### Error 500 en backend al iniciar
**Causa:** `DATABASE_URL` incorrecta o migraciones no aplicadas  
**Solución:**
1. Revisa que copiaste la Internal DB URL completa
2. Ejecuta `alembic upgrade head` en Shell
3. Restart el servicio

### Error CORS en frontend
**Causa:** Backend no tiene la URL del frontend en `CORS_ORIGINS`  
**Solución:** Edita variable y asegúrate de NO dejar `/` al final de la URL

### Login no funciona
**Causas posibles:**
1. `VITE_API_URL` mal configurada → Verifica en Network tab
2. Backend caído → Chequea `/docs`
3. Cookies bloqueadas → Usa token JWT (ya lo hace tu `client.ts`)

### PWA no se instala
**Causas:**
1. No es HTTPS → Render da HTTPS automático, verifica URL
2. Manifest incompleto → Ya tienes uno completo en `/public/manifest.json`
3. Service Worker no registra → Abre DevTools → Application → Service Workers

### Operaciones no se encolan offline
**Causa:** El interceptor en `client.ts` ya lo hace  
**Verificación:** Abre consola → modo avión → intenta POST → debe ver "🕓 Operación encolada"

---

## 📞 SOPORTE

Si algo falla:
1. **Logs de Render:** Ve al servicio → **Logs** → Revisa errores
2. **Browser DevTools:** Console + Network tab
3. **Shell de Render:** Prueba comandos manualmente

---

## 🎯 PRÓXIMOS PASOS (OPCIONAL)

- [ ] Dominio personalizado (ej: `app.tunaturista.com`)
- [ ] Redis para cache (Render Redis addon)
- [ ] Backups automáticos de PostgreSQL
- [ ] Monitoreo con Render metrics o Sentry
- [ ] CI/CD con GitHub Actions para tests antes de deploy

---

**¡Listo para producción!** 🚀
