# 🚀 Guía de Despliegue en Render

## 📋 Resumen del Problema y Solución

### ❌ Problema Identificado
Las migraciones de Alembic no se ejecutaban automáticamente en Render, causando el error:
```
la relación "rol" no existe
```

### ✅ Solución Implementada
Se creó un script de inicio (`start.sh`) que:
1. Ejecuta las migraciones de Alembic **ANTES** de iniciar el servidor
2. Verifica que DATABASE_URL esté configurada
3. Inicia el servidor Uvicorn solo si las migraciones fueron exitosas

---

## 🔧 Archivos Modificados

### 1. **`start.sh`** (NUEVO)
Script de inicio que ejecuta migraciones antes del servidor.

### 2. **`Dockerfile`** (MODIFICADO)
Ahora usa `start.sh` en lugar de ejecutar uvicorn directamente.

### 3. **`main.py`** (LIMPIADO)
Se eliminó la lógica de migración automática que no funcionaba en Render.

### 4. **`render.yaml`** (NUEVO - OPCIONAL)
Configuración Infrastructure as Code para Render.

---

## 📝 Pasos para Desplegar en Render

### Opción A: Configuración Manual (Si ya tienes el servicio)

1. **Ve a tu servicio en Render Dashboard**
   - https://dashboard.render.com

2. **Actualiza la configuración del servicio:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `./start.sh`

3. **Verifica las Variables de Entorno:**
   ```
   ENVIRONMENT=production
   DEBUG=false
   CREATE_SCHEMA_ON_STARTUP=false
   DATABASE_URL=(automático desde la BD PostgreSQL)
   SECRET_KEY=(genera uno seguro)
   CSRF_SECRET=(genera uno seguro)
   ```

4. **Commit y Push los cambios:**
   ```bash
   git add start.sh Dockerfile main.py render.yaml
   git commit -m "fix: Implementar ejecución automática de migraciones en Render"
   git push origin main
   ```

5. **Render detectará los cambios y redesplegrá automáticamente**

---

### Opción B: Configuración con render.yaml (Recomendado para nuevos servicios)

1. **Commit y Push todos los archivos:**
   ```bash
   git add .
   git commit -m "feat: Añadir configuración completa para Render"
   git push origin main
   ```

2. **En Render Dashboard:**
   - Click en "New" → "Blueprint"
   - Conecta tu repositorio
   - Render detectará automáticamente el `render.yaml`
   - Revisa la configuración y aprueba
   - Click en "Apply"

---

## 🔍 Verificación Post-Despliegue

### 1. Revisar los Logs
En Render Dashboard → Tu servicio → Logs, deberías ver:
```
========================================
🚀 Iniciando aplicación Inventario Backend
========================================
✓ Variables de entorno verificadas

📦 Ejecutando migraciones de base de datos...
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> abc123, Initial migration
✓ Migraciones aplicadas exitosamente

🌐 Iniciando servidor Uvicorn...
========================================
INFO: Started server process
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 2. Verificar la API
```bash
curl https://inventario-backend-o0gu.onrender.com/api/v1/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-09T16:45:00.000000",
  "version": "1.0.0"
}
```

### 3. Verificar que las tablas existan
Los logs deben mostrar que las migraciones se ejecutaron sin errores de "tabla no existe".

---

## ⚙️ Variables de Entorno Importantes

| Variable | Valor Recomendado | Descripción |
|----------|-------------------|-------------|
| `ENVIRONMENT` | `production` | Modo de ejecución |
| `DEBUG` | `false` | Desactiva modo debug |
| `CREATE_SCHEMA_ON_STARTUP` | `false` | NO crear schema (usamos Alembic) |
| `DATABASE_URL` | (automático) | URL de PostgreSQL desde Render |
| `SECRET_KEY` | (generar 32+ chars) | Clave para JWT |
| `CSRF_SECRET` | (generar) | Clave para CSRF tokens |
| `SSL_ENABLED` | `false` | Render maneja SSL |
| `SESSION_COOKIE_SECURE` | `false` | Render maneja HTTPS |
| `CORS_ORIGINS` | URL del frontend | Lista separada por comas |
| `TRUSTED_HOSTS` | Tu dominio Render | Host permitido |

---

## 🐛 Troubleshooting

### Error: "Permission denied: ./start.sh"
**Solución:** El Dockerfile ya incluye `RUN chmod +x start.sh`. Si persiste:
```bash
git update-index --chmod=+x start.sh
git commit -m "fix: Make start.sh executable"
git push
```

### Error: "alembic: command not found"
**Solución:** Verifica que `alembic` esté en `requirements.txt`:
```txt
alembic==1.13.1
```

### Error: "la relación X no existe" (persiste)
**Solución:**
1. Verifica que las migraciones estén en la carpeta `alembic/versions/`
2. Verifica que los logs muestren "✓ Migraciones aplicadas exitosamente"
3. Si es necesario, elimina y recrea la base de datos en Render

### Error: "Database connection failed"
**Solución:**
1. Verifica que la variable `DATABASE_URL` esté configurada
2. En Render: Settings → Environment → Verifica que esté conectada a la BD
3. Asegúrate de que la base de datos PostgreSQL esté activa

---

## 📦 Siguiente Paso: Desplegar el Frontend

Una vez que el backend esté funcionando correctamente:

1. **Actualiza la URL del backend en el frontend:**
   ```typescript
   // En el archivo de configuración del frontend
   const API_URL = "https://inventario-backend-o0gu.onrender.com/api/v1";
   ```

2. **Despliega el frontend como Static Site en Render:**
   - Build Command: `npm run build`
   - Publish Directory: `dist`

3. **Configura CORS en el backend:**
   - Añade la URL del frontend a `CORS_ORIGINS`
   - Ejemplo: `https://tu-frontend.onrender.com`

---

## 📚 Referencias

- [Render Web Services Documentation](https://render.com/docs/web-services)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

## ✅ Checklist de Despliegue

- [ ] Archivos modificados commiteados y pusheados
- [ ] Start Command actualizado en Render a `./start.sh`
- [ ] Variables de entorno configuradas
- [ ] Servicio redesplgado exitosamente
- [ ] Logs muestran migraciones ejecutadas
- [ ] Health check responde correctamente
- [ ] No hay errores de "tabla no existe"
- [ ] CORS configurado con URL del frontend
- [ ] Frontend apuntando a la URL correcta del backend

---

**Fecha de implementación:** 9 de noviembre de 2025
**Estado:** ✅ Listo para desplegar
