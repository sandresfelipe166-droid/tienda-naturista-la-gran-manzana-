from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from app.models.database import get_db
from app.models.models import Producto, Seccion, Laboratorio, Lote
from app.core.auth_middleware import require_permission
from app.core.roles import Permission

router = APIRouter(prefix="/inventory", tags=["Inventory"])

# Configuración en memoria (runtime) para cortes de stock y días por vencer
INVENTORY_CONFIG: Dict[str, Any] = {
    "ratio_alto": 2.0,          # factor multiplicador de stock_minimo para considerar ALTO
    "dias_por_vencer": 30,      # días para considerar un lote por vencer
}


def _producto_to_dict(p: Producto) -> Dict[str, Any]:
    return {
        "id_producto": p.id_producto,
        "codigo_barras": p.codigo_barras,
        "nombre_producto": p.nombre_producto,
        "descripcion": p.descripcion,
        "concentracion": p.concentracion,
        "requiere_receta": p.requiere_receta,
        "precio_compra": float(p.precio_compra) if p.precio_compra is not None else 0.0,
        "stock_minimo": p.stock_minimo,
        "stock_actual": p.stock_actual,
        "estado": p.estado,
        "seccion": {
            "id_seccion": p.id_seccion,
            "nombre_seccion": getattr(p.seccion, "nombre_seccion", None),
        },
        "laboratorio": {
            "id_laboratorio": p.id_laboratorio,
            "nombre_laboratorio": getattr(p.laboratorio, "nombre_laboratorio", None),
        },
    }


def _clasificar_stock(p: Producto, ratio_alto: float) -> str:
    if p.stock_actual is None or p.stock_minimo is None:
        return "SIN_CONFIG"
    if p.stock_actual <= p.stock_minimo:
        return "BAJO"
    if p.stock_actual >= (p.stock_minimo * ratio_alto):
        return "ALTO"
    return "NORMAL"


# =====================
# Configuración runtime
# =====================
@router.get("/config")
async def get_inventory_config(
    _user=Depends(require_permission(Permission.INVENTORY_READ)),
):
    return {"success": True, "message": "Configuración de inventario", "data": INVENTORY_CONFIG}


@router.put("/config")
async def update_inventory_config(
    ratio_alto: Optional[float] = Body(None, ge=1.0),
    dias_por_vencer: Optional[int] = Body(None, ge=1, le=365),
    _user=Depends(require_permission(Permission.INVENTORY_WRITE)),
):
    if ratio_alto is not None:
        INVENTORY_CONFIG["ratio_alto"] = float(ratio_alto)
    if dias_por_vencer is not None:
        INVENTORY_CONFIG["dias_por_vencer"] = int(dias_por_vencer)
    return {"success": True, "message": "Configuración actualizada", "data": INVENTORY_CONFIG}


# =====================
# Productos
# =====================
@router.get("/productos")
async def get_productos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _user=Depends(require_permission(Permission.INVENTORY_READ))
):
    """Listar productos del inventario (resumen + clasificación de stock)."""
    ratio = INVENTORY_CONFIG["ratio_alto"]
    productos = (
        db.query(Producto)
        .join(Seccion, Producto.id_seccion == Seccion.id_seccion)
        .join(Laboratorio, Producto.id_laboratorio == Laboratorio.id_laboratorio)
        .offset(skip)
        .limit(limit)
        .all()
    )

    data = []
    for p in productos:
        item = _producto_to_dict(p)
        item["estado_stock"] = _clasificar_stock(p, ratio)
        data.append(item)

    return {
        "success": True,
        "message": f"Encontrados {len(data)} productos",
        "data": data,
    }


