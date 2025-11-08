"""Router para gestión de entradas (compras/recepciones)."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth_middleware import require_permission
from app.core.roles import Permission
from app.models import models
from app.models.database import get_db

router = APIRouter(prefix="/entradas", tags=["Entradas"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_entrada(
    id_lote: int,
    cantidad: int,
    precio_compra_unitario: float,
    fecha_entrada: datetime | None = None,
    numero_factura_compra: str | None = None,
    proveedor: str | None = None,
    observaciones: str | None = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_permission(Permission.INVENTORY_WRITE)),
):
    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="Cantidad debe ser mayor a 0")
    if precio_compra_unitario < 0:
        raise HTTPException(status_code=400, detail="Precio unitario inválido")

    lote = db.query(models.Lote).filter(models.Lote.id_lote == id_lote).first()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")

    # Crear entrada
    fecha = fecha_entrada or datetime.now()
    precio_total = float(precio_compra_unitario) * int(cantidad)
    entrada = models.Entrada(
        id_usuario=current_user.id_usuario,
        id_lote=lote.id_lote,
        cantidad=int(cantidad),
        fecha_entrada=fecha,
        precio_compra_unitario=float(precio_compra_unitario),
        precio_compra_total=precio_total,
        numero_factura_compra=numero_factura_compra,
        proveedor=proveedor,
        observaciones=observaciones,
    )
    db.add(entrada)

    # Actualizar stock del lote y del producto
    lote.cantidad_disponible = int(getattr(lote, "cantidad_disponible", 0)) + int(cantidad)  # type: ignore[assignment]
    producto = (
        db.query(models.Producto).filter(models.Producto.id_producto == lote.id_producto).first()
    )
    if producto:
        producto.stock_actual = int(getattr(producto, "stock_actual", 0)) + int(cantidad)  # type: ignore[assignment]

    db.commit()
    db.refresh(entrada)
    return entrada


@router.get("/", response_model=list[dict])
def listar_entradas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    id_lote: int | None = None,
    mes: int | None = Query(None, ge=1, le=12),
    año: int | None = Query(None, alias="año"),
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_READ)),
):
    from sqlalchemy import extract

    q = db.query(models.Entrada)
    if id_lote:
        q = q.filter(models.Entrada.id_lote == id_lote)
    if mes:
        q = q.filter(extract("month", models.Entrada.fecha_entrada) == mes)
    if año:
        q = q.filter(extract("year", models.Entrada.fecha_entrada) == año)
    entradas = q.order_by(models.Entrada.fecha_entrada.desc()).offset(skip).limit(limit).all()
    # Serialización simple compatible con el frontend actual
    return [
        {
            "id_entrada": e.id_entrada,
            "id_lote": e.id_lote,
            "cantidad": e.cantidad,
            "fecha_entrada": e.fecha_entrada,
            "precio_compra_unitario": e.precio_compra_unitario,
            "precio_compra_total": e.precio_compra_total,
            "numero_factura_compra": e.numero_factura_compra,
            "proveedor": e.proveedor,
            "observaciones": e.observaciones,
        }
        for e in entradas
    ]


@router.get("/{id_entrada}", response_model=dict)
def obtener_entrada(
    id_entrada: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_READ)),
):
    e = db.query(models.Entrada).filter(models.Entrada.id_entrada == id_entrada).first()
    if not e:
        raise HTTPException(status_code=404, detail="Entrada no encontrada")
    return {
        "id_entrada": e.id_entrada,
        "id_lote": e.id_lote,
        "cantidad": e.cantidad,
        "fecha_entrada": e.fecha_entrada,
        "precio_compra_unitario": e.precio_compra_unitario,
        "precio_compra_total": e.precio_compra_total,
        "numero_factura_compra": e.numero_factura_compra,
        "proveedor": e.proveedor,
        "observaciones": e.observaciones,
    }


@router.get("/estadisticas/mes", response_model=dict)
def estadisticas_entradas_mes(
    mes: int = Query(..., ge=1, le=12),
    año: int = Query(..., alias="año"),
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_READ)),
):
    from sqlalchemy import extract, func

    q = db.query(
        func.count(models.Entrada.id_entrada).label("cantidad_entradas"),
        func.sum(models.Entrada.precio_compra_total).label("total_compras"),
        func.avg(models.Entrada.precio_compra_total).label("promedio_entrada"),
        func.sum(models.Entrada.cantidad).label("total_unidades"),
    ).filter(
        extract("month", models.Entrada.fecha_entrada) == mes,
        extract("year", models.Entrada.fecha_entrada) == año,
    )
    result = q.first()
    return {
        "mes": mes,
        "año": año,
        "cantidad_entradas": int(getattr(result, "cantidad_entradas", 0) or 0),
        "total_compras": float(getattr(result, "total_compras", 0) or 0),
        "promedio_entrada": float(getattr(result, "promedio_entrada", 0) or 0),
        "total_unidades": int(getattr(result, "total_unidades", 0) or 0),
    }


@router.get("/estadisticas/año", response_model=dict)
def estadisticas_entradas_año(
    año: int = Query(..., alias="año"),
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_READ)),
):
    from sqlalchemy import extract, func

    q = db.query(
        func.count(models.Entrada.id_entrada).label("cantidad_entradas"),
        func.sum(models.Entrada.precio_compra_total).label("total_compras"),
        func.avg(models.Entrada.precio_compra_total).label("promedio_entrada"),
        func.sum(models.Entrada.cantidad).label("total_unidades"),
    ).filter(
        extract("year", models.Entrada.fecha_entrada) == año,
    )
    result = q.first()
    return {
        "año": año,
        "cantidad_entradas": int(getattr(result, "cantidad_entradas", 0) or 0),
        "total_compras": float(getattr(result, "total_compras", 0) or 0),
        "promedio_entrada": float(getattr(result, "promedio_entrada", 0) or 0),
        "total_unidades": int(getattr(result, "total_unidades", 0) or 0),
    }
