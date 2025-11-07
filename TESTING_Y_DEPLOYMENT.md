# 🧪 Guía de Testing en Móvil y Deployment

## 1️⃣ Testing Local en Red (SIN INTERNET REQUERIDO)

### Paso 1: Configurar el Backend

```bash
# Ir al directorio del backend
cd C:\Users\cleiv\Desktop\inventario-backend

# Activar entorno virtual (si lo tienes)
# .venv\Scripts\Activate  # Windows

# Instalar dependencias si no están
pip install -r requirements.txt

# Ejecutar el servidor
python main.py

# Deberías ver algo como:
# Uvicorn running on http://0.0.0.0:8000
```

### Paso 2: Configurar el Frontend

```bash
# En otra terminal
cd C:\Users\cleiv\Desktop\inventario-frontend

# Instalar dependencias si no están
npm install

# Ejecutar servidor de desarrollo
npm run dev

# Deberías ver algo como:
# VITE v5.x.x ready in XXX ms
# ➜  Local:   http://localhost:3000
# ➜  Network: http://192.168.x.x:3000
```

### Paso 3: Encontrar tu IP local

**En Windows PowerShell:**
```powershell
ipconfig

# Busca algo como:
# IPv4 Address . . . . . . . . . . . : 192.168.x.x
```

Apunta esa dirección IP (ejemplo: `192.168.1.100`)

### Paso 4: Acceder desde el Teléfono/Tablet

1. **Asegúrate que teléfono y computadora estén en la MISMA RED WiFi**

2. **Abre el navegador en tu móvil y accede a:**
   ```
   http://192.168.1.100:3000
   ```

3. **Prueba:**
   - ✅ Login funciona
   - ✅ Sidebar se adapta a la pantalla
   - ✅ Girar el teléfono (vertical/horizontal) se reajusta automáticamente
   - ✅ Botones son fáciles de clickear con el dedo
   - ✅ No hay scroll horizontal

---

## 🔄 Testing Responsividad

### Checklist Mobile-First

#### En Teléfono (480px o menos):
- [ ] Sidebar colapsable y accesible
- [ ] Texto legible sin zoom
- [ ] Botones ≥ 44x44px
- [ ] Sin scroll horizontal
- [ ] Imágenes escalan correctamente
- [ ] Formularios accesibles

#### En Tablet Vertical (768px):
- [ ] 2-3 columnas de productos
- [ ] Sidebar visible o colapsable
- [ ] Espacio bien utilizado
- [ ] Números visibles

#### En Tablet Horizontal (1024px):
- [ ] Layout completo se ve bien
- [ ] Sidebar siempre visible
- [ ] Contenido bien distribuido

#### Girar Teléfono (Orientation Change):
- [ ] Al girar, todo se reajusta sin recargar
- [ ] Contenido permanece visible
- [ ] Sidebar se adapta

---

## 🧪 Testing en DevTools del Navegador

### Desde el Desktop (para simular móvil):

1. **Chrome/Edge:**
   - Press `F12` para abrir DevTools
   - Click en icono de teléfono 📱 (Device Toggle)
   - Selecciona dispositivo (iPhone 15, Samsung Galaxy, iPad, etc.)
   - Abre DevTools → More tools → Rendering → Throttle

2. **Prueba orientación:**
   - En DevTools, haz click en el icono de rotación
   - Comprueba que el layout se reajusta

3. **Prueba conexión lenta:**
   - Network tab → Throttle → "Slow 3G"
   - Verifica que la app sigue funcionando

### Safari en Mac:
- Develop → Enter Responsive Design Mode
- Simula diferentes dispositivos

---

## 📲 Testing Real en Móvil

### Opción 1: Red Local (Recomendado para desarrollo)

```bash
# Terminal 1: Backend
cd inventario-backend
python main.py

# Terminal 2: Frontend
cd inventario-frontend
npm run dev

# Luego accede desde móvil a:
# http://192.168.1.100:3000
```

### Opción 2: Ngrok (Acceso temporal desde cualquier lado)

```bash
# Instalar ngrok (si no lo tienes)
# https://ngrok.com/download

# En terminal 3:
ngrok http 8000

# Te dará URL como: https://1234-5678.ngrok.io
# Luego en otra terminal:
ngrok http 3000

# Te dará otra URL: https://9999-8888.ngrok.io

# Accede desde móvil a esa URL del frontend
```

---

## 🚀 Build para Producción

### Antes de Deployar

```bash
# 1. Asegurar que todo está limpio
npm run build

# 2. Verificar que no hay errores
npm run typecheck

# 3. Ejecutar tests (si los tienes)
npm run lint

# 4. Previsualizar el build
npm run preview

# Luego accede a http://localhost:4173
# Y prueba desde móvil: http://192.168.1.100:4173
```

### Build Production

```bash
cd inventario-frontend

# Build
npm run build

# Esto crea carpeta "dist" con los archivos compilados
# Esta carpeta es la que se deployará

# Verificar tamaño
ls -lah dist/
```

---

## ☁️ Deployment en la Nube (3 opciones)

