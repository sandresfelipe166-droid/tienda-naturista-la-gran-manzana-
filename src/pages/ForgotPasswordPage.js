import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '@/api/client';
export default function ForgotPasswordPage() {
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [codigo, setCodigo] = useState(null);
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const navigate = useNavigate();
    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setCodigo(null);
        setErrorMessage('');
        // Validar email
        if (!email.trim()) {
            setErrorMessage('El email es requerido');
            return;
        }
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            setErrorMessage('Por favor ingresa un email válido');
            return;
        }
        setLoading(true);
        try {
            const resp = await apiClient.post('/auth/reset-password-request', { email });
            // backend devuelve {message, codigo} en entorno de pruebas
            setMessage(resp.data.message || 'Revisa tu correo para el código');
            if (resp.data.codigo) {
                setCodigo(resp.data.codigo);
            }
        }
        catch (err) {
            const errorDetail = err.response?.data?.detail || err.message || 'Error al solicitar código';
            setErrorMessage(errorDetail);
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsx("div", { className: "login-container", children: _jsx("div", { className: "login-content", children: _jsxs("div", { className: "login-card", children: [_jsx("h2", { children: "Recuperar contrase\u00F1a" }), _jsxs("form", { onSubmit: handleSubmit, className: "login-form", children: [_jsx("div", { className: "form-group", children: _jsx("input", { type: "email", placeholder: "Correo registrado", value: email, onChange: (e) => setEmail(e.target.value), required: true, disabled: loading }) }), _jsx("button", { type: "submit", className: "login-button gradient-btn", disabled: loading, children: loading ? 'Enviando...' : 'Solicitar código' })] }), errorMessage && _jsx("div", { className: "error-message", children: errorMessage }), message && _jsx("div", { className: "info-message", children: message }), codigo && (_jsxs("div", { className: "info-message", children: ["C\u00F3digo (solo pruebas): ", _jsx("strong", { children: codigo }), _jsx("div", { children: _jsx("button", { onClick: () => navigate('/reset-password'), children: "Ir a restablecer" }) })] })), _jsx("div", { className: "login-footer", children: _jsx("a", { href: "/login", children: "Volver a login" }) })] }) }) }));
}
