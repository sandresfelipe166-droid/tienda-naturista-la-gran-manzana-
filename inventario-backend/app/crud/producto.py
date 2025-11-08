from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.models import Laboratorio, Lote, Producto, Seccion
from app.models.schemas import ProductoCreate, ProductoUpdate


def _build_productos_query(
    db: Session,
    nombre: str | None = None,
    id_seccion: int | None = None,
    id_laboratorio: int | None = None,
    estado: str | None = None,
):
    query = db.query(Producto)
    if nombre:
        query = query.filter(Producto.nombre_producto.ilike(f"%{nombre}%"))
    if id_seccion:
        query = query.filter(Producto.id_seccion == id_seccion)
    if id_laboratorio:
        query = query.filter(Producto.id_laboratorio == id_laboratorio)
    if estado:
        query = query.filter(Producto.estado == estado)
    return query


def count_productos(
    db: Session,
    nombre: str | None = None,
    id_seccion: int | None = None,
    id_laboratorio: int | None = None,
    estado: str | None = None,
) -> int:
    return _build_productos_query(db, nombre, id_seccion, id_laboratorio, estado).count()


def get_productos(db: Session, params: dict[str, Any]) -> list[Producto]:
    """Obtener lista de productos con filtros opcionales"""
    skip = params.get('skip', 0)
    limit = params.get('limit', 100)
    nombre = params.get('nombre')
    id_seccion = params.get('id_seccion')
    id_laboratorio = params.get('id_laboratorio')
    estado = params.get('estado')

    query = _build_productos_query(db, nombre, id_seccion, id_laboratorio, estado)
    return query.offset(skip).limit(limit).all()


def get_producto_by_id(db: Session, id_producto: int) -> Producto | None:
    """Obtener un producto por ID"""
    return db.query(Producto).filter(Producto.id_producto == id_producto).first()


def create_producto(db: Session, producto_data: ProductoCreate) -> Producto:
    """Crear un nuevo producto"""
    seccion = db.query(Seccion).filter(Seccion.id_seccion == producto_data.id_seccion).first()
    if not seccion:
        raise ValueError("La sección especificada no existe")

    laboratorio = (
        db.query(Laboratorio)
        .filter(Laboratorio.id_laboratorio == producto_data.id_laboratorio)
        .first()
    )
    if not laboratorio:
        raise ValueError("El laboratorio especificado no existe")

    db_producto = Producto(**producto_data.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto


def update_producto(
    db: Session, id_producto: int, producto_data: ProductoUpdate
) -> Producto | None:
    """Actualizar un producto existente"""
    producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
    if not producto:
        return None

    if producto_data.id_seccion is not None:
        seccion = db.query(Seccion).filter(Seccion.id_seccion == producto_data.id_seccion).first()
        if not seccion:
            raise ValueError("La sección especificada no existe")

    if producto_data.id_laboratorio is not None:
        laboratorio = (
            db.query(Laboratorio)
            .filter(Laboratorio.id_laboratorio == producto_data.id_laboratorio)
            .first()
        )
        if not laboratorio:
            raise ValueError("El laboratorio especificado no existe")

    update_data = producto_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(producto, field, value)

    db.commit()
    db.refresh(producto)
    return producto


def delete_producto(db: Session, id_producto: int, logical: bool = True) -> bool:
    """Eliminar un producto (lógico o físico)"""
    producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
    if not producto:
        return False

    if logical:
        producto.estado = "Inactivo"  # type: ignore[assignment]
        db.commit()
    else:
        db.delete(producto)
        db.commit()

    return True


def search_productos(db: Session, query: str, skip: int = 0, limit: int = 50) -> list[Producto]:
    """Buscar productos por nombre, principio activo o descripción"""
    search_filter = f"%{query}%"
    return (
        db.query(Producto)
        .filter(
            or_(
                Producto.nombre_producto.ilike(search_filter),
                Producto.principio_activo.ilike(search_filter),
                Producto.descripcion.ilike(search_filter),
            ),
            Producto.estado == "Activo",
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_productos_bajo_stock(db: Session) -> list[Producto]:
    """Obtener productos con stock actual menor o igual al mínimo, activos"""
    return (
        db.query(Producto)
        .filter(
            Producto.estado == "Activo",
            Producto.stock_actual <= Producto.stock_minimo,
        )
        .all()
    )


def get_total_productos_activos(db: Session) -> int:
    """Contar productos activos"""
    return db.query(Producto).filter(Producto.estado == "Activo").count()


def get_valor_total_stock(db: Session) -> float:
    """Calcular el valor total del stock (stock_actual * precio_compra) para productos activos"""
    total_valor = (
        db.query(func.sum(Producto.stock_actual * Producto.precio_compra))
        .filter(Producto.estado == "Activo")
        .scalar()
    )
    return total_valor or 0.0


def count_productos_bajo_stock(db: Session) -> int:
    """Contar productos con stock bajo"""
    return (
        db.query(Producto)
        .filter(Producto.estado == "Activo", Producto.stock_actual <= Producto.stock_minimo)
        .count()
    )


def get_productos_por_vencer(db: Session, dias: int = 30) -> list[Producto]:
    """Obtener productos que tienen lotes que vencen en los próximos 'dias' días"""
    fecha_limite = datetime.utcnow() + timedelta(days=dias)
    # Join con Lote para identificar productos con lotes próximos a vencer
    return (
        db.query(Producto)
        .join(Lote, Lote.id_producto == Producto.id_producto)
        .filter(
            Producto.estado == "Activo",
            Lote.estado == "Activo",
            Lote.cantidad_disponible > 0,
            Lote.fecha_vencimiento <= fecha_limite,
        )
        .distinct()
        .all()
    )
