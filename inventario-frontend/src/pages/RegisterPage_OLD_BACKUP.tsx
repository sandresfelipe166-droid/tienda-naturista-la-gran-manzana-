import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import apiClient from '../api/client'
import { useAuthStore } from '@/store/authStore'
import './RegisterPage.css'

type RoleType = 'viewer' | 'gestor' | 'admin'

interface RoleCardData {
  id: RoleType
  title: string
  description: string
  icon: string
  features: string[]
}

const ROLES: RoleCardData[] = [
  {
    id: 'viewer',
    title: 'Visualizador',
    description: 'Solo consulta de inventario',
    icon: '👁️',
    features: [
      '✓ Ver productos y stock',
      '✓ Consultar entradas',
      '✓ Ver reportes',
      '✗ No puede crear o editar'
    ]
  },
  {
    id: 'gestor',
    title: 'Gestor',
    description: 'Gestión de inventario',
    icon: '�',
    features: [
      '✓ Registrar entradas de productos',
      '✓ Editar información de productos',
      '✓ Gestionar lotes',
      '✗ No acceso a administración'
    ]
  },
  {
    id: 'admin',
    title: 'Administrador',
    description: 'Control total del sistema',
    icon: '👑',
    features: [
      '✓ Acceso total',
      '✓ Gestionar usuarios',
      '✓ Configurar laboratorios',
      '✓ Administrar secciones'
    ]
  }
]

export const RegisterPage = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [selectedRole, setSelectedRole] = useState<RoleType>('viewer')
  const [formData, setFormData] = useState({
    username: '',
    nombre_completo: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Si ya está logueado, redirigir al dashboard
  useEffect(() => {
    if (user) {
      console.log('👤 Usuario ya logueado, redirigiendo al dashboard')
      navigate('/dashboard', { replace: true })
    }
  }, [user, navigate])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

      console.log('🔍 Iniciando registro...', { formData, selectedRole })

    // Validaciones
    if (formData.password !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden')
      return
    }

    if (formData.password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres')
      return
    }

    setLoading(true)

    try {
      // Mapeo de rol a rol_id (1=admin, 2=gestor, 3=viewer)
      const rolMapping: Record<RoleType, number> = {
        admin: 1,
        gestor: 2,
        viewer: 3
      }

        const payload = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        nombre_completo: formData.nombre_completo,
        rol_id: rolMapping[selectedRole]
        }

        console.log('📤 Enviando petición de registro:', payload)

        const response = await apiClient.post('/auth/register', payload)

        console.log('✅ Registro exitoso:', response.data)

      // Registro exitoso, redirigir al login
      navigate('/login', { 
        state: { 
          message: '¡Registro exitoso! Ahora puedes iniciar sesión.' 
        } 
      })
    } catch (err: any) {
        console.error('❌ Error en registro:', err)
        console.error('❌ Detalles del error:', err.response?.data)
      setError(
        err.response?.data?.detail || 
        'Error al registrar usuario. Intenta nuevamente.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="register-container">
      <div className="register-card">
        <h1>Crear cuenta</h1>
        <p className="subtitle">Selecciona tu rol y completa el formulario</p>

        {/* Selector de roles */}
        <div className="role-selector">
          {ROLES.map((role) => (
            <div
              key={role.id}
              className={`role-card ${selectedRole === role.id ? 'selected' : ''}`}
              onClick={() => setSelectedRole(role.id)}
            >
              <div className="role-icon">{role.icon}</div>
              <h3>{role.title}</h3>
              <p className="role-description">{role.description}</p>
              <ul className="role-features">
                {role.features.map((feature, idx) => (
                  <li key={idx}>{feature}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit}>
          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label htmlFor="username">Nombre de usuario *</label>
            <input
              type="text"
              id="username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
              placeholder="Ej: juan_perez"
            />
          </div>

          <div className="form-group">
            <label htmlFor="nombre_completo">Nombre completo *</label>
            <input
              type="text"
              id="nombre_completo"
              value={formData.nombre_completo}
              onChange={(e) => setFormData({ ...formData, nombre_completo: e.target.value })}
              required
              placeholder="Ej: Juan Pérez González"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Contraseña *</label>
            <input
              type="password"
              id="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
              minLength={6}
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirmar contraseña *</label>
            <input
              type="password"
              id="confirmPassword"
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              required
              minLength={6}
            />
          </div>

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Registrando...' : 'Crear cuenta'}
          </button>
        </form>

        <div className="login-link">
          ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
        </div>
      </div>
    </div>
  )
}
