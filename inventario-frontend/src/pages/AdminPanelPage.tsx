import { useState } from 'react'
import { usePermissions } from '../hooks/usePermissions'
import { useLaboratorios, Laboratorio, LaboratorioCreate } from '../hooks/useLaboratorios'
import { useSecciones, Seccion, SeccionCreate } from '../hooks/useSecciones'
import { useUsuarios, Usuario, UsuarioUpdate } from '../hooks/useUsuarios'
import { Navigate } from 'react-router-dom'
import logger from '@/utils/logger'
import './AdminPanelPage.css'

type TabType = 'laboratorios' | 'secciones' | 'usuarios'

export const AdminPanelPage = () => {
  const { isAdmin } = usePermissions()
  const [activeTab, setActiveTab] = useState<TabType>('laboratorios')

  logger.debug('AdminPanelPage montado', { isAdmin: isAdmin() })

  // Si no es admin, redirigir
  if (!isAdmin()) {
    logger.info('Usuario sin permisos admin redirigido a dashboard')
    return <Navigate to="/dashboard" replace />
  }

  logger.debug('Panel de admin renderizado correctamente')

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h1>🌿 Panel de Administración</h1>
        <p>Gestiona laboratorios, secciones y usuarios</p>
      </div>

      <div className="admin-tabs">
        <button
          className={`tab-btn ${activeTab === 'laboratorios' ? 'active' : ''}`}
          onClick={() => setActiveTab('laboratorios')}
        >
          🏢 Laboratorios
        </button>
        <button
          className={`tab-btn ${activeTab === 'secciones' ? 'active' : ''}`}
          onClick={() => setActiveTab('secciones')}
        >
          📂 Secciones
        </button>
        <button
          className={`tab-btn ${activeTab === 'usuarios' ? 'active' : ''}`}
          onClick={() => setActiveTab('usuarios')}
        >
          👥 Usuarios
        </button>
      </div>

      <div className="admin-content">
        {activeTab === 'laboratorios' && <LaboratoriosManager />}
        {activeTab === 'secciones' && <SeccionesManager />}
        {activeTab === 'usuarios' && <UsuariosManager />}
      </div>
    </div>
  )
}

