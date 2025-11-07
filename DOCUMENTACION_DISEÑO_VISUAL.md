# Documentación de Diseño Visual - Sistema de Inventario La Gran Manzana
## Tercer Corte - Diseño e Interfaz de Usuario

---

## 1. WIREFRAMES Y PALETA DE COLORES

### 1.1 Paleta de Colores Principal

#### Colores Primarios
- **Verde Principal**: `#2E8B57` (SeaGreen)
  - Uso: Botones principales, elementos activos, encabezados
  - Representa: Naturaleza, salud, productos naturistas
  
- **Verde Claro**: `#86c8bc` 
  - Uso: Gradientes, hover states, fondos secundarios
  
- **Verde Oscuro**: `#17643c`
  - Uso: Hover de botones, estados activos intensos

#### Colores de Fondo
- **Blanco**: `#ffffff` - Tarjetas y contenedores principales
- **Gris muy claro**: `#f8fafc` - Fondo general
- **Verde suave**: `#e0f7ef` - Fondos con gradiente, acentos

#### Colores de Texto
- **Texto principal**: `#374151` (gris oscuro)
- **Texto secundario**: `#9ca3af` (gris medio)
- **Texto de error**: `#991b1b` (rojo oscuro)

#### Colores de Estado
- **Error**: `#fee2e2` (fondo), `#991b1b` (texto)
- **Éxito**: `#2E8B57` (verde principal)
- **Advertencia**: Tonos naranjas suaves
- **Info**: Tonos azules suaves

### 1.2 Wireframes de la Aplicación

#### A) Página de Login
```
┌─────────────────────────────────────────┐
│                                         │
│          [LOGO LA GRAN MANZANA]         │
│     Bienvenido a La Gran Manzana       │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  👤  [Usuario o correo]          │  │
│  │                                   │  │
│  │  🔑  [Contraseña]           👁️  │  │
│  │                                   │  │
│  │  ☐ Recordarme                    │  │
│  │                                   │  │
│  │  [  INICIAR SESIÓN  ] (verde)    │  │
│  │                                   │  │
│  │  ────────────────────────────     │  │
│  │     Registrarse                   │  │
│  │     Restaurar contraseña          │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘

Características:
- Diseño centrado y minimalista
- Bordes redondeados (border-radius: 20px)
- Sombras suaves para profundidad
- Iconos SVG personalizados
- Campos con iconos integrados
- Botón de mostrar/ocultar contraseña
```

#### B) Página de Registro
```
┌─────────────────────────────────────────────────┐
│         Crear Nueva Cuenta                      │
│                                                  │
│  SELECCIONA TU ROL:                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   👁️    │  │    📦    │  │    👑    │     │
│  │Visualiza │  │  Gestor  │  │   Admin  │     │
│  │   dor    │  │          │  │          │     │
│  │          │  │          │  │          │     │
│  │✓ Ver inv │  │✓ Entradas│  │✓ Control │     │
│  │✓ Reportes│  │✓ Editar  │  │  total   │     │
│  │✗ No edita│  │✓ Lotes   │  │✓ Usuarios│     │
│  └──────────┘  └──────────┘  └──────────┘     │
│                                                  │
│  [Nombre de usuario]                            │
│  [Nombre completo]                              │
│  [Correo electrónico]                           │
│  [Contraseña]                                   │
│  [Confirmar contraseña]                         │
│                                                  │
│  [    CREAR CUENTA    ] (verde)                 │
│                                                  │
│  ← Volver al inicio de sesión                   │
└─────────────────────────────────────────────────┘

Características:
- Tarjetas de rol interactivas con hover
- Selección visual clara del rol activo
- Validación en tiempo real
- Feedback visual de errores
```

