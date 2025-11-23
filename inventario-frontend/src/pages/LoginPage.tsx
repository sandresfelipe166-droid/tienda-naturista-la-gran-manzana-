console.log("LoginPage render");
import apiClient from '@/api/client';
import { unwrapApi } from '@/api/unwrap';
import { useAuthStore } from '@/store/authStore';
import { ApiResponse, UserInfo, UserResponse } from '@/types';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css';

// SVG icons
const UserIcon = () => (
    <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="#2E8B57" strokeWidth="2"><circle cx="12" cy="8" r="4" /><path d="M4 20c0-3.3 3.6-6 8-6s8 2.7 8 6" /></svg>
)
const KeyIcon = () => (
    <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="#2E8B57" strokeWidth="2"><circle cx="15" cy="15" r="3" /><path d="M2 15h10" /><path d="M6 15v-4" /></svg>
)

export default function LoginPage() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    const [showPassword, setShowPassword] = useState(false)
    const navigate = useNavigate()
    const { login } = useAuthStore()

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            // 1. Login: obtener token
            const response = await apiClient.post<{ access_token: string; token_type: string }>('/auth/login-json', {
                username,
                password,
            })
            const { access_token } = response.data
            // 2. Consultar /auth/me para obtener datos del usuario
            const meResp = await apiClient.get<ApiResponse<UserResponse>>('/auth/me', {
                headers: { Authorization: `Bearer ${access_token}` },
            })
            const backendUser = unwrapApi<UserResponse>(meResp.data)

            // 3. Mapear UserResponse del backend a UserInfo del frontend
            const user: UserInfo = {
                id: backendUser.id_usuario,
                email: backendUser.email,
                nombre: backendUser.nombre_completo?.split(' ')[0] || backendUser.nombre_usuario,
                apellido: backendUser.nombre_completo?.split(' ').slice(1).join(' ') || '',
                rol: {
                    id_rol: backendUser.id_rol,
                    nombre_rol: backendUser.id_rol === 1 ? 'admin' : backendUser.id_rol === 2 ? 'gestor' : 'viewer',
                    descripcion: ''
                },
                activo: backendUser.estado === 'Activo',
            }

            login(user, access_token, undefined)
            navigate('/dashboard')
        } catch (err: any) {
            const message = err.response?.data?.error?.message || 'Error al iniciar sesión'
            setError(message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="login-container">
            <div className="login-content">
                <div className="login-brand">
                    <img
                        src="/images/logo.png"
                        alt="Tienda Naturista La Gran Manzana"
                        className="brand-logo"
                        onError={(e) => {
                            e.currentTarget.style.display = 'none'
                        }}
                    />
                    <div className="welcome-title">Bienvenido a La Gran Manzana</div>
                </div>

                <div className="login-card">
                    <form onSubmit={handleSubmit} className="login-form fade-in">
                        {error && <div className="error-message">{error}</div>}

                        <div className="form-group">
                            <div className="input-with-icon">
                                <span className="input-icon"><UserIcon /></span>
                                <input
                                    id="username"
                                    name="username"
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    placeholder="Usuario o correo"
                                    required
                                    disabled={loading}
                                    autoComplete="username"
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <div className="input-with-icon">
                                <span className="input-icon"><KeyIcon /></span>
                                <input
                                    id="password"
                                    name="password"
                                    type={showPassword ? 'text' : 'password'}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Contraseña"
                                    required
                                    disabled={loading}
                                    autoComplete="current-password"
                                />
                                <button
                                    type="button"
                                    className="toggle-password-inline"
                                    aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                                    onClick={() => setShowPassword((v) => !v)}
                                    tabIndex={-1}
                                >
                                    {showPassword ? (
                                        <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="#2E8B57" strokeWidth="2"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z" /><circle cx="12" cy="12" r="3" /></svg>
                                    ) : (
                                        <svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="#2E8B57" strokeWidth="2"><path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a21.77 21.77 0 0 1 5.06-6.06" /><path d="M1 1l22 22" /></svg>
                                    )}
                                </button>
                            </div>
                        </div>

                        <label className="remember-me">
                            <input type="checkbox" />
                            <span>Recordarme</span>
                        </label>

                        <button type="submit" className="login-button gradient-btn" disabled={loading}>
                            {loading ? 'Cargando...' : 'Iniciar sesión'}
                        </button>
                    </form>

                    <div className="login-footer">
                        <a href="/register">Registrarse</a>
                        <a href="/forgot-password">Restaurar contraseña</a>
                    </div>
                </div>
            </div>
        </div>
    )
}
