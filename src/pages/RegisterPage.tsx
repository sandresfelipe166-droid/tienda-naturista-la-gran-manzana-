import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import apiClient from '../api/client'
import './RegisterPage.css'

export const RegisterPage = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    username: '',
    nombre_completo: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showToast, setShowToast] = useState(false)

  const showSuccessToast = () => {
    setShowToast(true)
    setTimeout(() => {
      setShowToast(false)
      navigate('/login')
    }, 3000)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validaciones
    if (formData.password !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden')
      return
    }

    if (formData.password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres')
      return
    }

    if (!formData.username || !formData.email || !formData.nombre_completo) {
      setError('Todos los campos son obligatorios')
      return
    }

    setLoading(true)

    try {
      const payload = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        nombre_completo: formData.nombre_completo,
        rol_id: 3 // Siempre viewer (👁️) por defecto
      }

      await apiClient.post('/auth/register', payload)

      // Registro exitoso - mostrar toast
      showSuccessToast()
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        'Error al registrar usuario. Verifica que el usuario y email no estén en uso.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {showToast && (
        <div className="toast-notification success">
          <div className="toast-icon">✅</div>
          <div className="toast-content">
            <div className="toast-title">¡Registro exitoso!</div>
            <div className="toast-message">
              Tu cuenta ha sido creada con rol de Visualizador. Ahora puedes iniciar sesión.
            </div>
          </div>
        </div>
      )}
      
      <div className="register-container">
      <div className="register-card">
        <h1>🌿 Crear cuenta</h1>
        <p className="subtitle">
          Regístrate como <strong>Visualizador 👁️</strong>. 
          El administrador asignará tu rol después.
        </p>

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
              disabled={loading}
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
              placeholder="Ej: Juan Pérez"
              disabled={loading}
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
              placeholder="Ej: juan@email.com"
              disabled={loading}
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
              placeholder="Mínimo 6 caracteres"
              disabled={loading}
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
              placeholder="Repite la contraseña"
              disabled={loading}
            />
          </div>

          <button type="submit" className="register-button" disabled={loading}>
            {loading ? 'Registrando...' : 'Crear cuenta'}
          </button>
        </form>

        <div className="login-link">
          ¿Ya tienes cuenta? <Link to="/login">Iniciar sesión</Link>
        </div>
      </div>
      </div>
    </>
  )
}

export default RegisterPage
