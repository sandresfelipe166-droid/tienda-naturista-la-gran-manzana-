# 🧪 GUÍA DE PRUEBAS - SISTEMA DE ROLES

## 🌐 URLs ACTIVAS

- **Backend**: http://127.0.0.1:8000
- **Frontend**: http://localhost:3001
- **Documentación API**: http://127.0.0.1:8000/docs

---

## ✅ PRUEBAS A REALIZAR

### 1. **REGISTRO DE USUARIOS**

#### A. Registrar Viewer (Solo Lectura) 👁️
1. Ir a: http://localhost:3001/register
2. Seleccionar la card **"Visualizador"**
3. Llenar formulario:
   - Nombre de usuario: `viewer_test`
   - Nombre completo: `Pedro Viewer`
   - Email: `viewer@test.com`
   - Contraseña: `123456`
   - Confirmar contraseña: `123456`
4. Click en "Crear cuenta"
5. **Resultado esperado**: Redirige a login con mensaje de éxito

#### B. Registrar Vendedor 🛒
1. Ir a: http://localhost:3001/register
2. Seleccionar la card **"Vendedor"**
3. Llenar formulario:
   - Nombre de usuario: `vendedor_test`
   - Nombre completo: `María Vendedor`
   - Email: `vendedor@test.com`
   - Contraseña: `123456`
   - Confirmar contraseña: `123456`
4. Click en "Crear cuenta"
5. **Resultado esperado**: Redirige a login con mensaje de éxito

#### C. Registrar Admin 👑
1. Ir a: http://localhost:3001/register
2. Seleccionar la card **"Administrador"**
3. Llenar formulario:
   - Nombre de usuario: `admin_test`
   - Nombre completo: `Carlos Admin`
   - Email: `admin@test.com`
   - Contraseña: `123456`
   - Confirmar contraseña: `123456`
4. Click en "Crear cuenta"
5. **Resultado esperado**: Redirige a login con mensaje de éxito

---

### 2. **PRUEBAS DE LOGIN Y PERMISOS**

#### Viewer (Solo Lectura) 👁️
1. Login: http://localhost:3001/login
   - Usuario: `viewer_test`
   - Contraseña: `123456`

2. **Verificar en Dashboard:**
   - ✅ Puede ver menú: Panel, Productos, Entradas, Ventas, Gastos, Cotización
   - ✅ Icono 👁️ aparece junto al nombre
   - ❌ **NO** debe ver botones "Nuevo Producto"
   - ❌ **NO** debe ver botones "Nueva Venta"
   - ❌ **NO** debe ver botones "Nueva Entrada"
   - ❌ **NO** debe ver botones "Nuevo Gasto"
   - ❌ **NO** debe ver botones "Nueva Cotización"
   - ❌ **NO** debe ver botón "Panel Admin"

3. **Probar acceso directo a admin:**
   - Ir manualmente a: http://localhost:3001/admin
   - **Resultado esperado**: Redirige automáticamente a /dashboard

#### Vendedor 🛒
1. Login: http://localhost:3001/login
   - Usuario: `vendedor_test`
   - Contraseña: `123456`

2. **Verificar en Dashboard:**
   - ✅ Puede ver menú: Panel, Productos, Entradas, Ventas, Cotizaciones
   - ✅ Icono 🛒 aparece junto al nombre
   - ✅ **SÍ** debe ver botón "Nueva Venta"
   - ✅ **SÍ** debe ver botón "Nueva Entrada"
   - ✅ **SÍ** debe ver botón "Nueva Cotización"
   - ❌ **NO** debe ver "Gastos" en el menú
   - ❌ **NO** debe ver botón "Nuevo Producto" 
   - ❌ **NO** debe ver botón "Nuevo Gasto"
   - ❌ **NO** debe ver botón "Panel Admin"

3. **Probar acceso directo a admin:**
   - Ir manualmente a: http://localhost:3001/admin
   - **Resultado esperado**: Redirige automáticamente a /dashboard

#### Admin 👑
1. Login: http://localhost:3001/login
   - Usuario: `admin_test`
   - Contraseña: `123456`

2. **Verificar en Dashboard:**
   - ✅ Puede ver TODO el menú (Panel, Productos, Entradas, Ventas, Gastos, Cotización, Devoluciones)
   - ✅ Icono 👑 aparece junto al nombre
   - ✅ **SÍ** debe ver botón "Nuevo Producto"
   - ✅ **SÍ** debe ver botón "Nueva Venta"
   - ✅ **SÍ** debe ver botón "Nueva Entrada"
   - ✅ **SÍ** debe ver botón "Nuevo Gasto"
   - ✅ **SÍ** debe ver botón "Nueva Cotización"
   - ✅ **SÍ** debe ver botón "👑 Admin" en header

3. **Probar Panel Admin:**
   - Click en botón "👑 Admin" en el header
   - **Resultado esperado**: Abre http://localhost:3001/admin
   - **Verificar pestañas:**
     - ✅ Laboratorios
     - ✅ Secciones
     - ✅ Usuarios
   - **Verificar botones:**
     - ✅ "➕ Nuevo Laboratorio"
     - ✅ "➕ Nueva Sección"

