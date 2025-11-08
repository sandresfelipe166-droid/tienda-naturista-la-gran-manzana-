import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '@/api/client';
export default function ResetPasswordPage() {
    const [email, setEmail] = useState('');
    const [codigo, setCodigo] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const navigate = useNavigate();
    const validatePassword = (password) => {
        if (!password)
            return 'La contraseña es requerida';
        if (password.length < 6)
            return 'La contraseña debe tener al menos 6 caracteres';
        if (password.length > 50)
            return 'La contraseña no puede exceder 50 caracteres';
        return null;
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setErrorMessage('');
        setSuccessMessage('');
        // Validaciones
        if (!email.trim()) {
            setErrorMessage('El email es requerido');
            return;
        }
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            setErrorMessage('Email inválido');
            return;
        }
        if (!codigo.trim()) {
            setErrorMessage('El código de recuperación es requerido');
            return;
        }
        if (codigo.length !== 6 || !/^\d+$/.test(codigo)) {
            setErrorMessage('El código debe ser 6 dígitos');
            return;
        }
        const passwordError = validatePassword(newPassword);
        if (passwordError) {
            setErrorMessage(passwordError);
            return;
        }
        if (newPassword !== confirmPassword) {
            setErrorMessage('Las contraseñas no coinciden');
            return;
        }
        setLoading(true);
        try {
            const resp = await apiClient.post('/auth/reset-password-confirm', {
                email,
                codigo,
                new_password: newPassword,
            });
            setSuccessMessage(resp.data.message || 'Contraseña cambiada correctamente');
            // Limpiar formulario
            setEmail('');
            setCodigo('');
            setNewPassword('');
            setConfirmPassword('');
            // Redirigir al login después de 2 segundos
            setTimeout(() => navigate('/login'), 2000);
        }
        catch (err) {
            const errorDetail = err.response?.data?.detail || err.message || 'Error al restablecer contraseña';
            setErrorMessage(errorDetail);
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsx("div", { className: "login-container", children: _jsx("div", { className: "login-content", children: _jsxs("div", { className: "login-card", children: [_jsx("h2", { children: "Restablecer contrase\u00F1a" }), _jsxs("form", { onSubmit: handleSubmit, className: "login-form", children: [_jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Email" }), _jsx("input", { type: "email", placeholder: "Correo registrado", value: email, onChange: (e) => setEmail(e.target.value), required: true, disabled: loading })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { children: "C\u00F3digo de recuperaci\u00F3n" }), _jsx("input", { type: "text", placeholder: "C\u00F3digo de 6 d\u00EDgitos", value: codigo, onChange: (e) => setCodigo(e.target.value.slice(0, 6)), maxLength: 6, required: true, disabled: loading })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Nueva contrase\u00F1a" }), _jsx("input", { type: "password", placeholder: "Nueva contrase\u00F1a (m\u00EDn. 6 caracteres)", value: newPassword, onChange: (e) => setNewPassword(e.target.value), required: true, disabled: loading })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Confirmar contrase\u00F1a" }), _jsx("input", { type: "password", placeholder: "Confirmar contrase\u00F1a", value: confirmPassword, onChange: (e) => setConfirmPassword(e.target.value), required: true, disabled: loading })] }), _jsx("button", { type: "submit", className: "login-button gradient-btn", disabled: loading, children: loading ? 'Procesando...' : 'Restablecer contraseña' })] }), errorMessage && _jsx("div", { className: "error-message", children: errorMessage }), successMessage && _jsx("div", { className: "success-message", children: successMessage }), message && _jsx("div", { className: "info-message", children: message }), _jsxs("div", { className: "login-footer", children: [_jsx("a", { href: "/login", children: "Volver a login" }), " | ", _jsx("a", { href: "/forgot-password", children: "Solicitar nuevo c\u00F3digo" })] })] }) }) }));
}
