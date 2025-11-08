# 🎯 Guía Rápida: Entregar la App al Docente

## ✅ Estado Actual
La aplicación está **100% funcional** como PWA instalable en Android, iOS y tablets. No necesitas publicar en tiendas - funciona desde el navegador con experiencia de app nativa.

---

## 📋 Opción 1: Entrega Local (Demo en tu PC)

### Para el día de la presentación:

1. **Inicia el backend** (en una terminal):
```powershell
cd c:\Users\cleiv\Desktop\inventario-backend
python main.py
```

2. **Inicia el frontend** (en otra terminal):
```powershell
cd c:\Users\cleiv\Desktop\inventario-frontend
npm run dev:mobile
```

3. **Obtén tu IP local**:
```powershell
ipconfig
```
Anota la IPv4 (ejemplo: `192.168.1.50`)

4. **En el celular del docente**:
   - Conéctalo a la **misma red Wi-Fi** que tu PC
   - Abre Chrome/Safari
   - Ve a: `http://TU_IP:5173`
   - Instala la app: menú → "Agregar a pantalla de inicio"
   - ✅ Ya puede usarla como app nativa

---

## 🌐 Opción 2: Entrega Online (Recomendado)

### Desplegar en Vercel (GRATIS):

1. **Crea cuenta en Vercel**: https://vercel.com

2. **Instala CLI**:
```powershell
npm install -g vercel
```

3. **Despliega el frontend**:
```powershell
cd c:\Users\cleiv\Desktop\inventario-frontend
vercel --prod
```

4. **Configura variables**:
En Vercel dashboard → Settings → Environment Variables:
```
VITE_API_URL = https://tu-backend.com
VITE_API_V1 = /api/v1
```

5. **Redeploy** tras configurar variables:
```powershell
vercel --prod
```

### Desplegar Backend (opciones):

**Railway (Gratis):**
- https://railway.app
- Conecta tu repo de GitHub
- Railway detecta FastAPI automáticamente

**Render (Gratis):**
- https://render.com
- New → Web Service
- Conecta repo, selecciona Python
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

6. **Comparte el link** con el docente:
```
https://tu-app.vercel.app
```

---

## 📱 Cómo Instalar (para el docente)

### Android:
1. Abre el link en Chrome
2. Menú (⋮) → **Instalar aplicación**
3. Confirmar → Listo ✅

### iPhone/iPad:
1. Abre el link en Safari
2. Botón Compartir (□↑) → **Añadir a pantalla de inicio**
3. Confirmar → Listo ✅

### Características que verá:
- ✅ Icono propio en pantalla de inicio
- ✅ Funciona sin barra del navegador
- ✅ Splash screen al abrir
- ✅ Funciona offline (datos en cache)
- ✅ Recibe notificaciones
- ✅ Se siente como app nativa

---

## 📦 Estructura de Archivos Generados

Build final en `dist/`:
```
dist/
  index.html (2 KB)
  manifest.json
  assets/
    vendor-react-*.js (160 KB) → React optimizado
    vendor-state-*.js (45 KB) → Zustand + TanStack
    vendor-http-*.js (37 KB) → Axios
    index-*.js (97 KB) → Tu código
    index-*.css (49 KB) → Estilos
```

Total: ~390 KB (excelente para móvil)

---

## 🎬 Demo Script (para presentar)

1. **Mostrar en PC**: abrir `http://localhost:5173`
2. **Abrir DevTools**: Application → Manifest (mostrar config PWA)
3. **Abrir en móvil**: misma IP en red local
4. **Instalar**: mostrar proceso en Android/iOS
5. **Usar app**: login, dashboard, productos
6. **Modo offline**: desconectar Wi-Fi, mostrar que sigue funcionando
7. **Responsive**: rotar dispositivo, mostrar en tablet

---

## 📄 Documentos para Entregar

1. **README.md** (crea este resumen):
```markdown
# Inventario Tienda Naturista - PWA

## Acceso
URL: https://tu-app.vercel.app

## Credenciales Demo
Usuario: admin
Password: admin123

## Instalación
Ver INSTALACION_MOVIL.md

## Tecnologías
- Frontend: React + TypeScript + Vite
- Backend: FastAPI + PostgreSQL
- PWA: Service Worker + Manifest
```

2. **Screenshots**: captura pantallas en móvil/tablet
3. **Video demo** (opcional): 1-2 minutos mostrando instalación y uso

---

## 🔧 Checklist Final

- [ ] Backend corriendo (local o desplegado)
- [ ] Frontend construido (`npm run build:mobile`)
- [ ] Probado en Android (Chrome)
- [ ] Probado en iOS (Safari)
- [ ] Probado en tablet
- [ ] Probado offline
- [ ] Screenshots capturadas
- [ ] Link compartido al docente
- [ ] Credenciales de prueba listas

---

## 🚨 Troubleshooting Rápido

### "No aparece botón de instalar"
- Debe ser HTTPS en producción (Vercel/Netlify lo dan gratis)
- O localhost/IP local en desarrollo

### "No carga en móvil (red local)"
- Firewall: `netsh advfirewall firewall add rule name="Vite" dir=in action=allow protocol=TCP localport=5173`
- Misma red Wi-Fi en ambos dispositivos

### "Backend no responde"
- Verifica CORS: debe incluir origen del frontend
- Revisa `.env` del backend (LOCAL_DEV_IP)

---

## 💡 Ventajas PWA vs App Nativa

| Característica | PWA | Nativa |
|---------------|-----|--------|
| Instalación | Desde navegador | Tienda (Play/App Store) |
| Aprobación | Inmediata | Días/semanas revisión |
| Costo | $0 | $25-$99 anual |
| Actualizaciones | Automáticas | Usuario debe actualizar |
| Cross-platform | Sí (1 código) | No (iOS ≠ Android) |
| Funciona offline | ✅ | ✅ |
| Notificaciones | ✅ | ✅ |

---

## 📞 Contacto

Si el docente tiene problemas:
1. Revisar INSTALACION_MOVIL.md
2. Verificar conexión a internet
3. Probar en Chrome/Safari actualizado
4. Video tutorial: [link si haces uno]

**¡Tu app está lista para entregar!** 🎉📱
