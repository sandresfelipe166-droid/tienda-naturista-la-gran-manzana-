# Sistema de Inventario — Proyecto Final

Aplicación completa de gestión de inventario para tienda naturista con backend FastAPI y frontend React + TypeScript.

## 🚀 Enlaces Rápidos
- **[docs/DEVELOPMENT_ENV_SETUP.md](docs/DEVELOPMENT_ENV_SETUP.md)** — Configurar entorno local (Windows/Linux)
- **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** — Guía completa para contribuir al proyecto
- **[docs/REDIS_WINDOWS_SETUP.md](docs/REDIS_WINDOWS_SETUP.md)** — Configurar Redis en Windows
- **[scripts/README.md](scripts/README.md)** — Documentación de scripts de utilidad

## 📋 Características principales
- ✅ Gestión de productos, entradas, salidas, ventas y cotizaciones
- ✅ Sistema de roles (admin, gestor, viewer)
- ✅ Autenticación JWT con password reset
- ✅ Rate limiting (en memoria + Redis distribuido)
- ✅ Métricas y health checks avanzados
- ✅ Logging estructurado y audit trail
- ✅ CI/CD con GitHub Actions (lint, tests, Docker)
- ✅ Responsive design (mobile friendly)

## 🛠️ Tech Stack

### Backend
- FastAPI 0.104.1
- SQLAlchemy 2.0.23 (PostgreSQL + async support)
- Alembic (migraciones)
- Redis 7 (cache + rate limiting)
- Pytest + httpx (testing)
- Ruff + Black + isort (linting)

### Frontend
- React 18
- TypeScript 5
- Vite 5
- TanStack Query (state management)
- Zustand (global state)
- Playwright (E2E testing)

## ⚡ Setup rápido (Windows - PowerShell)

```powershell
# 1. Clonar repo
git clone https://github.com/sandresfelipe166-droid/tienda-naturista-la-gran-manzana-.git
cd tienda-naturista-la-gran-manzana-

# 2. Configurar entornos (automatizado)
.\scripts\setup_dev.ps1 -Project all

# 3. Arrancar servicios con Docker Compose
Set-Location -Path ".\inventario-backend"
docker-compose up -d redis postgres

# 4. Ejecutar backend
& .\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 5. Ejecutar frontend (nueva terminal)
Set-Location -Path "..\inventario-frontend"
npm run dev
```

Accede a:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Docs API**: http://localhost:8000/docs

## 🧪 Ejecutar tests

### Backend
```powershell
Set-Location -Path ".\inventario-backend"
& .\.venv\Scripts\Activate.ps1
pytest --maxfail=1 -q
```

### Frontend (E2E)
```powershell
Set-Location -Path ".\inventario-frontend"
npm run test:e2e
```

## 📦 Estructura del Proyecto

```
inventario-app/
├── inventario-backend/          # API FastAPI
│   ├── app/
│   │   ├── core/                # Config, seguridad, middleware
│   │   ├── models/              # Modelos SQLAlchemy
│   │   ├── routers/             # Endpoints API
│   │   ├── crud/                # Operaciones CRUD
│   │   └── services/            # Lógica de negocio
│   ├── alembic/                 # Migraciones DB
│   ├── tests/                   # Tests unitarios
│   ├── docker-compose.yml       # Postgres + Redis
│   └── main.py                  # Entry point
│
├── inventario-frontend/         # UI React
│   ├── src/
│   │   ├── components/          # Componentes React
│   │   ├── pages/               # Páginas/vistas
│   │   ├── services/            # API calls
│   │   └── stores/              # Zustand stores
│   ├── public/                  # Assets estáticos
│   ├── tests/                   # Playwright E2E
│   └── vite.config.ts           # Configuración Vite
│
├── scripts/                     # Utilidades compartidas
│   ├── shared/                  # Scripts de roles y admin
│   ├── setup_dev.ps1            # Setup automatizado (Windows)
│   └── find_duplicates.py       # Detector de duplicados
│
├── docs/                        # Documentación del proyecto
│   ├── DEVELOPMENT_ENV_SETUP.md # Guía setup entorno
│   ├── CONTRIBUTING.md          # Guía contribución
│   ├── REDIS_WINDOWS_SETUP.md   # Configurar Redis (Windows)
│   ├── AUDIT_SUMMARY.md         # Informe auditoría y limpieza
│   └── MEJORAS_*.md             # Reportes de mejoras
│
├── .github/workflows/           # CI/CD (GitHub Actions)
└── render.yaml                  # Configuración despliegue Render
```

