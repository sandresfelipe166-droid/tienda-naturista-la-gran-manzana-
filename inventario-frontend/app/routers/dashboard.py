"""
Router de Dashboard de métricas
"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_middleware import require_permission
from app.core.cache import cache_manager
from app.core.roles import Permission
from app.crud.producto_advanced import (
    get_productos_por_laboratorio_stats,
    get_productos_por_seccion_stats,
    get_productos_stats,
)
from app.models.database import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics", response_model=dict)
def get_metrics(
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_READ)),
) -> dict[str, Any]:
    """
    Retorna métricas consolidadas del inventario:
    - Estadísticas generales de productos
    - Estadísticas por laboratorio
    - Estadísticas por sección
    Cacheado por 60s.
    """
    cache_key = "dashboard:metrics:v1"
    cached = cache_manager.get(cache_key)
    if cached:
        return {
            "success": True,
            "message": "Métricas obtenidas exitosamente (cache)",
            "data": cached,
        }

    stats = get_productos_stats(db)
    por_laboratorio = get_productos_por_laboratorio_stats(db)
    por_seccion = get_productos_por_seccion_stats(db)

    data = {
        "generales": stats,
        "por_laboratorio": por_laboratorio,
        "por_seccion": por_seccion,
    }

    cache_manager.set(cache_key, data, ttl=60)

    return {
        "success": True,
        "message": "Métricas obtenidas exitosamente",
        "data": data,
    }
