# Inventory Router Completion Tasks

## Current Task: Complete inventory.py router

### Pending Tasks:
- [x] Add new functions to app/crud/producto.py:
  - [x] get_total_productos_activos(db): Count active products
  - [x] get_valor_total_stock(db): Sum of (stock_actual * precio_compra) for active products
  - [x] count_productos_bajo_stock(db): Count products below minimum stock
- [x] Update app/services/producto_service.py to include these new methods
- [x] Complete app/routers/inventory.py:
  - [x] Import necessary dependencies
  - [x] Implement the / endpoint to return inventory summary
  - [x] Use proper error handling and response format
- [ ] Test the endpoint to ensure it returns correct data
- [ ] Add more endpoints like /reportes, /por-seccion (future task)

## Fase 1: Observabilidad y Seguridad (Plan aprobado)

- [x] Logging con request_id en todos los registros
  - [x] Nuevo: app/core/log_context.py (ContextVar + filtro de logging)
  - [x] app/core/request_id_middleware.py: propagar/limpiar request_id en contextvar
  - [x] app/core/logging_config.py: JSONFormatter robusto, filtros en handlers y uvicorn
- [x] Config endurecida
  - [x] app/core/config.py: create_schema_on_startup (default False), send_x_powered_by default False
  - [x] app/core/config.py: CSP toggle (csp_enabled, csp_default) aplicado a security_headers
  - [x] main.py: usar settings.create_schema_on_startup en vez de create_all por entorno
- [ ] Rate Limiting
  - [ ] Evaluar backend Redis opcional (settings.rate_limit_use_redis, rate_limit_redis_prefix)
  - [ ] Implementar clave distribuida IP+ruta+ventana en app/core/rate_limiter.py cuando Redis esté disponible
- [ ] Cache invalidation
  - [ ] Aplicar cache_manager.invalidate_cache([...]) en create/update/delete de productos, laboratorios y secciones
- [ ] Testing
  - [ ] Tests de security headers (incluye CSP condicional, HSTS según SSL)
  - [ ] Tests de rate limiting (in-memory) y cabeceras X-RateLimit-*
  - [ ] Tests /metrics (Prometheus on/off)
- [ ] DevOps (Fase 2)
  - [ ] Dockerfile multi-stage + docker-compose (Postgres + Redis)
  - [ ] .env.example y scripts de arranque (migrate/seed)
  - [ ] CI (pytest + lint)

Notas:
- No se cambiaron rutas ni contratos de API.
- Migraciones: preferir Alembic; create_all sólo si settings.create_schema_on_startup=true.