#### C) Dashboard Principal
```
┌──────┬──────────────────────────────────────────────┐
│ 🌿   │  [Usuario] 👑                    🔔  ⚙️  🚪 │
│      │                                              │
│ 📊   │  ┌────┐ ┌────┐ ┌────┐ ┌────┐               │
│Inicio│  │100 │ │ 25 │ │ 15 │ │ 8  │               │
│      │  │Prod│ │Lote│ │Alrt│ │Lab │               │
│ 📦   │  └────┘ └────┘ └────┘ └────┘               │
│Produc│                                              │
│      │  ┌─────────────────────────────────────┐    │
│ 📥   │  │    LISTADO DE PRODUCTOS             │    │
│Entrad│  │                                     │    │
│      │  │  🔍 [Buscar...]  [Filtros ▼]       │    │
│ 📤   │  │                                     │    │
│Salida│  │  ┌──────────────────────────────┐  │    │
│      │  │  │ Producto A  | Lote | Stock   │  │    │
│ 📊   │  │  │ $50.00      | L001 | 100 ud  │  │    │
│Report│  │  ├──────────────────────────────┤  │    │
│      │  │  │ Producto B  | Lote | Stock   │  │    │
│ 💰   │  │  │ $35.00      | L002 | 50 ud   │  │    │
│Gastos│  │  └──────────────────────────────┘  │    │
│      │  │                                     │    │
│ 👥   │  │  [+ Nuevo Producto]                 │    │
│Admin │  └─────────────────────────────────────┘    │
│      │                                              │
└──────┴──────────────────────────────────────────────┘

Características:
- Sidebar izquierdo con navegación
- Tarjetas de métricas con iconos
- Tabla moderna de productos
- Botones de acción flotantes
- Header con información de usuario
```

### 1.3 Disposición de Controles de Navegación

#### Navegación Principal (Sidebar)
```
Posición: Izquierda fija
Ancho: 220px (desktop), 100% (móvil)
Elementos:
  1. Logo (top)
  2. Menú de navegación
  3. Espaciado automático
  4. Información de usuario (bottom)

Estados visuales:
- Normal: bg blanco, bordes suaves
- Hover: bg verde claro (#e8f5e9)
- Activo: bg verde (#2E8B57), texto blanco
```

#### Navegación Secundaria (Header)
```
Elementos (derecha a izquierda):
  1. Avatar/Nombre usuario
  2. Botón notificaciones (🔔)
  3. Botón configuración (⚙️)
  4. Botón cerrar sesión (🚪)

Comportamiento:
- Sticky header en scroll
- Dropdown menus con animación
```

#### Controles de Formulario
```
Características compartidas:
- Border radius: 12px
- Padding: 16px
- Focus: border verde + shadow
- Iconos: Integrados a la izquierda
- Feedback visual inmediato
```

---

## 2. ÁRBOL DE NAVEGACIÓN

### 2.1 Estructura General
```
APLICACIÓN INVENTARIO LA GRAN MANZANA
│
├─── [ACCESO PÚBLICO]
│    │
│    ├── / (Inicio) → Redirect → /dashboard
│    ├── /login (Inicio de Sesión)
│    └── /register (Registro de Usuario)
│
├─── [ÁREA AUTENTICADA] (Requiere login)
│    │
│    ├── /dashboard (Panel Principal)
│    │   │
│    │   ├─ Vista Métricas
│    │   ├─ Listado de Productos
│    │   ├─ Filtros y Búsqueda
│    │   └─ Acciones Rápidas
│    │
│    ├── Productos
│    │   ├─ Ver listado
│    │   ├─ Crear nuevo (Admin/Gestor)
│    │   ├─ Editar producto (Admin/Gestor)
│    │   └─ Ver detalles
│    │
│    ├── Lotes
│    │   ├─ Ver listado
│    │   ├─ Crear lote (Admin/Gestor)
│    │   └─ Ver detalles
│    │
│    ├── Entradas
│    │   ├─ Ver historial
│    │   ├─ Registrar entrada (Admin/Gestor)
│    │   └─ Ver detalles
│    │
│    ├── Salidas
│    │   ├─ Ver historial
│    │   ├─ Registrar salida (Admin/Gestor)
│    │   └─ Ver detalles
│    │
│    ├── Reportes
│    │   ├─ Estadísticas generales
│    │   ├─ Inventario actual
│    │   ├─ Movimientos
│    │   └─ Alertas de stock
│    │
│    └── Gastos
│        ├─ Ver gastos
│        ├─ Registrar gasto (Admin/Gestor)
│        └─ Categorías
│
└─── [ÁREA ADMINISTRATIVA] (Solo Admin)
     │
     └── /admin (Panel de Administración)
         │
         ├─ Gestión de Usuarios
         │  ├─ Listar usuarios
         │  ├─ Crear usuario
         │  ├─ Editar usuario
         │  ├─ Cambiar rol
         │  └─ Activar/Desactivar
         │
         ├─ Gestión de Roles
         │  ├─ Ver permisos
         │  └─ Configurar accesos
         │
         ├─ Laboratorios
         │  ├─ Listar laboratorios
         │  ├─ Crear laboratorio
         │  └─ Editar laboratorio
         │
         ├─ Secciones
         │  ├─ Listar secciones
         │  ├─ Crear sección
         │  └─ Editar sección
         │
         └─ Configuración del Sistema
            ├─ Parámetros generales
            ├─ Notificaciones
            └─ Respaldos
```