// Componente para gestionar laboratorios
const LaboratoriosManager = () => {
  const { laboratorios, loading, error, crearLaboratorio, actualizarLaboratorio, eliminarLaboratorio } = useLaboratorios()
  const [showForm, setShowForm] = useState(false)
  const [editingLab, setEditingLab] = useState<Laboratorio | null>(null)
  const [formData, setFormData] = useState<LaboratorioCreate>({ 
    nombre_laboratorio: '', 
    descripcion: '' 
  })

  const handleSubmit = async () => {
    if (!formData.nombre_laboratorio.trim()) {
      alert('El nombre del laboratorio es obligatorio')
      return
    }

    let success = false
    if (editingLab) {
      // Actualizar
      success = await actualizarLaboratorio(editingLab.id_laboratorio, formData)
    } else {
      // Crear nuevo
      success = await crearLaboratorio(formData)
    }

    if (success) {
      setShowForm(false)
      setEditingLab(null)
      setFormData({ nombre_laboratorio: '', descripcion: '' })
    }
  }

  const handleEdit = (lab: Laboratorio) => {
    setEditingLab(lab)
    setFormData({
      nombre_laboratorio: lab.nombre_laboratorio,
      descripcion: lab.descripcion || ''
    })
    setShowForm(true)
  }

  const handleDelete = async (id: number) => {
    if (confirm('¿Estás seguro de eliminar este laboratorio?')) {
      await eliminarLaboratorio(id, 'logico')
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingLab(null)
    setFormData({ nombre_laboratorio: '', descripcion: '' })
  }

  return (
    <div className="manager-section">
      <div className="section-header">
        <h2>Laboratorios</h2>
        <button className="btn-add" onClick={() => setShowForm(!showForm)}>
          {showForm ? '✖ Cancelar' : '➕ Nuevo Laboratorio'}
        </button>
      </div>

      {error && (
        <div className="error-message" style={{
          padding: '12px',
          backgroundColor: '#fee',
          border: '1px solid #fcc',
          borderRadius: '4px',
          color: '#c33',
          marginBottom: '16px'
        }}>
          ⚠️ {error}
        </div>
      )}

      {showForm && (
        <div className="form-card">
          <h3>{editingLab ? 'Editar Laboratorio' : 'Nuevo Laboratorio'}</h3>
          <div className="form-group">
            <label>Nombre *</label>
            <input
              type="text"
              value={formData.nombre_laboratorio}
              onChange={(e) => setFormData({ ...formData, nombre_laboratorio: e.target.value })}
              placeholder="Ej: Laboratorio XYZ"
            />
          </div>
          <div className="form-group">
            <label>Descripción</label>
            <textarea
              value={formData.descripcion || ''}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              placeholder="Descripción del laboratorio"
              rows={3}
            />
          </div>
          <div className="form-actions">
            <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
              {loading ? 'Guardando...' : 'Guardar'}
            </button>
            <button className="btn-secondary" onClick={handleCancel}>
              Cancelar
            </button>
          </div>
        </div>
      )}

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Descripción</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} className="empty-state">
                  Cargando...
                </td>
              </tr>
            ) : laboratorios.length === 0 ? (
              <tr>
                <td colSpan={5} className="empty-state">
                  No hay laboratorios registrados
                </td>
              </tr>
            ) : (
              laboratorios.map((lab) => (
                <tr key={lab.id_laboratorio}>
                  <td>{lab.id_laboratorio}</td>
                  <td>{lab.nombre_laboratorio}</td>
                  <td>{lab.descripcion || '-'}</td>
                  <td>
                    <span className={`badge ${lab.estado === 'Activo' ? 'active' : 'inactive'}`}>
                      {lab.estado}
                    </span>
                  </td>
                  <td>
                    <button className="btn-icon" title="Editar" onClick={() => handleEdit(lab)}>✏️</button>
                    <button className="btn-icon" title="Eliminar" onClick={() => handleDelete(lab.id_laboratorio)}>🗑️</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Componente para gestionar secciones
const SeccionesManager = () => {
  const { secciones, loading, error, crearSeccion, actualizarSeccion, eliminarSeccion } = useSecciones()
  const [showForm, setShowForm] = useState(false)
  const [editingSeccion, setEditingSeccion] = useState<Seccion | null>(null)
  const [formData, setFormData] = useState<SeccionCreate>({ 
    nombre_seccion: '', 
    descripcion: '' 
  })

  const handleSubmit = async () => {
    if (!formData.nombre_seccion.trim()) {
      alert('El nombre de la sección es obligatorio')
      return
    }

    let success = false
    if (editingSeccion) {
      success = await actualizarSeccion(editingSeccion.id_seccion, formData)
    } else {
      success = await crearSeccion(formData)
    }

    if (success) {
      setShowForm(false)
      setEditingSeccion(null)
      setFormData({ nombre_seccion: '', descripcion: '' })
    }
  }

  const handleEdit = (seccion: Seccion) => {
    setEditingSeccion(seccion)
    setFormData({
      nombre_seccion: seccion.nombre_seccion,
      descripcion: seccion.descripcion || ''
    })
    setShowForm(true)
  }

  const handleDelete = async (id: number) => {
    if (confirm('¿Estás seguro de eliminar esta sección?')) {
      await eliminarSeccion(id, 'logico')
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingSeccion(null)
    setFormData({ nombre_seccion: '', descripcion: '' })
  }

  return (
    <div className="manager-section">
      <div className="section-header">
        <h2>Secciones</h2>
        <button className="btn-add" onClick={() => setShowForm(!showForm)}>
          {showForm ? '✖ Cancelar' : '➕ Nueva Sección'}
        </button>
      </div>

      {error && (
        <div className="error-message" style={{
          padding: '12px',
          backgroundColor: '#fee',
          border: '1px solid #fcc',
          borderRadius: '4px',
          color: '#c33',
          marginBottom: '16px'
        }}>
          ⚠️ {error}
        </div>
      )}

      {showForm && (
        <div className="form-card">
          <h3>{editingSeccion ? 'Editar Sección' : 'Nueva Sección'}</h3>
          <div className="form-group">
            <label>Nombre *</label>
            <input 
              type="text" 
              value={formData.nombre_seccion}
              onChange={(e) => setFormData({ ...formData, nombre_seccion: e.target.value })}
              placeholder="Ej: Vitaminas" 
            />
          </div>
          <div className="form-group">
            <label>Descripción</label>
            <textarea 
              value={formData.descripcion || ''}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              placeholder="Descripción de la sección" 
              rows={3} 
            />
          </div>
          <div className="form-actions">
            <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
              {loading ? 'Guardando...' : 'Guardar'}
            </button>
            <button className="btn-secondary" onClick={handleCancel}>
              Cancelar
            </button>
          </div>
        </div>
      )}

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th>Descripción</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} className="empty-state">
                  Cargando...
                </td>
              </tr>
            ) : secciones.length === 0 ? (
              <tr>
                <td colSpan={5} className="empty-state">
                  No hay secciones registradas
                </td>
              </tr>
            ) : (
              secciones.map((seccion) => (
                <tr key={seccion.id_seccion}>
                  <td>{seccion.id_seccion}</td>
                  <td>{seccion.nombre_seccion}</td>
                  <td>{seccion.descripcion || '-'}</td>
                  <td>
                    <span className={`badge ${seccion.estado === 'Activo' ? 'active' : 'inactive'}`}>
                      {seccion.estado}
                    </span>
                  </td>
                  <td>
                    <button className="btn-icon" title="Editar" onClick={() => handleEdit(seccion)}>✏️</button>
                    <button className="btn-icon" title="Eliminar" onClick={() => handleDelete(seccion.id_seccion)}>🗑️</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Componente para gestionar usuarios
const UsuariosManager = () => {
  const { usuarios, loading, error, actualizarUsuario, eliminarUsuario, fetchRoles } = useUsuarios()
  const [editingUser, setEditingUser] = useState<Usuario | null>(null)
  const [showEditModal, setShowEditModal] = useState(false)
  const [formData, setFormData] = useState<UsuarioUpdate>({})
  const [roles, setRoles] = useState<{ id_rol: number; nombre_rol: string; descripcion?: string }[]>([])

  // Cargar roles al montar el componente
  useState(() => {
    const loadRoles = async () => {
      const rolesData = await fetchRoles()
      setRoles(rolesData)
    }
    loadRoles()
  })

  const getRolBadgeClass = (nombreRol: string) => {
    const rol = nombreRol.toLowerCase()
    if (rol.includes('admin')) return 'badge-admin'
    if (rol.includes('vendedor')) return 'badge-vendedor'
    return 'badge-viewer'
  }

  const getRolIcon = (nombreRol: string) => {
    const rol = nombreRol.toLowerCase()
    if (rol.includes('admin')) return '👑'
    if (rol.includes('vendedor')) return '🛒'
    return '👁️'
  }

  const handleEdit = (user: Usuario) => {
    setEditingUser(user)
    setFormData({
      username: user.nombre_usuario,
      email: user.email,
      nombre_completo: user.nombre_completo || '',
      estado: user.estado,
      id_rol: user.id_rol
    })
    setShowEditModal(true)
  }

  const handleSubmit = async () => {
    if (!editingUser) return

    try {
      await actualizarUsuario(editingUser.id_usuario, formData)
      setShowEditModal(false)
      setEditingUser(null)
      setFormData({})
      alert('Usuario actualizado exitosamente')
    } catch (err: any) {
      alert(err.message || 'Error al actualizar usuario')
    }
  }

  const handleDelete = async (id: number, username: string) => {
    if (confirm(`¿Estás seguro de desactivar el usuario "${username}"?\n\nEsto realizará una eliminación lógica (cambio de estado).`)) {
      try {
        await eliminarUsuario(id)
        alert('Usuario desactivado exitosamente')
      } catch (err: any) {
        alert(err.message || 'Error al desactivar usuario')
      }
    }
  }

  const handleCancel = () => {
    setShowEditModal(false)
    setEditingUser(null)
    setFormData({})
  }

  return (
    <div className="manager-section">
      <div className="section-header">
        <h2>Usuarios del Sistema</h2>
        <div className="section-info">
          <span className="info-badge">Total: {usuarios.length}</span>
          <span className="info-badge active">
            Activos: {usuarios.filter(u => u.estado === 'Activo').length}
          </span>
          <span className="info-badge inactive">
            Inactivos: {usuarios.filter(u => u.estado === 'Inactivo').length}
          </span>
        </div>
      </div>

      {error && (
        <div className="error-message" style={{
          padding: '12px',
          backgroundColor: '#fee',
          border: '1px solid #fcc',
          borderRadius: '4px',
          color: '#c33',
          marginBottom: '16px'
        }}>
          ⚠️ {error}
        </div>
      )}

      {showEditModal && editingUser && (
        <div className="modal-overlay" onClick={handleCancel}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Editar Usuario</h3>
              <button className="btn-close" onClick={handleCancel}>✖</button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label>Nombre de Usuario</label>
                <input
                  type="text"
                  value={formData.username || ''}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  placeholder="Nombre de usuario"
                />
              </div>

              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email || ''}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="Email"
                />
              </div>

              <div className="form-group">
                <label>Nombre Completo</label>
                <input
                  type="text"
                  value={formData.nombre_completo || ''}
                  onChange={(e) => setFormData({ ...formData, nombre_completo: e.target.value })}
                  placeholder="Nombre completo"
                />
              </div>

              <div className="form-group">
                <label>Rol del Usuario</label>
                <select
                  value={formData.id_rol || ''}
                  onChange={(e) => setFormData({ ...formData, id_rol: parseInt(e.target.value) })}
                >
                  <option value="">Selecciona un rol</option>
                  {roles.map((rol) => (
                    <option key={rol.id_rol} value={rol.id_rol}>
                      {rol.id_rol === 1 && '👑 '}{rol.id_rol === 2 && '🛒 '}{rol.id_rol === 3 && '👁️ '}
                      {rol.nombre_rol}
                      {rol.descripcion && ` - ${rol.descripcion}`}
                    </option>
                  ))}
                </select>
                <small style={{ color: '#666', fontSize: '12px', marginTop: '4px', display: 'block' }}>
                  👑 Admin: Control total | 🛒 Gestor: Gestión de inventario | 👁️ Viewer: Solo visualización
                </small>
              </div>

              <div className="form-group">
                <label>Estado</label>
                <select
                  value={formData.estado || 'Activo'}
                  onChange={(e) => setFormData({ ...formData, estado: e.target.value as any })}
                >
                  <option value="Activo">Activo</option>
                  <option value="Inactivo">Inactivo</option>
                  <option value="Suspendido">Suspendido</option>
                </select>
              </div>

              <div className="form-group">
                <label>Nueva Contraseña (opcional)</label>
                <input
                  type="password"
                  value={formData.password || ''}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder="Dejar en blanco para mantener la actual"
                />
                <small style={{ color: '#666', fontSize: '12px' }}>
                  Solo completa este campo si deseas cambiar la contraseña
                </small>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
                {loading ? 'Guardando...' : 'Guardar Cambios'}
              </button>
              <button className="btn-secondary" onClick={handleCancel}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Usuario</th>
              <th>Email</th>
              <th>Nombre Completo</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Último Acceso</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={8} className="empty-state">
                  Cargando usuarios...
                </td>
              </tr>
            ) : usuarios.length === 0 ? (
              <tr>
                <td colSpan={8} className="empty-state">
                  No hay usuarios registrados
                </td>
              </tr>
            ) : (
              usuarios.map((user) => (
                <tr key={user.id_usuario}>
                  <td>{user.id_usuario}</td>
                  <td>
                    <strong>{user.nombre_usuario}</strong>
                  </td>
                  <td>{user.email}</td>
                  <td>{user.nombre_completo || '-'}</td>
                  <td>
                    <span className={`badge ${getRolBadgeClass(user.rol?.nombre_rol || '')}`}>
                      {getRolIcon(user.rol?.nombre_rol || '')} {user.rol?.nombre_rol || 'Sin rol'}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${user.estado === 'Activo' ? 'active' : 'inactive'}`}>
                      {user.estado}
                    </span>
                  </td>
                  <td>
                    {user.ultima_acceso 
                      ? new Date(user.ultima_acceso).toLocaleDateString('es-ES', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        })
                      : 'Nunca'
                    }
                  </td>
                  <td>
                    <button 
                      className="btn-icon" 
                      title="Editar" 
                      onClick={() => handleEdit(user)}
                    >
                      ✏️
                    </button>
                    <button 
                      className="btn-icon" 
                      title="Desactivar" 
                      onClick={() => handleDelete(user.id_usuario, user.nombre_usuario)}
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
