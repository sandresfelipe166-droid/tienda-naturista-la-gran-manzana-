# 🎯 RESUMEN SIMPLE - Sistema de Roles

## 📱 ¿QUÉ VAMOS A HACER?

### 1️⃣ PÁGINA DE REGISTRO CON SELECCIÓN DE ROL

Cuando alguien se registra, escoge uno de estos 3 roles:

```
┌─────────────────────────────────────────┐
│         CREAR CUENTA                     │
├─────────────────────────────────────────┤
│ Nombre: [___________]                    │
│ Email:  [___________]                    │
│ Password: [___________]                  │
│                                          │
│ Escoge tu rol:                           │
│                                          │
│ ┌────────────────┐                       │
│ │ 👁️ VIEWER      │ ← Solo VER           │
│ │ (Solo Lectura) │                       │
│ └────────────────┘                       │
│                                          │
│ ┌────────────────┐                       │
│ │ 🛒 VENDEDOR    │ ← Ver + Vender        │
│ │ (Ventas)       │                       │
│ └────────────────┘                       │
│                                          │
│ ┌────────────────┐                       │
│ │ 👑 ADMIN       │ ← CONTROL TOTAL       │
│ │ (Todo acceso)  │                       │
│ └────────────────┘                       │
│                                          │
│      [REGISTRARSE]                       │
└─────────────────────────────────────────┘
```

---

### 2️⃣ DASHBOARD SEGÚN EL ROL

Cada rol ve diferentes opciones en el menú lateral:

#### 👁️ VIEWER (Solo Lectura)
```
┌─────────────────┐
│ 📊 PANEL        │ ✅ Ve estadísticas
│ 🌿 PRODUCTOS    │ ✅ Ve lista (SIN botones de crear/editar)
│ 📥 ENTRADAS     │ ✅ Ve historial
│ 💰 VENTAS       │ ✅ Ve historial
│ 💸 GASTOS       │ ✅ Ve historial
│ 📋 COTIZACIÓN   │ ✅ Ve historial
└─────────────────┘
❌ NO puede modificar NADA
❌ NO ve panel de administración
```

#### 🛒 VENDEDOR
```
┌─────────────────┐
│ 📊 PANEL        │ ✅ Ve estadísticas
│ 🌿 PRODUCTOS    │ ✅ Ve + Actualiza stock
│ 📥 ENTRADAS     │ ✅ Ve + Crea entradas
│ 💰 VENTAS       │ ✅ Ve + Crea ventas
│ 💸 GASTOS       │ ✅ Ve + Crea gastos
│ 📋 COTIZACIÓN   │ ✅ Ve + Crea cotizaciones
└─────────────────┘
✅ Puede crear ventas, entradas, cotizaciones
❌ NO puede eliminar productos
❌ NO ve panel de administración
```

#### 👑 ADMIN (Control Total)
```
┌─────────────────┐
│ 📊 PANEL        │ ✅ Ve estadísticas
│ 🌿 PRODUCTOS    │ ✅ CRUD completo
│ 📥 ENTRADAS     │ ✅ CRUD completo
│ 💰 VENTAS       │ ✅ CRUD completo
│ 💸 GASTOS       │ ✅ CRUD completo
│ 📋 COTIZACIÓN   │ ✅ CRUD completo
│ 👑 ADMIN PANEL  │ ✅ Panel exclusivo
└─────────────────┘
✅ Puede hacer TODO
✅ Ve panel de administración
```

---

### 3️⃣ PANEL DE ADMINISTRACIÓN (Solo Admin 👑)

```
┌──────────────────────────────────────────────┐
│     👑 PANEL DE ADMINISTRACIÓN               │
├──────────────────────────────────────────────┤
│                                              │
│ [🏢 Laboratorios] [📦 Secciones] [👥 Usuarios] [⚙️ Config] │
│                                              │
│ ┌──────────────────────────────────────────┐ │
│ │ 🏢 GESTIÓN DE LABORATORIOS               │ │
│ │                                          │ │
│ │ [+ Nuevo Laboratorio]                    │ │
│ │                                          │ │
│ │ ┌────────────────────────────────────┐  │ │
│ │ │ ID │ Nombre      │ Acciones        │  │ │
│ │ ├────┼─────────────┼─────────────────┤  │ │
│ │ │ 1  │ NaturaVida  │ ✏️ Editar 🗑️ Eliminar│ │
│ │ │ 2  │ GreenLife   │ ✏️ Editar 🗑️ Eliminar│ │
│ │ │ 3  │ Bionatural  │ ✏️ Editar 🗑️ Eliminar│ │
│ │ └────────────────────────────────────┘  │ │
│ └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

**Solo el ADMIN puede:**
- ✅ Crear/Editar/Eliminar Laboratorios
- ✅ Crear/Editar/Eliminar Secciones
- ✅ Ver lista de usuarios
- ✅ Cambiar configuración del sistema
- ✅ Ver logs de auditoría

---

## 🔒 CÓMO FUNCIONA LA SEGURIDAD

### En cada botón/acción:

```tsx
// ❌ ANTES (todos pueden ver y hacer todo)
<button onClick={crearProducto}>+ Nuevo Producto</button>

