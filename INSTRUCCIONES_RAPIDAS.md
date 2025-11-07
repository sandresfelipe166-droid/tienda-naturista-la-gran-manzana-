# 🎯 INSTRUCCIONES - Recuperación de Contraseña

## Estado: ✅ FUNCIONANDO

---

## ⚡ Cómo Probar Rápidamente

### 1. Verificar que todo está corriendo

**Terminal 1 - Backend**: 
```bash
cd c:\Users\cleiv\Desktop\inventario-backend
python main.py
# Debería ver: "Uvic orn running on http://0.0.0.0:8000"
```

**Terminal 2 - Frontend**:
```bash
cd c:\Users\cleiv\Desktop\inventario-frontend
npm run dev
# Debería ver: "VITE v... ready in XXX ms"
```

---

## 2. En el Navegador

```
URL: http://localhost:3000/login

Paso 1: Click en "¿Olvidaste tu contraseña?"
Paso 2: Te lleva a /forgot-password
Paso 3: Ingresa un email de un usuario existente (ej: admin@example.com)
Paso 4: Click "Solicitar código"
Paso 5: ⭐ VAS A VER EL CÓDIGO EN PANTALLA (por DEBUG=true)
Paso 6: Click "Ir a restablecer" (o manualmente a /reset-password)
Paso 7: Ingresa:
   - Email
   - Código (que copiaste)
   - Nueva contraseña
   - Confirmar contraseña
Paso 8: Click "Restablecer contraseña"
Paso 9: ✅ Te redirige a /login
Paso 10: Login con la NUEVA contraseña
```

---

## 3. Si no tienes usuario de prueba

```bash
# Crear usuario con curl
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123",
    "nombre_completo": "Test User",
    "rol_id": 1
  }'
```

---

## 4. Script de Pruebas Automatizadas

```bash
python scripts/test_password_reset_flow.py
```

Esto prueba:
- ✅ Solicitar código
- ✅ Confirmar código válido
- ✅ Rechazar código inválido
- ✅ Bloqueo por intentos fallidos

---

## ⚙️ Configuración

### Archivo `.env` (ya existe)

```
ENVIRONMENT=development
DEBUG=true
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
PASSWORD_RESET_EXPIRE_MINUTES=15
```

**En Producción** (cambiar a):
```
DEBUG=false
ENVIRONMENT=production
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=app-password
```

---

## 🔍 Troubleshooting

### Error: "Request failed with status code 500"
**Solución**: Las migraciones ya se ejecutaron. Si persiste:
```bash
python -m alembic upgrade heads
python main.py  # Reiniciar backend
```

### Error: "User not found"
**Solución**: El email debe existir. Crea un usuario primero (ver paso 3)

### No veo el código en pantalla
**Solución**: Verifica que DEBUG=true en `.env`

### Email no se recibe (en producción)
**Solución**: Verifica credenciales SMTP en `.env`

---

## 📚 Archivos Importantes

- `app/routers/auth.py` - Lógica de reset
- `app/crud/user.py` - CRUD de usuarios
- `src/pages/ForgotPasswordPage.tsx` - Solicitar código
- `src/pages/ResetPasswordPage.tsx` - Cambiar contraseña
- `src/pages/LoginPage.css` - Estilos
- `.env` - Configuración
- `alembic/versions/` - Migraciones (ya ejecutadas)

---

## ✅ Checklist Final

- [x] Backend corriendo sin errores
- [x] Frontend corriendo sin errores
- [x] Base de datos actualizada (migraciones ejecutadas)
- [x] Archivo `.env` configurado
- [x] Endpoints funcionando
- [x] Validaciones en 2 capas (frontend + backend)
- [x] Seguridad implementada
- [x] Estilos aplicados
- [x] Documentación completa

---

**¡Listo para usar! 🚀**

Cualquier duda: Revisa los logs del backend en la terminal
