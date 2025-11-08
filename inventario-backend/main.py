import contextlib
import logging
import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.router import api_router
from app.core.cache import cache_manager
from app.core.compression import CompressionMiddleware
from app.core.config import settings
from app.core.config_validator import validate_config_on_startup
from app.core.error_responses import register_error_handlers
from app.core.exception_handlers import (
    database_exception_handler,
    general_exception_handler,
    http_exception_handler,
    inventario_exception_handler,
    validation_exception_handler,
)
from app.core.exceptions import InventarioException
from app.core.input_validation import InputValidationMiddleware
from app.core.metrics import MetricsMiddleware, get_prometheus_metrics
from app.core.rate_limiter import RateLimitMiddleware
from app.core.request_id_middleware import RequestIdMiddleware
from app.core.roles import DEFAULT_ROLES
from app.core.scheduler import scheduler_manager
from app.core.security_middleware import (
    APIKeyMiddleware,
    CSRFMiddleware,
    SecurityEventLogger,
    SecurityHeadersMiddleware,
)
from app.models.database import Base, SessionLocal, engine
from app.models.models import Rol
from app.routers.health import router as health_router
from app.routers.health_advanced import router as health_advanced_router
from app.routers.resilience import router as resilience_router
from app.routers.websocket import router as websocket_router

# Configure logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Validate configuration on startup
        validate_config_on_startup(settings, strict=False)
        
        # Create schema only if explicitly enabled and not during tests (prefer Alembic)
        if settings.create_schema_on_startup and os.getenv("TESTING") != "true":
            Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            _seed_default_roles(db)
        finally:
            db.close()
        # Start scheduler if enabled
        try:
            if settings.scheduler_enabled:
                scheduler_manager.start()
                interval = getattr(settings, "scheduler_interval_hours", 24)
                scheduler_manager.add_or_update_stock_bajo_job(interval)
        except Exception as e:
            logger.error(f"Scheduler start error: {e}")
    except Exception as e:
        logger.error(f"DB init error: {e}")
    yield
    # Shutdown scheduler on application shutdown
    try:
        if settings.scheduler_enabled:
            scheduler_manager.shutdown()
    except Exception as e:
        logger.error(f"Scheduler shutdown error: {e}")


# Create FastAPI app
app = FastAPI(
    title="Inventario Backend API",
    description="API para gestión de inventario de tienda naturista con autenticación JWT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add request ID middleware (early so downstream can use request.state.request_id)
app.add_middleware(RequestIdMiddleware)

# Add compression middleware (debe ir temprano para comprimir todas las respuestas)
app.add_middleware(CompressionMiddleware, minimum_size=500)

# Add CORS middleware with advanced configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=getattr(settings, "cors_allow_origin_regex", None),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=settings.cors_expose_headers,
    max_age=settings.cors_max_age,
)

# Add trusted host middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(APIKeyMiddleware)
app.add_middleware(SecurityEventLogger)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Add input validation middleware
app.add_middleware(InputValidationMiddleware)

# Add metrics middleware (optional)
if settings.metrics_enabled:
    app.add_middleware(MetricsMiddleware)

# Add exception handlers
app.add_exception_handler(InventarioException, inventario_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(IntegrityError, database_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Register new standardized error handlers (these override above if needed)
register_error_handlers(app)

# Include routers
app.include_router(api_router)
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(health_advanced_router, prefix="/api/v1", tags=["health"])
app.include_router(resilience_router, prefix="/api/v1/resilience", tags=["resilience"])
app.include_router(websocket_router, prefix="/api/v1/ws", tags=["websocket"])

# Expose Prometheus metrics endpoint if enabled
if settings.prometheus_enabled:

    async def prometheus_endpoint_async():
        return get_prometheus_metrics()

    app.add_api_route(
        "/metrics", prometheus_endpoint_async, include_in_schema=False, methods=["GET"]
    )

# Startup: initialize DB schema and seed default roles


def _seed_default_roles(db):
    existing = {r.nombre_rol for r in db.query(Rol).all()}
    to_insert = []
    for role in DEFAULT_ROLES:
        name = str(role.get("nombre_rol"))
        if name not in existing:
            to_insert.append(
                Rol(
                    nombre_rol=name,
                    descripcion=role.get("descripcion", ""),
                    permisos=role.get("permisos", ""),
                )
            )
    if to_insert:
        db.add_all(to_insert)
        db.commit()


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API de Inventario Backend",
        "version": "1.0.0",
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/api/v1/health",
        "health_detailed": "/api/v1/health/detailed",
        "metrics": "/api/v1/health/metrics",
        "websocket": "/api/v1/ws/notifications",
        "resilience": "/api/v1/resilience/circuit-breakers",
    }


if __name__ == "__main__":
    # Configurar logging de uvicorn
    log_level = "debug" if settings.debug else "info"

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=log_level,
        access_log=True,
    )
