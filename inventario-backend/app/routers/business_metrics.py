"""
Router para métricas de negocio agregadas.
"""
from datetime import date, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.core.auth_middleware import require_permission
from app.core.cache import cache_manager
from app.core.logging_config import get_logger
from app.core.roles import Permission
from app.models.database import get_db
from app.models.models import Lote, Producto, Venta

router = APIRouter(prefix="/metrics", tags=["Business Metrics"])
logger = get_logger()


@router.get("/business", response_model=dict)
def get_business_metrics(
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_READ)),
    dias_vencimiento: int = Query(default=30, ge=1, le=365),
) -> dict[str, Any]:
    """
    Retorna métricas clave de negocio agregadas:
    - Valor total del inventario (productos activos con stock)
    - Cantidad de productos bajo stock (stock < stock_minimo)
    - Cantidad de productos próximos a vencer en los próximos N días
    - Ventas del día (fecha = hoy)
    - Ventas de la semana actual (desde lunes hasta hoy)
    - Total de productos activos
    - Stock total (suma de stock de productos activos)
    Cacheado por 5 minutos.
    """
    cache_key = f"business:metrics:v1:{dias_vencimiento}"
    cached = cache_manager.get(cache_key)
    if cached:
        logger.info("Business metrics retrieved from cache")
        return {
            "success": True,
            "message": "Métricas de negocio obtenidas exitosamente (cache)",
            "data": cached,
        }

    # Valor total inventario: suma(precio_compra * stock) para productos activos
    valor_total_inventario_query = (
        db.query(func.sum(Producto.precio_compra * Producto.stock))
        .filter(Producto.estado == "Activo", Producto.stock > 0)
        .scalar()
    )
    valor_total_inventario = float(valor_total_inventario_query or 0.0)

    # Productos bajo stock: stock < stock_minimo y activos
    productos_bajo_stock_query = (
        db.query(func.count(Producto.id_producto))
        .filter(
            Producto.estado == "Activo",
            Producto.stock_minimo.isnot(None),
            text("stock < stock_minimo"),
        )
        .scalar()
    )
    productos_bajo_stock = int(productos_bajo_stock_query or 0)

    # Productos próximos a vencer: lotes con fecha_vencimiento entre hoy y +N días
    hoy = date.today()
    fecha_limite = hoy + timedelta(days=dias_vencimiento)
    productos_proximos_vencer_query = (
        db.query(func.count(func.distinct(Lote.id_producto)))
        .join(Producto, Lote.id_producto == Producto.id_producto)
        .filter(
            Producto.estado == "Activo",
            Lote.fecha_vencimiento.isnot(None),
            Lote.fecha_vencimiento >= hoy,
            Lote.fecha_vencimiento <= fecha_limite,
        )
        .scalar()
    )
    productos_proximos_vencer = int(productos_proximos_vencer_query or 0)

    # Ventas del día: suma del total de ventas con fecha_venta = hoy
    ventas_dia_query = (
        db.query(func.sum(Venta.total))
        .filter(func.date(Venta.fecha_venta) == hoy)
        .scalar()
    )
    ventas_dia = float(ventas_dia_query or 0.0)

    # Ventas de la semana: desde lunes de la semana actual hasta hoy
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    ventas_semana_query = (
        db.query(func.sum(Venta.total))
        .filter(
            func.date(Venta.fecha_venta) >= inicio_semana,
            func.date(Venta.fecha_venta) <= hoy,
        )
        .scalar()
    )
    ventas_semana = float(ventas_semana_query or 0.0)

    # Total productos activos
    total_productos_activos = (
        db.query(func.count(Producto.id_producto))
        .filter(Producto.estado == "Activo")
        .scalar()
        or 0
    )

    # Stock total (suma de stock de productos activos)
    stock_total = (
        db.query(func.sum(Producto.stock))
        .filter(Producto.estado == "Activo")
        .scalar()
        or 0
    )

    data = {
        "valor_total_inventario": round(valor_total_inventario, 2),
        "productos_bajo_stock": productos_bajo_stock,
        "productos_proximos_vencer": productos_proximos_vencer,
        "dias_vencimiento_parametro": dias_vencimiento,
        "ventas_dia": round(ventas_dia, 2),
        "ventas_semana": round(ventas_semana, 2),
        "total_productos_activos": total_productos_activos,
        "stock_total": stock_total,
        "fecha_consulta": datetime.utcnow().isoformat(),
    }

    cache_manager.set(cache_key, data, ttl=300)  # 5 minutos

    logger.info("Business metrics computed and cached", extra={"data": data})

    return {
        "success": True,
        "message": "Métricas de negocio obtenidas exitosamente",
        "data": data,
    }
