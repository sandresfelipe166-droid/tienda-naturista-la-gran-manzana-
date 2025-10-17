# Guía de Desarrollo

Este documento describe la arquitectura de seguridad, CI/CD, y cómo ejecutar y desarrollar localmente.

## 📐 Arquitectura de Seguridad

### CSRF (Cross-Site Request Forgery)

Implementamos protección CSRF mediante **tokens HMAC firmados** en lugar de tokens simples.

#### Flujo CSRF:

1. **Cliente realiza GET a una página**: El servidor responde con:
   - `X-CSRF-Token` header
   - `CSRF-Token` cookie

2. **Token HMAC**: Los tokens se firman con HMAC-SHA256 e incluyen:
   - Timestamp (para expiración)
   - Nonce (para único por sesión)
   - Firma HMAC

3. **Validación en mutaciones**: Al hacer POST/PUT/DELETE desde un navegador, el cliente debe incluir el token en:
   - Header: `X-CSRF-Token: <token>`
   - O cookie: `CSRF-Token: <token>`

#### Ejemplo (SPA - Single Page App):

```javascript
// 1. En el login o al iniciar la app, obtén el token de headers o cookies
const response = await fetch('/api/v1/some-get-endpoint', {
  credentials: 'include' // incluir cookies
});

// El servidor devuelve X-CSRF-Token en headers y CSRF-Token en cookies
const csrfToken = response.headers.get('X-CSRF-Token') 
  || document.cookie.split('; ').find(row => row.startsWith('CSRF-Token=')).split('=')[1];

// 2. En POST/PUT/DELETE, incluye el token
await fetch('/api/v1/products', {
  method: 'POST',
  headers: {
    'X-CSRF-Token': csrfToken,
    'Content-Type': 'application/json'
  },
  credentials: 'include',
  body: JSON.stringify({ name: 'Producto nuevo' })
});
```

#### Configuración:

- **Expiración de token**: 1 hora (configurable en `app/core/config.py` → `CSRF_TOKEN_EXPIRY_SECONDS`)
- **Secret**: Usa `SECRET_KEY` de tu config
- **Endpoints excluidos**: Rutas bajo `/api/` (API suele no necesitar CSRF si usa CORS + SameSite cookies)

Ver implementación en `app/core/csrf.py` y `app/core/security_middleware.py`.

### Rate Limiting

Dos modos de rate limiting:

#### 1. In-Memory (default)
- Usa deque con ventana deslizante (sliding window)
- Límite por defecto: 100 req/10 min por IP
- Ideal para desarrollo y monolitos

#### 2. Redis (producción)
- Usa sorted sets en Redis (`ZADD`, `ZREMRANGEBYSCORE`)
- Configurable: `REDIS_URL` en env
- Ideal para múltiples instancias (distribuido)

**Activar Redis:**
```bash
# En .env o como var de entorno:
REDIS_URL=redis://localhost:6379
```

Ver: `app/core/rate_limiter.py` y `app/core/rate_limiter_redis.py`.

### Logging Estructurado

- Logs en **JSON** para fácil parsing en agregadores (ELK, DataDog, etc.)
- Sanitización automática: secretos, tokens, contraseñas se redactan
- RequestID inyectado en contexto (disponible en todos los logs de una request)

Ver: `app/core/logging_config.py`.

---

## 🧪 Testing Local

### Prerequisitos
```bash
pip install -r requirements.txt
```

### Correr todos los tests
```bash
# Modo normal (usa SQLite en tests por defecto)
python -m pytest -q

# Con cobertura
python -m pytest --cov=app -q

# Modo verbose
python -m pytest -v
```

**Nota**: Los tests no dependen de PostgreSQL local. Usan SQLite automáticamente (configurable en `tests/conftest.py`).

### Correr tests específicos
```bash
# Tests de CSRF
python -m pytest tests/test_csrf.py -v

# Tests de rate limit
python -m pytest tests/test_rate_limit_and_request_id.py -v

# Tests de autenticación
python -m pytest tests/test_user_auth.py -v
```

---

## 🔍 Linting, Formatting y Type Checking Local

### 1. **Ruff** (lint + auto-fix)
```bash
# Check
ruff check .

# Auto-fix problemas simples
ruff check . --fix

# Format de imports y estilo
ruff format .
```

### 2. **Black** (formateador)
```bash
# Check sin modificar
black --check .

# Aplicar formato
black .
```