### OPCIÓN A: Render.com (Gratis - Recomendado)

#### Backend:

1. **Preparar repositorio:**
```bash
cd inventario-backend
git init
git add .
git commit -m "Initial backend"
git push origin main
```

2. **En Render.com:**
   - New Web Service
   - Conectar GitHub
   - Seleccionar rama `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port 8000`
   - Variables de entorno (copiar de .env)

3. **Base de datos:**
   - New PostgreSQL Database
   - Copiar connection string
   - Agregar a variables de entorno como `DATABASE_URL`

#### Frontend:

1. **En Vercel.com (Mejor que Render para frontend):**
   - Importar proyecto desde GitHub
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`

2. **Environment Variables:**
   - `VITE_API_URL=https://tu-backend-render.onrender.com`

---

### OPCIÓN B: Railway.app (Muy fácil)

```bash
# Instalar CLI
npm install -g @railway/cli

# Login
railway login

# Crear proyecto
railway init

# Deploy
railway up
```

Railway configura todo automáticamente.

---

### OPCIÓN C: Docker + Heroku

```bash
# 1. Crear cuenta en heroku.com
# 2. Instalar Heroku CLI
# 3. Login
heroku login

# 4. Crear app
heroku create mi-inventario

# 5. Deploy
git push heroku main

# 6. Ver logs
heroku logs --tail
```

---

## 🔧 Troubleshooting

### "No puedo acceder desde el teléfono"

```bash
# 1. Verificar que estés en la misma red
# Windows: ipconfig
# Buscar IPv4, ej: 192.168.1.100

# 2. Verificar que el firewall no bloquea
# Windows Defender → Allow App Through Firewall
# Permitir Python y Node.js

# 3. Verificar que los servidores estén corriendo
# Backend: http://localhost:8000 → debe funcionar en desktop
# Frontend: http://localhost:3000 → debe funcionar en desktop

# 4. Verificar CORS en backend
# main.py debe tener CORS configurado
```

### "La app es lenta en móvil"

```bash
# 1. Revisar Network en DevTools
# ¿Se descargan todas las imágenes?

# 2. Habilitar compresión en el backend
# (Ya está configurado en main.py)

# 3. Reducir tamaño de imágenes
# Idealmente ≤ 100KB por imagen

# 4. Verificar carga de datos
# ¿Se carga mucha información a la vez?
```

### "Error CORS desde el teléfono"

```python
# En inventario-backend/main.py, verificar:

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar a dominio específico en prod
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
```

### "No funciona sin internet"

La app ahora tiene **Service Worker**, entonces:
- Las páginas ya visitadas se cargan desde cache
- Las API llamadas recientemente están en cache
- Muestra "Offline" si no hay conexión

---

## 📊 Metricas de Performance

### Monitorear en Production

```bash
# Chrome DevTools → Lighthouse
# Scoring:
# - Performance: ≥ 90
# - Accessibility: ≥ 90
# - Best Practices: ≥ 90
# - SEO: ≥ 90
```

### Comandos para analizar:

```bash
# Frontend size
npm run build
# Ver tamaño en dist/

# Verificar dependencias no usadas
npm ls

# Verificar vulnerabilidades
npm audit
```

---

## ✅ Checklist Final Antes de Entregar

- [ ] App funciona en teléfono vertical
- [ ] App funciona en teléfono horizontal
- [ ] App funciona en tablet vertical
- [ ] App funciona en tablet horizontal
- [ ] Sidebar accesible en todos los tamaños
- [ ] Botones ≥ 44x44px
- [ ] Sin scroll horizontal
- [ ] Login funciona desde móvil
- [ ] Productos se cargan correctamente
- [ ] Formularios son usables en móvil
- [ ] Imágenes se escalan correctamente
- [ ] Cache funciona (Service Worker)
- [ ] Performance Lighthouse ≥ 90
- [ ] Texto legible sin zoom
- [ ] Colores accesibles (contrast ≥ 4.5:1)
- [ ] Touch-friendly (no elementos muy pequeños)
- [ ] Responsive en todas las orientaciones

---

## 🎓 Para tu Docente

**URL de demostración:**
```
https://inventario-tudominio.vercel.app
```

**Incluir en documentación:**
1. ✅ Funciona en cualquier dispositivo
2. ✅ Funciona en cualquier orientación
3. ✅ Responsive desde 320px hasta 2560px
4. ✅ Optimizado para touch
5. ✅ Funciona offline (PWA)
6. ✅ Performance optimizado
7. ✅ Seguro (HTTPS, CORS, etc.)

---

## 📝 Comandos Rápidos

```bash
# Desarrollo completo
npm run dev              # Frontend
python main.py          # Backend (en otra terminal)

# Construir para producción
npm run build           # Frontend
python -m pip freeze    # Backend (ver dependencias)

# Testing en móvil local
# Accede a http://192.168.1.100:3000

# Testing con Ngrok
ngrok http 3000         # Frontend
ngrok http 8000         # Backend
```

¡**Listo para entregar!** 🎉