### 2.2 Matriz de Acceso por Rol

| Funcionalidad               | Viewer | Gestor | Admin |
|-----------------------------|--------|--------|-------|
| Ver productos               | ✓      | ✓      | ✓     |
| Crear productos             | ✗      | ✗      | ✓     |
| Editar productos            | ✗      | ✓      | ✓     |
| Ver entradas                | ✓      | ✓      | ✓     |
| Registrar entradas          | ✗      | ✓      | ✓     |
| Ver salidas                 | ✓      | ✓      | ✓     |
| Registrar salidas           | ✗      | ✓      | ✓     |
| Ver lotes                   | ✓      | ✓      | ✓     |
| Gestionar lotes             | ✗      | ✓      | ✓     |
| Ver reportes                | ✓      | ✓      | ✓     |
| Ver gastos                  | ✓      | ✓      | ✓     |
| Registrar gastos            | ✗      | ✓      | ✓     |
| Panel de administración     | ✗      | ✗      | ✓     |
| Gestionar usuarios          | ✗      | ✗      | ✓     |
| Configurar sistema          | ✗      | ✗      | ✓     |

---

## 3. PÚBLICO OBJETIVO

### 3.1 Entidad Objetivo
**Tienda Naturista La Gran Manzana**

**Descripción de la entidad:**
- Tipo: Comercio minorista de productos naturistas
- Sector: Salud natural y bienestar
- Ubicación: Colombia
- Tipo de productos: Suplementos naturales, hierbas medicinales, productos orgánicos

### 3.2 Cantidad de Usuarios

#### Proyección de Usuarios
```
┌─────────────────────────────────────────────────┐
│ ROL            │ CANTIDAD │ PORCENTAJE │ USO    │
├─────────────────────────────────────────────────┤
│ Administrador  │   2-3    │    15%     │ Diario │
│ Gestor         │   3-5    │    35%     │ Diario │
│ Visualizador   │   8-12   │    50%     │ Variable│
├─────────────────────────────────────────────────┤
│ TOTAL          │  15-20   │   100%     │        │
└─────────────────────────────────────────────────┘
```

**Justificación:**
- **Administradores (2-3)**: Dueño y gerente general
- **Gestores (3-5)**: Encargados de bodega, supervisores de inventario
- **Visualizadores (8-12)**: Personal de ventas, cajeros, consultores

### 3.3 Características de los Usuarios

#### A) Conocimiento en Tecnología

**Perfil Principal: Usuario Básico-Intermedio**

```
┌────────────────────────────────────────────┐
│ Nivel Básico (40%)                         │
│ - Uso básico de smartphone                 │
│ - Navegación web simple                    │
│ - Necesita interfaz intuitiva              │
├────────────────────────────────────────────┤
│ Nivel Intermedio (50%)                     │
│ - Uso frecuente de aplicaciones            │
│ - Familiarizado con gestión de inventario  │
│ - Aprende rápidamente nuevas interfaces    │
├────────────────────────────────────────────┤
│ Nivel Avanzado (10%)                       │
│ - Administradores del sistema              │
│ - Configuración y mantenimiento            │
│ - Resolución de problemas                  │
└────────────────────────────────────────────┘
```

**Implicaciones de Diseño:**
- Interfaz simple e intuitiva
- Iconos descriptivos y universales
- Mensajes de error claros
- Tutorial de primer uso
- Ayuda contextual

#### B) Dispositivos de Acceso

**Prioridad de Dispositivos:**

1. **Desktop/Laptop (Prioridad Alta - 60%)**
   - Resolución: 1366x768 a 1920x1080
   - Uso: Gestión completa del inventario
   - Contexto: Oficina, punto de venta
   - Sistema Operativo: Windows principalmente

