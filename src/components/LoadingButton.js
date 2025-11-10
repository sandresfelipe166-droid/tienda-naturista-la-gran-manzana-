import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
export function LoadingButton({ isLoading = false, loadingText = 'Cargando...', icon, variant = 'primary', children, disabled, className = '', ...props }) {
    const variantClasses = {
        primary: 'btn-primary',
        secondary: 'btn-secondary',
        danger: 'btn-danger',
        success: 'btn-success',
    };
    return (_jsx("button", { className: `loading-button ${variantClasses[variant]} ${className} ${isLoading ? 'loading' : ''}`, disabled: disabled || isLoading, ...props, children: isLoading ? (_jsxs(_Fragment, { children: [_jsx("span", { className: "spinner", children: _jsx("svg", { width: "16", height: "16", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "2", className: "spinner-icon", children: _jsx("path", { d: "M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83" }) }) }), _jsx("span", { children: loadingText })] })) : (_jsxs(_Fragment, { children: [icon && _jsx("span", { className: "btn-icon", children: icon }), _jsx("span", { children: children })] })) }));
}
/**
 * Estilos CSS para LoadingButton (agregar a index.css o DashboardPage.css)
 */
export const loadingButtonStyles = `
.loading-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.loading-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-button.loading {
  cursor: wait;
}

.loading-button .spinner {
  display: inline-flex;
  align-items: center;
}

.loading-button .spinner-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-success {
  background: #10b981;
  color: white;
}
`;
