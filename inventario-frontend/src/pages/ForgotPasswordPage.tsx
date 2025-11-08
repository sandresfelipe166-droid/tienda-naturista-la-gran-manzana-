import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import apiClient from '@/api/client'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [codigo, setCodigo] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage('')
    setCodigo(null)
    setErrorMessage('')
    
    // Validar email
    if (!email.trim()) {
      setErrorMessage('El email es requerido')
      return
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      setErrorMessage('Por favor ingresa un email válido')
      return
    }
    
    setLoading(true)
    try {
      const resp = await apiClient.post('/auth/reset-password-request', { email })
      // backend devuelve {message, codigo} en entorno de pruebas
      setMessage(resp.data.message || 'Revisa tu correo para el código')
      if (resp.data.codigo) {
        setCodigo(resp.data.codigo)
      }
    } catch (err: any) {
      const errorDetail = err.response?.data?.detail || err.message || 'Error al solicitar código'
      setErrorMessage(errorDetail)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-content">
        <div className="login-card">
          <h2>Recuperar contraseña</h2>
          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <input
                type="email"
                placeholder="Correo registrado"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <button type="submit" className="login-button gradient-btn" disabled={loading}>
              {loading ? 'Enviando...' : 'Solicitar código'}
            </button>
          </form>

          {errorMessage && <div className="error-message">{errorMessage}</div>}
          {message && <div className="info-message">{message}</div>}
          {codigo && (
            <div className="info-message">
              Código (solo pruebas): <strong>{codigo}</strong>
              <div><button onClick={() => navigate('/reset-password')}>Ir a restablecer</button></div>
            </div>
          )}

          <div className="login-footer">
            <a href="/login">Volver a login</a>
          </div>
        </div>
      </div>
    </div>
  )
}
