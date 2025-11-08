# 📍 ARCHIVOS - DÓNDE ABRIR CADA UNO

## 🎯 COMIENZA POR AQUÍ

```
C:\Users\cleiv\Desktop\inventario-frontend\EMPEZAR_AQUI.md
```

**Lee este primero.** Es el resumen ejecutivo en 2 minutos.

---

## 📚 GUÍAS EN ORDEN DE LECTURA

### 1️⃣ EMPEZAR_AQUI.md (5 min)
```
Path: inventario-frontend/EMPEZAR_AQUI.md
```
- Qué se creó
- Cómo empezar (3 pasos)
- Verificación rápida

### 2️⃣ INSTALACION.md (10 min)
```
Path: inventario-frontend/INSTALACION.md
```
- Instalar Node.js
- Instalar dependencias
- Iniciar servidor
- Troubleshooting

### 3️⃣ ESTADO_FINAL.md (5 min)
```
Path: inventario-frontend/ESTADO_FINAL.md
```
- Estructura completa
- Archivos creados
- Cómo funciona

### 4️⃣ TODO_CREADO.md (3 min)
```
Path: inventario-frontend/TODO_CREADO.md
```
- Lista de lo que se creó
- Características
- Próximos pasos

### 5️⃣ README.md (5 min)
```
Path: inventario-frontend/README.md
```
- Documentación del proyecto
- Estructura carpetas
- Tecnologías
- Troubleshooting

### 6️⃣ VISUAL_RESUMEN.md (5 min)
```
Path: inventario-frontend/VISUAL_RESUMEN.md
```
- Resumen visual
- Diagrama de flujo
- Stack de tecnologías

---

## 🛠️ ARCHIVOS DE CONFIGURACIÓN

### package.json
```
Path: inventario-frontend/package.json
```
Dependencias:
- react@18.2.0
- @vitejs/plugin-react@4.2.1
- react-router-dom@6.20.0
- axios@1.6.0
- zustand@4.4.0
- @tanstack/react-query@5.28.0

### vite.config.ts
```
Path: inventario-frontend/vite.config.ts
```
Configuración:
- Port: 5173
- Alias: @/ → src/
- Proxy: /api → http://localhost:8000/api/v1

### .env
```
Path: inventario-frontend/.env
```
Variables:
```
VITE_API_URL=http://localhost:8000
VITE_API_V1=/api/v1
```

---

## 📁 CÓDIGO FUENTE (src/)

### Páginas
```
inventario-frontend/src/pages/
├── LoginPage.tsx          - Página de login
├── LoginPage.css          - Estilos login
├── DashboardPage.tsx      - Panel principal
└── DashboardPage.css      - Estilos dashboard
```

### Configuración General
```
inventario-frontend/src/
├── main.tsx               - Entry point React
├── App.tsx                - Router y rutas
├── App.css                - Estilos globales
└── index.css              - Normalización CSS
```

### API
```
inventario-frontend/src/api/
└── client.ts              - Axios client con interceptores
```

### Estado Global
```
inventario-frontend/src/store/
└── authStore.ts           - Zustand auth store
```

### Custom Hooks
```
inventario-frontend/src/hooks/
└── useProducts.ts         - React Query hooks
```

### Tipos TypeScript
```
inventario-frontend/src/types/
└── index.ts               - Tipos compartidos
```

---

## 🎨 ARCHIVOS HTML & CSS

### index.html
```
Path: inventario-frontend/index.html
```
- Estructura HTML base
- Script de React

### Global Styles
```
inventario-frontend/src/index.css
- Estilos globales
- Reset CSS
```

### Component Styles
```
LoginPage.css              - Estilos login (gradient)
DashboardPage.css          - Estilos dashboard (grid)
App.css                    - Estilos App
```

---

## 📖 DOCUMENTACIÓN ADICIONAL

### Documentos backend (referencia)
```
C:\Users\cleiv\Desktop\inventario-backend\README.md
C:\Users\cleiv\Desktop\inventario-backend\PROJECT_ASSESSMENT.md
```

---

## 🚀 ORDEN RECOMENDADO DE APERTURA

### Paso 1: Leer
```
1. Abre: EMPEZAR_AQUI.md
   Tiempo: 5 min
   Qué hace: Resumen ejecutivo
```

### Paso 2: Instalar
```
2. Abre: INSTALACION.md
   Tiempo: 10 min
   Qué hace: Pasos para instalar
```

