# 🔧 SOLUCIONES A PROBLEMAS ESPECÍFICOS

## ❌ "Railway no me funcionó"

### Posibles causas y soluciones:

#### 1. Error: "Build failed"
**Causa:** Railway no encuentra el directorio correcto
**Solución:**
- Settings → Root Directory → Cambiar a: `inventario-backend`
- Guardar y esperar a que redespliegue

#### 2. Error: "Cannot find module"
**Causa:** Dependencias no instaladas correctamente
**Solución:**
- Verificar que existe `requirements.txt` en `inventario-backend/`
- En Railway Settings → Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 3. Error: "Database connection failed"
**Causa:** No agregaste PostgreSQL
**Solución:**
- En Railway Dashboard → Click "New"
- Database → Add PostgreSQL
- Esperar 1 minuto
- Railway conecta automáticamente la variable `DATABASE_URL`

#### 4. Error: "503 Service Unavailable"
**Causa:** El servicio no está corriendo
**Solución:**
- Ver los logs en Railway (click en el servicio → Deployments → Ver logs)
- Buscar errores rojos
- Verificar que todas las variables de entorno estén configuradas

---

## ❌ "Render no me funcionó"

### Posibles causas y soluciones:

#### 1. Backend muy lento o no carga
**Causa:** Plan gratuito de Render "duerme" después de 15 min de inactividad
**Solución:**
- **Alternativa 1:** Usar Railway (mejor para este proyecto)
- **Alternativa 2:** Usar plan pagado de Render ($7/mes)
- **Alternativa 3:** Agregar un "keep-alive" (ping cada 10 min)

#### 2. Error en build de frontend
**Causa:** Render busca en el root, no en `inventario-frontend/`
**Solución:**
- En Render Dashboard → Tu servicio → Settings
- Root Directory: `inventario-frontend`
- Build Command: `npm install && npm run build`
- Publish Directory: `dist`

#### 3. Error: "Failed to connect to database"
**Causa:** No creaste la base de datos PostgreSQL
**Solución:**
- En Render Dashboard → New → PostgreSQL
- Copiar la URL de conexión
- Pegarla en las variables de entorno del backend como `DATABASE_URL`

---

## 🎯 COMPARACIÓN: ¿Cuál usar?

### ✅ RECOMENDADO: Vercel + Railway

| Aspecto | Vercel (Frontend) | Railway (Backend) |
|---------|-------------------|-------------------|
| Velocidad | ⚡ Muy rápido | ⚡ Muy rápido |
| Precio | 🆓 Gratis | 💵 $5 gratis/mes |
| Facilidad | ⭐⭐⭐⭐⭐ Muy fácil | ⭐⭐⭐⭐ Fácil |
| Python | ❌ No soporta bien | ✅ Excelente |
| React | ✅ Perfecto | ❌ No es para frontend |
| Base de datos | ❌ No incluida | ✅ PostgreSQL incluido |

### ⚠️ Render + Render

| Aspecto | Render (ambos) |
|---------|----------------|
| Velocidad | 🐌 Lento en plan gratuito |
| Precio | 🆓 Gratis pero con limitaciones |
| Facilidad | ⭐⭐⭐ Mediana |
| Problema | Se "duerme" y tarda en despertar |

---

## 🚀 ALTERNATIVAS ADICIONALES

### Si Railway también falla:

#### Opción 1: **Netlify + Railway**
- Frontend en Netlify (similar a Vercel)
- Backend en Railway
- Pasos casi idénticos a Vercel

#### Opción 2: **Vercel + Render**
- Frontend en Vercel
- Backend en Render (aguantar la lentitud)
- Considera que el backend tardará ~30 seg en responder la primera vez

#### Opción 3: **Fly.io para todo**
- Más técnico pero muy bueno
- Requiere usar Docker
- Ya tienes Dockerfile, así que es posible

#### Opción 4: **Azure/AWS (si tienes créditos estudiantiles)**
- Azure: App Service + PostgreSQL
- AWS: Elastic Beanstalk + RDS
- Más complejo pero profesional

---

## 📱 "No puedo abrir en el celular"

### Problema 1: "No carga la página"
**Soluciones:**
1. Verificar que escribiste bien la URL (sin espacios)
2. Probar con WiFi y con datos móviles
3. Probar en modo incógnito del navegador
4. Intentar otro navegador (Chrome, Safari, Firefox)

### Problema 2: "Carga pero aparece página en blanco"
**Soluciones:**
1. Abrir consola del navegador:
   - Android Chrome: Conectar a PC → chrome://inspect
   - iPhone Safari: Settings → Safari → Advanced → Web Inspector
