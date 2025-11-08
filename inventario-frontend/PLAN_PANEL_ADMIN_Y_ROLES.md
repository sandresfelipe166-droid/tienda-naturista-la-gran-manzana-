# 🎯 PLAN: Panel de Administración y Sistema de Roles

## 📋 RESUMEN DE REQUERIMIENTOS

### Necesidad 1: Panel de Administración
**Objetivo:** Área exclusiva donde solo el ADMIN puede:
- ✅ Gestionar Laboratorios (Crear, Editar, Eliminar)
- ✅ Gestionar Secciones (Crear, Editar, Eliminar)
- ✅ Gestionar Usuarios (Ver, Crear, Editar, Desactivar)
- ✅ Gestionar Roles y Permisos
- ✅ Ver logs de auditoría
- ✅ Configuración del sistema

### Necesidad 2: Registro con Selección de Rol
**Objetivo:** Durante el registro, el usuario escoge su rol y según eso:
- ✅ **Admin**: Ve y modifica TODO
- ✅ **Vendedor**: Puede registrar ventas, ver productos, crear entradas
- ✅ **Viewer**: Solo puede VER (sin modificar nada)

---

## 🏗️ ARQUITECTURA DE LA SOLUCIÓN

### 1. Sistema de Roles y Permisos

```typescript
// Roles disponibles
enum UserRole {
  ADMIN = 'admin',
  VENDEDOR = 'vendedor',
  VIEWER = 'viewer'
}

// Permisos por rol
const ROLE_PERMISSIONS = {
  admin: {
    productos: { read: true, create: true, update: true, delete: true },
    ventas: { read: true, create: true, update: true, delete: true },
    entradas: { read: true, create: true, update: true, delete: true },
    gastos: { read: true, create: true, update: true, delete: true },
    cotizaciones: { read: true, create: true, update: true, delete: true },
    laboratorios: { read: true, create: true, update: true, delete: true },
    secciones: { read: true, create: true, update: true, delete: true },
    usuarios: { read: true, create: true, update: true, delete: true },
    configuracion: { read: true, update: true },
    logs: { read: true }
  },
  vendedor: {
    productos: { read: true, create: false, update: true, delete: false },
    ventas: { read: true, create: true, update: true, delete: false },
    entradas: { read: true, create: true, update: false, delete: false },
    gastos: { read: true, create: true, update: false, delete: false },
    cotizaciones: { read: true, create: true, update: true, delete: false },
    laboratorios: { read: true, create: false, update: false, delete: false },
    secciones: { read: true, create: false, update: false, delete: false },
    usuarios: { read: false, create: false, update: false, delete: false },
    configuracion: { read: false, update: false },
    logs: { read: false }
  },
  viewer: {
    productos: { read: true, create: false, update: false, delete: false },
    ventas: { read: true, create: false, update: false, delete: false },
    entradas: { read: true, create: false, update: false, delete: false },
    gastos: { read: true, create: false, update: false, delete: false },
    cotizaciones: { read: true, create: false, update: false, delete: false },
    laboratorios: { read: true, create: false, update: false, delete: false },
    secciones: { read: true, create: false, update: false, delete: false },
    usuarios: { read: false, create: false, update: false, delete: false },
    configuracion: { read: false, update: false },
    logs: { read: false }
  }
}
```

---

## 📱 PÁGINAS NUEVAS A CREAR

### 1. Página de Registro con Selección de Rol
**Archivo:** `src/pages/RegisterPage.tsx`

```tsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    nombre: '',
    email: '',
    password: '',
    rol: 'viewer' // Default: viewer (menos permisos)
  })

  const roles = [
    { 
      value: 'viewer', 
      label: 'Viewer (Solo Lectura)',
      description: 'Puede ver productos, ventas y reportes. No puede modificar nada.',
      icon: '👁️'
    },
    { 
      value: 'vendedor', 
      label: 'Vendedor',
      description: 'Puede registrar ventas, crear entradas y gestionar cotizaciones.',
      icon: '🛒'
    },
    { 
      value: 'admin', 
      label: 'Administrador',
      description: 'Acceso total: gestionar productos, usuarios, configuración y más.',
      icon: '👑'
    }
  ]

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await apiClient.post('/auth/register', formData)
      navigate('/login')
    } catch (error) {
      console.error('Error al registrar:', error)
    }
  }

  return (
    <div className="register-page">
      <div className="register-card">
        <h1>Crear Cuenta</h1>
        <form onSubmit={handleSubmit}>
          <input 
            type="text" 
            placeholder="Nombre completo"
            value={formData.nombre}
            onChange={(e) => setFormData({...formData, nombre: e.target.value})}
          />
          <input 
            type="email" 
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
          />
          <input 
            type="password" 
            placeholder="Contraseña"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
          />
          
          <div className="role-selection">
            <h3>Selecciona tu rol:</h3>
            {roles.map(role => (
              <div 
                key={role.value}
                className={`role-card ${formData.rol === role.value ? 'selected' : ''}`}
                onClick={() => setFormData({...formData, rol: role.value})}
              >
                <span className="role-icon">{role.icon}</span>
                <h4>{role.label}</h4>
                <p>{role.description}</p>
              </div>
            ))}
          </div>

          <button type="submit">Registrarse</button>
        </form>
      </div>
    </div>
  )
}
```

