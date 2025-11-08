import csv
import io
from typing import Any

from sqlalchemy.orm import Session, joinedload

from app.core import cache as cache_mod
from app.models.filters import (
    ProductoFilters,
    apply_exact_filter,
    apply_range_filter,
    apply_text_filter,
)
from app.models.models import Laboratorio, Producto, Seccion


def _build_productos_query(db: Session, filters: ProductoFilters):
    """
    Construye un query SQLAlchemy para productos aplicando los mismos filtros
    que usamos en las consultas avanzadas, incluyendo joins para laboratorio y sección.
    """
    query = db.query(Producto).options(
        joinedload(Producto.laboratorio),
        joinedload(Producto.seccion),
    )

    # Filtros de texto y exactos
    query = apply_text_filter(query, Producto.nombre_producto, filters.nombre)
    query = apply_text_filter(query, Producto.principio_activo, filters.principio_activo)
    query = apply_exact_filter(query, Producto.codigo_barras, filters.codigo_barras)

    # Relaciones
    query = apply_exact_filter(query, Producto.id_laboratorio, filters.id_laboratorio)
    query = apply_exact_filter(query, Producto.id_seccion, filters.id_seccion)

    # Rangos
    query = apply_range_filter(
        query, Producto.precio_compra, filters.precio_min, filters.precio_max
    )
    query = apply_range_filter(query, Producto.stock_actual, filters.stock_min, filters.stock_max)

    # Booleanos
    if bool(filters.stock_bajo):
        query = query.filter(Producto.stock_actual <= Producto.stock_minimo)
    query = apply_exact_filter(query, Producto.requiere_receta, filters.requiere_receta)
    query = apply_exact_filter(query, Producto.forma_farmaceutica, filters.forma_farmaceutica)

    # Estado
    if filters.estado:
        query = query.filter(Producto.estado == filters.estado)

    return query


def _safe_str(value: Any) -> str:
    return "" if value is None else str(value)


def _safe_bool(value: Any) -> bool:
    try:
        return bool(value)
    except Exception:
        return False


def _safe_float(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except Exception:
        return None


def _producto_row(p: Producto) -> list[str]:
    """
    Convierte un producto a una fila CSV en el orden de columnas definido.
    Fuerza tipos de salida a str para cumplir con la firma.
    """
    precio = _safe_float(getattr(p, "precio_compra", None))
    requiere_receta = _safe_bool(getattr(p, "requiere_receta", False))
    return [
        _safe_str(getattr(p, "id_producto", "")),
        _safe_str(getattr(p, "nombre_producto", "")),
        _safe_str(getattr(p, "principio_activo", "")),
        _safe_str(getattr(p, "forma_farmaceutica", "")),
        _safe_str(getattr(p, "codigo_barras", "")),
        "Sí" if requiere_receta else "No",
        f"{precio:.2f}" if precio is not None else "",
        _safe_str(getattr(p, "stock_actual", 0)),
        _safe_str(getattr(p, "stock_minimo", 0)),
        _safe_str(getattr(p, "estado", "")),
        _safe_str(getattr(getattr(p, "laboratorio", None), "nombre_laboratorio", "")),
        _safe_str(getattr(getattr(p, "seccion", None), "nombre_seccion", "")),
    ]


@cache_mod.cache_manager.cache_result(ttl=120, key_prefix="export:productos")
def generate_productos_csv(db: Session, filters: ProductoFilters) -> bytes:
    """
    Genera un CSV completo de productos aplicando filtros.
    El resultado se devuelve como bytes (contenido del archivo CSV).
    Se cachea por 120 segundos para peticiones idénticas.
    """
    query = _build_productos_query(db, filters)
    productos = query.order_by(Producto.nombre_producto.asc()).all()

    output = io.StringIO(newline="")
    writer = csv.writer(output)
    # Cabeceras
    writer.writerow(
        [
            "ID",
            "Nombre",
            "Principio Activo",
            "Forma Farmacéutica",
            "Código Barras",
            "Requiere Receta",
            "Precio Compra",
            "Stock Actual",
            "Stock Mínimo",
            "Estado",
            "Laboratorio",
            "Sección",
        ]
    )

    for p in productos:
        writer.writerow(_producto_row(p))

    return output.getvalue().encode("utf-8")


@cache_mod.cache_manager.cache_result(ttl=120, key_prefix="export:laboratorios")
def generate_laboratorios_csv(db: Session) -> bytes:
    """
    Genera un CSV sencillo con información de laboratorios y el total de productos asociados.
    """
    laboratorios = db.query(Laboratorio).options(joinedload(Laboratorio.productos)).all()

    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(
        [
            "ID",
            "Nombre",
            "País Origen",
            "Teléfono",
            "Email",
            "Dirección",
            "Estado",
            "Total Productos",
        ]
    )

    for lab in laboratorios:
        writer.writerow(
            [
                _safe_str(getattr(lab, "id_laboratorio", "")),
                _safe_str(getattr(lab, "nombre_laboratorio", "")),
                _safe_str(getattr(lab, "pais_origen", "")),
                _safe_str(getattr(lab, "telefono", "")),
                _safe_str(getattr(lab, "email", "")),
                _safe_str(getattr(lab, "direccion", "")),
                _safe_str(getattr(lab, "estado", "")),
                _safe_str(len(getattr(lab, "productos", []) or [])),
            ]
        )

    return output.getvalue().encode("utf-8")


@cache_mod.cache_manager.cache_result(ttl=120, key_prefix="export:secciones")
def generate_secciones_csv(db: Session) -> bytes:
    """
    Genera un CSV sencillo con información de secciones y el total de productos asociados.
    """
    secciones = db.query(Seccion).options(joinedload(Seccion.productos)).all()

    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(
        [
            "ID",
            "Nombre",
            "Descripción",
            "Ubicación",
            "Capacidad Máxima",
            "Temperatura Recomendada",
            "Estado",
            "Total Productos",
        ]
    )

    for sec in secciones:
        writer.writerow(
            [
                _safe_str(getattr(sec, "id_seccion", "")),
                _safe_str(getattr(sec, "nombre_seccion", "")),
                _safe_str(getattr(sec, "descripcion", "")),
                _safe_str(getattr(sec, "ubicacion_fisica", "")),
                _safe_str(getattr(sec, "capacidad_maxima", 0)),
                _safe_str(getattr(sec, "temperatura_recomendada", "")),
                _safe_str(getattr(sec, "estado", "")),
                _safe_str(len(getattr(sec, "productos", []) or [])),
            ]
        )

    return output.getvalue().encode("utf-8")
