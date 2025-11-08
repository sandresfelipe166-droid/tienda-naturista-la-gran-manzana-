from fastapi import APIRouter

from app.routers import (
    alertas,
    auth,
    cotizaciones,
    entradas,
    gastos,
    inventory,
    laboratorios,
    productos,
    roles,
    secciones,
    ventas,
)
from app.routers.business_metrics import router as business_metrics_router
from app.routers.dashboard import router as dashboard_router
from app.routers.notificaciones import router as notificaciones_router
from app.routers.productos_advanced import router as productos_advanced_router
from app.routers.reportes import router as reportes_router
from app.routers.scheduler import router as scheduler_router
from app.routers.users import router as users_router

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
api_router.include_router(roles.router)  # Roles router
# Nuevos routers: ventas, gastos y cotizaciones
api_router.include_router(ventas.router)
api_router.include_router(gastos.router)
api_router.include_router(cotizaciones.router)
# Advanced and Phase 2 routers
api_router.include_router(productos_advanced_router)
api_router.include_router(reportes_router)
api_router.include_router(dashboard_router)
api_router.include_router(notificaciones_router)
api_router.include_router(scheduler_router)
api_router.include_router(entradas.router)
# Business metrics
api_router.include_router(business_metrics_router)


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
            "productos_advanced": "/api/v1/productos",
            "inventory": "/api/v1/inventory",
            "ventas": "/api/v1/ventas",
            "gastos": "/api/v1/gastos",
            "cotizaciones": "/api/v1/cotizaciones",
            "entradas": "/api/v1/entradas",
            "reportes": "/api/v1/reportes",
            "dashboard": "/api/v1/dashboard",
            "business_metrics": "/api/v1/metrics/business",
            "notificaciones": "/api/v1/notificaciones",
            "scheduler": "/api/v1/scheduler",
        },
    }
