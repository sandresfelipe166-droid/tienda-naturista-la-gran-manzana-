import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useMemo } from 'react';
import { useProducts } from '@/hooks/useProducts';
import { useLotes } from '@/hooks/useLotes';
export default function VentaForm({ onSubmit, onCancel, loading }) {
    const [id_cliente, setIdCliente] = useState(1);
    const [metodo_pago, setMetodoPago] = useState('Efectivo');
    const [detalles, setDetalles] = useState([]);
    // Estado para agregar nuevo item
    const [nuevoProductoId, setNuevoProductoId] = useState(0);
    const [nuevoLoteId, setNuevoLoteId] = useState(0);
    const [nuevaCantidad, setNuevaCantidad] = useState(1);
    const [nuevoPrecio, setNuevoPrecio] = useState(0);
    const [errors, setErrors] = useState({});
    // Obtener productos
    const { data: productosData } = useProducts({});
    const productos = Array.isArray(productosData?.items) ? productosData.items : [];
    // Obtener lotes del producto seleccionado para el nuevo item
    const { data: lotes = [] } = useLotes(nuevoProductoId > 0 ? nuevoProductoId : undefined);
    const productoSeleccionado = productos.find(p => p.id === nuevoProductoId);
    const loteSeleccionado = lotes.find(l => l.id_lote === nuevoLoteId);
    const isValid = useMemo(() => {
        const e = {};
        if (id_cliente <= 0)
            e.id_cliente = 'Cliente requerido';
        if (!metodo_pago.trim())
            e.metodo_pago = 'Método de pago requerido';
        if (detalles.length === 0)
            e.detalles = 'Debe agregar al menos un producto';
        setErrors(e);
        return Object.keys(e).length === 0;
    }, [id_cliente, metodo_pago, detalles]);
    const agregarDetalle = () => {
        if (nuevoProductoId <= 0 || nuevoLoteId <= 0 || nuevaCantidad <= 0 || nuevoPrecio < 0) {
            setErrors({ nuevo_item: 'Complete todos los campos del producto' });
            return;
        }
        if (loteSeleccionado && nuevaCantidad > loteSeleccionado.cantidad_disponible) {
            setErrors({ nuevo_item: `Stock insuficiente. Disponible: ${loteSeleccionado.cantidad_disponible}` });
            return;
        }
        const nuevoDetalle = {
            id_lote: nuevoLoteId,
            cantidad: nuevaCantidad,
            precio_unitario: nuevoPrecio,
            producto_nombre: productoSeleccionado?.nombre,
            lote_numero: loteSeleccionado?.numero_lote,
            stock_disponible: loteSeleccionado?.cantidad_disponible,
        };
        setDetalles([...detalles, nuevoDetalle]);
        // Reset form
        setNuevoProductoId(0);
        setNuevoLoteId(0);
        setNuevaCantidad(1);
        setNuevoPrecio(0);
        setErrors({});
    };
    const eliminarDetalle = (index) => {
        setDetalles(detalles.filter((_, i) => i !== index));
    };
    const calcularTotal = () => {
        return detalles.reduce((sum, d) => sum + (d.cantidad * d.precio_unitario), 0);
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!isValid || loading)
            return;
        await onSubmit({ id_cliente, metodo_pago, detalles });
    };
    return (_jsxs("form", { className: "form", onSubmit: handleSubmit, children: [_jsxs("div", { className: "form-grid", children: [_jsxs("div", { className: "form-field", children: [_jsx("label", { children: "ID Cliente *" }), _jsx("input", { type: "number", value: id_cliente, onChange: (e) => setIdCliente(Number(e.target.value)), min: 1 }), errors.id_cliente && _jsx("span", { className: "form-error", children: errors.id_cliente })] }), _jsxs("div", { className: "form-field", children: [_jsx("label", { children: "M\u00E9todo de Pago *" }), _jsxs("select", { value: metodo_pago, onChange: (e) => setMetodoPago(e.target.value), children: [_jsx("option", { value: "Efectivo", children: "Efectivo" }), _jsx("option", { value: "Tarjeta", children: "Tarjeta" }), _jsx("option", { value: "Transferencia", children: "Transferencia" }), _jsx("option", { value: "Cr\u00E9dito", children: "Cr\u00E9dito" })] }), errors.metodo_pago && _jsx("span", { className: "form-error", children: errors.metodo_pago })] }), _jsx("div", { className: "form-field form-field-full", style: { marginTop: '1rem', borderTop: '2px solid #e5e7eb', paddingTop: '1rem' }, children: _jsx("h3", { style: { marginBottom: '0.5rem', fontSize: '1rem', fontWeight: 600 }, children: "Agregar Productos" }) }), _jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Producto" }), _jsxs("select", { value: nuevoProductoId, onChange: (e) => {
                                    setNuevoProductoId(Number(e.target.value));
                                    setNuevoLoteId(0);
                                }, children: [_jsx("option", { value: 0, children: "-- Selecciona un producto --" }), productos.map((p) => (_jsxs("option", { value: p.id, children: [p.nombre, " (Stock: ", p.cantidad, ")"] }, p.id)))] })] }), _jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Lote" }), _jsxs("select", { value: nuevoLoteId, onChange: (e) => setNuevoLoteId(Number(e.target.value)), disabled: nuevoProductoId <= 0, children: [_jsx("option", { value: 0, children: "-- Selecciona un lote --" }), lotes.map((lote) => (_jsxs("option", { value: lote.id_lote, children: [lote.numero_lote, " (Disp: ", lote.cantidad_disponible, ", $", lote.precio_compra.toFixed(2), ")"] }, lote.id_lote)))] })] }), _jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Cantidad" }), _jsx("input", { type: "number", value: nuevaCantidad, onChange: (e) => setNuevaCantidad(Number(e.target.value)), min: 1, disabled: nuevoLoteId <= 0 })] }), _jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Precio Unitario" }), _jsx("input", { type: "number", value: nuevoPrecio, onChange: (e) => setNuevoPrecio(Number(e.target.value)), min: 0, step: "0.01", disabled: nuevoLoteId <= 0 })] }), _jsxs("div", { className: "form-field form-field-full", children: [errors.nuevo_item && _jsx("span", { className: "form-error", children: errors.nuevo_item }), _jsx("button", { type: "button", className: "btn-primary", onClick: agregarDetalle, disabled: nuevoProductoId <= 0 || nuevoLoteId <= 0, style: { width: '100%', marginTop: '0.5rem' }, children: "\u2795 Agregar a la Venta" })] }), detalles.length > 0 && (_jsxs("div", { className: "form-field form-field-full", style: { marginTop: '1rem' }, children: [_jsx("h3", { style: { marginBottom: '0.5rem', fontSize: '1rem', fontWeight: 600 }, children: "Productos en la Venta" }), _jsx("div", { style: { border: '1px solid #e5e7eb', borderRadius: '8px', overflow: 'hidden' }, children: _jsxs("table", { style: { width: '100%', fontSize: '0.85rem' }, children: [_jsx("thead", { style: { backgroundColor: '#f9fafb' }, children: _jsxs("tr", { children: [_jsx("th", { style: { padding: '0.5rem', textAlign: 'left' }, children: "Producto" }), _jsx("th", { style: { padding: '0.5rem', textAlign: 'left' }, children: "Lote" }), _jsx("th", { style: { padding: '0.5rem', textAlign: 'center' }, children: "Cant." }), _jsx("th", { style: { padding: '0.5rem', textAlign: 'right' }, children: "Precio" }), _jsx("th", { style: { padding: '0.5rem', textAlign: 'right' }, children: "Subtotal" }), _jsx("th", { style: { padding: '0.5rem', textAlign: 'center' }, children: "Acci\u00F3n" })] }) }), _jsxs("tbody", { children: [detalles.map((detalle, idx) => (_jsxs("tr", { style: { borderTop: '1px solid #e5e7eb' }, children: [_jsx("td", { style: { padding: '0.5rem' }, children: detalle.producto_nombre }), _jsx("td", { style: { padding: '0.5rem' }, children: detalle.lote_numero }), _jsx("td", { style: { padding: '0.5rem', textAlign: 'center' }, children: detalle.cantidad }), _jsxs("td", { style: { padding: '0.5rem', textAlign: 'right' }, children: ["$", detalle.precio_unitario.toFixed(2)] }), _jsxs("td", { style: { padding: '0.5rem', textAlign: 'right' }, children: ["$", (detalle.cantidad * detalle.precio_unitario).toFixed(2)] }), _jsx("td", { style: { padding: '0.5rem', textAlign: 'center' }, children: _jsx("button", { type: "button", onClick: () => eliminarDetalle(idx), style: {
                                                                    background: 'none',
                                                                    border: 'none',
                                                                    cursor: 'pointer',
                                                                    fontSize: '1.2rem',
                                                                    color: '#dc2626'
                                                                }, title: "Eliminar", children: "\uD83D\uDDD1\uFE0F" }) })] }, idx))), _jsxs("tr", { style: { backgroundColor: '#f0fdf4', fontWeight: 'bold', borderTop: '2px solid #10b981' }, children: [_jsx("td", { colSpan: 4, style: { padding: '0.75rem', textAlign: 'right' }, children: "TOTAL:" }), _jsxs("td", { style: { padding: '0.75rem', textAlign: 'right', fontSize: '1.1rem' }, children: ["$", calcularTotal().toFixed(2)] }), _jsx("td", {})] })] })] }) })] })), errors.detalles && _jsx("span", { className: "form-error", children: errors.detalles })] }), _jsxs("div", { className: "form-actions", children: [onCancel && (_jsx("button", { type: "button", className: "btn-outline", onClick: onCancel, disabled: loading, children: "Cancelar" })), _jsx("button", { type: "submit", className: "btn-primary", disabled: !isValid || loading, children: loading ? 'Procesando…' : `Registrar Venta - $${calcularTotal().toFixed(2)}` })] })] }));
}
