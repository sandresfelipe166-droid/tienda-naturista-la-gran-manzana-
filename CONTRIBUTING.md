# Guía de Contribución — Sistema de Inventario

Este documento te ayuda a configurar tu entorno, ejecutar tests, hacer linting y contribuir al proyecto.

## 📋 Requisitos previos
- **Python 3.11** (el proyecto usa `py311` target)
- **Node.js 16+** (para frontend tooling)
- **Docker & Docker Compose** (opcional pero recomendado para Postgres y Redis)
- **Git** (para control de versiones)

---

## 🚀 Setup rápido (Windows - PowerShell)

### Opción A: Usar script automatizado
```powershell
Set-Location -Path "C:\Users\cleiv\Desktop\inventario-app"
.\scripts\setup_dev.ps1 -Project all
```

Esto creará virtualenvs e instalará dependencias en backend y frontend.

### Opción B: Manualmente
#### Backend
```powershell
Set-Location -Path ".\inventario-backend"
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

#### Frontend
```powershell
Set-Location -Path ".\inventario-frontend"
npm install
# Python tools (opcional si usas pyright, ruff, etc.)
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

---

## 🧪 Ejecutar tests

### Backend
```powershell
Set-Location -Path ".\inventario-backend"
& .\.venv\Scripts\Activate.ps1
pytest --maxfail=1 --disable-warnings -q
# O usa el script:
.\run_tests.ps1
```

### Frontend (E2E con Playwright)
```powershell
Set-Location -Path ".\inventario-frontend"
npm run test:e2e
```

---

## 🔍 Linting & Formatting

El proyecto usa **ruff**, **black** e **isort** para mantener estilo consistente.

### Verificar formato (sin modificar)
```powershell
Set-Location -Path ".\inventario-backend"  # o frontend
& .\.venv\Scripts\Activate.ps1
ruff check .
isort --check-only .
black --check .
```

### Aplicar formato automáticamente
```powershell
ruff format .
isort .
black .
```

---

## 🐳 Servicios con Docker Compose

### Arrancar Postgres + Redis
```powershell
Set-Location -Path ".\inventario-backend"
docker-compose up -d redis postgres
```

### Detener servicios
```powershell
docker-compose down
```

---

## 📁 Estructura del proyecto
```
inventario-app/
├── inventario-backend/      # API FastAPI
│   ├── app/                 # Código principal
│   ├── tests/               # Tests unitarios
│   ├── alembic/             # Migraciones DB
│   └── docker-compose.yml   # Postgres + Redis
├── inventario-frontend/     # UI React + Vite
│   ├── src/                 # Código React/TypeScript
│   ├── public/              # Assets estáticos
│   └── tests/               # Tests E2E Playwright
├── scripts/                 # Utilidades compartidas
│   ├── shared/              # Scripts de roles y admin
│   ├── setup_dev.ps1        # Setup automatizado (Windows)
│   └── find_duplicates.py   # Detector de archivos duplicados
└── .github/workflows/       # CI/CD (GitHub Actions)
```

---

## 🛠️ Flujo de trabajo recomendado

1. **Crea una rama** desde `main`:
   ```bash
   git checkout -b feature/mi-nueva-feature
   ```

2. **Haz cambios y formatea**:
   ```powershell
   ruff format .
   isort .
   black .
   ```

3. **Ejecuta tests**:
   ```powershell
   pytest -q
   ```

4. **Commit y push**:
   ```bash
   git add .
   git commit -m "feat: descripción clara del cambio"
   git push origin feature/mi-nueva-feature
   ```

5. **Abre un Pull Request** en GitHub. El CI ejecutará linting + tests automáticamente.

---

## 🔧 Scripts de utilidad

Ver [`scripts/README.md`](scripts/README.md) para detalles sobre scripts de roles y administración.

---

## 🆘 Troubleshooting

### `ModuleNotFoundError: No module named 'brotli'`
- **Causa**: No instalaste las dependencias en el venv activo.
- **Solución**:
  ```powershell
  & .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

### `Set-ExecutionPolicy` bloqueado
- **Solución**:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Tests fallan con error de base de datos
- **Causa**: Postgres no está corriendo o la URL está incorrecta.
- **Solución**: Arranca Postgres con Docker Compose o usa SQLite (es el default en tests).

---

## 📝 Convenciones de código

- **Python**: PEP 8 + black + isort (line length 100)
- **TypeScript/React**: ESLint + Prettier (configurados en `.vscode/settings.json`)
- **Commits**: Usa [Conventional Commits](https://www.conventionalcommits.org/):
  - `feat:` — nueva funcionalidad
  - `fix:` — corrección de bug
  - `docs:` — cambios en documentación
  - `refactor:` — cambio que no altera funcionalidad
  - `test:` — añadir o modificar tests

---

## 🚢 CI/CD

El proyecto usa **GitHub Actions** para:
- **Lint & Format check** — `ruff`, `black`, `isort`
- **Tests** — `pytest` con SQLite + Redis + Postgres como servicios
- **Build** — valida que el proyecto compila correctamente

Ver [`.github/workflows/ci.yml`](inventario-backend/.github/workflows/ci.yml) para detalles.

---

## 🤝 ¿Necesitas ayuda?
- Revisa [`DEVELOPMENT_ENV_SETUP.md`](DEVELOPMENT_ENV_SETUP.md) para guía de setup.
- Revisa [`REDIS_WINDOWS_SETUP.md`](REDIS_WINDOWS_SETUP.md) para configurar Redis en Windows.
- Abre un issue en GitHub si encuentras un bug o tienes una pregunta.

---

¡Gracias por contribuir al proyecto! 🎉
