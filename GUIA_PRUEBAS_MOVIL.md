# Guía rápida: pruebas desde dispositivos móviles (LAN)

Este flujo te permite abrir el frontend de Vite (React) desde el celular en la misma red Wi‑Fi, y que el backend (FastAPI) acepte las peticiones.

## 1) Requisitos
- PC y teléfono conectados a la MISMA red Wi‑Fi.
- Firewall de Windows permitiendo el puerto 5173 (frontend) y 8000 (backend) o los que uses.
- Backend corriendo (FastAPI) y base de datos accesible.

## 2) Levantar el frontend accesible en LAN
En la carpeta `inventario-frontend`:

- Instala dependencias (primera vez):
  - `npm install`
  - `npx playwright install` (opcional, solo si vas a correr e2e)
- Ejecuta el servidor de desarrollo para móviles:
  - `npm run dev:mobile`

Esto expone Vite en `http://0.0.0.0:5173`. Desde el celular, abre `http://IP_DE_TU_PC:5173` (ej: `http://192.168.1.50:5173`).

Tip: Obtén tu IP con `ipconfig` (Windows). Busca la IPv4 del adaptador Wi‑Fi o Ethernet.

## 3) Configurar el backend para aceptar el origen móvil
En `inventario-backend` puedes usar variables de entorno para CORS y Trusted Hosts:

- `LOCAL_DEV_IP`: IP de tu PC en la red local (ej: `192.168.1.50`).
- `DEV_CLIENT_PORT`: Puerto donde corre Vite (por defecto `5173`).
- `ALLOW_ALL_HOSTS_DEV`: En desarrollo, permite todos los hosts (por defecto `true`).

Ejemplo `.env` (colócalo en `inventario-backend/.env`):

```
ENVIRONMENT=development
LOCAL_DEV_IP=192.168.1.50
DEV_CLIENT_PORT=5173
ALLOW_ALL_HOSTS_DEV=true
# Opcional: CORS_ORIGINS si quieres control completo
# CORS_ORIGINS=http://localhost:5173,http://192.168.1.50:5173
```

Reinicia el backend después de cambiar el `.env`.

## 4) Probar en el móvil
- Abre `http://IP_DE_TU_PC:5173` en el navegador móvil.
- Inicia sesión y navega por los flujos clave.

## 5) Depuración y herramientas
- Chrome en Android: activa “Depuración USB” y usa `chrome://inspect` desde tu PC.
- Safari en iOS: Web Inspector (requiere habilitar en ajustes de Safari y conectar por cable o misma red con proxy remota).
- Pruebas E2E (opcional): `npm run test:e2e` (en PC) para validar smoke responsive.

## 6) Checklist rápido móvil
- Diseño responsive: cabecera, menú hamburguesa, tarjetas/listas.
- Scroll infinito / paginación.
- Formularios: teclado, tipos (email, number), validaciones.
- Errores: mensajes visibles y accesibles.
- Performance: carga inicial razonable, sin bloqueos.

Si algo no funciona desde el móvil:
- Revisa que el celular y el PC están en la misma red.
- Prueba con datos móviles desactivados (para forzar Wi‑Fi).
- Verifica que el puerto 5173 está abierto en Windows Firewall.
- Ajusta el `.env` del backend o usa `CORS_ORIGINS` explícito.
