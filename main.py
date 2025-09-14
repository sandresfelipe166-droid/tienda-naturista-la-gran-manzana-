from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.api.v1.router import api_router
import logging
import uvicorn
import os
import contextlib
from app.models.database import Base, engine, SessionLocal
from app.models.models import Rol
from app.core.roles import DEFAULT_ROLES
from app.core.config import settings
from app.core.rate_limiter import RateLimitMiddleware
from app.core.input_validation import InputValidationMiddleware
from app.core.exception_handlers import (
    inventario_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    database_exception_handler,
    general_exception_handler
)
from app.core.exceptions import InventarioException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Avoid creating schema during tests; rely on migrations or test setup
        if os.getenv("TESTING") != "true":
            Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            _seed_default_roles(db)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"DB init error: {e}")
    yield

# Create FastAPI app
app = FastAPI(
    title="Inventario Backend API",
    description="API para gestión de inventario de tienda naturista con autenticación JWT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.trusted_hosts
)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware
)

# Add input validation middleware
app.add_middleware(
    InputValidationMiddleware
)

# Add exception handlers
app.add_exception_handler(InventarioException, inventario_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(IntegrityError, database_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Versioned API only
app.include_router(api_router)

# Basic security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Startup: initialize DB schema and seed default roles

def _seed_default_roles(db):
    existing = {r.nombre_rol for r in db.query(Rol).all()}
    to_insert = []
    for role in DEFAULT_ROLES:
        name = str(role.get("nombre_rol"))
        if name not in existing:
            to_insert.append(Rol(
                nombre_rol=name,
                descripcion=role.get("descripcion", ""),
                permisos=role.get("permisos", ""),
            ))
    if to_insert:
        db.add_all(to_insert)
        db.commit()

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Bienvenido a la API de Inventario Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