### Paso 3: Ejecutar
```
3. PowerShell:
   npm install
   npm run dev
```

### Paso 4: Probar
```
4. Abre navegador:
   http://localhost:5173
```

### Paso 5: Explorar
```
5. Abre archivos en VS Code:
   - src/App.tsx
   - src/pages/LoginPage.tsx
   - src/store/authStore.ts
   - src/api/client.ts
```

---

## 🔧 EDITAR ARCHIVOS

### Para cambiar puerto
```
Archivo: vite.config.ts
Busca: port: 5173
Cambia: port: 3000 (o el que quieras)
```

### Para cambiar URL backend
```
Archivo: .env
Línea 1: VITE_API_URL=http://localhost:8000
Cambia: A tu URL del backend
```

### Para agregar dependencias
```
Terminal: npm install --save <package>
Archivo: package.json (se actualiza automáticamente)
```

---

## 📝 CREAR NUEVOS ARCHIVOS

### Crear nueva página
```
1. Crea: src/pages/NombrePage.tsx
2. Exporta: export default function NombrePage() {...}
3. Importa en App.tsx: import NombrePage from '@/pages/NombrePage'
4. Agrega ruta en App.tsx
```

### Crear nuevo componente
```
1. Crea: src/components/NombreComponent.tsx
2. Exporta: export default function NombreComponent() {...}
3. Usa en cualquier página: import NombreComponent from '@/components/NombreComponent'
```

### Crear nuevo hook
```
1. Crea: src/hooks/useNombre.ts
2. Exporta: export const useNombre = () => {...}
3. Usa: const { data } = useNombre()
```

---

## ✨ ACCESOS RÁPIDOS

### Abrir en VS Code
```powershell
# Desde PowerShell
code C:\Users\cleiv\Desktop\inventario-frontend
```

### Abrir carpeta en Explorer
```powershell
# Desde PowerShell
explorer C:\Users\cleiv\Desktop\inventario-frontend
```

### Ver URL del frontend
```
http://localhost:5173
```

### Ver URL del backend
```
http://localhost:8000
```

### Ver documentación backend
```
http://localhost:8000/docs
```

---

## 🗂️ RESUMEN VISUAL

```
inventario-frontend/
│
├── 📖 EMPEZAR_AQUI.md          ← COMIENZA AQUÍ ⭐
│
├── 📖 INSTALACION.md           ← Lee segundo
│
├── 📖 ESTADO_FINAL.md          ← Para referencia
│
├── 📖 TODO_CREADO.md
│
├── 📖 README.md
│
├── 📖 VISUAL_RESUMEN.md
│
├── 📋 package.json
│
├── 📋 vite.config.ts
│
├── 📋 .env
│
└── 📁 src/
    ├── main.tsx
    ├── App.tsx                 ← Router principal
    ├── pages/
    │   ├── LoginPage.tsx       ← Edita aquí
    │   └── DashboardPage.tsx   ← Edita aquí
    ├── api/
    │   └── client.ts           ← Cliente HTTP
    ├── store/
    │   └── authStore.ts        ← Estado auth
    └── hooks/
        └── useProducts.ts      ← Hooks CRUD
```

---

## 🎯 PRÓXIMAS ACCIONES

1. **Hoy:**
   - Lee EMPEZAR_AQUI.md
   - Ejecuta npm install
   - Prueba npm run dev

2. **Mañana:**
   - Lee INSTALACION.md detalladamente
   - Explora src/App.tsx
   - Entiendo el flujo de login

3. **Semana:**
   - Crea nueva página ProductsList
   - Agrega componentes
   - Implementa CRUD

---

## 📞 REFERENCIAS RÁPIDAS

### Npm commands
```
npm run dev       - Inicia servidor (puerto 5173)
npm run build     - Compila para producción
npm run preview   - Vista previa de build
npm install       - Instala dependencias
npm list          - Lista todas las dependencias
```

### Backend commands
```
uvicorn main:app --reload   - Inicia backend (puerto 8000)
```

### Rutas importantes
```
http://localhost:5173       - Frontend
http://localhost:8000       - Backend
http://localhost:8000/docs  - Backend API docs
```

---

**¡LISTO! Ahora abre `EMPEZAR_AQUI.md` y comienza.** 🚀

---

**Última actualización:** 17 Octubre 2025
**Status:** ✅ Todo configurado
**Próximo:** Leer EMPEZAR_AQUI.md
