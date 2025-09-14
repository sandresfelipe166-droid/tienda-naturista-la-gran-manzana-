from fastapi import APIRouter, Depends
from app.routers import auth, secciones, alertas, laboratorios, productos, inventory
from app.routers.users import router as users_router
from app.models.database import get_db

# Main API router for version 1
api_router = APIRouter(prefix="/api/v1")

# Include all domain routers
api_router.include_router(secciones.router)
api_router.include_router(alertas.router)
api_router.include_router(laboratorios.router)
api_router.include_router(inventory.router)
# Add productos and auth under /api/v1 to align with tests and API info
api_router.include_router(productos.router, prefix="/productos")
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(users_router)

# Health check endpoint
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# DB health check (simple SELECT 1)
@api_router.get("/db-health")
async def db_health(db=Depends(get_db)):
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"database": "ok"}
    except Exception as e:
        return {"database": "error", "detail": str(e)}

# API info endpoint
@api_router.get("/")
async def api_info():
    return {
        "title": "Inventario Backend API",
        "version": "1.0.0",
        "description": "API para gestión de inventario de tienda naturista",
        "endpoints": {
            "auth": "/api/v1/auth",
            "secciones": "/api/v1/secciones",
            "alertas": "/api/v1/alertas",
            "laboratorios": "/api/v1/laboratorios",
            "productos": "/api/v1/productos",
            "inventory": "/api/v1/inventory"
        }
    }
