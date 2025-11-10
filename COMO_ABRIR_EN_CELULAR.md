# 📱 GUÍA RÁPIDA: Abrir la app en tu celular

## Tu red Wi-Fi: AKATSUKI
## Tu IP: 192.168.1.60

---

## ⚡ Pasos Rápidos (5 minutos)

### 1️⃣ Abrir puertos en firewall (SOLO UNA VEZ)

Abre PowerShell **como Administrador** (clic derecho → Ejecutar como administrador) y pega estos comandos:

```powershell
# Permitir frontend (Vite)
netsh advfirewall firewall add rule name="Vite Dev Server" dir=in action=allow protocol=TCP localport=5173

# Permitir backend (FastAPI)
netsh advfirewall firewall add rule name="FastAPI Backend" dir=in action=allow protocol=TCP localport=8000
```

✅ Verás "Correcto" dos veces

---

### 2️⃣ Iniciar el backend

Abre una terminal normal (no necesita admin):

```powershell
cd c:\Users\cleiv\Desktop\inventario-backend
python main.py
```

Espera ver: `Uvicorn running on http://0.0.0.0:8000`

---

### 3️⃣ Iniciar el frontend

Abre OTRA terminal:

```powershell
cd c:\Users\cleiv\Desktop\inventario-frontend
npm run dev:mobile
```

Espera ver: `Local: http://localhost:5173/` y `Network: http://192.168.1.60:5173/`

---

### 4️⃣ Abrir en tu celular/tablet

1. **Conecta tu dispositivo a la red Wi-Fi "AKATSUKI"**
2. **Abre el navegador** (Chrome en Android / Safari en iPhone)
3. **Escribe en la barra de direcciones**:

```
http://192.168.1.60:5173
```

4. Presiona Enter

✅ **¡La app debería cargar!**

---

## 📲 Instalar como App

Una vez que cargue en el navegador:

### Android (Chrome):
1. Toca el menú **⋮** (esquina superior derecha)
2. Selecciona **"Instalar aplicación"** o **"Agregar a pantalla de inicio"**
3. Confirma el nombre
4. ✅ Aparecerá el icono en tu pantalla de inicio

### iPhone/iPad (Safari):
1. Toca el botón **Compartir** (□↑)
2. Desplaza y selecciona **"Añadir a pantalla de inicio"**
3. Confirma el nombre
4. ✅ Aparecerá el icono en tu pantalla de inicio

---

## 🔍 Búsqueda en navegador móvil

Simplemente escribe la dirección tal cual:

```
192.168.1.60:5173
```

O con http:

```
http://192.168.1.60:5173
```

El navegador entiende que es una dirección local.

---

## ❌ Si no funciona

### Problema: "No se puede conectar"

**Solución 1**: Verifica que estás en la misma red
- En el celular: Settings → Wi-Fi → Debe decir "AKATSUKI"
- En la PC: debe ser la misma red

**Solución 2**: Reinicia el servidor frontend
```powershell
# Presiona Ctrl+C en la terminal del frontend
npm run dev:mobile
```

**Solución 3**: Desactiva datos móviles
- Fuerza al celular a usar solo Wi-Fi

**Solución 4**: Prueba con la IP completa
```
http://192.168.1.60:5173/
```

### Problema: "Página en blanco"

**Solución**: Verifica que el backend esté corriendo
- Debe decir `Uvicorn running` en su terminal
- Prueba abrir en el celular: `http://192.168.1.60:8000/`
- Debe mostrar un JSON con "message": "Bienvenido..."

---

## 🎯 Resumen Visual

```
Tu PC (192.168.1.60)
├─ Backend: puerto 8000 ✅
└─ Frontend: puerto 5173 ✅
       ↓
   Wi-Fi AKATSUKI
       ↓
Tu Celular/Tablet
└─ Navegador: http://192.168.1.60:5173
```

---

## 📝 Credenciales de prueba

Cuando te pida login:
```
Usuario: admin
Password: admin123
```

---

## ✅ Checklist

- [ ] PowerShell como admin ejecutado (firewall)
- [ ] Backend corriendo (puerto 8000)
- [ ] Frontend corriendo (puerto 5173)
- [ ] Celular conectado a Wi-Fi "AKATSUKI"
- [ ] Navegador abierto en: `http://192.168.1.60:5173`
- [ ] Login funcionando
- [ ] App instalada en pantalla de inicio

---

¡Listo! Ya puedes usar la app desde cualquier dispositivo conectado a tu red Wi-Fi. 📱✨