---

### 2. Panel de Administración
**Archivo:** `src/pages/AdminPanelPage.tsx`

```tsx
import { useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { Navigate } from 'react-router-dom'

export default function AdminPanelPage() {
  const { user } = useAuthStore()
  const [activeTab, setActiveTab] = useState('laboratorios')

  // Solo admins pueden acceder
  if (user?.rol !== 'admin') {
    return <Navigate to="/dashboard" />
  }

  const tabs = [
    { id: 'laboratorios', label: 'Laboratorios', icon: '🏢' },
    { id: 'secciones', label: 'Secciones', icon: '📦' },
    { id: 'usuarios', label: 'Usuarios', icon: '👥' },
    { id: 'configuracion', label: 'Configuración', icon: '⚙️' },
    { id: 'logs', label: 'Logs de Auditoría', icon: '📊' }
  ]

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h1>👑 Panel de Administración</h1>
        <p>Gestión completa del sistema</p>
      </div>

      <div className="admin-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      <div className="admin-content">
        {activeTab === 'laboratorios' && <LaboratoriosManager />}
        {activeTab === 'secciones' && <SeccionesManager />}
        {activeTab === 'usuarios' && <UsuariosManager />}
        {activeTab === 'configuracion' && <ConfiguracionPanel />}
        {activeTab === 'logs' && <LogsViewer />}
      </div>
    </div>
  )
}

// Componente para gestionar laboratorios
function LaboratoriosManager() {
  const [laboratorios, setLaboratorios] = useState([])
  const [isCreating, setIsCreating] = useState(false)

  return (
    <div className="manager-section">
      <div className="section-header">
        <h2>🏢 Gestión de Laboratorios</h2>
        <button className="btn-primary" onClick={() => setIsCreating(true)}>
          + Nuevo Laboratorio
        </button>
      </div>

      <table className="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Productos</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {/* Datos de laboratorios */}
        </tbody>
      </table>
    </div>
  )
}

// Similar para Secciones, Usuarios, etc.
```

---

### 3. Hook para Permisos
**Archivo:** `src/hooks/usePermissions.ts`

```typescript
import { useAuthStore } from '@/store/authStore'

export function usePermissions() {
  const { user } = useAuthStore()

  const can = (resource: string, action: string): boolean => {
    if (!user) return false
    
    const permissions = ROLE_PERMISSIONS[user.rol as keyof typeof ROLE_PERMISSIONS]
    if (!permissions) return false

    const resourcePerms = permissions[resource as keyof typeof permissions]
    if (!resourcePerms) return false

    return resourcePerms[action as keyof typeof resourcePerms] === true
  }

  const isAdmin = () => user?.rol === 'admin'
  const isVendedor = () => user?.rol === 'vendedor'
  const isViewer = () => user?.rol === 'viewer'

  return { can, isAdmin, isVendedor, isViewer }
}

// Uso en componentes:
const { can, isAdmin } = usePermissions()

// Ejemplo: Mostrar botón solo si tiene permiso
{can('productos', 'create') && (
  <button onClick={handleCreate}>+ Nuevo Producto</button>
)}

// Ejemplo: Mostrar panel admin solo a admins
{isAdmin() && (
  <Link to="/admin">Panel de Administración</Link>
)}
```

---

### 4. Componente de Protección de Rutas
**Archivo:** `src/components/ProtectedRoute.tsx`

