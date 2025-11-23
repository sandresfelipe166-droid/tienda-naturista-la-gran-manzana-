# 🚀 CREAR TABLAS EN RAILWAY

## Opción 1: Variables de Entorno (MÁS FÁCIL)

1. Ve a tu proyecto en Railway
2. Haz clic en el servicio **backend**
3. Ve a la pestaña **Variables**
4. **AGREGA** esta nueva variable:
   ```
   CREATE_SCHEMA_ON_STARTUP=true
   ```
5. Guarda y Railway redesplegará automáticamente
6. Las tablas se crearán al iniciar la aplicación

## Opción 2: Crear un Usuario Admin Inicial

Después de que las tablas estén creadas, ve a Railway y ejecuta este comando en el **backend**:

```bash
python -m app.scripts.seed_roles
```

Esto creará los roles por defecto (Admin, Gerente, Empleado).

## ✅ Verificar que Funcionó

Visita: https://tienda-naturista-la-gran-manzana-production-625c.up.railway.app/api/v1/health

Deberías ver:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

Si ya no ves errores de "relation does not exist", ¡significa que las tablas se crearon correctamente!

## 📝 Nota Importante

La variable `CREATE_SCHEMA_ON_STARTUP=true` es útil para deployment inicial, pero **después** deberías:
1. Eliminar esa variable
2. Habilitar las migraciones de Alembic de nuevo en `entrypoint.sh`
3. Usar migraciones para cambios futuros en la base de datos

Pero para entregar el martes, esta solución te permite avanzar rápido.
