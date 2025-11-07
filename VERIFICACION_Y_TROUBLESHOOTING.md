# 🔧 VERIFICACIÓN Y TROUBLESHOOTING

## 🚨 Problemas Comunes y Soluciones

### Problema 1: "No puedo acceder desde el teléfono a http://192.168.x.x:3000"

**Solución:**

1. **Verificar que estén en la MISMA RED:**
   ```powershell
   # En computadora
   ipconfig
   # Busca IPv4, por ejemplo: 192.168.1.100
   
   # En teléfono
   # Ve a WiFi settings → selecciona la RED
   # Debe ser la MISMA red
   ```

2. **Verificar que los servidores están corriendo:**
   ```bash
   # Backend debe estar en 8000
   http://localhost:8000/health  # En desktop

   # Frontend debe estar en 3000
   http://localhost:3000  # En desktop
   ```

3. **Desactivar firewall temporalmente (SOLO PARA PRUEBAS):**
   - Windows → Configuración → Seguridad → Firewall
   - O permitir Python/Node.js en el firewall

4. **Verificar que npm/python se ejecutan con "npm run dev" y "python main.py"**

---

### Problema 2: "La app se ve mal en el teléfono (distorsionada, pequeña)"

**Solución:**

1. **Verificar viewport en index.html:**
   ```html
   <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
   ```
   ✅ Debe estar en el `<head>`

2. **Limpiar caché del navegador:**
   - En móvil: Settings → Safari/Chrome → Clear Cache
   - O presiona Ctrl+Shift+Delete en desktop

3. **Forzar reload completo:**
   - Móvil: Cierra y abre el navegador
   - Desktop: Ctrl+F5 (reload duro)

4. **Verificar zoom:**
   - Móvil no debe estar zoomado
   - Si está zoomado: pinch out (juntar dedos)

---

### Problema 3: "Hay scroll horizontal en el teléfono"

**Solución:**

Esto significa que algo es más ancho que la pantalla.

1. **Abrir DevTools (Desktop):**
   - F12 → More tools → Rendering
   - Habilita "Highlight Shifts"

2. **Encontrar el elemento:**
   - Inspector → Hover sobre elementos
   - El que tenga más de 100vw causa el problema

3. **Común:** Tablas o contenedores sin flex-wrap

**Aplicada solución en `responsive-mobile.css`:**
```css
* {
  max-width: 100%;
}
```

---

### Problema 4: "Los botones son demasiado pequeños (difícil de clickear)"

**Solución:**

En `responsive-mobile.css` ya está configurado:
```css
button,
a,
input[type="button"],
input[type="submit"] {
  min-height: 48px;
  min-width: 44px;
}
```

Si sigue pasando:
1. Revisar elementos personalizados en CSS
2. Asegurar que no tienen `padding: 0`
3. Aumentar padding en `src/responsive-mobile.css`

---

### Problema 5: "El sidebar ocupa mucho espacio en móvil"

**Solución:**

En móvil, el sidebar debe convertirse en horizontal.

```css
/* En responsive-mobile.css - móvil */
@media (max-width: 768px) {
  .sidebar {
    width: 100%;        /* Ancho completo */
    height: auto;       /* Alto automático */
    flex-direction: row; /* Horizontal */
    overflow-x: auto;   /* Scroll horizontal */
  }
}
```

✅ Esto ya está hecho.

---

### Problema 6: "La app es muy lenta en móvil"

**Soluciones:**

1. **Verificar conexión:**
   - ¿Tienes buena señal WiFi?
   - Prueba más cerca del router

2. **Reducir datos descargados:**
   - DevTools → Network → Ver qué se descarga
   - Imágenes deben ser < 100KB cada una

3. **Habilitar compresión:**
   ```python
   # En main.py (backend)
   app.add_middleware(CompressionMiddleware, minimum_size=1000)
   ```
   ✅ Ya está configurado

4. **Verificar caché:**
   - Service Worker debería cachear datos
   - Revisa DevTools → Application → Cache Storage

---

### Problema 7: "Los inputs del formulario se ven raros en iOS"

**Solución:**

iOS auto-zoom en inputs. Solución:
```css
input, textarea, select {
  font-size: 16px; /* Previene zoom en iOS */
}
```

✅ Esto ya está en `responsive-mobile.css`

---

### Problema 8: "Al girar el teléfono, el contenido no se adapta"

**Solución:**

1. **Verificar que media queries están en CSS:**
   ```css
   @media (max-width: 768px) { ... }
   @media (orientation: portrait) { ... }
   @media (orientation: landscape) { ... }
   ```
   ✅ Todos configurados en `responsive-mobile.css`