2. Ver errores JavaScript
3. Verificar que `VITE_API_URL` esté correcta en Vercel

### Problema 3: "No puedo hacer login"
**Soluciones:**
1. Verificar que el backend esté corriendo
2. Abrir `[tu-backend]/api/v1/health` en el navegador del celular
3. Si no carga, el problema es el backend
4. Verificar CORS en Railway

### Problema 4: "Solo funciona en WiFi de mi casa"
**Causa:** Posiblemente estés usando `localhost` en alguna parte
**Solución:**
1. Verificar que `VITE_API_URL` sea la URL pública de Railway
2. NO debe contener `localhost` ni `127.0.0.1` ni `192.168.x.x`
3. Debe ser: `https://[nombre].up.railway.app`

---

## 🔑 "Problemas con credenciales/login"

### No puedo crear usuario
**Solución:**
1. Verificar que el backend tenga conexión a la base de datos
2. Ver logs en Railway
3. Si es error de roles, ejecutar el script de inicialización:
   - Conectar a la base de datos de Railway
   - Ejecutar migraciones de Alembic

### Olvidé mi contraseña de admin
**Solución temporal:**
1. Crear un nuevo usuario desde el registro
2. Conectarse a la base de datos de Railway
3. Cambiar el rol del nuevo usuario a admin

---

## ⏰ "Tengo poco tiempo, ¿cuál es lo MÁS RÁPIDO?"

### Plan Express (20 minutos):

1. **Backend en Railway** (10 min)
   - Crear cuenta con GitHub
   - New Project → Deploy from repo
   - Agregar PostgreSQL
   - Cambiar Root Directory a `inventario-backend`
   - Copiar solo estas variables esenciales:
     ```
     ENVIRONMENT=production
     DATABASE_URL=${{DATABASE_URL}}
     SECRET_KEY=[generar con script]
     CSRF_SECRET=[generar con script]
     CORS_ORIGINS=*
     TRUSTED_HOSTS=*
     ```
   - Esperar deploy

2. **Frontend en Vercel** (10 min)
   - Crear cuenta con GitHub
   - Import Project → seleccionar repo
   - Root Directory: `inventario-frontend`
   - Agregar solo esta variable:
     ```
     VITE_API_URL=[URL de Railway]
     ```
   - Deploy

3. **Probar** (2 min)
   - Abrir URL de Vercel en celular
   - Si funciona, ¡listo!
   - Si no, revisar logs

**IMPORTANTE:** Después del deploy express, DEBES actualizar CORS:
- Railway → CORS_ORIGINS → Cambiar `*` por URL exacta de Vercel

---

## 📞 AYUDA EN VIVO

Si nada funciona, puedes:

1. **Ver los logs:**
   - Railway: Dashboard → Tu servicio → Deployments → Logs
   - Vercel: Dashboard → Tu proyecto → Deployments → Ver logs

2. **Probar paso a paso:**
   - Backend: `[backend-url]/api/v1/health`
   - Documentación: `[backend-url]/docs`
   - Frontend: `[frontend-url]`

3. **Verificar variables:**
   - Railway: TODAS las variables deben estar sin errores de tipeo
   - Vercel: `VITE_API_URL` debe tener la URL correcta de Railway

4. **Redesplegar:**
   - Railway: Click "Restart"
   - Vercel: Deployments → "Redeploy"

---

## ✅ LISTA DE VERIFICACIÓN FINAL

Antes de darte por vencido, verifica:

- [ ] El backend está desplegado y verde en Railway/Render
- [ ] Puedes abrir `[backend]/api/v1/health` y ver respuesta JSON
- [ ] El frontend está desplegado en Vercel
- [ ] `VITE_API_URL` en Vercel tiene la URL correcta del backend
- [ ] `CORS_ORIGINS` en Railway tiene la URL exacta de Vercel
- [ ] No hay espacios extras en las variables de entorno
- [ ] Root Directory está correctamente configurado
- [ ] Has esperado suficiente tiempo después de cambios (2-3 min)
- [ ] Lo probaste en modo incógnito del navegador
- [ ] La URL no tiene `localhost` ni IP local

---

## 🎯 SI TODO FALLA: Plan B

### Opción nuclear (garantizada):
1. Usa **Heroku** (tiene mejor documentación)
2. Sigue tutorial oficial: https://devcenter.heroku.com/articles/getting-started-with-python
3. Tardará 1-2 horas pero FUNCIONA

### O contacta:
- Discord de Railway: https://discord.gg/railway
- Comunidad de Vercel: https://vercel.com/community
- Reddit: r/webdev o r/learnprogramming

---

**¡No te rindas! Con paciencia y siguiendo los pasos correctos, SÍ funciona!** 💪
