import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import apiClient from '@/api/client';
import { unwrapApi } from '@/api/unwrap';
import './LoginPage.css';
// SVG icons
const UserIcon = () => (_jsxs("svg", { width: "22", height: "22", fill: "none", viewBox: "0 0 24 24", stroke: "#2E8B57", strokeWidth: "2", children: [_jsx("circle", { cx: "12", cy: "8", r: "4" }), _jsx("path", { d: "M4 20c0-3.3 3.6-6 8-6s8 2.7 8 6" })] }));
const KeyIcon = () => (_jsxs("svg", { width: "22", height: "22", fill: "none", viewBox: "0 0 24 24", stroke: "#2E8B57", strokeWidth: "2", children: [_jsx("circle", { cx: "15", cy: "15", r: "3" }), _jsx("path", { d: "M2 15h10" }), _jsx("path", { d: "M6 15v-4" })] }));
export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const navigate = useNavigate();
    const { login } = useAuthStore();
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            // 1. Login: obtener token
            const response = await apiClient.post('/auth/login-json', {
                username,
                password,
            });
            const { access_token } = response.data;
            // 2. Consultar /auth/me para obtener datos del usuario
            const meResp = await apiClient.get('/auth/me', {
                headers: { Authorization: `Bearer ${access_token}` },
            });
            const backendUser = unwrapApi(meResp.data);
            // 3. Mapear UserResponse del backend a UserInfo del frontend
            const user = {
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
            };
            login(user, access_token, undefined);
            navigate('/dashboard');
        }
        catch (err) {
            const message = err.response?.data?.error?.message || 'Error al iniciar sesión';
            setError(message);
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsx("div", { className: "login-container", children: _jsxs("div", { className: "login-content", children: [_jsxs("div", { className: "login-brand", children: [_jsx("img", { src: "/images/logo.png", alt: "Tienda Naturista La Gran Manzana", className: "brand-logo", onError: (e) => {
                                e.currentTarget.style.display = 'none';
                            } }), _jsx("div", { className: "welcome-title", children: "Bienvenido a La Gran Manzana" })] }), _jsxs("div", { className: "login-card", children: [_jsxs("form", { onSubmit: handleSubmit, className: "login-form fade-in", children: [error && _jsx("div", { className: "error-message", children: error }), _jsx("div", { className: "form-group", children: _jsxs("div", { className: "input-with-icon", children: [_jsx("span", { className: "input-icon", children: _jsx(UserIcon, {}) }), _jsx("input", { id: "username", name: "username", type: "text", value: username, onChange: (e) => setUsername(e.target.value), placeholder: "Usuario o correo", required: true, disabled: loading, autoComplete: "username" })] }) }), _jsx("div", { className: "form-group", children: _jsxs("div", { className: "input-with-icon", children: [_jsx("span", { className: "input-icon", children: _jsx(KeyIcon, {}) }), _jsx("input", { id: "password", name: "password", type: showPassword ? 'text' : 'password', value: password, onChange: (e) => setPassword(e.target.value), placeholder: "Contrase\u00F1a", required: true, disabled: loading, autoComplete: "current-password" }), _jsx("button", { type: "button", className: "toggle-password-inline", "aria-label": showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña', onClick: () => setShowPassword((v) => !v), tabIndex: -1, children: showPassword ? (_jsxs("svg", { width: "22", height: "22", fill: "none", viewBox: "0 0 24 24", stroke: "#2E8B57", strokeWidth: "2", children: [_jsx("path", { d: "M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z" }), _jsx("circle", { cx: "12", cy: "12", r: "3" })] })) : (_jsxs("svg", { width: "22", height: "22", fill: "none", viewBox: "0 0 24 24", stroke: "#2E8B57", strokeWidth: "2", children: [_jsx("path", { d: "M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a21.77 21.77 0 0 1 5.06-6.06" }), _jsx("path", { d: "M1 1l22 22" })] })) })] }) }), _jsxs("label", { className: "remember-me", children: [_jsx("input", { type: "checkbox" }), _jsx("span", { children: "Recordarme" })] }), _jsx("button", { type: "submit", className: "login-button gradient-btn", disabled: loading, children: loading ? 'Cargando...' : 'Iniciar sesión' })] }), _jsxs("div", { className: "login-footer", children: [_jsx("a", { href: "/register", children: "Registrarse" }), _jsx("a", { href: "/forgot-password", children: "Restaurar contrase\u00F1a" })] })] })] }) }));
}
