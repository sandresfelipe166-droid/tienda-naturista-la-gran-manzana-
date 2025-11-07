import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient from '@/api/client'

export default function ResetPasswordPage() {
  const [email, setEmail] = useState('')
  const [codigo, setCodigo] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const navigate = useNavigate()

  const validatePassword = (password: string): string | null => {
    if (!password) return 'La contraseña es requerida'
    if (password.length < 6) return 'La contraseña debe tener al menos 6 caracteres'
    if (password.length > 50) return 'La contraseña no puede exceder 50 caracteres'
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage('')
    setErrorMessage('')
    setSuccessMessage('')
    
    // Validaciones
    if (!email.trim()) {
      setErrorMessage('El email es requerido')
      return
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      setErrorMessage('Email inválido')
      return
    }
    
    if (!codigo.trim()) {
      setErrorMessage('El código de recuperación es requerido')
      return
    }
    
    if (codigo.length !== 6 || !/^\d+$/.test(codigo)) {
      setErrorMessage('El código debe ser 6 dígitos')
      return
    }
    
    const passwordError = validatePassword(newPassword)
    if (passwordError) {
      setErrorMessage(passwordError)
      return
    }
    
    if (newPassword !== confirmPassword) {
      setErrorMessage('Las contraseñas no coinciden')
      return
    }
    
    setLoading(true)
    try {
      const resp = await apiClient.post('/auth/reset-password-confirm', {
        email,
        codigo,
        new_password: newPassword,
      })
      setSuccessMessage(resp.data.message || 'Contraseña cambiada correctamente')
      
      // Limpiar formulario
      setEmail('')
      setCodigo('')
      setNewPassword('')
      setConfirmPassword('')
      
      // Redirigir al login después de 2 segundos
      setTimeout(() => navigate('/login'), 2000)
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail || err.message || 'Error al restablecer contraseña'
      setErrorMessage(errorDetail)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-content">
        <div className="login-card">
          <h2>Restablecer contraseña</h2>
          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                placeholder="Correo registrado"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Código de recuperación</label>
              <input
                type="text"
                placeholder="Código de 6 dígitos"
                value={codigo}
                onChange={(e) => setCodigo(e.target.value.slice(0, 6))}
                maxLength={6}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Nueva contraseña</label>
              <input
                type="password"
                placeholder="Nueva contraseña (mín. 6 caracteres)"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Confirmar contraseña</label>
              <input
                type="password"
                placeholder="Confirmar contraseña"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <button type="submit" className="login-button gradient-btn" disabled={loading}>
              {loading ? 'Procesando...' : 'Restablecer contraseña'}
            </button>
          </form>

          {errorMessage && <div className="error-message">{errorMessage}</div>}
          {successMessage && <div className="success-message">{successMessage}</div>}
          {message && <div className="info-message">{message}</div>}

          <div className="login-footer">
            <a href="/login">Volver a login</a> | <a href="/forgot-password">Solicitar nuevo código</a>
          </div>
        </div>
      </div>
    </div>
  )
}
