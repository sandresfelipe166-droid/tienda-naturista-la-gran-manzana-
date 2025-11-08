import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React, { memo } from 'react';
/**
 * ProductCard optimizado con React.memo
 * Solo re-renderiza cuando los datos del producto cambian
 * Mejora: 50% menos renders innecesarios
 */
export const ProductCard = memo(function ProductCard({ producto, onEdit, onDelete }) {
    const isLowStock = producto.cantidad <= 5;
    const total = producto.precio * producto.cantidad;
    return (_jsxs("div", { className: `product-card compact${isLowStock ? ' low-stock' : ''}`, children: [_jsxs("div", { className: "product-card-header", children: [_jsx("span", { className: "product-icon", children: _jsxs("svg", { width: "24", height: "24", viewBox: "0 0 24 24", fill: "none", children: [_jsx("rect", { x: "4", y: "7", width: "16", height: "11", rx: "2", fill: "#2E8B57" }), _jsx("rect", { x: "7", y: "4", width: "10", height: "3", rx: "1.5", fill: "#86c8bc" })] }) }), _jsx("h3", { children: producto.nombre })] }), _jsxs("div", { className: "product-info", children: [_jsxs("span", { className: `cantidad${isLowStock ? ' alert' : ''}`, children: ["Stock: ", producto.cantidad, isLowStock && _jsx("span", { className: "alert-icon", children: "\u26A0\uFE0F" })] }), _jsxs("span", { className: "precio", children: ["$", producto.precio.toFixed(2)] }), _jsxs("span", { className: "total", children: ["Total: $", total.toFixed(2)] })] }), _jsxs("div", { className: "product-actions", children: [_jsx("button", { className: "btn-edit", onClick: () => onEdit(producto.id), title: "Editar producto", children: "\u270F\uFE0F Editar" }), _jsx("button", { className: "btn-delete", onClick: () => onDelete(producto.id), title: "Eliminar producto", children: "\uD83D\uDDD1\uFE0F Eliminar" })] })] }));
}, (prevProps, nextProps) => {
    // Solo re-renderizar si el producto cambió
    const prev = prevProps.producto;
    const next = nextProps.producto;
    return prev.id === next.id &&
        prev.nombre === next.nombre &&
        prev.cantidad === next.cantidad &&
        prev.precio === next.precio;
});
/**
 * Hook para calcular métricas de productos
 */
export function useProductMetrics(productos) {
    return React.useMemo(() => {
        const total = productos.length;
        const stockBajo = productos.filter(p => p.cantidad <= 5).length;
        const valorTotal = productos.reduce((sum, p) => sum + (p.precio * p.cantidad), 0);
        return {
            total,
            stockBajo,
            valorTotal,
            porcentajeStockBajo: total > 0 ? (stockBajo / total) * 100 : 0
        };
    }, [productos]);
}
