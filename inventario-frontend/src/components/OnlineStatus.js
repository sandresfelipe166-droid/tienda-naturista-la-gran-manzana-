import { jsx as _jsx } from "react/jsx-runtime";
import { useEffect, useState } from 'react';
export function OnlineStatus() {
    const [online, setOnline] = useState(navigator.onLine);
    useEffect(() => {
        const on = () => setOnline(true);
        const off = () => setOnline(false);
        window.addEventListener('online', on);
        window.addEventListener('offline', off);
        return () => {
            window.removeEventListener('online', on);
            window.removeEventListener('offline', off);
        };
    }, []);
    if (online)
        return null;
    return (_jsx("div", { style: {
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            zIndex: 1000,
            background: '#b00020',
            color: 'white',
            textAlign: 'center',
            padding: '8px',
            fontSize: 14
        }, children: "Sin conexi\u00F3n. Algunos datos pueden no estar actualizados." }));
}
