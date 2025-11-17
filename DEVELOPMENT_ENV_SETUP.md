# Configuración del entorno de desarrollo (Windows & Linux)

Este archivo resume pasos rápidos para reproducir el entorno y correr tests localmente.

## Requisitos
- Python 3.11
- Node.js (para frontend tooling) - recomendado 16+ (Vite y Playwright funcionan bien con 18+)
- Docker (opcional pero recomendado para Redis/Postgres) y Docker Compose

## Backend (Windows - PowerShell)
1. Abre PowerShell en `c:\Users\cleiv\Desktop\inventario-app\inventario-backend`.
2. Crea y activa venv:

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
```

> Si PowerShell bloquea la ejecución de scripts, ejecuta como administrador:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

3. Instala dependencias:

```powershell
pip install -U pip
pip install -r requirements.txt
```

4. Arrancar servicios necesarios (opcional, se usan para integración y pruebas que lo requieran):

```powershell
# desde la carpeta inventario-backend
docker-compose up -d postgres redis
```

5. Ejecutar pruebas:

```powershell
python -m pytest -q
# O usar run_tests.ps1: & .\run_tests.ps1
```

## Frontend (Windows - PowerShell)
1. Abre PowerShell en `c:\Users\cleiv\Desktop\inventario-app\inventario-frontend`.
2. Node & npm

```powershell
# Verifica versión
node -v
npm -v
# Instalar dependencias JavaScript
npm install
```

3. (Opcional) Crear venv para herramientas Python:

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Ejecutar lint/tests e2e:

```powershell
npm run lint
npm run test:e2e
```

## Usando `scripts/setup_dev.ps1`
- Ejecuta `.
  scripts\setup_dev.ps1 -Project all` desde el root del repo para crear venvs e instalar dependencias en ambas carpetas.

## Notas comunes
- Requisitos de versión Python: `pyproject.toml` indica `target-version=py311`, la codebase usa Python 3.11.
- Tests de pytest deberían ejecutarse con SQLite por defecto (ver `tests/conftest.py`). Si algunos tests requieren Redis, arranca `redis` con Docker Compose.
- `requirements.txt` incluye `brotli`. Si el test lanza `ModuleNotFoundError: brotli`, significa que no instalaste las dependencias en el venv activo.

---

Si quieres, puedo:
- Consolidar scripts duplicados (por ejemplo mover `fix_roles.py` a `scripts/` y eliminar dupes)
- Crear un PR con una limpieza de archivos binarios (`redis-windows`) fuera del repo y referencia de descarga
- Añadir un archivo `CONTRIBUTING.md` con todos estos pasos

Dime cuál te parece la prioridad y lo hago.