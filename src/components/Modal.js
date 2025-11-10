import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect } from 'react';
export default function Modal({ isOpen, title, onClose, children, footer, width = 640 }) {
    useEffect(() => {
        const handler = (e) => {
            if (e.key === 'Escape')
                onClose();
        };
        if (isOpen)
            document.addEventListener('keydown', handler);
        return () => document.removeEventListener('keydown', handler);
    }, [isOpen, onClose]);
    if (!isOpen)
        return null;
    return (_jsx("div", { className: "modal-overlay", role: "dialog", "aria-modal": "true", children: _jsxs("div", { className: "modal-content", style: { width: typeof width === 'number' ? `${width}px` : width }, onClick: (e) => e.stopPropagation(), children: [_jsxs("div", { className: "modal-header", children: [_jsx("h3", { children: title }), _jsx("button", { className: "modal-close", onClick: onClose, "aria-label": "Cerrar", children: "\u00D7" })] }), _jsx("div", { className: "modal-body", children: children }), footer && _jsx("div", { className: "modal-footer", children: footer })] }) }));
}