// ✅ DESPUÉS (solo si tiene permiso)
{can('productos', 'create') && (
  <button onClick={crearProducto}>+ Nuevo Producto</button>
)}
```

### Resultado visual:

#### Admin ve:
```
[+ Nuevo Producto] [✏️ Editar] [🗑️ Eliminar]
```

#### Vendedor ve:
```
[✏️ Editar Stock]
```

#### Viewer ve:
```
(Sin botones, solo tabla de lectura)
```

---

## 📁 ARCHIVOS QUE VAMOS A CREAR

```
src/
├── pages/
│   ├── RegisterPage.tsx          ← NUEVO: Registro con selección de rol
│   ├── RegisterPage.css          ← NUEVO: Estilos del registro
│   ├── AdminPanelPage.tsx        ← NUEVO: Panel de admin
│   └── AdminPanelPage.css        ← NUEVO: Estilos del panel
├── components/
│   ├── ProtectedRoute.tsx        ← NUEVO: Proteger rutas por rol
│   └── admin/                    ← NUEVO: Componentes del panel admin
│       ├── LaboratoriosManager.tsx
│       ├── SeccionesManager.tsx
│       ├── UsuariosManager.tsx
│       └── ConfiguracionPanel.tsx
├── hooks/
│   └── usePermissions.ts         ← NUEVO: Hook para verificar permisos
└── App.tsx                       ← MODIFICAR: Agregar nuevas rutas
```

---

## 🚀 PASOS PARA IMPLEMENTAR

### Paso 1: Sistema de Permisos (30 min)
```bash
1. Crear src/hooks/usePermissions.ts
2. Definir permisos de cada rol
3. Crear función can('recurso', 'acción')
```

### Paso 2: Página de Registro (30 min)
```bash
1. Crear src/pages/RegisterPage.tsx
2. Agregar selector de rol con cards
3. Enviar rol al backend al registrarse
```

### Paso 3: Panel de Administración (2 horas)
```bash
1. Crear src/pages/AdminPanelPage.tsx
2. Crear tabs: Laboratorios, Secciones, Usuarios, Config
3. Implementar CRUD de laboratorios
4. Implementar CRUD de secciones
```

### Paso 4: Actualizar Dashboard (1 hora)
```bash
1. Importar usePermissions en DashboardPage
2. Ocultar botones según permisos:
   - Crear: solo admin y vendedor
   - Editar: solo admin y vendedor
   - Eliminar: solo admin
3. Agregar menú "ADMINISTRACIÓN" solo para admin
```

### Paso 5: Probar (30 min)
```bash
1. Registrar usuario con rol "viewer"
   → Ver que NO puede crear/editar/eliminar
2. Registrar usuario con rol "vendedor"
   → Ver que PUEDE crear ventas
3. Registrar usuario con rol "admin"
   → Ver que puede acceder a panel admin
```

---

## 💡 EJEMPLO PRÁCTICO

### Escenario: Usuario "viewer" intenta crear producto

```tsx
// En DashboardPage.tsx
const { can } = usePermissions()

// Botón solo aparece si tiene permiso
{can('productos', 'create') ? (
  <button onClick={() => setProductModalOpen(true)}>
    + Nuevo Producto
  </button>
) : (
  <span className="no-permission">
    🔒 No tienes permiso para crear productos
  </span>
)}
```

**Resultado:**
- **Admin** ve: `[+ Nuevo Producto]`
- **Vendedor** ve: `(sin botón)`
- **Viewer** ve: `🔒 No tienes permiso para crear productos`

---

## ✅ CHECKLIST RÁPIDO

Para implementar completo:

- [ ] 1. Crear hook de permisos (usePermissions.ts)
- [ ] 2. Crear página de registro con selector de rol
- [ ] 3. Crear panel de administración (solo admin)
- [ ] 4. Agregar gestión de laboratorios en panel admin
- [ ] 5. Agregar gestión de secciones en panel admin
- [ ] 6. Actualizar dashboard para ocultar botones según rol
- [ ] 7. Probar con 3 usuarios (admin, vendedor, viewer)

---

## 🎯 RESULTADO FINAL

### Para tu docente:
1. Se registra
2. Escoge rol (admin, vendedor, o viewer)
3. Ve dashboard personalizado según su rol
4. Si es admin, puede entrar a "Panel de Administración"

### Para tu proyecto:
- ✅ Sistema de roles completo
- ✅ Seguridad por permisos
- ✅ UI adaptativa según rol
- ✅ Panel de admin exclusivo

---

**¿Quieres que empecemos a crear los archivos?** 🚀

Puedo empezar por:
1. ✅ Hook de permisos (más fácil)
2. ✅ Página de registro
3. ✅ Panel de administración

**¿Por cuál empezamos?**
