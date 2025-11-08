import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../api/client';
import './RegisterPage.css';
export const RegisterPage = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        username: '',
        nombre_completo: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showToast, setShowToast] = useState(false);
    const showSuccessToast = () => {
        setShowToast(true);
        setTimeout(() => {
            setShowToast(false);
            navigate('/login');
        }, 3000);
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        // Validaciones
        if (formData.password !== formData.confirmPassword) {
            setError('Las contraseñas no coinciden');
            return;
        }
        if (formData.password.length < 6) {
            setError('La contraseña debe tener al menos 6 caracteres');
            return;
        }
        if (!formData.username || !formData.email || !formData.nombre_completo) {
            setError('Todos los campos son obligatorios');
            return;
        }
        setLoading(true);
        try {
            const payload = {
                username: formData.username,
                email: formData.email,
                password: formData.password,
                nombre_completo: formData.nombre_completo,
                rol_id: 3 // Siempre viewer (👁️) por defecto
            };
            await apiClient.post('/auth/register', payload);
            // Registro exitoso - mostrar toast
            showSuccessToast();
        }
        catch (err) {
            setError(err.response?.data?.detail ||
                'Error al registrar usuario. Verifica que el usuario y email no estén en uso.');
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsxs(_Fragment, { children: [showToast && (_jsxs("div", { className: "toast-notification success", children: [_jsx("div", { className: "toast-icon", children: "\u2705" }), _jsxs("div", { className: "toast-content", children: [_jsx("div", { className: "toast-title", children: "\u00A1Registro exitoso!" }), _jsx("div", { className: "toast-message", children: "Tu cuenta ha sido creada con rol de Visualizador. Ahora puedes iniciar sesi\u00F3n." })] })] })), _jsx("div", { className: "register-container", children: _jsxs("div", { className: "register-card", children: [_jsx("h1", { children: "\uD83C\uDF3F Crear cuenta" }), _jsxs("p", { className: "subtitle", children: ["Reg\u00EDstrate como ", _jsx("strong", { children: "Visualizador \uD83D\uDC41\uFE0F" }), ". El administrador asignar\u00E1 tu rol despu\u00E9s."] }), _jsxs("form", { onSubmit: handleSubmit, children: [error && _jsx("div", { className: "error-message", children: error }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "username", children: "Nombre de usuario *" }), _jsx("input", { type: "text", id: "username", value: formData.username, onChange: (e) => setFormData({ ...formData, username: e.target.value }), required: true, placeholder: "Ej: juan_perez", disabled: loading })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "nombre_completo", children: "Nombre completo *" }), _jsx("input", { type: "text", id: "nombre_completo", value: formData.nombre_completo, onChange: (e) => setFormData({ ...formData, nombre_completo: e.target.value }), required: true, placeholder: "Ej: Juan P\u00E9rez", disabled: loading })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "email", children: "Email *" }), _jsx("input", { type: "email", id: "email", value: formData.email, onChange: (e) => setFormData({ ...formData, email: e.target.value }), required: true, placeholder: "Ej: juan@email.com", disabled: loading })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "password", children: "Contrase\u00F1a *" }), _jsx("input", { type: "password", id: "password", value: formData.password, onChange: (e) => setFormData({ ...formData, password: e.target.value }), required: true, placeholder: "M\u00EDnimo 6 caracteres", disabled: loading })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "confirmPassword", children: "Confirmar contrase\u00F1a *" }), _jsx("input", { type: "password", id: "confirmPassword", value: formData.confirmPassword, onChange: (e) => setFormData({ ...formData, confirmPassword: e.target.value }), required: true, placeholder: "Repite la contrase\u00F1a", disabled: loading })] }), _jsx("button", { type: "submit", className: "register-button", disabled: loading, children: loading ? 'Registrando...' : 'Crear cuenta' })] }), _jsxs("div", { className: "login-link", children: ["\u00BFYa tienes cuenta? ", _jsx(Link, { to: "/login", children: "Iniciar sesi\u00F3n" })] })] }) })] }));
};
export default RegisterPage;