```tsx
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { usePermissions } from '@/hooks/usePermissions'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: 'admin' | 'vendedor' | 'viewer'
  requiredPermission?: { resource: string; action: string }
}

export function ProtectedRoute({ 
  children, 
  requiredRole,
  requiredPermission 
}: ProtectedRouteProps) {
  const { user } = useAuthStore()
  const { can } = usePermissions()

  if (!user) {
    return <Navigate to="/login" />
  }

  if (requiredRole && user.rol !== requiredRole) {
    return <Navigate to="/dashboard" />
  }

  if (requiredPermission) {
    const { resource, action } = requiredPermission
    if (!can(resource, action)) {
      return (
        <div className="access-denied">
          <h2>🚫 Acceso Denegado</h2>
          <p>No tienes permisos para acceder a esta sección.</p>
        </div>
      )
    }
  }

  return <>{children}</>
}

// Uso en rutas:
<Route path="/admin" element={
  <ProtectedRoute requiredRole="admin">
    <AdminPanelPage />
  </ProtectedRoute>
} />
```

---

## 🎨 MODIFICACIONES AL DASHBOARD EXISTENTE

### Actualizar `DashboardPage.tsx`

```tsx
import { usePermissions } from '@/hooks/usePermissions'

export default function DashboardPage() {
  const { can, isAdmin } = usePermissions()

  const sidebarMenu = [
    { id: 'panel', icon: '📊', label: 'PANEL DE CONTROL', visible: true },
    { id: 'productos', icon: '🌿', label: 'PRODUCTOS', visible: can('productos', 'read') },
    { id: 'entradas', icon: '📥', label: 'ENTRADAS', visible: can('entradas', 'read') },
    { id: 'ventas', icon: '💰', label: 'VENTAS', visible: can('ventas', 'read') },
    { id: 'gastos', icon: '💸', label: 'GASTOS', visible: can('gastos', 'read') },
    { id: 'cotizacion', icon: '📋', label: 'COTIZACIÓN', visible: can('cotizaciones', 'read') },
    { id: 'admin', icon: '👑', label: 'ADMINISTRACIÓN', visible: isAdmin() }, // NUEVO
  ]

  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <nav className="sidebar-menu">
          {sidebarMenu.filter(item => item.visible).map(item => (
            <div
              key={item.id}
              className={`sidebar-item ${activeView === item.id ? 'active' : ''}`}
              onClick={() => item.id === 'admin' ? navigate('/admin') : setActiveView(item.id)}
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span className="sidebar-label">{item.label}</span>
            </div>
          ))}
        </nav>
      </aside>

      {/* Contenido del dashboard */}
      <div className="dashboard-main-area">
        {/* Deshabilitar botones según permisos */}
        {activeView === 'productos' && (
          <div>
            {can('productos', 'create') && (
              <button onClick={() => setProductModalOpen(true)}>
                + Nuevo Producto
              </button>
            )}
            
            <table>
              {/* Lista de productos */}
              <tbody>
                {productos.map(p => (
                  <tr key={p.id}>
                    <td>{p.nombre}</td>
                    <td>{p.cantidad}</td>
                    <td>
                      {can('productos', 'update') && (
                        <button onClick={() => handleEdit(p.id)}>✏️</button>
                      )}
                      {can('productos', 'delete') && (
                        <button onClick={() => handleDelete(p.id)}>🗑️</button>
                      )}
                      {!can('productos', 'update') && !can('productos', 'delete') && (
                        <span className="read-only">Solo lectura</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
```

---

## 🗺️ RUTAS ACTUALIZADAS

### `src/App.tsx`

```tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage' // NUEVO
import DashboardPage from '@/pages/DashboardPage'
import AdminPanelPage from '@/pages/AdminPanelPage' // NUEVO
import { ProtectedRoute } from '@/components/ProtectedRoute'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Rutas públicas */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} /> {/* NUEVO */}

        {/* Rutas protegidas */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } />

        {/* Panel de administración (solo admin) */}
        <Route path="/admin" element={
          <ProtectedRoute requiredRole="admin">
            <AdminPanelPage />
          </ProtectedRoute>
        } /> {/* NUEVO */}

        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  )
}
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Fase 1: Backend (Preparación)
- [ ] Verificar que endpoint `/auth/register` permite campo `rol`
- [ ] Verificar que tabla `usuarios` tiene columna `rol`
- [ ] Crear endpoints para gestionar laboratorios (CRUD)
- [ ] Crear endpoints para gestionar secciones (CRUD)
- [ ] Crear endpoint para listar usuarios (solo admin)
- [ ] Crear endpoint para logs de auditoría

### Fase 2: Frontend - Sistema de Permisos
- [ ] Crear `src/hooks/usePermissions.ts`
- [ ] Crear `src/components/ProtectedRoute.tsx`
- [ ] Actualizar `src/store/authStore.ts` para manejar rol

### Fase 3: Frontend - Página de Registro
- [ ] Crear `src/pages/RegisterPage.tsx`
- [ ] Crear estilos `src/pages/RegisterPage.css`
- [ ] Agregar ruta `/register` en App.tsx

### Fase 4: Frontend - Panel de Administración
- [ ] Crear `src/pages/AdminPanelPage.tsx`
- [ ] Crear componentes:
  - [ ] `src/components/admin/LaboratoriosManager.tsx`
  - [ ] `src/components/admin/SeccionesManager.tsx`
  - [ ] `src/components/admin/UsuariosManager.tsx`
  - [ ] `src/components/admin/ConfiguracionPanel.tsx`
  - [ ] `src/components/admin/LogsViewer.tsx`
- [ ] Crear estilos `src/pages/AdminPanelPage.css`
- [ ] Agregar ruta `/admin` en App.tsx

### Fase 5: Frontend - Actualizar Dashboard
- [ ] Integrar `usePermissions` en DashboardPage
- [ ] Ocultar/mostrar botones según permisos
- [ ] Deshabilitar inputs en modo solo-lectura
- [ ] Agregar indicadores visuales de permisos

### Fase 6: Testing
- [ ] Probar registro con cada rol
- [ ] Probar acceso a dashboard con cada rol
- [ ] Probar panel admin (solo admin)
- [ ] Probar permisos de creación/edición/eliminación
- [ ] Probar navegación entre secciones

---

## 🎨 VISUALIZACIÓN POR ROL

### Admin 👑
```
Dashboard:
✅ Ver productos, ventas, entradas, gastos, cotizaciones
✅ Crear, editar, eliminar TODO
✅ Acceso a Panel de Administración
✅ Gestionar laboratorios y secciones
✅ Ver usuarios y logs
```

### Vendedor 🛒
```
Dashboard:
✅ Ver productos (puede actualizar stock)
✅ Crear y gestionar ventas
✅ Crear entradas de inventario
✅ Ver gastos (puede crear)
✅ Gestionar cotizaciones
❌ NO puede eliminar productos
❌ NO puede acceder a panel admin
❌ NO puede ver usuarios
```

### Viewer 👁️
```
Dashboard:
✅ Ver productos (solo lectura)
✅ Ver ventas (solo lectura)
✅ Ver entradas (solo lectura)
✅ Ver gastos (solo lectura)
✅ Ver cotizaciones (solo lectura)
❌ NO puede crear/editar/eliminar NADA
❌ NO puede acceder a panel admin
❌ Todos los botones de acción deshabilitados
```

---

## 🚀 IMPLEMENTACIÓN PASO A PASO

### Paso 1: Crear Hook de Permisos (10 min)
```bash
# Crear archivo
touch src/hooks/usePermissions.ts
# Copiar código del hook
```

### Paso 2: Crear Página de Registro (30 min)
```bash
# Crear archivos
touch src/pages/RegisterPage.tsx
touch src/pages/RegisterPage.css
# Implementar formulario con selección de rol
```

### Paso 3: Crear Panel Admin (1-2 horas)
```bash
# Crear archivos
touch src/pages/AdminPanelPage.tsx
touch src/pages/AdminPanelPage.css
mkdir src/components/admin
touch src/components/admin/LaboratoriosManager.tsx
touch src/components/admin/SeccionesManager.tsx
# Implementar gestión de laboratorios y secciones
```

### Paso 4: Actualizar Dashboard con Permisos (1 hora)
```bash
# Modificar DashboardPage.tsx
# Agregar validaciones de permisos
# Ocultar/deshabilitar según rol
```

### Paso 5: Testing Completo (30 min)
```bash
# Probar cada rol
# Verificar permisos
# Ajustar UI según feedback
```

---

## 📊 TIEMPO ESTIMADO

| Tarea | Tiempo |
|-------|--------|
| Backend (si falta) | 1-2 horas |
| Sistema de permisos | 30 min |
| Página de registro | 30 min |
| Panel de administración | 2-3 horas |
| Actualizar dashboard | 1 hora |
| Estilos y UI | 1 hora |
| Testing | 30 min |
| **TOTAL** | **6-8 horas** |

---

## 🎯 RESULTADO FINAL

### Para el Docente 👨‍🏫
- ✅ Puede registrarse y escoger rol (admin, vendedor, viewer)
- ✅ Ve dashboard personalizado según rol
- ✅ Admin tiene panel exclusivo de administración
- ✅ Permisos se aplican automáticamente

### Para el Proyecto 📱
- ✅ Sistema de roles robusto y escalable
- ✅ Seguridad por permisos en frontend y backend
- ✅ UI adaptativa según rol
- ✅ Panel de administración completo

---

**¿Te parece bien este plan? ¿Empezamos a implementar?** 🚀
