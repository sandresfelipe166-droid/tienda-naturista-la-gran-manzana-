# Despliegue profesional del Frontend (PWA)

Este documento describe los pasos y buenas prácticas para desplegar la PWA `inventario-frontend` en Render (Static Site) de forma profesional, segura y reproducible.

1) Objetivo
- Desplegar la carpeta `dist/` generada por Vite como sitio estático.
- Permitir que cualquier teléfono en la misma red (Wi‑Fi) abra la URL y pueda "instalar" la PWA.
- Asegurar CORS y variables de entorno para que el frontend apunte al backend de producción.

2) Requisitos previos
- Cuenta en Render (o hosting estático equivalente).
- Dominio o subdominio (opcional) para la UI.
- Backend desplegado y público (por ejemplo `https://inventario-backend.onrender.com`).

3) Build (local / CI)
- Ejecutar en CI o localmente con Node 18+ recomendado.

Comandos (PowerShell):
```powershell
cd inventario-frontend
npm ci
# build optimizado para móvil/producción
npm run build:mobile
```

El build generará `dist/` con `manifest.json`, `sw.js` y los assets. El service worker ya está incluido en `public/sw.js`.

4) Despliegue en Render (Static Site)
- En el repositorio raíz ya existe `render.yaml` con la configuración para el servicio `inventario-frontend`.
- Asegúrate de configurar en Render (Web UI o CLI) las siguientes variables de entorno (si no deseas usar las del `render.yaml`):
  - `VITE_API_URL` := `https://<tu-backend>.onrender.com`
  - `VITE_API_V1` := `/api/v1`

- Build Command (ya establecido): `npm ci && npm run build:mobile`
- Publish Directory: `inventario-frontend/dist`

5) Buenas prácticas y seguridad
- Usar `Cache-Control` largo para assets versionados (ya configurado en `render.yaml`).
- Configurar headers de seguridad (CSP si aplica) y HSTS a nivel del hosting o reverse proxy.
- Si usas Sentry u otras herramientas, pasar sólo DSNs y claves públicas como `VITE_` vars.

6) Probar la PWA en teléfono (Wi‑Fi)
- Opción rápida: `npm run preview:mobile` y abrir `http://<IP_DE_TU_PC>:4173` en el teléfono.
- Opción profesional: acceder a la URL pública del sitio en Render, abrir en el navegador del teléfono y desde el menú seleccionar "Añadir a pantalla de inicio" o aceptar el prompt de instalación.

7) CORS y Backend
- Asegúrate que el backend (servicio `inventario-backend`) permita solicitudes desde el origen del frontend. En `render.yaml` del backend hay una variable `CORS_ORIGINS` que debe incluir la URL del frontend.

8) Actualizaciones y SW
- Hacer `cache-busting` usando hashes (Vite ya lo hace). El `sw.js` implementa una estrategia network-first para `/api` y cache-first para assets.
- Para forzar la actualización de SW en clientes, enviar un mensaje `SKIP_WAITING` desde el frontend cuando detectes nueva versión.

9) Despliegue automático
- Render hará auto-deploy en cada push al repo si `autoDeploy: true` está activo en `render.yaml`.
- Para control más fino, usa GitHub Actions para construir y publicar artifacts o pre-render step.

10) Soporte y rollback
- Mantén copias de seguridad del backend (DB) antes de cambios en migraciones. El frontend es safe-to-rollback porque es estático.

Si quieres, genero el workflow de GitHub Actions que construya el frontend y valide el artefacto antes de que Render lo despliegue.
