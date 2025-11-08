# 🚀 INSTALACIÓN DEL FRONTEND - PASO A PASO

## 📍 Ubicación del Proyecto

```
C:\Users\cleiv\Desktop\inventario-frontend\
```

## ✅ PASO 1: INSTALAR NODE.JS

**Si aún no tienes Node.js instalado:**

1. Ve a https://nodejs.org/
2. Descarga la versión **LTS**
3. Ejecuta el instalador y acepta todo
4. **Reinicia tu computadora o cierra completamente PowerShell**

**Verifica la instalación:**
```powershell
node --version
npm --version
```

---

## ✅ PASO 2: ABRIR LA CARPETA DEL FRONTEND

**En PowerShell:**
```powershell
cd C:\Users\cleiv\Desktop\inventario-frontend
```

---

## ✅ PASO 3: INSTALAR DEPENDENCIAS

```powershell
npm install
```

**Esto descargará ~500 MB. Espera a que termine completamente.**

Deberías ver algo como:
```
added 350 packages in 45s
```

---

## ✅ PASO 4: VERIFICAR LA INSTALACIÓN

```powershell
npm list react
npm list vite
```

Deberían mostrar versiones (v18, v5, etc.)

---

## ✅ PASO 5: ASEGÚRATE QUE EL BACKEND ESTÉ CORRIENDO

En otra ventana PowerShell:
```powershell
cd C:\Users\cleiv\Desktop\inventario-backend
uvicorn main:app --reload
```

Deberías ver:
```
Uvicorn running on http://127.0.0.1:8000
```

---

## ✅ PASO 6: INICIAR EL FRONTEND

**En la primera ventana PowerShell (donde hiciste npm install):**

```powershell
npm run dev
```

Verás algo como:
```
VITE v5.0.8  ready in 234 ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

---

## ✅ PASO 7: ABRIR EN EL NAVEGADOR

Abre tu navegador y ve a:
```
http://localhost:5173
```

O abre http://localhost:3000 si lo configuraste así.

---

## 🔐 CREDENCIALES DE PRUEBA

**Email:** admin@example.com
**Password:** tu_password

(O usa tus credenciales del backend)

---

## 🎯 ¿QUÉ DEBERÍAS VER?

1. Página de login con gradient
2. Inputs para email y password
3. Botón "Iniciar Sesión"
4. Ejemplo de credenciales abajo

**Después de login:**
1. Página de bienvenida
2. Tu nombre (usuario)
3. Botón "Cerrar Sesión"
4. Grid de productos

---

## 🚨 ERRORES COMUNES

### Error: "npm: El término 'npm' no se reconoce"
**Solución:** Node.js no está instalado correctamente. Descarga desde https://nodejs.org/

### Error: "Cannot find module 'react'"
**Solución:** Ejecuta `npm install` nuevamente

### Error: "ECONNREFUSED" o "Cannot connect to backend"
**Solución:** Verifica que el backend esté corriendo en http://localhost:8000

### Error: "Error al iniciar sesión"
**Solución:** Verifica que las credenciales sean correctas en el backend

### Puerto 5173 ya está en uso
**Solución:** 
```powershell
# Mata el proceso o cambia el puerto en vite.config.ts
# Busca: port: 5173 y cambia a port: 5174
```

---

## 📦 ESTRUCTURA CREADA

```
inventario-frontend/
├── src/
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   ├── LoginPage.css
│   │   ├── DashboardPage.tsx
│   │   └── DashboardPage.css
│   ├── api/
│   │   └── client.ts
│   ├── store/
│   │   └── authStore.ts
│   ├── hooks/
│   │   └── useProducts.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   ├── App.css
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── .env
├── .gitignore
└── README.md
```

---

## 🔧 COMANDOS ÚTILES

```powershell
# Desarrollo
npm run dev          # Inicia el servidor

# Producción
npm run build        # Compila para producción
npm run preview      # Vista previa de producción

# Linting (opcional)
npm run lint         # Verifica errores
```

---

## 📝 PRÓXIMOS PASOS

Después de que funcione:

1. **Crear más páginas:**
   - ProductsList.tsx
   - ProductForm.tsx
   - AlertsList.tsx

2. **Crear componentes:**
   - Header.tsx
   - Sidebar.tsx
   - ProductCard.tsx

3. **Agregar funcionalidades:**
   - CRUD de productos
   - Gestión de alertas
   - Reportes

4. **Mejoras UI:**
   - Material-UI
   - Tailwind CSS
   - React Icons

---

## ✨ TIPS

✅ Usa `npm install --save <package>` para agregar paquetes
✅ Usa `npm uninstall <package>` para remover paquetes
✅ Mantén el server corriendo con `npm run dev`
✅ Usa Ctrl+C para detener el servidor
✅ Abre DevTools (F12) para ver errores
✅ Revisa la pestaña Network para ver requests

---

## 🎉 ¡LISTO!

Ya tienes todo configurado. Abre http://localhost:5173 y ¡comienza a desarrollar! 🚀

---

**Última actualización:** 17 Octubre 2025
**Status:** ✅ Listo para usar