@router.get("/productos/bajo-stock")
async def get_productos_bajo_stock(
    db: Session = Depends(get_db),
    _user=Depends(require_permission(Permission.INVENTORY_READ))
):
    """Obtener productos con stock bajo (stock_actual <= stock_minimo)."""
    productos = (
        db.query(Producto)
        .join(Seccion, Producto.id_seccion == Seccion.id_seccion)
        .join(Laboratorio, Producto.id_laboratorio == Laboratorio.id_laboratorio)
        .filter(
            Producto.estado == "Activo",
            Producto.stock_actual.isnot(None),
            Producto.stock_minimo.isnot(None),
            Producto.stock_actual <= Producto.stock_minimo,
        )
        .all()
    )

    data = [
        {
            "id_producto": p.id_producto,
            "nombre_producto": p.nombre_producto,
            "stock_actual": p.stock_actual,
            "stock_minimo": p.stock_minimo,
            "diferencia": (p.stock_minimo - p.stock_actual) if (p.stock_minimo is not None and p.stock_actual is not None) else None,
            "seccion": getattr(p.seccion, "nombre_seccion", None),
            "laboratorio": getattr(p.laboratorio, "nombre_laboratorio", None),
        }
        for p in productos
    ]

    return {
        "success": True,
        "message": ("No hay productos con stock bajo" if not data else f"Encontrados {len(data)} productos con stock bajo"),
        "data": data,
    }


@router.get("/productos/alto-stock")
async def get_productos_alto_stock(
    ratio_alto: Optional[float] = Query(None, ge=1.0, description="Factor multiplicador del stock_minimo para considerar stock alto (usa config si no se envía)"),
    db: Session = Depends(get_db),
    _user=Depends(require_permission(Permission.INVENTORY_READ))
):
    """Obtener productos con stock alto usando ratio_alto (default INVENTORY_CONFIG)."""
    ratio = ratio_alto if ratio_alto is not None else INVENTORY_CONFIG["ratio_alto"]
    productos = (
        db.query(Producto)
        .join(Seccion, Producto.id_seccion == Seccion.id_seccion)
        .join(Laboratorio, Producto.id_laboratorio == Laboratorio.id_laboratorio)
        .filter(
            Producto.estado == "Activo",
            Producto.stock_actual.isnot(None),
            Producto.stock_minimo.isnot(None),
            Producto.stock_actual >= (Producto.stock_minimo * ratio),
        )
        .all()
    )

    data = [
        {
            "id_producto": p.id_producto,
            "nombre_producto": p.nombre_producto,
            "stock_actual": p.stock_actual,
            "stock_minimo": p.stock_minimo,
            "ratio": (float(p.stock_actual) / float(p.stock_minimo)) if (p.stock_minimo and p.stock_minimo != 0) else None,
            "seccion": getattr(p.seccion, "nombre_seccion", None),
            "laboratorio": getattr(p.laboratorio, "nombre_laboratorio", None),
        }
        for p in productos
    ]

    return {
        "success": True,
        "message": ("No hay productos con stock alto" if not data else f"Encontrados {len(data)} productos con stock alto"),
        "data": data,
    }


# Debe ir después de rutas estáticas /productos/bajo-stock y /productos/alto-stock
@router.get("/productos/{producto_id}")
async def get_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_permission(Permission.INVENTORY_READ))
):
    """Obtener un producto específico"""
    producto = (
        db.query(Producto)
        .filter(Producto.id_producto == producto_id)
        .first()
    )

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    item = _producto_to_dict(producto)
    item["estado_stock"] = _clasificar_stock(producto, INVENTORY_CONFIG["ratio_alto"])
    return {
        "success": True,
        "message": "Producto obtenido exitosamente",
        "data": item,
    }


# =====================
# Lotes
# =====================
@router.get("/lotes/por-vencer")
async def get_lotes_por_vencer(
    dias: Optional[int] = Query(None, ge=1, le=365, description="Días para considerar por vencer (usa config si no se envía)"),
    db: Session = Depends(get_db),
    _user=Depends(require_permission(Permission.INVENTORY_READ))
):
    """Listar lotes próximos a vencer con días restantes."""
    dias_considerados = dias if dias is not None else INVENTORY_CONFIG["dias_por_vencer"]
    fecha_limite = datetime.now() + timedelta(days=dias_considerados)

    lotes = (
        db.query(Lote)
        .join(Producto, Lote.id_producto == Producto.id_producto)
        .filter(
            Lote.estado == "Activo",
            Lote.cantidad_disponible > 0,
            Lote.fecha_vencimiento <= fecha_limite,
        )
        .all()
    )

    data = []
    hoy = datetime.now()
    for l in lotes:
        dias_restantes = (l.fecha_vencimiento - hoy).days if l.fecha_vencimiento else None
        data.append({
            "id_lote": l.id_lote,
            "id_producto": l.id_producto,
            "producto": getattr(l.producto, "nombre_producto", None) if hasattr(l, "producto") else None,
            "numero_lote": l.numero_lote,
            "fecha_vencimiento": l.fecha_vencimiento.isoformat() if l.fecha_vencimiento else None,
            "cantidad_disponible": l.cantidad_disponible,
            "dias_restantes": dias_restantes,
        })

    return {
        "success": True,
        "message": ("No hay lotes por vencer" if not data else f"Encontrados {len(data)} lotes por vencer en {dias_considerados} días"),
        "data": data,
    }