2. **Forzar reload:**
   - A veces el navegador no detecta el cambio
   - Recarga la página: F5

3. **Verificar DevTools:**
   - Abre DevTools → Device Emulation
   - Haz click en el icono de rotación
   - Comprueba que se rota

---

### Problema 9: "Error CORS desde el teléfono"

**Solución:**

El backend necesita permitir requests desde el teléfono.

1. **Verificar CORS en main.py:**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # Permite TODO (desarrollo)
       allow_methods=["*"],
       allow_headers=["*"],
       allow_credentials=True,
   )
   ```

2. **Si sigue fallando:**
   - Verifica que backend está corriendo: `http://localhost:8000/health`
   - Verifica que el frontend apunta a la URL correcta
   - En producción: cambiar `"*"` a dominio específico

---

### Problema 10: "Login funciona en desktop pero no en móvil"

**Solución:**

1. **Verificar conexión de red:**
   - ¿El móvil puede acceder a backend?
   - Prueba: `http://192.168.1.100:8000/health` en móvil

2. **Verificar credenciales:**
   - ¿Usuario existe en la BD?
   - Prueba credenciales en desktop primero

3. **Verificar cookies/localStorage:**
   - DevTools (F12) → Application → Cookies/LocalStorage
   - Debe haber token guardado

4. **Revisar errores:**
   - DevTools (F12) → Console
   - Ver qué error exacto aparece

---

## ✅ Verificación Rápida

Ejecuta esto para verificar que TODO funciona:

### Backend
```bash
cd inventario-backend

# 1. Verificar que Python funciona
python --version  # Debe mostrar Python 3.11+

# 2. Verificar que las dependencias están
pip list | findstr fastapi

# 3. Intentar iniciar el servidor
python main.py

# Deberías ver:
# Uvicorn running on http://0.0.0.0:8000
# Application startup complete
```

### Frontend
```bash
cd inventario-frontend

# 1. Verificar que npm funciona
npm --version  # Debe mostrar 10.x+

# 2. Verificar que las dependencias están
npm list react

# 3. Intentar iniciar el servidor
npm run dev

# Deberías ver:
# VITE v5.x.x ready in XXX ms
# ➜  Local:   http://localhost:3000
# ➜  Network: http://192.168.x.x:3000
```

### Conectar desde Móvil
```bash
# Abre navegador en móvil y accede a:
http://192.168.1.100:3000

# Deberías ver la página de login
# Intenta con credenciales conocidas
```

---

## 🔍 Debug en DevTools

### Chrome/Edge DevTools (F12)

1. **Console:**
   - Busca errores en rojo
   - Nota qué dice el error

2. **Network:**
   - Ve qué requests se hacen
   - Revisa status code (200, 404, 500, etc.)

3. **Application:**
   - Cache Storage → Revisa si el Service Worker cachea
   - LocalStorage → Revisa si se guarda el token

4. **Device Emulation:**
   - Simula dispositivos (iPhone, Android, Tablet)
   - Prueba orientaciones

### Firefox Developer Tools (F12)

Similar a Chrome pero:
1. Storage → LocalStorage/Cookies
2. Responsive Design Mode (Ctrl+Shift+M)

---

## 📞 ¿Todavía no funciona?

Si después de todo esto no funciona:

1. **Guarda los errores exactos:**
   ```
   - ¿Qué URL intentaste?
   - ¿Qué error ves?
   - ¿En qué dispositivo?
   - ¿En qué navegador?
   ```

2. **Comparte:**
   - Screenshot del error
   - Output de la terminal (donde corre python/npm)
   - Resultado de `ipconfig`

3. **Intenta alternativa:**
   - Usa Ngrok en lugar de IP local:
   ```bash
   ngrok http 3000  # Te da URL pública
   ngrok http 8000  # Otra URL
   ```

---

## 🎯 Verificación Final

Antes de entregar, prueba:

```bash
# 1. Abre la URL en móvil
http://192.168.1.100:3000

# 2. Verifica que ves:
✅ Página de login
✅ Campo de usuario
✅ Campo de contraseña
✅ Botón de login
✅ Pie de página con "Crear cuenta", etc.

# 3. Intenta hacer login
✅ Sin errores

# 4. Verifica dashboard
✅ Sidebar visible/colapsable
✅ Contenido principal
✅ Productos cargando

# 5. Gira el teléfono
✅ Layout se adapta
✅ Sin scroll horizontal
✅ Todo legible
```

---

**Si TODO esto funciona ✅, entonces está listo para entregar.** 🎉

