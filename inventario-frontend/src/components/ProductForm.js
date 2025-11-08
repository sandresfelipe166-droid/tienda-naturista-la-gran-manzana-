import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useMemo, useState } from 'react';
import { useSecciones, useLaboratorios } from '@/hooks/useCatalogs';
const emptyValues = {
    nombre: '',
    descripcion: '',
    precio: 0,
    cantidad: 0,
};
export default function ProductForm({ initialValues, loading, onSubmit, onCancel }) {
    const [values, setValues] = useState({ ...emptyValues, id_seccion: undefined, id_laboratorio: undefined });
    const [errors, setErrors] = useState({});
    const { data: secciones = [] } = useSecciones();
    const { data: laboratorios = [] } = useLaboratorios();
    useEffect(() => {
        if (initialValues) {
            setValues({
                nombre: initialValues.nombre ?? '',
                descripcion: initialValues.descripcion ?? '',
                precio: typeof initialValues.precio === 'number' ? initialValues.precio : 0,
                cantidad: typeof initialValues.cantidad === 'number' ? initialValues.cantidad : 0,
                id_seccion: initialValues.id_seccion,
                id_laboratorio: initialValues.id_laboratorio,
            });
        }
    }, [initialValues]);
    const isValid = useMemo(() => {
        const e = {};
        if (!values.nombre || values.nombre.trim().length < 2)
            e.nombre = 'Ingresa un nombre válido';
        if (values.precio <= 0)
            e.precio = 'El precio debe ser mayor a 0';
        if (values.cantidad < 0)
            e.cantidad = 'La cantidad no puede ser negativa';
        if (!values.id_seccion)
            e.id_seccion = 'Selecciona una sección';
        if (!values.id_laboratorio)
            e.id_laboratorio = 'Selecciona un laboratorio';
        setErrors(e);
        return Object.keys(e).length === 0;
    }, [values]);
    const handleChange = (e) => {
        const { name, value } = e.target;
        const numeric = new Set(['precio', 'cantidad', 'id_seccion', 'id_laboratorio']);
        setValues((v) => ({
            ...v,
            [name]: numeric.has(name) ? (value === '' ? undefined : Number(value)) : value,
        }));
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!isValid || loading)
            return;
        await onSubmit(values);
    };
    return (_jsxs("form", { className: "form", onSubmit: handleSubmit, children: [_jsxs("div", { className: "form-grid", children: [_jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Nombre" }), _jsx("input", { name: "nombre", value: values.nombre, onChange: handleChange, placeholder: "Ej. T\u00E9 de Manzanilla 20 sobres" }), errors.nombre && _jsx("span", { className: "form-error", children: errors.nombre })] }), _jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Secci\u00F3n" }), _jsxs("select", { name: "id_seccion", value: values.id_seccion ?? '', onChange: handleChange, children: [_jsx("option", { value: "", children: "Selecciona secci\u00F3n" }), secciones.map((s) => (_jsx("option", { value: s.id_seccion, children: s.nombre_seccion }, s.id_seccion)))] }), errors.id_seccion && _jsx("span", { className: "form-error", children: errors.id_seccion })] }), _jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Laboratorio" }), _jsxs("select", { name: "id_laboratorio", value: values.id_laboratorio ?? '', onChange: handleChange, children: [_jsx("option", { value: "", children: "Selecciona laboratorio" }), laboratorios.map((l) => (_jsx("option", { value: l.id_laboratorio, children: l.nombre_laboratorio }, l.id_laboratorio)))] }), errors.id_laboratorio && _jsx("span", { className: "form-error", children: errors.id_laboratorio })] }), _jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Precio" }), _jsx("input", { name: "precio", type: "number", step: "0.01", value: values.precio, onChange: handleChange }), errors.precio && _jsx("span", { className: "form-error", children: errors.precio })] }), _jsxs("div", { className: "form-field", children: [_jsx("label", { children: "Cantidad" }), _jsx("input", { name: "cantidad", type: "number", step: "1", value: values.cantidad, onChange: handleChange }), errors.cantidad && _jsx("span", { className: "form-error", children: errors.cantidad })] }), _jsxs("div", { className: "form-field form-field-full", children: [_jsx("label", { children: "Descripci\u00F3n" }), _jsx("textarea", { name: "descripcion", rows: 3, value: values.descripcion, onChange: handleChange, placeholder: "Detalles del producto" })] })] }), _jsxs("div", { className: "form-actions", children: [onCancel && (_jsx("button", { type: "button", className: "btn-outline", onClick: onCancel, disabled: loading, children: "Cancelar" })), _jsx("button", { type: "submit", className: "btn-primary", disabled: !isValid || loading, children: loading ? 'Guardando…' : 'Guardar' })] })] }));
}
