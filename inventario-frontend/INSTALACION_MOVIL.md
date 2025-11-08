# 📱 Guía: Instalar la App en Móviles (Android, iOS y Tablets)

La aplicación funciona como **PWA (Progressive Web App)** - puedes instalarla desde el navegador como si fuera una app nativa, sin necesidad de descargar APK o publicar en tiendas.

---

## 🎯 Opción 1: Instalación desde la red local (para pruebas)

### Requisitos
- PC y móvil en la **misma red Wi-Fi**
- Backend y frontend corriendo
- Firewall de Windows permitiendo puertos 5173 (frontend) y 8000 (backend)

### Paso 1: Obtén tu IP local
En tu PC, abre PowerShell:
```powershell
ipconfig
```
Busca la **IPv4** del adaptador Wi-Fi (ejemplo: `192.168.1.50`)

### Paso 2: Configura el backend
Crea o edita `inventario-backend\.env`:
```
ENVIRONMENT=development
LOCAL_DEV_IP=192.168.1.50
DEV_CLIENT_PORT=5173
ALLOW_ALL_HOSTS_DEV=true
ALLOW_MOBILE_SCHEMES_DEV=true
```

### Paso 3: Configura el frontend
Crea o edita `inventario-frontend\.env.local`:
```
VITE_API_URL=http://192.168.1.50:8000
VITE_API_V1=/api/v1
```

### Paso 4: Inicia los servidores
**Backend:**
```powershell
cd c:\Users\cleiv\Desktop\inventario-backend
python main.py
```

**Frontend:**
```powershell
cd c:\Users\cleiv\Desktop\inventario-frontend
npm run dev:mobile
```

### Paso 5: Abre en el móvil
En el navegador del celular/tablet, ve a:
```
http://192.168.1.50:5173
```
(Usa TU IP en lugar de 192.168.1.50)

### Paso 6: Instalar como PWA

#### En Android (Chrome):
1. Toca el menú (⋮) → **Instalar aplicación** / **Agregar a pantalla de inicio**
2. Confirma el nombre y listo ✅

#### En iPhone/iPad (Safari):
1. Toca el botón **Compartir** (□↑)
2. Selecciona **Añadir a pantalla de inicio**
3. Confirma el nombre y listo ✅

#### En tablets (cualquier navegador):
- Sigue los mismos pasos según el sistema operativo

---

## 🌐 Opción 2: Despliegue en Internet (para entregar al docente)

### Paso 1: Construir la aplicación
```powershell
cd c:\Users\cleiv\Desktop\inventario-frontend
npm run build:mobile
```

### Paso 2: Subir a hosting
Puedes usar:
- **Vercel**: `vercel --prod` (gratis, fácil)
- **Netlify**: `netlify deploy --prod`
- **GitHub Pages**: configurar en el repositorio
- **Render** / **Railway**: hosting gratuito con backend incluido

### Paso 3: Configurar variables de producción
En el servicio de hosting, configura:
```
VITE_API_URL=https://tu-backend-produccion.com
VITE_API_V1=/api/v1
```

### Paso 4: El docente puede instalar
1. Abre la URL en cualquier navegador móvil
2. Instala como PWA (pasos anteriores)
3. La app funciona como nativa: icono en pantalla, sin barra de navegador

---

## ✅ Características PWA instalada
- ✅ Funciona offline (cache inteligente)
- ✅ Icono en pantalla principal
- ✅ Splash screen al abrir
- ✅ Sin barra del navegador (modo standalone)
- ✅ Notificaciones push (si implementas)
- ✅ Compatible: Android, iOS, tablets, desktop

---

## 🚀 Opción 3: App Nativa (futuro, si lo necesitas)

Si más adelante quieres publicar en Google Play o App Store:

### Instalar Capacitor
```powershell
npm install @capacitor/core @capacitor/cli @capacitor/android @capacitor/ios --save-dev
```

### Inicializar proyecto
```powershell
npx cap init
npx cap add android
npx cap add ios
```

### Sincronizar y abrir
```powershell
npm run build
npx cap sync
npx cap open android  # Abre Android Studio
npx cap open ios      # Abre Xcode (solo en Mac)
```

Luego compila el APK desde Android Studio o IPA desde Xcode.

---

## 📝 Checklist para entregar al docente

- [ ] Backend corriendo y accesible (local o internet)
- [ ] Frontend construido y accesible (local o internet)
- [ ] Probado login y navegación básica
- [ ] Instalado como PWA en tu celular (captura pantalla)
- [ ] Documento con URL de acceso o pasos de instalación local
- [ ] (Opcional) Video demostrando la instalación y uso

---

## 🔧 Troubleshooting

### No aparece opción de instalar
- Verifica que uses HTTPS en producción (o localhost en desarrollo)
- Revisa que `manifest.json` esté accesible: `http://tu-url/manifest.json`
- Comprueba que el service worker se registre (DevTools → Application → Service Workers)

### Backend no responde desde móvil
- Verifica que PC y móvil estén en la misma red
- Desactiva datos móviles (forzar uso de Wi-Fi)
- Abre puerto 8000 en firewall: `netsh advfirewall firewall add rule name="FastAPI" dir=in action=allow protocol=TCP localport=8000`
- Prueba con `curl http://TU_IP:8000/` desde el móvil

### La app se ve mal en móvil
- Importa estilos responsive: `import '@/responsive/breakpoints.css'` en `main.tsx`
- Verifica viewport meta tag en `index.html`

---

## 📞 Soporte
Si tienes problemas, revisa:
- `GUIA_PRUEBAS_MOVIL.md` (configuración LAN)
- Logs del navegador (DevTools en móvil vía USB debugging)
- Backend logs en consola

**¡Tu app ya está lista para instalar en cualquier dispositivo!** 📱✨
