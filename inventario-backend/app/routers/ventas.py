"""Router para gestión de ventas."""

from datetime import datetime
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.core.auth_middleware import require_permission
from app.core.roles import Permission
from app.models import models, schemas
from app.models.database import get_db

router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.post("/", response_model=schemas.VentaResponse, status_code=status.HTTP_201_CREATED)
def crear_venta(
    venta: schemas.VentaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_permission(Permission.INVENTORY_WRITE)),
):
    """Crear una nueva venta con sus detalles."""
    # Verificar que el cliente existe
    cliente = db.query(models.Cliente).filter(models.Cliente.id_cliente == venta.id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Calcular totales
    subtotal = 0
    detalles_procesados = []

    for detalle in venta.detalles:
        # Verificar que el lote existe y tiene stock suficiente
        lote = db.query(models.Lote).filter(models.Lote.id_lote == detalle.id_lote).first()
        if not lote:
            raise HTTPException(status_code=404, detail=f"Lote {detalle.id_lote} no encontrado")
        # Conversión a int para evitar advertencias de tipado con ColumnElement
        if int(getattr(lote, "cantidad_disponible", 0)) < int(detalle.cantidad):
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para lote {detalle.id_lote}. Disponible: {getattr(lote, 'cantidad_disponible', 0)}",
            )

        # Calcular subtotal del detalle
        subtotal_detalle = detalle.precio_unitario * detalle.cantidad
        detalles_procesados.append(
            {
                "id_lote": detalle.id_lote,
                "cantidad": detalle.cantidad,
                "precio_unitario": detalle.precio_unitario,
                "subtotal": subtotal_detalle,
                "lote": lote,
            }
        )
        subtotal += subtotal_detalle

    # Calcular total
    total = subtotal - venta.descuento + venta.impuestos

    # Crear la venta
    db_venta = models.Venta(
        id_usuario=current_user.id_usuario,
        id_cliente=venta.id_cliente,
        fecha_venta=venta.fecha_venta or datetime.now(),
        subtotal=subtotal,
        descuento=venta.descuento,
        impuestos=venta.impuestos,
        total=total,
        metodo_pago=venta.metodo_pago,
        estado="Activo",
    )
    db.add(db_venta)
    db.flush()

    # Crear los detalles y actualizar stock
    for detalle_data in detalles_procesados:
        db_detalle = models.DetalleVenta(
            id_venta=db_venta.id_venta,
            id_lote=detalle_data["id_lote"],
            cantidad=detalle_data["cantidad"],
            precio_unitario=detalle_data["precio_unitario"],
            subtotal=detalle_data["subtotal"],
        )
        db.add(db_detalle)

        # Actualizar stock del lote
        lote = detalle_data["lote"]
        lote.cantidad_disponible -= detalle_data["cantidad"]

        # Actualizar stock del producto
        producto = (
            db.query(models.Producto)
            .filter(models.Producto.id_producto == lote.id_producto)
            .first()
        )
        if producto:
            producto.stock_actual -= detalle_data["cantidad"]

    db.commit()
    db.refresh(db_venta)

    return db_venta


@router.get("/", response_model=list[schemas.VentaResponse])
def listar_ventas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    mes: int | None = Query(None, ge=1, le=12),
    año: int | None = Query(None, ge=2000),
    id_cliente: int | None = None,
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_READ)),
):
    """Listar ventas con filtros opcionales."""
    query = db.query(models.Venta)

    if mes:
        query = query.filter(extract('month', models.Venta.fecha_venta) == mes)
    if año:
        query = query.filter(extract('year', models.Venta.fecha_venta) == año)
    if id_cliente:
        query = query.filter(models.Venta.id_cliente == id_cliente)

    ventas = query.order_by(models.Venta.fecha_venta.desc()).offset(skip).limit(limit).all()
    return ventas


@router.get("/{id_venta}", response_model=schemas.VentaResponse)
def obtener_venta(
    id_venta: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_READ)),
):
    """Obtener detalles de una venta específica."""
    venta = db.query(models.Venta).filter(models.Venta.id_venta == id_venta).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta


@router.get("/estadisticas/mes", response_model=schemas.VentaEstadisticasMes)
def estadisticas_ventas_mes(
    mes: int = Query(..., ge=1, le=12),
    año: int = Query(..., ge=2000),
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_READ)),
):
    """Obtener estadísticas de ventas de un mes específico."""
    resultado = (
        db.query(
            func.sum(models.Venta.total).label("total_ventas"),
            func.count(models.Venta.id_venta).label("cantidad_ventas"),
            func.avg(models.Venta.total).label("promedio_venta"),
        )
        .filter(
            extract('month', models.Venta.fecha_venta) == mes,
            extract('year', models.Venta.fecha_venta) == año,
            models.Venta.estado == "Activo",
        )
        .first()
    )

    return {
        "mes": mes,
        "año": año,
        "total_ventas": getattr(resultado, "total_ventas", 0.0) or 0.0,
        "cantidad_ventas": getattr(resultado, "cantidad_ventas", 0) or 0,
        "promedio_venta": getattr(resultado, "promedio_venta", 0.0) or 0.0,
    }


@router.get("/estadisticas/año", response_model=schemas.VentaEstadisticasAño)
def estadisticas_ventas_año(
    año: int = Query(..., ge=2000),
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_READ)),
):
    """Obtener estadísticas de ventas de un año completo."""
    # Estadísticas totales del año
    resultado_año = (
        db.query(
            func.sum(models.Venta.total).label("total_ventas"),
            func.count(models.Venta.id_venta).label("cantidad_ventas"),
        )
        .filter(extract('year', models.Venta.fecha_venta) == año, models.Venta.estado == "Activo")
        .first()
    )

    # Estadísticas por mes
    resultado_meses = (
        db.query(
            extract('month', models.Venta.fecha_venta).label("mes"),
            func.sum(models.Venta.total).label("total_ventas"),
            func.count(models.Venta.id_venta).label("cantidad_ventas"),
            func.avg(models.Venta.total).label("promedio_venta"),
        )
        .filter(extract('year', models.Venta.fecha_venta) == año, models.Venta.estado == "Activo")
        .group_by(extract('month', models.Venta.fecha_venta))
        .all()
    )

    meses = [
        {
            "mes": int(r.mes),
            "año": año,
            "total_ventas": r.total_ventas or 0.0,
            "cantidad_ventas": r.cantidad_ventas or 0,
            "promedio_venta": r.promedio_venta or 0.0,
        }
        for r in resultado_meses
    ]

    return {
        "año": año,
        "total_ventas": getattr(resultado_año, "total_ventas", 0.0) or 0.0,
        "cantidad_ventas": getattr(resultado_año, "cantidad_ventas", 0) or 0,
        "meses": meses,
    }


@router.patch("/{id_venta}", response_model=schemas.VentaResponse)
def actualizar_venta(
    id_venta: int,
    venta_update: schemas.VentaUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_WRITE)),
):
    """Actualizar estado de una venta (anular, etc.)."""
    venta = db.query(models.Venta).filter(models.Venta.id_venta == id_venta).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    if venta_update.estado:
        cast(Any, venta).estado = venta_update.estado

    db.commit()
    db.refresh(venta)
    return venta