---

### 3. **PRUEBAS DE VALIDACIÓN**

#### A. Contraseñas no coinciden
1. Ir a registro
2. Llenar formulario con contraseñas diferentes
3. **Resultado esperado**: Error "Las contraseñas no coinciden"

#### B. Contraseña muy corta
1. Ir a registro
2. Usar contraseña de menos de 6 caracteres
3. **Resultado esperado**: Error de validación

#### C. Email duplicado
1. Intentar registrar usuario con email ya existente
2. **Resultado esperado**: Error "Email already registered"

#### D. Username duplicado
1. Intentar registrar usuario con username ya existente
2. **Resultado esperado**: Error "Username already taken"

---

### 4. **PRUEBAS DE NAVEGACIÓN**

#### A. Menú lateral filtrado
1. Login como **Viewer**
2. **Verificar que NO aparecen**:
   - ❌ Laboratorios
   - ❌ Secciones
   - ❌ Usuarios

2. Login como **Vendedor**
3. **Verificar que NO aparecen**:
   - ❌ Gastos (si no tiene permiso de lectura)

3. Login como **Admin**
4. **Verificar que APARECEN TODOS**

#### B. Protección de rutas
1. Sin login, intentar ir a:
   - http://localhost:3001/dashboard
   - **Resultado**: Redirige a /login

2. Como Viewer, intentar ir a:
   - http://localhost:3001/admin
   - **Resultado**: Redirige a /dashboard

3. Como Vendedor, intentar ir a:
   - http://localhost:3001/admin
   - **Resultado**: Redirige a /dashboard

4. Como Admin, ir a:
   - http://localhost:3001/admin
   - **Resultado**: Acceso permitido

---

## 🔍 CHECKLIST RÁPIDO

### Frontend Funcionando ✅
- [ ] Servidor corriendo en http://localhost:3001
- [ ] Página de registro carga correctamente
- [ ] 3 cards de roles se muestran
- [ ] Formulario funcional

### Backend Funcionando ✅
- [ ] Servidor corriendo en http://127.0.0.1:8000
- [ ] Endpoint POST /api/v1/auth/register funciona
- [ ] Endpoint POST /api/v1/auth/login funciona
- [ ] Roles en BD: 1=admin, 2=vendedor, 3=viewer

### Permisos Funcionando ✅
- [ ] Viewer solo ve, no puede crear/editar
- [ ] Vendedor puede crear ventas/entradas
- [ ] Admin ve botón "Panel Admin"
- [ ] Admin accede a /admin
- [ ] Viewer/Vendedor NO acceden a /admin

### UI/UX ✅
- [ ] Iconos de roles aparecen (👑/🛒/👁️)
- [ ] Nombre + rol se muestra en header
- [ ] Botones se ocultan según permisos
- [ ] Menú se filtra según permisos

---

## 🐛 PROBLEMAS CONOCIDOS

### Si no funciona el registro:
1. Verificar que backend tenga tabla `rol` con datos:
```sql
SELECT * FROM rol;
-- Debe tener: id_rol=1 (admin), id_rol=2 (vendedor), id_rol=3 (viewer)
```

2. Si faltan roles, crear manualmente:
```sql
INSERT INTO rol (id_rol, nombre_rol, descripcion) VALUES
(1, 'admin', 'Administrador con acceso total'),
(2, 'vendedor', 'Vendedor con acceso a ventas y entradas'),
(3, 'viewer', 'Visualizador solo lectura');
```

### Si no aparecen permisos:
1. Verificar que el login devuelva el rol correctamente
2. Abrir DevTools → Network → Ver respuesta de /auth/login
3. Verificar que `rol.nombre_rol` exista en la respuesta

### Si botón "Admin" no aparece:
1. Verificar en consola del navegador:
```javascript
// En DevTools Console:
localStorage.getItem('auth-storage')
// Debe mostrar el usuario con rol
```

---

## 📊 RESUMEN DE ROLES

| Característica | Viewer 👁️ | Vendedor 🛒 | Admin 👑 |
|----------------|-----------|------------|---------|
| Ver productos | ✅ | ✅ | ✅ |
| Crear productos | ❌ | ❌ | ✅ |
| Ver ventas | ✅ | ✅ | ✅ |
| Crear ventas | ❌ | ✅ | ✅ |
| Ver entradas | ✅ | ✅ | ✅ |
| Crear entradas | ❌ | ✅ | ✅ |
| Ver gastos | ✅ | ✅ | ✅ |
| Crear gastos | ❌ | ❌ | ✅ |
| Ver cotizaciones | ✅ | ✅ | ✅ |
| Crear cotizaciones | ❌ | ✅ | ✅ |
| Panel Admin | ❌ | ❌ | ✅ |
| Gestionar usuarios | ❌ | ❌ | ✅ |
| Gestionar laboratorios | ❌ | ❌ | ✅ |
| Gestionar secciones | ❌ | ❌ | ✅ |

---

**¡Listo para probar!** 🚀