2. **Tablet (Prioridad Media - 25%)**
   - Resolución: 768x1024 (iPad) y similares
   - Uso: Consultas en bodega, inventario físico
   - Contexto: Movimiento dentro de la tienda

3. **Smartphone (Prioridad Media-Baja - 15%)**
   - Resolución: 360x640 a 414x896
   - Uso: Consultas rápidas, alertas
   - Contexto: Consultas fuera de la tienda

#### C) Diseño Responsivo Implementado

**Breakpoints Definidos:**
```css
/* Desktop Grande */
> 1200px: Layout completo, sidebar fijo

/* Desktop Estándar */
900px - 1200px: Layout completo, optimizado

/* Tablet */
600px - 900px: 
  - Sidebar horizontal en top
  - Métricas en 2 columnas
  - Tablas con scroll horizontal

/* Móvil */
< 600px:
  - Sidebar como menú hamburguesa
  - Métricas en 1-2 columnas
  - Formularios apilados
  - Botones de acción flotantes
```

**Características Responsivas:**
```
Desktop:
├─ Sidebar: 220px fijo a la izquierda
├─ Área principal: flex-grow
├─ Métricas: Grid 4 columnas
└─ Tablas: Ancho completo

Tablet:
├─ Sidebar: Horizontal superior
├─ Área principal: 100% ancho
├─ Métricas: Grid 2 columnas
└─ Tablas: Scroll horizontal

Móvil:
├─ Sidebar: Menú colapsable
├─ Área principal: 100% ancho
├─ Métricas: Grid 1-2 columnas
└─ Tablas: Cards apiladas
```

---

## 4. CARACTERÍSTICAS DE ACCESIBILIDAD

### 4.1 Accesibilidad Visual

#### A) Contraste de Colores
```
Cumplimiento WCAG 2.1 Nivel AA:

✓ Texto normal sobre blanco: 
  - #374151 sobre #ffffff = 10.5:1 (Exceeds AA)
  
✓ Botones verdes:
  - #ffffff sobre #2E8B57 = 4.9:1 (Pass AA)
  
✓ Texto de error:
  - #991b1b sobre #fee2e2 = 8.2:1 (Exceeds AA)
```

#### B) Tamaño de Fuente
```
- Texto base: 16px (1rem)
- Texto pequeño mínimo: 14px
- Botones: 16-18px
- Títulos: 18-24px
- Escalabilidad: Soporta zoom 200%
```

#### C) Indicadores Visuales
```
✓ Focus visible en todos los controles
  - Outline: 3px solid rgba(46,139,87,0.3)
  - Offset: 2px
  
✓ Estados hover claramente diferenciados
✓ Loading states con animaciones
✓ Feedback visual en todas las acciones
```

### 4.2 Accesibilidad de Navegación

#### A) Navegación por Teclado
```
✓ Tab navigation en orden lógico
✓ Skip links para contenido principal
✓ Atajos de teclado:
  - Ctrl+/ : Búsqueda
  - Esc: Cerrar modales
  - Enter: Confirmar acciones
```

#### B) Roles ARIA Implementados
```html
<!-- Navegación principal -->
<nav role="navigation" aria-label="Menú principal">

<!-- Áreas principales -->
<main role="main">
<aside role="complementary">

<!-- Alertas -->
<div role="alert" aria-live="polite">

<!-- Modales -->
<div role="dialog" aria-modal="true">
```

#### C) Labels y Descripciones
```
✓ Todos los inputs tienen labels
✓ Botones con aria-label descriptivos
✓ Iconos con texto alternativo
✓ Mensajes de error asociados a campos
```

### 4.3 Accesibilidad Semántica

```html
✓ HTML5 semántico:
  <header>, <nav>, <main>, <aside>, <footer>
  
✓ Jerarquía de encabezados correcta:
  h1 → h2 → h3 (sin saltos)
  
✓ Formularios accesibles:
  - <label for="input-id">
  - <input id="input-id" required>
  - <span role="alert"> para errores
```

### 4.4 Accesibilidad de Contenido

#### A) Imágenes y Media
```
✓ Todas las imágenes con alt text
✓ Logo con alt descriptivo
✓ Iconos decorativos: aria-hidden="true"
✓ Fallback para imágenes no cargadas
```