### 3. **isort** (organizar imports)
```bash
# Check
isort --check-only .

# Aplicar
isort .
```

### 4. **Pyright** (type checking)
```bash
# Instalación (requiere Node.js):
# - Instala Node.js desde nodejs.org o nvm-windows
# - Luego: pip install pyright

# Type check en modo strict
pyright --strict

# Type check en modo default
pyright
```

**Si pyright falla por Node.js**: 
- Opción 1: Instala Node.js (recomendado).
- Opción 2: Corre en CI (GitHub Actions) donde Node está preinstalado.

### Todo junto (como lo hace el CI):
```bash
# Formatear todo
ruff format .
isort .
black .

# Validar que esté bien formateado
ruff check . --exit-zero || true
isort --check-only . && black --check . && echo "Formatting OK"

# Type check
pyright --strict

# Tests
python -m pytest -q
```

---

## 🐳 Docker Local

### Build
```bash
docker build -t inventario-backend:local .
```

### Ejecutar
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/inventario" \
  -e SECRET_KEY="your-secret-key" \
  inventario-backend:local
```

---

## 🚀 CI/CD (GitHub Actions)

El workflow está en `.github/workflows/ci.yml`.

### Stages del CI:

1. **Setup**: Checkout, cache pip, install Python
2. **Lint & Format**:
   - `ruff check . --fix` (auto-fix)
   - `isort --check-only .` + `black --check .` (verificar)
   - Si no está formateado, **falla el job**
3. **Type Check**: `pyright --strict`
4. **Tests**: `python -m pytest -q`
5. **Docker Build**: `docker build -t inventario-backend:ci .` (no push)

### Triggerear CI:
- Push a `main` o pull request hacia `main`

### Logs del CI:
- Ir a GitHub → Actions → workflow log
- Ver qué exactamente falló (formatting, type errors, test failures, etc.)

---

## 🛠️ Variables de Entorno

### Desarrollo
```bash
# .env.local o en terminal:
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/inventario
# REDIS_URL=redis://localhost:6379  # Opcional, para testing de rate limiting distribuido
```

### Testing (auto en pytest)
```bash
TESTING=true
DATABASE_URL=sqlite:///./test.db  # Forzado por conftest.py
```

### Producción
```bash
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<generated-strong-key>
DATABASE_URL=postgresql+psycopg2://<user>:<pass>@<prod-host>:5432/<db>
REDIS_URL=redis://<redis-host>:6379  # Recomendado
```

---

## 📝 Commit y PR Workflow

1. Crea rama desde `main`:
   ```bash
   git checkout -b feature/tu-feature
   ```

2. Haz cambios y formatea:
   ```bash
   ruff format .
   isort .
   black .
   python -m pytest -q  # Verifica tests locales
   ```

3. Commit:
   ```bash
   git add .
   git commit -m "feat: tu cambio descriptivo"
   ```

4. Push:
   ```bash
   git push origin feature/tu-feature
   ```

5. Abre PR en GitHub
   - CI corre automáticamente
   - Si falla: revisa logs, corrige, push (CI re-corre)
   - Si pasa: requiere aprobación para merge

---

## 🆘 Troubleshooting

### "pyright: not found" o KeyboardInterrupt
- **Causa**: Node.js no instalado
- **Solución**: Instala Node.js (nodejs.org) o corre pyright en CI

### "Tests fallan con DB connection"
- **Causa**: PostgreSQL no está corriendo
- **Solución**: Los tests usan SQLite por defecto. Si ves error, verifica `tests/conftest.py`

### "ruff/black/isort: not found"
- **Solución**: `pip install ruff black isort` (ya están en `requirements.txt`)

### Formatting falla en CI pero funciona localmente
- **Causa**: Versiones diferentes
- **Solución**: Verifica `requirements.txt` coincida con lo que instalaste

---

## 📚 Referencias

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/20/)
- [Pytest](https://docs.pytest.org/)
- [Pyright](https://github.com/microsoft/pyright)
- [OWASP CSRF Prevention](https://owasp.org/www-community/attacks/csrf)

---

## ✨ Próximos Pasos Recomendados

- [ ] Añadir tests para Redis rate limiter (CI con Redis service)
- [ ] Integrar pre-commit hooks locales (git hooks)
- [ ] Documento de deployment (staging/production)
- [ ] Monitoreo y alertas (Sentry, DataDog, etc.)
