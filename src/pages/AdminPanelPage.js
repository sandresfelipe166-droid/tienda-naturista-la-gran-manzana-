import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { usePermissions } from '../hooks/usePermissions';
import { useLaboratorios } from '../hooks/useLaboratorios';
import { useSecciones } from '../hooks/useSecciones';
import { useUsuarios } from '../hooks/useUsuarios';
import { Navigate } from 'react-router-dom';
import './AdminPanelPage.css';
export const AdminPanelPage = () => {
    const { isAdmin } = usePermissions();
    const [activeTab, setActiveTab] = useState('laboratorios');
    console.log('🔍 AdminPanelPage montado', { isAdmin: isAdmin() });
    // Si no es admin, redirigir
    if (!isAdmin()) {
        console.log('❌ No es admin, redirigiendo...');
        return _jsx(Navigate, { to: "/dashboard", replace: true });
    }
    console.log('✅ Es admin, mostrando panel');
    return (_jsxs("div", { className: "admin-panel", children: [_jsxs("div", { className: "admin-header", children: [_jsx("h1", { children: "\uD83C\uDF3F Panel de Administraci\u00F3n" }), _jsx("p", { children: "Gestiona laboratorios, secciones y usuarios" })] }), _jsxs("div", { className: "admin-tabs", children: [_jsx("button", { className: `tab-btn ${activeTab === 'laboratorios' ? 'active' : ''}`, onClick: () => setActiveTab('laboratorios'), children: "\uD83C\uDFE2 Laboratorios" }), _jsx("button", { className: `tab-btn ${activeTab === 'secciones' ? 'active' : ''}`, onClick: () => setActiveTab('secciones'), children: "\uD83D\uDCC2 Secciones" }), _jsx("button", { className: `tab-btn ${activeTab === 'usuarios' ? 'active' : ''}`, onClick: () => setActiveTab('usuarios'), children: "\uD83D\uDC65 Usuarios" })] }), _jsxs("div", { className: "admin-content", children: [activeTab === 'laboratorios' && _jsx(LaboratoriosManager, {}), activeTab === 'secciones' && _jsx(SeccionesManager, {}), activeTab === 'usuarios' && _jsx(UsuariosManager, {})] })] }));
};
// Componente para gestionar laboratorios
const LaboratoriosManager = () => {
    const { laboratorios, loading, error, crearLaboratorio, actualizarLaboratorio, eliminarLaboratorio } = useLaboratorios();
    const [showForm, setShowForm] = useState(false);
    const [editingLab, setEditingLab] = useState(null);
    const [formData, setFormData] = useState({
        nombre_laboratorio: '',
        descripcion: ''
    });
    const handleSubmit = async () => {
        if (!formData.nombre_laboratorio.trim()) {
            alert('El nombre del laboratorio es obligatorio');
            return;
        }
        let success = false;
        if (editingLab) {
            // Actualizar
            success = await actualizarLaboratorio(editingLab.id_laboratorio, formData);
        }
        else {
            // Crear nuevo
            success = await crearLaboratorio(formData);
        }
        if (success) {
            setShowForm(false);
            setEditingLab(null);
            setFormData({ nombre_laboratorio: '', descripcion: '' });
        }
    };
    const handleEdit = (lab) => {
        setEditingLab(lab);
        setFormData({
            nombre_laboratorio: lab.nombre_laboratorio,
            descripcion: lab.descripcion || ''
        });
        setShowForm(true);
    };
    const handleDelete = async (id) => {
        if (confirm('¿Estás seguro de eliminar este laboratorio?')) {
            await eliminarLaboratorio(id, 'logico');
        }
    };
    const handleCancel = () => {
        setShowForm(false);
        setEditingLab(null);
        setFormData({ nombre_laboratorio: '', descripcion: '' });
    };
    return (_jsxs("div", { className: "manager-section", children: [_jsxs("div", { className: "section-header", children: [_jsx("h2", { children: "Laboratorios" }), _jsx("button", { className: "btn-add", onClick: () => setShowForm(!showForm), children: showForm ? '✖ Cancelar' : '➕ Nuevo Laboratorio' })] }), error && (_jsxs("div", { className: "error-message", style: {
                    padding: '12px',
                    backgroundColor: '#fee',
                    border: '1px solid #fcc',
                    borderRadius: '4px',
                    color: '#c33',
                    marginBottom: '16px'
                }, children: ["\u26A0\uFE0F ", error] })), showForm && (_jsxs("div", { className: "form-card", children: [_jsx("h3", { children: editingLab ? 'Editar Laboratorio' : 'Nuevo Laboratorio' }), _jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Nombre *" }), _jsx("input", { type: "text", value: formData.nombre_laboratorio, onChange: (e) => setFormData({ ...formData, nombre_laboratorio: e.target.value }), placeholder: "Ej: Laboratorio XYZ" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Descripci\u00F3n" }), _jsx("textarea", { value: formData.descripcion || '', onChange: (e) => setFormData({ ...formData, descripcion: e.target.value }), placeholder: "Descripci\u00F3n del laboratorio", rows: 3 })] }), _jsxs("div", { className: "form-actions", children: [_jsx("button", { className: "btn-primary", onClick: handleSubmit, disabled: loading, children: loading ? 'Guardando...' : 'Guardar' }), _jsx("button", { className: "btn-secondary", onClick: handleCancel, children: "Cancelar" })] })] })), _jsx("div", { className: "table-container", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "ID" }), _jsx("th", { children: "Nombre" }), _jsx("th", { children: "Descripci\u00F3n" }), _jsx("th", { children: "Estado" }), _jsx("th", { children: "Acciones" })] }) }), _jsx("tbody", { children: loading ? (_jsx("tr", { children: _jsx("td", { colSpan: 5, className: "empty-state", children: "Cargando..." }) })) : laboratorios.length === 0 ? (_jsx("tr", { children: _jsx("td", { colSpan: 5, className: "empty-state", children: "No hay laboratorios registrados" }) })) : (laboratorios.map((lab) => (_jsxs("tr", { children: [_jsx("td", { children: lab.id_laboratorio }), _jsx("td", { children: lab.nombre_laboratorio }), _jsx("td", { children: lab.descripcion || '-' }), _jsx("td", { children: _jsx("span", { className: `badge ${lab.estado === 'Activo' ? 'active' : 'inactive'}`, children: lab.estado }) }), _jsxs("td", { children: [_jsx("button", { className: "btn-icon", title: "Editar", onClick: () => handleEdit(lab), children: "\u270F\uFE0F" }), _jsx("button", { className: "btn-icon", title: "Eliminar", onClick: () => handleDelete(lab.id_laboratorio), children: "\uD83D\uDDD1\uFE0F" })] })] }, lab.id_laboratorio)))) })] }) })] }));
};
// Componente para gestionar secciones
const SeccionesManager = () => {
    const { secciones, loading, error, crearSeccion, actualizarSeccion, eliminarSeccion } = useSecciones();
    const [showForm, setShowForm] = useState(false);
    const [editingSeccion, setEditingSeccion] = useState(null);
    const [formData, setFormData] = useState({
        nombre_seccion: '',
        descripcion: ''
    });
    const handleSubmit = async () => {
        if (!formData.nombre_seccion.trim()) {
            alert('El nombre de la sección es obligatorio');
            return;
        }
        let success = false;
        if (editingSeccion) {
            success = await actualizarSeccion(editingSeccion.id_seccion, formData);
        }
        else {
            success = await crearSeccion(formData);
        }
        if (success) {
            setShowForm(false);
            setEditingSeccion(null);
            setFormData({ nombre_seccion: '', descripcion: '' });
        }
    };
    const handleEdit = (seccion) => {
        setEditingSeccion(seccion);
        setFormData({
            nombre_seccion: seccion.nombre_seccion,
            descripcion: seccion.descripcion || ''
        });
        setShowForm(true);
    };
    const handleDelete = async (id) => {
        if (confirm('¿Estás seguro de eliminar esta sección?')) {
            await eliminarSeccion(id, 'logico');
        }
    };
    const handleCancel = () => {
        setShowForm(false);
        setEditingSeccion(null);
        setFormData({ nombre_seccion: '', descripcion: '' });
    };
    return (_jsxs("div", { className: "manager-section", children: [_jsxs("div", { className: "section-header", children: [_jsx("h2", { children: "Secciones" }), _jsx("button", { className: "btn-add", onClick: () => setShowForm(!showForm), children: showForm ? '✖ Cancelar' : '➕ Nueva Sección' })] }), error && (_jsxs("div", { className: "error-message", style: {
                    padding: '12px',
                    backgroundColor: '#fee',
                    border: '1px solid #fcc',
                    borderRadius: '4px',
                    color: '#c33',
                    marginBottom: '16px'
                }, children: ["\u26A0\uFE0F ", error] })), showForm && (_jsxs("div", { className: "form-card", children: [_jsx("h3", { children: editingSeccion ? 'Editar Sección' : 'Nueva Sección' }), _jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Nombre *" }), _jsx("input", { type: "text", value: formData.nombre_seccion, onChange: (e) => setFormData({ ...formData, nombre_seccion: e.target.value }), placeholder: "Ej: Vitaminas" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Descripci\u00F3n" }), _jsx("textarea", { value: formData.descripcion || '', onChange: (e) => setFormData({ ...formData, descripcion: e.target.value }), placeholder: "Descripci\u00F3n de la secci\u00F3n", rows: 3 })] }), _jsxs("div", { className: "form-actions", children: [_jsx("button", { className: "btn-primary", onClick: handleSubmit, disabled: loading, children: loading ? 'Guardando...' : 'Guardar' }), _jsx("button", { className: "btn-secondary", onClick: handleCancel, children: "Cancelar" })] })] })), _jsx("div", { className: "table-container", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "ID" }), _jsx("th", { children: "Nombre" }), _jsx("th", { children: "Descripci\u00F3n" }), _jsx("th", { children: "Estado" }), _jsx("th", { children: "Acciones" })] }) }), _jsx("tbody", { children: loading ? (_jsx("tr", { children: _jsx("td", { colSpan: 5, className: "empty-state", children: "Cargando..." }) })) : secciones.length === 0 ? (_jsx("tr", { children: _jsx("td", { colSpan: 5, className: "empty-state", children: "No hay secciones registradas" }) })) : (secciones.map((seccion) => (_jsxs("tr", { children: [_jsx("td", { children: seccion.id_seccion }), _jsx("td", { children: seccion.nombre_seccion }), _jsx("td", { children: seccion.descripcion || '-' }), _jsx("td", { children: _jsx("span", { className: `badge ${seccion.estado === 'Activo' ? 'active' : 'inactive'}`, children: seccion.estado }) }), _jsxs("td", { children: [_jsx("button", { className: "btn-icon", title: "Editar", onClick: () => handleEdit(seccion), children: "\u270F\uFE0F" }), _jsx("button", { className: "btn-icon", title: "Eliminar", onClick: () => handleDelete(seccion.id_seccion), children: "\uD83D\uDDD1\uFE0F" })] })] }, seccion.id_seccion)))) })] }) })] }));
};
// Componente para gestionar usuarios
const UsuariosManager = () => {
    const { usuarios, loading, error, actualizarUsuario, eliminarUsuario, fetchRoles } = useUsuarios();
    const [editingUser, setEditingUser] = useState(null);
    const [showEditModal, setShowEditModal] = useState(false);
    const [formData, setFormData] = useState({});
    const [roles, setRoles] = useState([]);
    // Cargar roles al montar el componente
    useState(() => {
        const loadRoles = async () => {
            const rolesData = await fetchRoles();
            setRoles(rolesData);
        };
        loadRoles();
    });
    const getRolBadgeClass = (nombreRol) => {
        const rol = nombreRol.toLowerCase();
        if (rol.includes('admin'))
            return 'badge-admin';
        if (rol.includes('vendedor'))
            return 'badge-vendedor';
        return 'badge-viewer';
    };
    const getRolIcon = (nombreRol) => {
        const rol = nombreRol.toLowerCase();
        if (rol.includes('admin'))
            return '👑';
        if (rol.includes('vendedor'))
            return '🛒';
        return '👁️';
    };
    const handleEdit = (user) => {
        setEditingUser(user);
        setFormData({
            username: user.nombre_usuario,
            email: user.email,
            nombre_completo: user.nombre_completo || '',
            estado: user.estado,
            id_rol: user.id_rol
        });
        setShowEditModal(true);
    };
    const handleSubmit = async () => {
        if (!editingUser)
            return;
        try {
            await actualizarUsuario(editingUser.id_usuario, formData);
            setShowEditModal(false);
            setEditingUser(null);
            setFormData({});
            alert('Usuario actualizado exitosamente');
        }
        catch (err) {
            alert(err.message || 'Error al actualizar usuario');
        }
    };
    const handleDelete = async (id, username) => {
        if (confirm(`¿Estás seguro de desactivar el usuario "${username}"?\n\nEsto realizará una eliminación lógica (cambio de estado).`)) {
            try {
                await eliminarUsuario(id);
                alert('Usuario desactivado exitosamente');
            }
            catch (err) {
                alert(err.message || 'Error al desactivar usuario');
            }
        }
    };
    const handleCancel = () => {
        setShowEditModal(false);
        setEditingUser(null);
        setFormData({});
    };
    return (_jsxs("div", { className: "manager-section", children: [_jsxs("div", { className: "section-header", children: [_jsx("h2", { children: "Usuarios del Sistema" }), _jsxs("div", { className: "section-info", children: [_jsxs("span", { className: "info-badge", children: ["Total: ", usuarios.length] }), _jsxs("span", { className: "info-badge active", children: ["Activos: ", usuarios.filter(u => u.estado === 'Activo').length] }), _jsxs("span", { className: "info-badge inactive", children: ["Inactivos: ", usuarios.filter(u => u.estado === 'Inactivo').length] })] })] }), error && (_jsxs("div", { className: "error-message", style: {
                    padding: '12px',
                    backgroundColor: '#fee',
                    border: '1px solid #fcc',
                    borderRadius: '4px',
                    color: '#c33',
                    marginBottom: '16px'
                }, children: ["\u26A0\uFE0F ", error] })), showEditModal && editingUser && (_jsx("div", { className: "modal-overlay", onClick: handleCancel, children: _jsxs("div", { className: "modal-content", onClick: (e) => e.stopPropagation(), children: [_jsxs("div", { className: "modal-header", children: [_jsx("h3", { children: "Editar Usuario" }), _jsx("button", { className: "btn-close", onClick: handleCancel, children: "\u2716" })] }), _jsxs("div", { className: "modal-body", children: [_jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Nombre de Usuario" }), _jsx("input", { type: "text", value: formData.username || '', onChange: (e) => setFormData({ ...formData, username: e.target.value }), placeholder: "Nombre de usuario" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Email" }), _jsx("input", { type: "email", value: formData.email || '', onChange: (e) => setFormData({ ...formData, email: e.target.value }), placeholder: "Email" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Nombre Completo" }), _jsx("input", { type: "text", value: formData.nombre_completo || '', onChange: (e) => setFormData({ ...formData, nombre_completo: e.target.value }), placeholder: "Nombre completo" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Rol del Usuario" }), _jsxs("select", { value: formData.id_rol || '', onChange: (e) => setFormData({ ...formData, id_rol: parseInt(e.target.value) }), children: [_jsx("option", { value: "", children: "Selecciona un rol" }), roles.map((rol) => (_jsxs("option", { value: rol.id_rol, children: [rol.id_rol === 1 && '👑 ', rol.id_rol === 2 && '🛒 ', rol.id_rol === 3 && '👁️ ', rol.nombre_rol, rol.descripcion && ` - ${rol.descripcion}`] }, rol.id_rol)))] }), _jsx("small", { style: { color: '#666', fontSize: '12px', marginTop: '4px', display: 'block' }, children: "\uD83D\uDC51 Admin: Control total | \uD83D\uDED2 Gestor: Gesti\u00F3n de inventario | \uD83D\uDC41\uFE0F Viewer: Solo visualizaci\u00F3n" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Estado" }), _jsxs("select", { value: formData.estado || 'Activo', onChange: (e) => setFormData({ ...formData, estado: e.target.value }), children: [_jsx("option", { value: "Activo", children: "Activo" }), _jsx("option", { value: "Inactivo", children: "Inactivo" }), _jsx("option", { value: "Suspendido", children: "Suspendido" })] })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Nueva Contrase\u00F1a (opcional)" }), _jsx("input", { type: "password", value: formData.password || '', onChange: (e) => setFormData({ ...formData, password: e.target.value }), placeholder: "Dejar en blanco para mantener la actual" }), _jsx("small", { style: { color: '#666', fontSize: '12px' }, children: "Solo completa este campo si deseas cambiar la contrase\u00F1a" })] })] }), _jsxs("div", { className: "modal-footer", children: [_jsx("button", { className: "btn-primary", onClick: handleSubmit, disabled: loading, children: loading ? 'Guardando...' : 'Guardar Cambios' }), _jsx("button", { className: "btn-secondary", onClick: handleCancel, children: "Cancelar" })] })] }) })), _jsx("div", { className: "table-container", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "ID" }), _jsx("th", { children: "Usuario" }), _jsx("th", { children: "Email" }), _jsx("th", { children: "Nombre Completo" }), _jsx("th", { children: "Rol" }), _jsx("th", { children: "Estado" }), _jsx("th", { children: "\u00DAltimo Acceso" }), _jsx("th", { children: "Acciones" })] }) }), _jsx("tbody", { children: loading ? (_jsx("tr", { children: _jsx("td", { colSpan: 8, className: "empty-state", children: "Cargando usuarios..." }) })) : usuarios.length === 0 ? (_jsx("tr", { children: _jsx("td", { colSpan: 8, className: "empty-state", children: "No hay usuarios registrados" }) })) : (usuarios.map((user) => (_jsxs("tr", { children: [_jsx("td", { children: user.id_usuario }), _jsx("td", { children: _jsx("strong", { children: user.nombre_usuario }) }), _jsx("td", { children: user.email }), _jsx("td", { children: user.nombre_completo || '-' }), _jsx("td", { children: _jsxs("span", { className: `badge ${getRolBadgeClass(user.rol?.nombre_rol || '')}`, children: [getRolIcon(user.rol?.nombre_rol || ''), " ", user.rol?.nombre_rol || 'Sin rol'] }) }), _jsx("td", { children: _jsx("span", { className: `badge ${user.estado === 'Activo' ? 'active' : 'inactive'}`, children: user.estado }) }), _jsx("td", { children: user.ultima_acceso
                                            ? new Date(user.ultima_acceso).toLocaleDateString('es-ES', {
                                                year: 'numeric',
                                                month: 'short',
                                                day: 'numeric'
                                            })
                                            : 'Nunca' }), _jsxs("td", { children: [_jsx("button", { className: "btn-icon", title: "Editar", onClick: () => handleEdit(user), children: "\u270F\uFE0F" }), _jsx("button", { className: "btn-icon", title: "Desactivar", onClick: () => handleDelete(user.id_usuario, user.nombre_usuario), children: "\uD83D\uDDD1\uFE0F" })] })] }, user.id_usuario)))) })] }) })] }));
};