# =====================
# Secciones y Laboratorios
# =====================
@router.get("/secciones")
async def get_secciones(
    db: Session = Depends(get_db),
    _user=Depends(require_permission(Permission.INVENTORY_READ))
):
    """Obtener lista de secciones activas"""
    secciones = db.query(Seccion).filter(Seccion.estado == "Activo").all()
    data = [
        {"id_seccion": s.id_seccion, "nombre_seccion": s.nombre_seccion, "estado": s.estado}
        for s in secciones
    ]
    return {"success": True, "message": f"Encontradas {len(data)} secciones activas", "data": data}


@router.get("/laboratorios")
async def get_laboratorios(
    db: Session = Depends(get_db),
    _user=Depends(require_permission(Permission.INVENTORY_READ))
):
    """Obtener lista de laboratorios activos"""
    laboratorios = db.query(Laboratorio).filter(Laboratorio.estado == "Activo").all()
    data = [
        {"id_laboratorio": l.id_laboratorio, "nombre_laboratorio": l.nombre_laboratorio, "estado": l.estado}
        for l in laboratorios
    ]
    return {"success": True, "message": f"Encontrados {len(data)} laboratorios activos", "data": data}


# =====================
# Dashboard
# =====================
@router.get("/dashboard/stats")
async def get_dashboard_stats(
    ratio_alto: Optional[float] = Query(None, ge=1.0),
    db: Session = Depends(get_db),
    _user=Depends(require_permission(Permission.INVENTORY_READ))
):
    """Obtener estadísticas para el dashboard."""
    ratio = ratio_alto if ratio_alto is not None else INVENTORY_CONFIG["ratio_alto"]

    total_productos = db.query(Producto).filter(Producto.estado == "Activo").count()

    bajo = db.query(Producto).filter(
        Producto.estado == "Activo",
        Producto.stock_actual.isnot(None),
        Producto.stock_minimo.isnot(None),
        Producto.stock_actual <= Producto.stock_minimo,
    ).count()

    alto = db.query(Producto).filter(
        Producto.estado == "Activo",
        Producto.stock_actual.isnot(None),
        Producto.stock_minimo.isnot(None),
        Producto.stock_actual >= (Producto.stock_minimo * ratio),
    ).count()

    normal = db.query(Producto).filter(
        Producto.estado == "Activo",
        Producto.stock_actual.isnot(None),
        Producto.stock_minimo.isnot(None),
        Producto.stock_actual > Producto.stock_minimo,
        Producto.stock_actual < (Producto.stock_minimo * ratio),
    ).count()

    sin_config = db.query(Producto).filter(
        Producto.estado == "Activo",
        or_(Producto.stock_actual.is_(None), Producto.stock_minimo.is_(None)),
    ).count()

    valor_inventario = (
        db.query(func.sum(Producto.stock_actual * Producto.precio_compra))
        .filter(Producto.estado == "Activo")
        .scalar()
        or 0
    )

    fecha_limite = datetime.now() + timedelta(days=INVENTORY_CONFIG["dias_por_vencer"])

    productos_por_vencer = db.query(Lote).filter(
        Lote.fecha_vencimiento <= fecha_limite,
        Lote.cantidad_disponible > 0,
        Lote.estado == "Activo",
    ).count()

    return {
        "success": True,
        "message": "Estadísticas de inventario",
        "data": {
            "total_productos": total_productos,
            "valor_inventario": float(valor_inventario),
            "productos_por_vencer": productos_por_vencer,
            "stock": {
                "bajo": bajo,
                "normal": normal,
                "alto": alto,
                "sin_config": sin_config,
                "ratio_alto": ratio,
            },
            "config": INVENTORY_CONFIG,
        },
    }
