"""
CRUD avanzado para productos con filtros, paginación y caché
"""

from typing import Any

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.filters import (
    ProductoFilters,
    apply_exact_filter,
    apply_range_filter,
    apply_text_filter,
)
from app.models.models import Laboratorio, Producto, Seccion
from app.models.pagination import PaginationParams, create_paginated_response, paginate_query


def get_productos_advanced(
    db: Session,
    filters: ProductoFilters,
    pagination: PaginationParams,
    sort_by: str = "nombre_producto",
    order: str = "asc",
) -> dict[str, Any]:
    """
    Obtener productos con filtros avanzados y paginación

    Args:
        db: Sesión de base de datos
        filters: Filtros a aplicar
        pagination: Parámetros de paginación
        sort_by: Campo por el cual ordenar
        order: Dirección del ordenamiento (asc/desc)

    Returns:
        Dict con datos paginados y metadata
    """
    # Construir query base con joins para optimizar
    query = db.query(Producto).options(
        joinedload(Producto.laboratorio), joinedload(Producto.seccion)
    )

    # Aplicar filtros de texto
    query = apply_text_filter(query, Producto.nombre_producto, filters.nombre)
    query = apply_text_filter(query, Producto.principio_activo, filters.principio_activo)
    query = apply_exact_filter(query, Producto.codigo_barras, filters.codigo_barras)

    # Aplicar filtros por relaciones
    query = apply_exact_filter(query, Producto.id_laboratorio, filters.id_laboratorio)
    query = apply_exact_filter(query, Producto.id_seccion, filters.id_seccion)

    # Aplicar filtros de rango
    query = apply_range_filter(
        query, Producto.precio_compra, filters.precio_min, filters.precio_max
    )
    query = apply_range_filter(query, Producto.stock_actual, filters.stock_min, filters.stock_max)

    # Aplicar filtros booleanos
    if filters.stock_bajo:
        query = query.filter(Producto.stock_actual <= Producto.stock_minimo)

    query = apply_exact_filter(query, Producto.requiere_receta, filters.requiere_receta)
    query = apply_exact_filter(query, Producto.forma_farmaceutica, filters.forma_farmaceutica)

    # Aplicar filtro de estado
    if filters.estado:
        query = query.filter(Producto.estado == filters.estado)

    # Aplicar ordenamiento seguro
    allowed_sort_fields = {
        "id_producto",
        "nombre_producto",
        "precio_compra",
        "stock_actual",
        "stock_minimo",
        "estado",
        "codigo_barras",
        "requiere_receta",
        "forma_farmaceutica",
        "principio_activo",
        "id_laboratorio",
        "id_seccion",
    }
    sort_field = sort_by if sort_by in allowed_sort_fields else "nombre_producto"
    order_column = getattr(Producto, sort_field)
    if str(order).lower() == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())

    # Aplicar paginación
    items, total = paginate_query(query, pagination.page, pagination.size)

    # Crear respuesta paginada
    return create_paginated_response(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size,
        message="Productos obtenidos exitosamente",
    )


def search_productos_advanced(
    db: Session,
    search_term: str,
    pagination: PaginationParams,
    filters: ProductoFilters | None = None,
) -> dict[str, Any]:
    """
    Búsqueda avanzada de productos con múltiples campos

    Args:
        db: Sesión de base de datos
        search_term: Término de búsqueda
        pagination: Parámetros de paginación
        filters: Filtros adicionales opcionales

    Returns:
        Dict con resultados paginados
    """
    # Query base con búsqueda en múltiples campos
    search_filter = f"%{search_term}%"
    query = (
        db.query(Producto)
        .options(joinedload(Producto.laboratorio), joinedload(Producto.seccion))
        .filter(
            or_(
                Producto.nombre_producto.ilike(search_filter),
                Producto.principio_activo.ilike(search_filter),
                Producto.descripcion.ilike(search_filter),
                Producto.codigo_barras.ilike(search_filter),
                Producto.forma_farmaceutica.ilike(search_filter),
            )
        )
    )

    # Aplicar filtros adicionales si se proporcionan
    if filters:
        if filters.id_laboratorio:
            query = query.filter(Producto.id_laboratorio == filters.id_laboratorio)
        if filters.id_seccion:
            query = query.filter(Producto.id_seccion == filters.id_seccion)
        if filters.estado:
            query = query.filter(Producto.estado == filters.estado)
        if filters.requiere_receta is not None:
            query = query.filter(Producto.requiere_receta == filters.requiere_receta)

    # Ordenar por relevancia (productos que coinciden en nombre primero)
    query = query.order_by(
        Producto.nombre_producto.ilike(search_filter).desc(), Producto.nombre_producto.asc()
    )

    # Aplicar paginación
    items, total = paginate_query(query, pagination.page, pagination.size)

    return create_paginated_response(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size,
        message=f"Se encontraron {total} productos",
    )


