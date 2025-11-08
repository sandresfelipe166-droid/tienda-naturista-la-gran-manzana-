"""Router para gestión de cotizaciones."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import extract
from sqlalchemy.orm import Session

from app.core.auth_middleware import require_permission
from app.core.roles import Permission
from app.models import models, schemas
from app.models.database import get_db

router = APIRouter(prefix="/cotizaciones", tags=["Cotizaciones"])


def generar_numero_cotizacion(db: Session, año: int) -> str:
    """Generar número de cotizaci ón auto-incrementable por año."""
    # Obtener el último número de cotización del año
    ultima_cotizacion = (
        db.query(models.Cotizacion)
        .filter(extract('year', models.Cotizacion.fecha_cotizacion) == año)
        .order_by(models.Cotizacion.id_cotizacion.desc())
        .first()
    )

    if ultima_cotizacion is not None and getattr(ultima_cotizacion, "numero_cotizacion", None):
        # Extraer el número secuencial
        partes = ultima_cotizacion.numero_cotizacion.split('-')
        if len(partes) == 3:
            ultimo_numero = int(partes[2])
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
    else:
        nuevo_numero = 1

    return f"COT-{año}-{nuevo_numero:05d}"


@router.post("/", response_model=schemas.CotizacionResponse, status_code=status.HTTP_201_CREATED)
def crear_cotizacion(
    cotizacion: schemas.CotizacionCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_permission(Permission.PRODUCT_WRITE)),
):
    """Crear una nueva cotización."""
    # Verificar que el cliente existe
    cliente = (
        db.query(models.Cliente).filter(models.Cliente.id_cliente == cotizacion.id_cliente).first()
    )
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Calcular totales
    subtotal = 0
    detalles_procesados = []

    for detalle in cotizacion.detalles:
        # Verificar que el producto existe
        producto = (
            db.query(models.Producto)
            .filter(models.Producto.id_producto == detalle.id_producto)
            .first()
        )
        if not producto:
            raise HTTPException(
                status_code=404, detail=f"Producto {detalle.id_producto} no encontrado"
            )

        # Calcular subtotal del detalle
        subtotal_detalle = detalle.precio_unitario * detalle.cantidad
        detalles_procesados.append(
            {
                "id_producto": detalle.id_producto,
                "cantidad": detalle.cantidad,
                "precio_unitario": detalle.precio_unitario,
                "subtotal": subtotal_detalle,
            }
        )
        subtotal += subtotal_detalle

    # Calcular total
    total = subtotal - cotizacion.descuento + cotizacion.impuestos

    # Generar número de cotización si no se provee
    fecha_cot = cotizacion.fecha_cotizacion or datetime.now()
    numero_cot = cotizacion.numero_cotizacion or generar_numero_cotizacion(db, fecha_cot.year)

    # Crear la cotización
    db_cotizacion = models.Cotizacion(
        id_usuario=current_user.id_usuario,
        id_cliente=cotizacion.id_cliente,
        numero_cotizacion=numero_cot,
        fecha_cotizacion=fecha_cot,
        fecha_vencimiento=cotizacion.fecha_vencimiento,
        subtotal=subtotal,
        descuento=cotizacion.descuento,
        impuestos=cotizacion.impuestos,
        total=total,
        estado="Pendiente",
        observaciones=cotizacion.observaciones,
    )
    db.add(db_cotizacion)
    db.flush()

    # Crear los detalles
    for detalle_data in detalles_procesados:
        db_detalle = models.DetalleCotizacion(
            id_cotizacion=db_cotizacion.id_cotizacion, **detalle_data
        )
        db.add(db_detalle)

    db.commit()
    db.refresh(db_cotizacion)

    return db_cotizacion


@router.get("/", response_model=list[schemas.CotizacionResponse])
def listar_cotizaciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    estado: str | None = None,
    mes: int | None = Query(None, ge=1, le=12),
    año: int | None = Query(None, ge=2000),
    id_cliente: int | None = None,
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.PRODUCT_READ)),
):
    """Listar cotizaciones con filtros opcionales."""
    query = db.query(models.Cotizacion)

    if estado:
        query = query.filter(models.Cotizacion.estado == estado)
    if mes:
        query = query.filter(extract('month', models.Cotizacion.fecha_cotizacion) == mes)
    if año:
        query = query.filter(extract('year', models.Cotizacion.fecha_cotizacion) == año)
    if id_cliente:
        query = query.filter(models.Cotizacion.id_cliente == id_cliente)

    cotizaciones = (
        query.order_by(models.Cotizacion.fecha_cotizacion.desc()).offset(skip).limit(limit).all()
    )
    return cotizaciones


@router.get("/estadisticas", response_model=schemas.CotizacionEstadisticas)
def estadisticas_cotizaciones(
    año: int | None = Query(None, ge=2000),
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.PRODUCT_READ)),
):
    """Obtener estadísticas de cotizaciones."""
    query = db.query(models.Cotizacion)

    if año:
        query = query.filter(extract('year', models.Cotizacion.fecha_cotizacion) == año)

    total = query.count()
    pendientes = query.filter(models.Cotizacion.estado == "Pendiente").count()
    aceptadas = query.filter(models.Cotizacion.estado == "Aceptada").count()
    rechazadas = query.filter(models.Cotizacion.estado == "Rechazada").count()
    convertidas = query.filter(models.Cotizacion.estado == "Convertida").count()

    tasa_conversion = (convertidas / total * 100) if total > 0 else 0.0

    return {
        "total_cotizaciones": total,
        "pendientes": pendientes,
        "aceptadas": aceptadas,
        "rechazadas": rechazadas,
        "convertidas": convertidas,
        "tasa_conversion": tasa_conversion,
    }


@router.get("/{id_cotizacion}", response_model=schemas.CotizacionResponse)
def obtener_cotizacion(
    id_cotizacion: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.PRODUCT_READ)),
):
    """Obtener detalles de una cotización específica."""
    cotizacion = (
        db.query(models.Cotizacion).filter(models.Cotizacion.id_cotizacion == id_cotizacion).first()
    )
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotizacion no encontrada")
    return cotizacion


@router.patch("/{id_cotizacion}", response_model=schemas.CotizacionResponse)
def actualizar_cotizacion(
    id_cotizacion: int,
    cotizacion_update: schemas.CotizacionUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.PRODUCT_WRITE)),
):
    """Actualizar estado de una cotización."""
    cotizacion = (
        db.query(models.Cotizacion).filter(models.Cotizacion.id_cotizacion == id_cotizacion).first()
    )
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    update_data = cotizacion_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cotizacion, field, value)

    db.commit()
    db.refresh(cotizacion)
    return cotizacion


@router.post("/{id_cotizacion}/convertir-venta", response_model=schemas.VentaResponse)
def convertir_cotizacion_a_venta(
    id_cotizacion: int,
    metodo_pago: str,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_permission(Permission.INVENTORY_WRITE)),
):
    """Convertir una cotización en una venta."""
    cotizacion = (
        db.query(models.Cotizacion).filter(models.Cotizacion.id_cotizacion == id_cotizacion).first()
    )
    if not cotizacion:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")

    estado_actual = getattr(cotizacion, "estado", None)
    if estado_actual not in ("Pendiente", "Aceptada"):
        raise HTTPException(
            status_code=400, detail="Solo se pueden convertir cotizaciones pendientes o aceptadas"
        )

    # Crear la venta
    db_venta = models.Venta(
        id_usuario=current_user.id_usuario,
        id_cliente=cotizacion.id_cliente,
        fecha_venta=datetime.now(),
        subtotal=cotizacion.subtotal,
        descuento=cotizacion.descuento,
        impuestos=cotizacion.impuestos,
        total=cotizacion.total,
        metodo_pago=metodo_pago,
        estado="Activo",
    )
    db.add(db_venta)
    db.flush()

    # Convertir detalles de cotización a detalles de venta
    # Nota: Esto requiere encontrar lotes disponibles para cada producto
    for detalle_cot in cotizacion.detalles:
        # Buscar un lote disponible para este producto
        lote = (
            db.query(models.Lote)
            .filter(
                models.Lote.id_producto == detalle_cot.id_producto,
                models.Lote.cantidad_disponible >= detalle_cot.cantidad,
                models.Lote.estado == "Activo",
            )
            .first()
        )

        if not lote:
            raise HTTPException(
                status_code=400,
                detail=f"No hay stock suficiente para el producto {detalle_cot.id_producto}",
            )

        db_detalle = models.DetalleVenta(
            id_venta=db_venta.id_venta,
            id_lote=lote.id_lote,
            cantidad=detalle_cot.cantidad,
            precio_unitario=detalle_cot.precio_unitario,
            subtotal=detalle_cot.subtotal,
        )
        db.add(db_detalle)

        # Actualizar stock
        lote.cantidad_disponible -= detalle_cot.cantidad
        producto = (
            db.query(models.Producto)
            .filter(models.Producto.id_producto == lote.id_producto)
            .first()
        )
        if producto:
            producto.stock_actual -= detalle_cot.cantidad

    # Actualizar cotización
    cotizacion.estado = "Convertida"  # type: ignore[assignment]
    cotizacion.id_venta_relacionada = db_venta.id_venta  # type: ignore[assignment]

    db.commit()
    db.refresh(db_venta)

    return db_venta
