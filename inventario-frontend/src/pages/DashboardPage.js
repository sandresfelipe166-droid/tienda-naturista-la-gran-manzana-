import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useEffect, useMemo, useState } from 'react';
import { useSecciones, useLaboratorios } from '@/hooks/useCatalogs';
import Modal from '@/components/Modal';
import ProductForm from '@/components/ProductForm';
import EntradaForm from '@/components/EntradaForm';
import VentaForm from '@/components/VentaForm';
import { useCreateProduct, useUpdateProduct, useDeleteProduct } from '@/hooks/useProducts';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useProducts } from '@/hooks/useProducts';
import './DashboardPage.css';
import { useVentasMes, useVentasAnio, useGastosMes, useGastosAnio } from '@/hooks/useStats';
import { useVentasListado } from '@/hooks/useVentas';
import { useGastosListado } from '@/hooks/useGastos';
import { useCreateVenta } from '@/hooks/useCreateVenta';
import { useCreateGasto } from '@/hooks/useCreateGasto';
import { useCrearEntrada, useEntradasListado, useEntradasMes, useEntradasAnio } from '@/hooks/useEntradas';
import { useCotizacionesListado, useCotizacionEstadisticas, useCrearCotizacion, useConvertirCotizacionAVenta } from '@/hooks/useCotizaciones';
import { NotificationPanel } from '@/components/NotificationPanel';
import { useInventoryNotifications, useNotificationPermission } from '@/hooks/useInventoryNotifications';
import { usePermissions } from '@/hooks/usePermissions';
import { AdminPanelPage } from '@/pages/AdminPanelPage';
const sidebarMenu = [
    { id: 'panel', icon: _jsxs("svg", { width: "20", height: "20", viewBox: "0 0 24 24", fill: "none", children: [_jsx("rect", { x: "3", y: "3", width: "7", height: "7", rx: "1", fill: "currentColor" }), _jsx("rect", { x: "14", y: "3", width: "7", height: "7", rx: "1", fill: "currentColor" }), _jsx("rect", { x: "14", y: "14", width: "7", height: "7", rx: "1", fill: "currentColor" }), _jsx("rect", { x: "3", y: "14", width: "7", height: "7", rx: "1", fill: "currentColor" })] }), label: 'PANEL DE CONTROL', permission: null },
    { id: 'productos', icon: _jsxs("svg", { width: "20", height: "20", viewBox: "0 0 24 24", fill: "none", children: [_jsx("rect", { x: "4", y: "7", width: "16", height: "11", rx: "2", stroke: "currentColor", strokeWidth: "2", fill: "none" }), _jsx("rect", { x: "7", y: "4", width: "10", height: "3", rx: "1.5", fill: "currentColor" })] }), label: 'PRODUCTOS', permission: 'productos' },
    { id: 'entradas', icon: _jsxs("svg", { width: "20", height: "20", viewBox: "0 0 24 24", fill: "none", children: [_jsx("path", { d: "M12 5v14M5 12h14", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round" }), _jsx("path", { d: "M12 5l-4 4M12 5l4 4", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round" })] }), label: 'ENTRADAS', permission: 'entradas' },
    { id: 'ventas', icon: _jsx("svg", { width: "20", height: "20", viewBox: "0 0 24 24", fill: "none", children: _jsx("path", { d: "M9 5l7 7-7 7", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round" }) }), label: 'VENTAS', permission: 'ventas' },
    { id: 'gastos', icon: _jsxs("svg", { width: "20", height: "20", viewBox: "0 0 24 24", fill: "none", children: [_jsx("circle", { cx: "12", cy: "12", r: "9", stroke: "currentColor", strokeWidth: "2", fill: "none" }), _jsx("path", { d: "M8 12h8", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round" })] }), label: 'GASTOS', permission: 'gastos' },
    { id: 'cotizacion', icon: _jsx("svg", { width: "20", height: "20", viewBox: "0 0 24 24", fill: "none", children: _jsx("path", { d: "M4 7h16M4 12h16M4 17h10", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round" }) }), label: 'COTIZACIÓN', permission: 'cotizaciones' },
    { id: 'devoluciones', icon: _jsx("svg", { width: "20", height: "20", viewBox: "0 0 24 24", fill: "none", children: _jsx("path", { d: "M9 14l-4-4 4-4M5 10h10a4 4 0 014 4v0", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round" }) }), label: 'DEVOLUCIONES', permission: null },
    { id: 'admin', icon: '👑', label: 'ADMINISTRACIÓN', requireAdmin: true },
];
export default function DashboardPage() {
    const navigate = useNavigate();
    const { user, logout } = useAuthStore();
    const { can, isAdmin, getRoleName } = usePermissions();
    const [search, setSearch] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');
    const [seccionId, setSeccionId] = useState(undefined);
    const [laboratorioId, setLaboratorioId] = useState(undefined);
    const [soloStockBajo, setSoloStockBajo] = useState(false);
    const [isNotificationPanelOpen, setIsNotificationPanelOpen] = useState(false);
    // Solicitar permisos de notificación al cargar el dashboard
    const { permission, requestPermission } = useNotificationPermission();
    const { unreadCount } = useInventoryNotifications();
    useEffect(() => {
        if (permission === 'default') {
            requestPermission();
        }
    }, [permission, requestPermission]);
    useEffect(() => {
        const t = setTimeout(() => setDebouncedSearch(search.trim()), 350);
        return () => clearTimeout(t);
    }, [search]);
    const productFilters = useMemo(() => ({
        nombre: debouncedSearch || undefined,
        id_seccion: seccionId,
        id_laboratorio: laboratorioId,
        stock_bajo: soloStockBajo ? true : undefined,
    }), [debouncedSearch, seccionId, laboratorioId, soloStockBajo]);
    const { data: productsData, isLoading: productsLoading } = useProducts(productFilters);
    const { data: secciones = [] } = useSecciones();
    const { data: laboratorios = [] } = useLaboratorios();
    const [activeView, setActiveView] = useState('panel');
    const [isProductModalOpen, setProductModalOpen] = useState(false);
    const [isEntradaModalOpen, setEntradaModalOpen] = useState(false);
    const [toast, setToast] = useState(null);
    const [isEditModalOpen, setEditModalOpen] = useState(false);
    const [editingProduct, setEditingProduct] = useState(null);
    const [isDeleteModalOpen, setDeleteModalOpen] = useState(false);
    const [deletingId, setDeletingId] = useState(null);
    const createProduct = useCreateProduct();
    const updateProduct = useUpdateProduct();
    const deleteProduct = useDeleteProduct();
    const createVenta = useCreateVenta();
    const createGasto = useCreateGasto();
    const crearEntrada = useCrearEntrada();
    const crearCotizacion = useCrearCotizacion();
    const convertirCotizacion = useConvertirCotizacionAVenta();
    const [isVentaModalOpen, setVentaModalOpen] = useState(false);
    const [isGastoModalOpen, setGastoModalOpen] = useState(false);
    const [isCotizacionModalOpen, setCotizacionModalOpen] = useState(false);
    // Control de sidebar en móvil
    const [sidebarExpanded, setSidebarExpanded] = useState(false);
    // Fecha actual para filtros de estadísticas
    const now = new Date();
    const currentMonth = now.getMonth() + 1;
    const currentYear = now.getFullYear();
    // Filtros de fecha para Ventas
    const [ventasMonth, setVentasMonth] = useState(currentMonth);
    const [ventasYear, setVentasYear] = useState(currentYear);
    // Filtros de fecha para Gastos
    const [gastosMonth, setGastosMonth] = useState(currentMonth);
    const [gastosYear, setGastosYear] = useState(currentYear);
    // Filtros de fecha para Entradas
    const [entradasMonth, setEntradasMonth] = useState(currentMonth);
    const [entradasYear, setEntradasYear] = useState(currentYear);
    const { data: ventasMes } = useVentasMes(ventasMonth, ventasYear, true);
    const { data: ventasAnio } = useVentasAnio(ventasYear, true);
    const { data: gastosMes } = useGastosMes(gastosMonth, gastosYear, true);
    const { data: gastosAnio } = useGastosAnio(gastosYear, true);
    const { data: entradasMes } = useEntradasMes(entradasMonth, entradasYear, true);
    const { data: entradasAnio } = useEntradasAnio(entradasYear, true);
    const { data: ventasLista = [] } = useVentasListado({ mes: ventasMonth, año: ventasYear, limit: 50 });
    const { data: gastosLista = [] } = useGastosListado({ mes: gastosMonth, año: gastosYear, limit: 50 });
    const { data: entradasLista = [] } = useEntradasListado({ mes: entradasMonth, año: entradasYear, limit: 50 });
    const { data: cotizacionesLista = [] } = useCotizacionesListado({ limit: 50 });
    const { data: cotizacionesStats } = useCotizacionEstadisticas(true);
    const yearOptions = useMemo(() => {
        const years = [];
        for (let y = currentYear; y >= currentYear - 5; y--)
            years.push(y);
        return years;
    }, [currentYear]);
    const handleLogout = () => {
        logout();
        navigate('/login');
    };
    const productos = Array.isArray(productsData?.items)
        ? productsData.items
        : Array.isArray(productsData)
            ? productsData
            : [];
    const visibleProductos = soloStockBajo ? productos.filter(p => p.cantidad <= 5) : productos;
    // Calcular métricas reales
    const totalProductos = productos.length;
    const stockBajo = productos.filter(p => p.cantidad <= 5).length;
    // Métricas con iconos coloridos (estilo primera imagen)
    const metrics = [
        {
            label: 'Total Productos',
            value: totalProductos.toString(),
            icon: _jsxs("svg", { width: "32", height: "32", viewBox: "0 0 24 24", fill: "none", children: [_jsx("rect", { x: "3", y: "6", width: "18", height: "15", rx: "2", fill: "#7c3aed" }), _jsx("path", { d: "M8 11h8M8 14h5", stroke: "#fff", strokeWidth: "2", strokeLinecap: "round" })] }),
            bgColor: '#ede9fe',
            iconColor: '#7c3aed',
        },
        {
            label: 'Stock Bajo',
            value: stockBajo.toString(),
            icon: _jsxs("svg", { width: "32", height: "32", viewBox: "0 0 24 24", fill: "none", children: [_jsx("path", { d: "M12 8v4m0 4h.01", stroke: "#f59e0b", strokeWidth: "2", strokeLinecap: "round" }), _jsx("circle", { cx: "12", cy: "12", r: "9", stroke: "#f59e0b", strokeWidth: "2", fill: "none" })] }),
            bgColor: '#fef3c7',
            iconColor: '#f59e0b',
        },
        {
            label: 'Laboratorios Activos',
            value: laboratorios.length.toString(),
            icon: _jsxs("svg", { width: "32", height: "32", viewBox: "0 0 24 24", fill: "none", children: [_jsx("rect", { x: "4", y: "6", width: "16", height: "12", rx: "2", fill: "#06b6d4" }), _jsx("path", { d: "M7 10h10M7 13h7", stroke: "#fff", strokeWidth: "2", strokeLinecap: "round" })] }),
            bgColor: '#cffafe',
            iconColor: '#06b6d4',
        },
        {
            label: 'Secciones Activas',
            value: secciones.length.toString(),
            icon: _jsxs("svg", { width: "32", height: "32", viewBox: "0 0 24 24", fill: "none", children: [_jsx("rect", { x: "4", y: "6", width: "16", height: "12", rx: "2", fill: "#f59e42" }), _jsx("path", { d: "M7 10h10M7 13h7", stroke: "#fff", strokeWidth: "2", strokeLinecap: "round" })] }),
            bgColor: '#fef3c7',
            iconColor: '#f59e42',
        },
    ];
    // Función para renderizar contenido según la vista activa
    const renderContent = () => {
        // Vista: PRODUCTOS
        if (activeView === 'productos') {
            return (_jsxs("div", { className: "dashboard-grid", children: [_jsx("div", { className: "dashboard-column", children: _jsxs("div", { className: "productos-view", children: [_jsxs("div", { className: "section-header", children: [_jsx("h2", { children: "\uD83C\uDF3F Productos Naturistas" }), can('productos', 'create') && (_jsx("button", { className: "add-btn", onClick: () => setProductModalOpen(true), children: "+ Nuevo Producto" }))] }), _jsxs("div", { className: "section-toolbar", children: [_jsx("div", { className: "search-bar", children: _jsx("input", { type: "search", value: search, onChange: (e) => setSearch(e.target.value), placeholder: "Buscar por nombre, ej. 'Moringa', 'Manzanilla'" }) }), _jsxs("div", { className: "filters", children: [_jsxs("select", { value: seccionId ?? '', onChange: (e) => setSeccionId(e.target.value ? Number(e.target.value) : undefined), children: [_jsx("option", { value: "", children: "Secci\u00F3n (todas)" }), secciones.map(s => (_jsx("option", { value: s.id_seccion, children: s.nombre_seccion }, s.id_seccion)))] }), _jsxs("select", { value: laboratorioId ?? '', onChange: (e) => setLaboratorioId(e.target.value ? Number(e.target.value) : undefined), children: [_jsx("option", { value: "", children: "Laboratorio (todos)" }), laboratorios.map(l => (_jsx("option", { value: l.id_laboratorio, children: l.nombre_laboratorio }, l.id_laboratorio)))] }), _jsxs("label", { className: "toggle-stock-bajo", children: [_jsx("input", { type: "checkbox", checked: soloStockBajo, onChange: (e) => setSoloStockBajo(e.target.checked) }), _jsx("span", { children: "Solo stock bajo" })] })] })] }), productsLoading ? (_jsx("p", { children: "Cargando productos..." })) : visibleProductos.length > 0 ? (_jsx("div", { className: "products-table", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "Nombre" }), _jsx("th", { children: "Stock" }), _jsx("th", { children: "Precio" }), _jsx("th", { children: "Total" }), _jsx("th", { children: "Estado" }), _jsx("th", { children: "Acciones" })] }) }), _jsx("tbody", { children: visibleProductos.map((producto) => {
                                                    const isLowStock = producto.cantidad <= 5;
                                                    const total = producto.precio * producto.cantidad;
                                                    return (_jsxs("tr", { className: isLowStock ? 'low-stock-row' : '', children: [_jsx("td", { children: producto.nombre }), _jsx("td", { className: isLowStock ? 'stock-alert' : '', children: producto.cantidad }), _jsxs("td", { children: ["$", producto.precio.toFixed(2)] }), _jsxs("td", { children: ["$", total.toFixed(2)] }), _jsx("td", { children: isLowStock ? (_jsx("span", { className: "badge badge-warning", children: "\u26A0\uFE0F Stock Bajo" })) : (_jsx("span", { className: "badge badge-success", children: "\u2713 Disponible" })) }), _jsxs("td", { className: "actions", children: [_jsx("button", { className: "btn-edit", title: "Editar", onClick: () => {
                                                                            setEditingProduct(producto);
                                                                            setEditModalOpen(true);
                                                                        }, children: "\u270F\uFE0F" }), _jsx("button", { className: "btn-delete", title: "Eliminar", onClick: () => {
                                                                            setDeletingId(producto.id);
                                                                            setDeleteModalOpen(true);
                                                                        }, children: "\uD83D\uDDD1\uFE0F" })] })] }, producto.id));
                                                }) })] }) })) : (_jsxs("div", { className: "empty-state", children: [_jsx("p", { children: "\uD83C\uDF31 No hay productos registrados" }), _jsx("button", { className: "add-btn", children: "+ Agregar primer producto" })] }))] }) }), _jsx("div", { className: "dashboard-column", children: isEditModalOpen && editingProduct ? (_jsx(Modal, { isOpen: isEditModalOpen, onClose: () => setEditModalOpen(false), title: "Editar Producto", width: 720, children: _jsx(ProductForm, { initialValues: editingProduct, loading: updateProduct.isPending, onCancel: () => setEditModalOpen(false), onSubmit: async (values) => {
                                    try {
                                        await updateProduct.mutateAsync({ id: editingProduct.id, data: values });
                                        setEditModalOpen(false);
                                        setEditingProduct(null);
                                        setActiveView('productos');
                                        setToast({ message: 'Producto actualizado con éxito', type: 'success' });
                                    }
                                    catch (e) {
                                        const msg = e?.response?.data?.detail || e?.message || 'Error al actualizar producto';
                                        setToast({ message: msg, type: 'error' });
                                    }
                                    finally {
                                        setTimeout(() => setToast(null), 2500);
                                    }
                                } }) })) : (_jsx("div", { className: "info-card", children: _jsx("p", { children: "Selecciona un producto para ver detalles o editar." }) })) })] }));
        }
        // Vista: ENTRADAS (Pedidos/Compras)
        if (activeView === 'entradas') {
            return (_jsxs("div", { className: "entradas-view", children: [_jsxs("div", { className: "section-header", children: [_jsx("h2", { children: "\uD83D\uDCE5 Entradas de Inventario" }), can('entradas', 'create') && (_jsx("button", { className: "add-btn", onClick: () => setEntradaModalOpen(true), children: "+ Nueva Entrada" }))] }), _jsx("div", { className: "section-toolbar", children: _jsxs("div", { className: "filters", children: [_jsx("select", { value: entradasMonth, onChange: (e) => setEntradasMonth(Number(e.target.value)), children: Array.from({ length: 12 }).map((_, idx) => (_jsxs("option", { value: idx + 1, children: ["Mes ", idx + 1] }, idx + 1))) }), _jsx("select", { value: entradasYear, onChange: (e) => setEntradasYear(Number(e.target.value)), children: yearOptions.map((y) => (_jsx("option", { value: y, children: y }, y))) })] }) }), _jsxs("div", { className: "stats-mini", children: [_jsxs("div", { className: "stat-mini-card", children: [_jsx("span", { className: "stat-mini-label", children: "Compras Mensuales" }), _jsxs("span", { className: "stat-mini-value", children: ["$", (entradasMes?.total_compras ?? 0).toFixed(2)] })] }), _jsxs("div", { className: "stat-mini-card", children: [_jsx("span", { className: "stat-mini-label", children: "Compras Anuales" }), _jsxs("span", { className: "stat-mini-value", children: ["$", (entradasAnio?.total_compras ?? 0).toFixed(2)] })] }), _jsxs("div", { className: "stat-mini-card", children: [_jsx("span", { className: "stat-mini-label", children: "Unidades Recibidas (mes)" }), _jsx("span", { className: "stat-mini-value", children: entradasMes?.total_unidades ?? 0 })] }), _jsxs("div", { className: "stat-mini-card", children: [_jsx("span", { className: "stat-mini-label", children: "# Entradas (mes)" }), _jsx("span", { className: "stat-mini-value", children: entradasMes?.cantidad_entradas ?? 0 })] })] }), _jsx("div", { className: "products-table", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "Fecha" }), _jsx("th", { children: "Lote" }), _jsx("th", { children: "Cantidad" }), _jsx("th", { children: "Proveedor" }), _jsx("th", { children: "Costo" }), _jsx("th", { children: "Total" }), _jsx("th", { children: "Acciones" })] }) }), _jsx("tbody", { children: entradasLista.length === 0 ? (_jsx("tr", { children: _jsx("td", { colSpan: 7, className: "text-center", children: "No hay registros de entradas" }) })) : (entradasLista.map((e) => (_jsxs("tr", { children: [_jsx("td", { children: new Date(e.fecha_entrada).toLocaleDateString() }), _jsxs("td", { children: ["#", e.id_lote] }), _jsx("td", { children: e.cantidad }), _jsx("td", { children: e.proveedor ?? '-' }), _jsxs("td", { children: ["$", (e.precio_compra_unitario ?? 0).toFixed(2)] }), _jsxs("td", { children: ["$", (e.precio_compra_total ?? 0).toFixed(2)] }), _jsx("td", { children: "-" })] }, e.id_entrada)))) })] }) })] }));
        }
        // Vista: VENTAS
        if (activeView === 'ventas') {
            return (_jsxs("div", { className: "ventas-view", children: [_jsxs("div", { className: "section-header", children: [_jsx("h2", { children: "\uD83D\uDCB0 Registro de Ventas" }), can('ventas', 'create') && (_jsx("button", { className: "add-btn", onClick: () => setVentaModalOpen(true), children: "+ Nueva Venta" }))] }), _jsx("div", { className: "section-toolbar", children: _jsxs("div", { className: "filters", children: [_jsx("select", { value: ventasMonth, onChange: (e) => setVentasMonth(Number(e.target.value)), children: Array.from({ length: 12 }).map((_, idx) => (_jsxs("option", { value: idx + 1, children: ["Mes ", idx + 1] }, idx + 1))) }), _jsx("select", { value: ventasYear, onChange: (e) => setVentasYear(Number(e.target.value)), children: yearOptions.map((y) => (_jsx("option", { value: y, children: y }, y))) })] }) }), _jsxs("div", { className: "stats-mini", children: [_jsxs("div", { className: "stat-mini-card", children: [_jsx("span", { className: "stat-mini-label", children: "Ventas Mensuales" }), _jsxs("span", { className: "stat-mini-value", children: ["$", (ventasMes?.total_ventas ?? 0).toFixed(2)] })] }), _jsxs("div", { className: "stat-mini-card", children: [_jsx("span", { className: "stat-mini-label", children: "Ventas Anuales" }), _jsxs("span", { className: "stat-mini-value", children: ["$", (ventasAnio?.total_ventas ?? 0).toFixed(2)] })] }), _jsxs("div", { className: "stat-mini-card", children: [_jsx("span", { className: "stat-mini-label", children: "Promedio Ticket (mes)" }), _jsxs("span", { className: "stat-mini-value", children: ["$", (ventasMes?.promedio_venta ?? 0).toFixed(2)] })] })] }), _jsx("div", { className: "products-table", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "Fecha" }), _jsx("th", { children: "Cliente" }), _jsx("th", { children: "Total" }), _jsx("th", { children: "Estado" })] }) }), _jsx("tbody", { children: ventasLista.length === 0 ? (_jsx("tr", { children: _jsx("td", { colSpan: 4, className: "text-center", children: "No hay registros de ventas" }) })) : (ventasLista.map((v) => (_jsxs("tr", { children: [_jsx("td", { children: new Date(v.fecha_venta).toLocaleDateString() }), _jsx("td", { children: v.cliente }), _jsxs("td", { children: ["$", v.total.toFixed(2)] }), _jsx("td", { children: v.estado })] }, v.id_venta)))) })] }) })] }));
        }
        // Vista: GASTOS
        if (activeView === 'gastos') {
            return (_jsxs("div", { className: "gastos-view", children: [_jsxs("div", { className: "section-header", children: [_jsx("h2", { children: "\uD83D\uDCB8 Control de Gastos" }), can('gastos', 'create') && (_jsx("button", { className: "add-btn", onClick: () => setGastoModalOpen(true), children: "+ Nuevo Gasto" }))] }), _jsx("div", { className: "section-toolbar", children: _jsxs("div", { className: "filters", children: [_jsx("select", { value: gastosMonth, onChange: (e) => setGastosMonth(Number(e.target.value)), children: Array.from({ length: 12 }).map((_, idx) => (_jsxs("option", { value: idx + 1, children: ["Mes ", idx + 1] }, idx + 1))) }), _jsx("select", { value: gastosYear, onChange: (e) => setGastosYear(Number(e.target.value)), children: yearOptions.map((y) => (_jsx("option", { value: y, children: y }, y))) })] }) }), _jsxs("div", { className: "stats-mini", children: [_jsxs("div", { className: "stat-mini-card", children: [_jsx("span", { className: "stat-mini-label", children: "Gastos Mensuales" }), _jsxs("span", { className: "stat-mini-value", children: ["$", (gastosMes?.total_gastos ?? 0).toFixed(2)] })] }), _jsxs("div", { className: "stat-mini-card", children: [_jsx("span", { className: "stat-mini-label", children: "Gastos Anuales" }), _jsxs("span", { className: "stat-mini-value", children: ["$", (gastosAnio?.total_gastos ?? 0).toFixed(2)] })] }), _jsxs("div", { className: "stat-mini-card", children: [_jsx("span", { className: "stat-mini-label", children: "# Registros (mes)" }), _jsx("span", { className: "stat-mini-value", children: gastosMes?.cantidad_gastos ?? 0 })] })] }), _jsx("div", { className: "products-table", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "Fecha" }), _jsx("th", { children: "Concepto" }), _jsx("th", { children: "Categor\u00EDa" }), _jsx("th", { children: "Monto" }), _jsx("th", { children: "M\u00E9todo Pago" })] }) }), _jsx("tbody", { children: gastosLista.length === 0 ? (_jsx("tr", { children: _jsx("td", { colSpan: 5, className: "text-center", children: "No hay registros de gastos" }) })) : (gastosLista.map((g) => (_jsxs("tr", { children: [_jsx("td", { children: new Date(g.fecha_gasto).toLocaleDateString() }), _jsx("td", { children: g.concepto }), _jsx("td", { children: g.categoria }), _jsxs("td", { children: ["$", g.monto.toFixed(2)] }), _jsx("td", { children: g.metodo_pago ?? '-' })] }, g.id_gasto)))) })] }) })] }));
        }
        // Vista: COTIZACIÓN
        if (activeView === 'cotizacion') {
            return (_jsxs("div", { className: "cotizacion-view", children: [_jsxs("div", { className: "section-header", children: [_jsx("h2", { children: "\uD83D\uDCCB Cotizaciones" }), can('cotizaciones', 'create') && (_jsx("button", { className: "add-btn", onClick: () => setCotizacionModalOpen(true), children: "+ Nueva Cotizaci\u00F3n" }))] }), _jsxs("div", { className: "stats-mini", children: [_jsxs("div", { className: "stat-mini-card", children: [_jsx("span", { className: "stat-mini-label", children: "Total Cotizaciones" }), _jsx("span", { className: "stat-mini-value", children: cotizacionesStats?.total_cotizaciones ?? 0 })] }), _jsxs("div", { className: "stat-mini-card", children: [_jsx("span", { className: "stat-mini-label", children: "Monto Cotizado" }), _jsxs("span", { className: "stat-mini-value", children: ["$", (cotizacionesStats?.total_monto_cotizado ?? 0).toFixed(2)] })] }), _jsxs("div", { className: "stat-mini-card", children: [_jsx("span", { className: "stat-mini-label", children: "Pendientes" }), _jsx("span", { className: "stat-mini-value", children: cotizacionesStats?.cotizaciones_pendientes ?? 0 })] }), _jsxs("div", { className: "stat-mini-card", children: [_jsx("span", { className: "stat-mini-label", children: "Tasa Conversi\u00F3n" }), _jsxs("span", { className: "stat-mini-value", children: [((cotizacionesStats?.tasa_conversion ?? 0) * 100).toFixed(1), "%"] })] })] }), _jsx("div", { className: "products-table", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "N\u00B0 Cotizaci\u00F3n" }), _jsx("th", { children: "Fecha" }), _jsx("th", { children: "Cliente" }), _jsx("th", { children: "Total" }), _jsx("th", { children: "Estado" }), _jsx("th", { children: "Acciones" })] }) }), _jsx("tbody", { children: cotizacionesLista.length === 0 ? (_jsx("tr", { children: _jsx("td", { colSpan: 6, className: "text-center", children: "No hay cotizaciones registradas" }) })) : (cotizacionesLista.map((cot) => (_jsxs("tr", { children: [_jsx("td", { children: cot.numero_cotizacion }), _jsx("td", { children: new Date(cot.fecha_cotizacion).toLocaleDateString() }), _jsxs("td", { children: ["Cliente #", cot.id_cliente] }), _jsxs("td", { children: ["$", cot.total.toFixed(2)] }), _jsx("td", { children: _jsx("span", { className: `badge ${cot.estado === 'Pendiente' ? 'badge-warning' : cot.estado === 'Aprobada' ? 'badge-success' : 'badge-error'}`, children: cot.estado }) }), _jsx("td", { children: cot.estado === 'Aprobada' && (_jsx("button", { className: "btn-primary", style: { fontSize: '0.8rem', padding: '0.3rem 0.6rem' }, onClick: async () => {
                                                        try {
                                                            await convertirCotizacion.mutateAsync(cot.id_cotizacion);
                                                            setToast({ message: 'Cotización convertida a venta', type: 'success' });
                                                        }
                                                        catch (e) {
                                                            setToast({ message: e?.response?.data?.detail || 'Error al convertir', type: 'error' });
                                                        }
                                                        finally {
                                                            setTimeout(() => setToast(null), 2500);
                                                        }
                                                    }, children: "Convertir a Venta" })) })] }, cot.id_cotizacion)))) })] }) })] }));
        }
        // Vista: DEVOLUCIONES
        if (activeView === 'devoluciones') {
            return (_jsxs("div", { className: "devoluciones-view", children: [_jsxs("div", { className: "section-header", children: [_jsx("h2", { children: "\u21A9\uFE0F Devoluciones" }), _jsx("button", { className: "add-btn", children: "+ Nueva Devoluci\u00F3n" })] }), _jsx("div", { className: "info-card", children: _jsx("p", { children: "Registra las devoluciones de productos (clientes o proveedores)" }) }), _jsx("div", { className: "products-table", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "Fecha" }), _jsx("th", { children: "Tipo" }), _jsx("th", { children: "Cliente/Proveedor" }), _jsx("th", { children: "Producto" }), _jsx("th", { children: "Cantidad" }), _jsx("th", { children: "Motivo" }), _jsx("th", { children: "Acciones" })] }) }), _jsx("tbody", { children: _jsx("tr", { children: _jsx("td", { colSpan: 7, className: "text-center", children: "No hay registros de devoluciones" }) }) })] }) })] }));
        }
        // Vista: ADMINISTRACI�N  
        if (activeView === 'admin') {
            return _jsx(AdminPanelPage, {});
        }
        // Vista por defecto: Panel de control
        return (_jsx(_Fragment, { children: _jsxs("div", { className: "dashboard-grid", children: [_jsxs("div", { className: "dashboard-column", children: [_jsxs("div", { className: "dashboard-section", children: [_jsx("h2", { children: "Panel de Control" }), _jsx("div", { className: "welcome-card", children: _jsxs("div", { className: "welcome-content", children: [_jsx("div", { className: "welcome-icon", children: _jsxs("svg", { width: "48", height: "48", viewBox: "0 0 24 24", fill: "none", children: [_jsx("circle", { cx: "12", cy: "12", r: "10", fill: "#2E8B57" }), _jsx("path", { d: "M8 12l2 2 4-4", stroke: "#fff", strokeWidth: "2", strokeLinecap: "round" })] }) }), _jsxs("div", { className: "welcome-text", children: [_jsxs("h3", { children: ["\u00A1Bienvenido, ", user?.nombre, "!"] }), _jsx("p", { children: "Gestiona tu inventario de forma eficiente y profesional." })] })] }) })] }), _jsxs("div", { className: "dashboard-section", children: [_jsx("div", { className: "section-header", children: _jsx("h2", { children: "Actividad Reciente" }) }), _jsxs("div", { className: "activity-card", children: [_jsxs("div", { className: "activity-item", children: [_jsx("div", { className: "activity-icon", children: "\uD83D\uDCE6" }), _jsxs("div", { className: "activity-text", children: [_jsx("p", { className: "activity-title", children: "Producto agregado" }), _jsx("p", { className: "activity-time", children: "Hace 2 horas" })] })] }), _jsxs("div", { className: "activity-item", children: [_jsx("div", { className: "activity-icon", children: "\u2705" }), _jsxs("div", { className: "activity-text", children: [_jsx("p", { className: "activity-title", children: "Venta realizada" }), _jsx("p", { className: "activity-time", children: "Hace 4 horas" })] })] }), _jsxs("div", { className: "activity-item", children: [_jsx("div", { className: "activity-icon", children: "\u26A0\uFE0F" }), _jsxs("div", { className: "activity-text", children: [_jsx("p", { className: "activity-title", children: "Stock bajo detectado" }), _jsx("p", { className: "activity-time", children: "Hace 1 d\u00EDa" })] })] })] })] })] }), _jsx("div", { className: "dashboard-column", children: _jsxs("div", { className: "dashboard-section", children: [_jsxs("div", { className: "section-header", children: [_jsx("h2", { children: "Productos Destacados" }), _jsx("button", { className: "view-all-btn", children: "Ver todos \u2192" })] }), productsLoading ? (_jsx("p", { children: "Cargando productos..." })) : productos.length > 0 ? (_jsx("div", { className: "products-list", children: productos.slice(0, 6).map((producto) => {
                                        const isLowStock = producto.cantidad <= 5;
                                        return (_jsxs("div", { className: `product-card compact${isLowStock ? ' low-stock' : ''}`, children: [_jsxs("div", { className: "product-card-header", children: [_jsx("span", { className: "product-icon", children: _jsxs("svg", { width: "24", height: "24", viewBox: "0 0 24 24", fill: "none", children: [_jsx("rect", { x: "4", y: "7", width: "16", height: "11", rx: "2", fill: "#2E8B57" }), _jsx("rect", { x: "7", y: "4", width: "10", height: "3", rx: "1.5", fill: "#86c8bc" })] }) }), _jsx("h3", { children: producto.nombre })] }), _jsxs("div", { className: "product-info", children: [_jsxs("span", { className: `cantidad${isLowStock ? ' alert' : ''}`, children: ["Stock: ", producto.cantidad, isLowStock && _jsx("span", { className: "alert-icon", children: "\u26A0\uFE0F" })] }), _jsxs("span", { className: "precio", children: ["$", producto.precio] })] })] }, producto.id));
                                    }) })) : (_jsx("p", { children: "No hay productos disponibles" }))] }) })] }) }));
    };
    return (_jsxs("div", { className: `dashboard-layout${sidebarExpanded ? ' sidebar-expanded' : ''}`, children: [_jsxs("aside", { className: `sidebar${sidebarExpanded ? ' expanded' : ''}`, children: [_jsx("div", { className: "sidebar-logo", children: _jsx("img", { src: "/images/logo.png", alt: "Logo" }) }), _jsx("nav", { className: "sidebar-menu", role: "navigation", "aria-label": "Men\u00FA principal", children: sidebarMenu.map((item) => {
                            // Verificar permisos: si tiene permission y no tiene el permiso, no mostrar
                            if (item.permission && !can(item.permission, 'read')) {
                                return null;
                            }
                            // Si requiere ser admin y no lo es, no mostrar
                            if (item.requireAdmin && !isAdmin()) {
                                return null;
                            }
                            // Tooltip preview for Productos
                            let tooltipContent = null;
                            if (item.id === 'productos') {
                                tooltipContent = (_jsxs("div", { className: "sidebar-tooltip", children: [_jsx("div", { className: "tooltip-title", children: "Productos" }), _jsxs("div", { className: "tooltip-count", children: ["Total: ", _jsx("b", { children: productos.length })] }), productos.length > 0 && (_jsx("div", { className: "tooltip-list", children: productos.slice(0, 2).map(p => (_jsxs("div", { className: "tooltip-product", children: [_jsx("span", { className: "tp-name", children: p.nombre }), _jsxs("span", { className: "tp-stock", children: ["Stock: ", p.cantidad] })] }, p.id))) }))] }));
                            }
                            return (_jsxs("div", { className: `sidebar-item ${activeView === item.id ? 'active' : ''}`, title: item.label, onClick: () => {
                                    // Si es el botón de admin, cambiar la vista a 'admin'
                                    if (item.id === 'admin') {
                                        setActiveView('admin');
                                    }
                                    else {
                                        setActiveView(item.id);
                                    }
                                }, children: [_jsx("span", { className: "sidebar-icon", "aria-hidden": "true", children: item.icon }), _jsx("span", { className: "sidebar-label", children: item.label }), tooltipContent && (_jsx("div", { className: "sidebar-tooltip-container", children: tooltipContent }))] }, item.label));
                        }) })] }), _jsxs("div", { className: `dashboard-main-area${sidebarExpanded ? ' expanded' : ''}`, children: [_jsx("header", { className: "dashboard-header", children: _jsxs("div", { className: "header-content", children: [_jsxs("div", { className: "row", style: { alignItems: 'center', gap: '.5rem' }, children: [_jsx("button", { className: "sidebar-toggle-btn", "aria-label": sidebarExpanded ? 'Contraer menú' : 'Expandir menú', onClick: () => setSidebarExpanded(v => !v), style: {
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                width: 36,
                                                height: 36,
                                                borderRadius: 8,
                                                border: '1px solid #e2e8f0',
                                                background: '#fff',
                                                cursor: 'pointer'
                                            }, children: _jsx("svg", { width: "18", height: "18", viewBox: "0 0 24 24", fill: "none", children: _jsx("path", { d: "M4 7h16M4 12h16M4 17h16", stroke: "#2E8B57", strokeWidth: "2", strokeLinecap: "round" }) }) }), _jsx("h1", { style: { margin: 0 }, children: "Sistema de Inventario" })] }), _jsxs("div", { className: "user-info", children: [_jsx("div", { className: "notification-bell-wrapper", style: { position: 'relative', marginRight: '1rem' }, children: _jsxs("button", { className: "notification-bell-btn", onClick: () => setIsNotificationPanelOpen(!isNotificationPanelOpen), style: {
                                                    background: 'none',
                                                    border: 'none',
                                                    cursor: 'pointer',
                                                    fontSize: '1.5rem',
                                                    position: 'relative'
                                                }, title: "Notificaciones", children: ["\uD83D\uDD14", unreadCount > 0 && (_jsx("span", { className: "notification-badge", style: {
                                                            position: 'absolute',
                                                            top: '-5px',
                                                            right: '-5px',
                                                            background: '#ef4444',
                                                            color: 'white',
                                                            borderRadius: '50%',
                                                            width: '18px',
                                                            height: '18px',
                                                            fontSize: '0.7rem',
                                                            display: 'flex',
                                                            alignItems: 'center',
                                                            justifyContent: 'center',
                                                            fontWeight: 'bold'
                                                        }, children: unreadCount > 9 ? '9+' : unreadCount }))] }) }), _jsxs("span", { className: "user-name", children: [getRoleName() === 'admin' && '👑 ', getRoleName() === 'gestor' && '� ', getRoleName() === 'viewer' && '�️ ', user?.nombre || 'Usuario', " (", getRoleName(), ")"] }), isAdmin() && (_jsx("button", { onClick: () => navigate('/admin'), className: "admin-button", style: {
                                                marginRight: '0.5rem',
                                                padding: '0.5rem 1rem',
                                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                                color: 'white',
                                                border: 'none',
                                                borderRadius: '6px',
                                                cursor: 'pointer',
                                                fontWeight: '600'
                                            }, children: "\uD83D\uDC51 Admin" })), _jsx("button", { onClick: handleLogout, className: "logout-button", children: "Cerrar Sesi\u00F3n" })] })] }) }), _jsxs("main", { className: "dashboard-main", children: [activeView === 'panel' && (_jsx("div", { className: "metrics-row", children: metrics.map((m) => (_jsxs("div", { className: "metric-card modern", style: { backgroundColor: m.bgColor }, children: [_jsx("div", { className: "metric-icon-circle", style: { backgroundColor: m.iconColor }, children: m.icon }), _jsxs("div", { className: "metric-info", children: [_jsx("span", { className: "metric-label", children: m.label }), _jsx("span", { className: "metric-value", children: m.value })] })] }, m.label))) })), renderContent()] }), _jsx(Modal, { isOpen: isProductModalOpen, onClose: () => setProductModalOpen(false), title: "Nuevo Producto", width: 720, children: _jsx(ProductForm, { loading: createProduct.isPending, onCancel: () => setProductModalOpen(false), onSubmit: async (values) => {
                                try {
                                    await createProduct.mutateAsync(values);
                                    setProductModalOpen(false);
                                    setActiveView('productos');
                                    setToast({ message: 'Producto guardado con éxito', type: 'success' });
                                }
                                catch (e) {
                                    const msg = e?.response?.data?.detail || e?.message || 'Error al crear producto';
                                    setToast({ message: msg, type: 'error' });
                                }
                                finally {
                                    setTimeout(() => setToast(null), 2500);
                                }
                            } }) }), _jsx(Modal, { isOpen: isVentaModalOpen, onClose: () => setVentaModalOpen(false), title: "Nueva Venta", width: 820, children: _jsx(VentaForm, { loading: createVenta.isPending, onCancel: () => setVentaModalOpen(false), onSubmit: async (values) => {
                                try {
                                    await createVenta.mutateAsync({
                                        id_cliente: values.id_cliente,
                                        metodo_pago: values.metodo_pago,
                                        detalles: values.detalles.map(d => ({
                                            id_lote: d.id_lote,
                                            cantidad: d.cantidad,
                                            precio_unitario: d.precio_unitario,
                                        }))
                                    });
                                    setVentaModalOpen(false);
                                    setToast({ message: 'Venta registrada con éxito', type: 'success' });
                                }
                                catch (e) {
                                    const msg = e?.response?.data?.detail || e?.message || 'Error al crear venta';
                                    setToast({ message: msg, type: 'error' });
                                }
                                finally {
                                    setTimeout(() => setToast(null), 2500);
                                }
                            } }) }), _jsx(Modal, { isOpen: isGastoModalOpen, onClose: () => setGastoModalOpen(false), title: "Nuevo Gasto", width: 720, children: _jsxs("div", { className: "form-grid", children: [_jsxs("div", { className: "form-row", children: [_jsx("label", { children: "Fecha" }), _jsx("input", { id: "gasto-fecha", type: "datetime-local", defaultValue: new Date().toISOString().slice(0, 16) })] }), _jsxs("div", { className: "form-row", children: [_jsx("label", { children: "Concepto" }), _jsx("input", { id: "gasto-concepto", type: "text" })] }), _jsxs("div", { className: "form-row", children: [_jsx("label", { children: "Categor\u00EDa" }), _jsx("input", { id: "gasto-categoria", type: "text", defaultValue: "Otros" })] }), _jsxs("div", { className: "form-row", children: [_jsx("label", { children: "Monto" }), _jsx("input", { id: "gasto-monto", type: "number", min: 0, step: "0.01" })] }), _jsxs("div", { className: "form-row", children: [_jsx("label", { children: "M\u00E9todo de pago" }), _jsx("input", { id: "gasto-metodo", type: "text", defaultValue: "Efectivo" })] }), _jsx("div", { className: "form-actions", children: _jsx("button", { className: "add-btn", onClick: async () => {
                                            const fecha_gasto = document.getElementById('gasto-fecha').value;
                                            const concepto = document.getElementById('gasto-concepto').value;
                                            const categoria = document.getElementById('gasto-categoria').value;
                                            const monto = Number(document.getElementById('gasto-monto').value);
                                            const metodo_pago = document.getElementById('gasto-metodo').value;
                                            try {
                                                await createGasto.mutateAsync({ fecha_gasto, concepto, categoria, monto, metodo_pago });
                                                setGastoModalOpen(false);
                                                setToast({ message: 'Gasto creado', type: 'success' });
                                            }
                                            catch (e) {
                                                setToast({ message: e?.response?.data?.detail || e?.message || 'Error al crear gasto', type: 'error' });
                                            }
                                            finally {
                                                setTimeout(() => setToast(null), 2500);
                                            }
                                        }, children: "Crear" }) })] }) }), _jsx(Modal, { isOpen: isEntradaModalOpen, onClose: () => setEntradaModalOpen(false), title: "Registrar Entrada", width: 720, children: _jsx(EntradaForm, { loading: crearEntrada.isPending, onCancel: () => setEntradaModalOpen(false), onSubmit: async (values) => {
                                try {
                                    await crearEntrada.mutateAsync({
                                        id_lote: values.id_lote,
                                        cantidad: values.cantidad,
                                        precio_compra_unitario: values.costo,
                                        fecha_entrada: new Date(values.fecha).toISOString(),
                                        proveedor: values.proveedor,
                                        observaciones: values.observaciones,
                                    });
                                    setEntradaModalOpen(false);
                                    setToast({ message: 'Entrada registrada con éxito', type: 'success' });
                                }
                                catch (e) {
                                    const msg = e?.response?.data?.detail || e?.message || 'Error al registrar entrada';
                                    setToast({ message: msg, type: 'error' });
                                }
                                finally {
                                    setTimeout(() => setToast(null), 2500);
                                }
                            } }) }), _jsx(Modal, { isOpen: isCotizacionModalOpen, onClose: () => setCotizacionModalOpen(false), title: "Nueva Cotizaci\u00F3n", width: 720, children: _jsxs("div", { className: "form-grid", children: [_jsxs("div", { className: "form-row", children: [_jsx("label", { children: "ID Cliente *" }), _jsx("input", { id: "cot-id-cliente", type: "number", min: 1, defaultValue: 1 })] }), _jsxs("div", { className: "form-row", children: [_jsx("label", { children: "ID Producto *" }), _jsx("input", { id: "cot-id-producto", type: "number", min: 1 })] }), _jsxs("div", { className: "form-row", children: [_jsx("label", { children: "Cantidad *" }), _jsx("input", { id: "cot-cantidad", type: "number", min: 1, defaultValue: 1 })] }), _jsxs("div", { className: "form-row", children: [_jsx("label", { children: "Precio Unitario *" }), _jsx("input", { id: "cot-precio", type: "number", min: 0, step: "0.01", defaultValue: 0 })] }), _jsxs("div", { className: "form-row", children: [_jsx("label", { children: "Descuento" }), _jsx("input", { id: "cot-descuento", type: "number", min: 0, step: "0.01", defaultValue: 0 })] }), _jsxs("div", { className: "form-row", children: [_jsx("label", { children: "Impuestos" }), _jsx("input", { id: "cot-impuestos", type: "number", min: 0, step: "0.01", defaultValue: 0 })] }), _jsxs("div", { className: "form-row form-field-full", children: [_jsx("label", { children: "Observaciones" }), _jsx("textarea", { id: "cot-observaciones", rows: 3 })] }), _jsxs("div", { className: "form-actions", children: [_jsx("button", { className: "btn-outline", onClick: () => setCotizacionModalOpen(false), children: "Cancelar" }), _jsx("button", { className: "add-btn", onClick: async () => {
                                                const id_cliente = Number(document.getElementById('cot-id-cliente').value);
                                                const id_producto = Number(document.getElementById('cot-id-producto').value);
                                                const cantidad = Number(document.getElementById('cot-cantidad').value);
                                                const precio_unitario = Number(document.getElementById('cot-precio').value);
                                                const descuento = Number(document.getElementById('cot-descuento').value);
                                                const impuestos = Number(document.getElementById('cot-impuestos').value);
                                                const observaciones = document.getElementById('cot-observaciones').value;
                                                try {
                                                    await crearCotizacion.mutateAsync({
                                                        id_cliente,
                                                        descuento,
                                                        impuestos,
                                                        observaciones,
                                                        detalles: [{ id_producto, cantidad, precio_unitario }]
                                                    });
                                                    setCotizacionModalOpen(false);
                                                    setToast({ message: 'Cotización creada con éxito', type: 'success' });
                                                }
                                                catch (e) {
                                                    setToast({ message: e?.response?.data?.detail || e?.message || 'Error al crear cotización', type: 'error' });
                                                }
                                                finally {
                                                    setTimeout(() => setToast(null), 2500);
                                                }
                                            }, children: "Crear Cotizaci\u00F3n" })] })] }) }), _jsx(Modal, { isOpen: isEditModalOpen, onClose: () => setEditModalOpen(false), title: "Editar Producto", width: 720, children: editingProduct && (_jsx(ProductForm, { initialValues: editingProduct, loading: updateProduct.isPending, onCancel: () => setEditModalOpen(false), onSubmit: async (values) => {
                                try {
                                    await updateProduct.mutateAsync({ id: editingProduct.id, data: values });
                                    setEditModalOpen(false);
                                    setEditingProduct(null);
                                    setActiveView('productos');
                                    setToast({ message: 'Producto actualizado con éxito', type: 'success' });
                                }
                                catch (e) {
                                    const msg = e?.response?.data?.detail || e?.message || 'Error al actualizar producto';
                                    setToast({ message: msg, type: 'error' });
                                }
                                finally {
                                    setTimeout(() => setToast(null), 2500);
                                }
                            } })) }), _jsx(Modal, { isOpen: isDeleteModalOpen, onClose: () => setDeleteModalOpen(false), title: "Confirmar eliminaci\u00F3n", width: 520, children: _jsxs("div", { className: "confirm-body", children: [_jsx("p", { children: "\u00BFSeguro que deseas eliminar este producto? Esta acci\u00F3n no se puede deshacer." }), _jsxs("div", { className: "confirm-actions", children: [_jsx("button", { className: "btn-outline", onClick: () => setDeleteModalOpen(false), children: "Cancelar" }), _jsx("button", { className: "btn-danger", onClick: async () => {
                                                try {
                                                    if (deletingId != null) {
                                                        await deleteProduct.mutateAsync(deletingId);
                                                    }
                                                    setToast({ message: 'Producto eliminado con éxito', type: 'success' });
                                                }
                                                catch (e) {
                                                    const msg = e?.response?.data?.detail || e?.message || 'Error al eliminar producto';
                                                    setToast({ message: msg, type: 'error' });
                                                }
                                                finally {
                                                    setDeleteModalOpen(false);
                                                    setDeletingId(null);
                                                    setTimeout(() => setToast(null), 2500);
                                                }
                                            }, disabled: deleteProduct.isPending, children: deleteProduct.isPending ? 'Eliminando…' : 'Eliminar' })] })] }) })] }), toast && (_jsx("div", { className: `toast ${toast.type === 'error' ? 'toast-error' : 'toast-success'}`, children: toast.message })), isNotificationPanelOpen && (_jsx(NotificationPanel, { onClose: () => setIsNotificationPanelOpen(false) }))] }));
}