def get_productos_stats(db: Session, filters: ProductoFilters | None = None) -> dict[str, Any]:
    """
    Obtener estadísticas de productos con filtros opcionales

    Args:
        db: Sesión de base de datos
        filters: Filtros opcionales

    Returns:
        Dict con estadísticas
    """
    query = db.query(Producto)

    # Aplicar filtros si se proporcionan
    if filters:
        if filters.id_laboratorio:
            query = query.filter(Producto.id_laboratorio == filters.id_laboratorio)
        if filters.id_seccion:
            query = query.filter(Producto.id_seccion == filters.id_seccion)
        if filters.estado:
            query = query.filter(Producto.estado == filters.estado)

    # Calcular estadísticas
    total_productos = query.count()

    productos_activos = query.filter(Producto.estado == "Activo").count()

    productos_bajo_stock = query.filter(
        Producto.estado == "Activo", Producto.stock_actual <= Producto.stock_minimo
    ).count()

    valor_total = (
        db.query(func.sum(Producto.stock_actual * Producto.precio_compra))
        .filter(Producto.estado == "Activo")
        .scalar()
        or 0.0
    )

    stock_total = (
        db.query(func.sum(Producto.stock_actual)).filter(Producto.estado == "Activo").scalar() or 0
    )

    precio_promedio = (
        db.query(func.avg(Producto.precio_compra)).filter(Producto.estado == "Activo").scalar()
        or 0.0
    )

    return {
        "total_productos": total_productos,
        "productos_activos": productos_activos,
        "productos_inactivos": total_productos - productos_activos,
        "productos_bajo_stock": productos_bajo_stock,
        "valor_total_inventario": round(float(valor_total), 2),
        "stock_total": int(stock_total),
        "precio_promedio": round(float(precio_promedio), 2),
        "porcentaje_bajo_stock": round(
            (productos_bajo_stock / productos_activos * 100) if productos_activos > 0 else 0, 2
        ),
    }


def get_top_productos(db: Session, limit: int = 10, criterio: str = "stock") -> list[Producto]:
    """
    Obtener top productos según criterio

    Args:
        db: Sesión de base de datos
        limit: Número de productos a retornar
        criterio: Criterio de ordenamiento (stock, precio, nombre)

    Returns:
        Lista de productos
    """
    query = db.query(Producto).filter(Producto.estado == "Activo")

    if criterio == "stock":
        query = query.order_by(Producto.stock_actual.desc())
    elif criterio == "precio":
        query = query.order_by(Producto.precio_compra.desc())
    elif criterio == "stock_bajo":
        query = query.filter(Producto.stock_actual <= Producto.stock_minimo).order_by(
            Producto.stock_actual.asc()
        )
    else:
        query = query.order_by(Producto.nombre_producto.asc())

    return query.limit(limit).all()


def get_productos_por_laboratorio_stats(db: Session) -> list[dict[str, Any]]:
    """
    Obtener estadísticas de productos agrupados por laboratorio

    Returns:
        Lista de diccionarios con estadísticas por laboratorio
    """
    results = (
        db.query(
            Laboratorio.nombre_laboratorio,
            func.count(Producto.id_producto).label('total_productos'),
            func.sum(Producto.stock_actual).label('stock_total'),
            func.sum(Producto.stock_actual * Producto.precio_compra).label('valor_total'),
        )
        .join(Producto, Producto.id_laboratorio == Laboratorio.id_laboratorio)
        .filter(Producto.estado == "Activo")
        .group_by(Laboratorio.nombre_laboratorio)
        .order_by(func.count(Producto.id_producto).desc())
        .all()
    )

    return [
        {
            "laboratorio": r.nombre_laboratorio,
            "total_productos": r.total_productos,
            "stock_total": int(r.stock_total or 0),
            "valor_total": round(float(r.valor_total or 0), 2),
        }
        for r in results
    ]


def get_productos_por_seccion_stats(db: Session) -> list[dict[str, Any]]:
    """
    Obtener estadísticas de productos agrupados por sección

    Returns:
        Lista de diccionarios con estadísticas por sección
    """
    results = (
        db.query(
            Seccion.nombre_seccion,
            func.count(Producto.id_producto).label('total_productos'),
            func.sum(Producto.stock_actual).label('stock_total'),
            func.sum(Producto.stock_actual * Producto.precio_compra).label('valor_total'),
        )
        .join(Producto, Producto.id_seccion == Seccion.id_seccion)
        .filter(Producto.estado == "Activo")
        .group_by(Seccion.nombre_seccion)
        .order_by(func.count(Producto.id_producto).desc())
        .all()
    )

    return [
        {
            "seccion": r.nombre_seccion,
            "total_productos": r.total_productos,
            "stock_total": int(r.stock_total or 0),
            "valor_total": round(float(r.valor_total or 0), 2),
        }
        for r in results
    ]