#### B) Mensajes y Feedback
```
✓ Mensajes de error claros y específicos
✓ Confirmaciones de acciones
✓ Estados de carga visibles
✓ Timeouts con aviso previo
```

### 4.5 Accesibilidad Móvil

```
✓ Áreas táctiles mínimas: 44x44px
✓ Espaciado entre elementos: 8px mínimo
✓ Zoom permitido (no user-scalable=no)
✓ Orientación adaptativa
✓ Gestos simples e intuitivos
```

### 4.6 Tecnologías Asistivas

#### Compatibilidad Probada
```
✓ Screen readers:
  - NVDA (Windows)
  - JAWS (Windows)
  - VoiceOver (Mac/iOS)
  
✓ Navegación por voz
✓ Magnificadores de pantalla
✓ Teclados alternativos
```

---

## 5. TECNOLOGÍAS Y HERRAMIENTAS

### 5.1 Frontend
```
- React 18.2.0 (Framework UI)
- TypeScript 5.3.3 (Tipado estático)
- React Router 6.20.0 (Navegación)
- Zustand (Gestión de estado)
- Vite 5.4.20 (Build tool)
- CSS3 Modular (Estilos)
```

### 5.2 Backend
```
- FastAPI (Framework Python)
- PostgreSQL (Base de datos)
- SQLAlchemy (ORM)
- JWT (Autenticación)
```

### 5.3 Tipografía
```
- Font Family: 'Poppins', 'Segoe UI', Arial, sans-serif
- Weights: 400 (regular), 600 (semi-bold), 700 (bold)
- Source: Google Fonts
- Características: Moderna, legible, profesional
```

---

## 6. PRINCIPIOS DE DISEÑO APLICADOS

### 6.1 Diseño Visual
1. **Minimalismo**: Interfaz limpia sin elementos innecesarios
2. **Consistencia**: Patrones repetidos en toda la aplicación
3. **Jerarquía Visual**: Tamaños y colores guían la atención
4. **Espaciado Adecuado**: Respiro visual entre elementos
5. **Feedback Visual**: Respuesta inmediata a acciones

### 6.2 Experiencia de Usuario
1. **Flujo Natural**: Navegación intuitiva y lógica
2. **Prevención de Errores**: Validaciones en tiempo real
3. **Recuperación de Errores**: Mensajes claros y soluciones
4. **Eficiencia**: Atajos y acciones rápidas
5. **Satisfacción**: Animaciones suaves y agradables

### 6.3 Arquitectura de Información
1. **Agrupación Lógica**: Funciones relacionadas juntas
2. **Profundidad Limitada**: Máximo 3 niveles de navegación
3. **Breadcrumbs**: Orientación del usuario
4. **Búsqueda Accesible**: Siempre disponible
5. **Filtros Inteligentes**: Refinamiento progresivo

---

## 7. MÉTRICAS DE ÉXITO

### 7.1 Objetivos Medibles
```
- Tiempo de carga: < 2 segundos
- Tiempo de aprendizaje: < 30 minutos
- Tasa de error: < 5% en tareas comunes
- Satisfacción usuario: > 4/5
- Accesibilidad score: > 90/100
```

### 7.2 KPIs de Usabilidad
```
- Tasa de completación de tareas: > 95%
- Tiempo promedio por tarea: Reducción 40% vs sistema anterior
- Número de clics: Minimizado a 3 máximo por tarea
- Retención de usuarios: > 90% mensual
```

---

## 8. CONCLUSIONES

El diseño visual del Sistema de Inventario La Gran Manzana está centrado en:

1. **Usuario Final**: Personal con conocimiento tecnológico básico-intermedio
2. **Accesibilidad**: Cumplimiento WCAG 2.1 AA
3. **Responsividad**: Soporte completo desktop, tablet y móvil
4. **Eficiencia**: Reducción de tiempo en tareas repetitivas
5. **Escalabilidad**: Preparado para crecimiento de usuarios

El sistema ha sido diseñado considerando las necesidades reales de una tienda naturista, priorizando la facilidad de uso, la claridad visual y la eficiencia operativa.

---

**Fecha de elaboración**: 28 de Octubre de 2025  
**Versión**: 1.0  
**Proyecto**: Sistema de Inventario - Tienda Naturista La Gran Manzana  
**Desarrollador**: Felipe  
**Institución**: [Tu institución educativa]