## 🔐 Configuración de Seguridad

El proyecto implementa múltiples capas de seguridad:
- **CSRF Protection** con tokens HMAC firmados
- **Rate Limiting** distribuido (Redis) + en memoria
- **CORS** configurado con origins permitidos
- **JWT Authentication** con refresh tokens
- **Password hashing** con bcrypt
- **Input sanitization** y validación estricta
- **Audit trail** para todas las operaciones críticas

Ver [`inventario-backend/DEVELOPMENT.md`](inventario-backend/DEVELOPMENT.md) para detalles completos.

## 📊 Base de Datos

### Migraciones con Alembic
```powershell
# Crear nueva migración
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

### Poblar roles iniciales
```powershell
Set-Location -Path ".\inventario-backend"
python fix_roles_final.py
```

## 🐳 Docker & Docker Compose

### Solo servicios (Postgres + Redis)
```powershell
docker-compose up -d redis postgres
```

### Backend completo con servicios
```powershell
docker-compose up -d
```

El backend estará disponible en `http://localhost:8000`.

## 🔧 Scripts de Utilidad

Ver [`scripts/README.md`](scripts/README.md) para documentación completa de:
- `check_roles.py` — verificar roles en DB
- `fix_roles.py` — configurar roles principales
- `fix_roles_final.py` — limpiar roles obsoletos
- `setup_inventory_roles.py` — roles para gestión de inventario
- `find_duplicates.py` — detectar archivos duplicados
- `setup_dev.ps1` — automatizar setup de entorno (Windows)

## 📝 Variables de Entorno

### Backend (`.env`)
```env
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=<tu-secret-key-seguro>
CSRF_SECRET=<tu-csrf-secret>
DATABASE_URL=postgresql+psycopg2://admin:admin123@localhost:5432/inventario
REDIS_URL=redis://localhost:6379
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173
```

### Frontend (`.env`)
```env
VITE_API_URL=http://localhost:8000
```

## 🚢 CI/CD

El proyecto usa **GitHub Actions** para:
1. **Lint & Format** — ruff, black, isort (job: `lint-and-format`)
2. **Tests con SQLite** — pytest con servicios Redis + Postgres (job: `test`)
3. **Tests con Postgres** — pytest contra DB real (job: `test-with-postgres`)

Ver [`.github/workflows/ci.yml`](inventario-backend/.github/workflows/ci.yml).

## 🐛 Troubleshooting

### `ModuleNotFoundError: No module named 'brotli'`
```powershell
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### PowerShell: `cannot be loaded because running scripts is disabled`
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Tests fallan con `Connection refused` (Redis)
```powershell
docker-compose up -d redis
```

### Frontend no conecta con backend
- Verifica que el backend esté corriendo en `http://localhost:8000`
- Revisa `CORS_ORIGINS` en el `.env` del backend

## 📚 Documentación Adicional

- [`inventario-backend/DEVELOPMENT.md`](inventario-backend/DEVELOPMENT.md) — Arquitectura de seguridad, testing, CI/CD
- [`inventario-backend/README.md`](inventario-backend/README.md) — README específico del backend
- [`inventario-frontend/README.md`](inventario-frontend/README.md) — README específico del frontend
- [`docs/AUDIT_SUMMARY.md`](docs/AUDIT_SUMMARY.md) — Informe de auditoría y limpieza del proyecto
- [`docs/MEJORAS_IMPLEMENTADAS.md`](docs/MEJORAS_IMPLEMENTADAS.md) — Resumen de mejoras implementadas

## 🤝 Contribuir

1. Lee la [Guía de Contribución](docs/CONTRIBUTING.md)
2. Haz fork del proyecto
3. Crea una rama (`git checkout -b feature/mi-feature`)
4. Formatea el código (`ruff format . && isort . && black .`)
5. Ejecuta tests (`pytest -q`)
6. Commit (`git commit -m 'feat: nueva funcionalidad'`)
7. Push (`git push origin feature/mi-feature`)
8. Abre un Pull Request

## 📄 Licencia

Este proyecto es parte de un trabajo académico para la **Tienda Naturista La Gran Manzana**.

## 👥 Autores

- **Sandres Felipe** — [sandresfelipe166-droid](https://github.com/sandresfelipe166-droid)

---

¡Gracias por usar este proyecto! 🎉
