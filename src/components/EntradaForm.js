import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useMemo, useState } from 'react';
import { useProducts } from '@/hooks/useProducts';
import { useLotes } from '@/hooks/useLotes';
const initial = {
    fecha: new Date().toISOString().slice(0, 10),
    id_producto: 0,
    id_lote: 0,
    cantidad: 1,
    proveedor: '',
    costo: 0,
    observaciones: '',
};
export default function EntradaForm({ onSubmit, onCancel, loading }) {
    const [values, setValues] = useState(initial);
    const [errors, setErrors] = useState({});
    // Obtener todos los productos activos
    const { data: productosData } = useProducts({});
    const productos = Array.isArray(productosData?.items) ? productosData.items : [];
    // Obtener lotes del producto seleccionado
    const { data: lotes = [] } = useLotes(values.id_producto > 0 ? values.id_producto : undefined);
    const isValid = useMemo(() => {
        const e = {};
        if (values.id_producto <= 0)
            e.id_producto = 'Producto requerido';
        if (values.id_lote <= 0)
            e.id_lote = 'Lote requerido';
        if (values.cantidad <= 0)
            e.cantidad = 'Cantidad debe ser mayor a 0';
        if (values.costo < 0)
            e.costo = 'Costo no puede ser negativo';
        if (!values.proveedor.trim())
            e.proveedor = 'Proveedor requerido';
        setErrors(e);
        return Object.keys(e).length === 0;
    }, [values]);
    const handleChange = (e) => {
        const { name, value } = e.target;
        setValues((v) => ({
            ...v,
            [name]: name === 'cantidad' || name === 'costo' || name === 'id_producto' || name === 'id_lote' ? Number(value) : value,
        }));
        // Si cambió el producto, resetear el lote
        if (name === 'id_producto') {
            setValues((v) => ({ ...v, id_producto: Number(value), id_lote: 0 }));
        }
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!isValid || loading)
            return;
        await onSubmit(values);
    };
    return (_jsxs("form", { className: "form", onSubmit: handleSubmit, children: [_jsxs("div", { className: "form-grid", children: [_jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Fecha" }), _jsx("input", { type: "date", name: "fecha", value: values.fecha, onChange: handleChange })] }), _jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Producto *" }), _jsxs("select", { name: "id_producto", value: values.id_producto, onChange: handleChange, children: [_jsx("option", { value: 0, children: "-- Selecciona un producto --" }), productos.map((p) => (_jsxs("option", { value: p.id, children: [p.nombre, " (Stock actual: ", p.cantidad, ")"] }, p.id)))] }), errors.id_producto && _jsx("span", { className: "form-error", children: errors.id_producto })] }), _jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Lote *" }), _jsxs("select", { name: "id_lote", value: values.id_lote, onChange: handleChange, disabled: values.id_producto <= 0, children: [_jsx("option", { value: 0, children: "-- Selecciona un lote --" }), lotes.map((lote) => (_jsxs("option", { value: lote.id_lote, children: [lote.numero_lote, " (Disp: ", lote.cantidad_disponible, ", Venc: ", new Date(lote.fecha_vencimiento).toLocaleDateString(), ")"] }, lote.id_lote)))] }), errors.id_lote && _jsx("span", { className: "form-error", children: errors.id_lote })] }), _jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Cantidad *" }), _jsx("input", { type: "number", name: "cantidad", value: values.cantidad, onChange: handleChange, min: 1 }), errors.cantidad && _jsx("span", { className: "form-error", children: errors.cantidad })] }), _jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Proveedor *" }), _jsx("input", { name: "proveedor", value: values.proveedor, onChange: handleChange, placeholder: "Nombre del proveedor" }), errors.proveedor && _jsx("span", { className: "form-error", children: errors.proveedor })] }), _jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Costo Unitario *" }), _jsx("input", { type: "number", name: "costo", step: "0.01", value: values.costo, onChange: handleChange, min: 0 }), errors.costo && _jsx("span", { className: "form-error", children: errors.costo })] }), _jsxs("div", { className: "form-field form-field-full", children: [_jsx("label", { children: "Observaciones" }), _jsx("textarea", { name: "observaciones", rows: 3, value: values.observaciones, onChange: handleChange, placeholder: "Notas adicionales (opcional)" })] })] }), _jsxs("div", { className: "form-actions", children: [onCancel && (_jsx("button", { type: "button", className: "btn-outline", onClick: onCancel, disabled: loading, children: "Cancelar" })), _jsx("button", { type: "submit", className: "btn-primary", disabled: !isValid || loading, children: loading ? 'Guardando…' : 'Registrar Entrada' })] })] }));
}
