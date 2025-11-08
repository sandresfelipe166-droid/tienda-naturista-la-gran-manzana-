"""
Modelos y utilidades para filtros avanzados
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductoFilters(BaseModel):
    """Filtros avanzados para productos"""

    # Búsqueda por texto
    nombre: str | None = Field(default=None, description="Buscar por nombre (parcial)")
    codigo_barras: str | None = Field(default=None, description="Buscar por código de barras")
    principio_activo: str | None = Field(default=None, description="Buscar por principio activo")

    # Filtros por relaciones
    id_laboratorio: int | None = Field(default=None, description="Filtrar por laboratorio")
    id_seccion: int | None = Field(default=None, description="Filtrar por sección")

    # Filtros por rangos
    precio_min: float | None = Field(default=None, ge=0, description="Precio mínimo")
    precio_max: float | None = Field(default=None, ge=0, description="Precio máximo")
    stock_min: int | None = Field(default=None, ge=0, description="Stock mínimo")
    stock_max: int | None = Field(default=None, ge=0, description="Stock máximo")

    # Filtros booleanos
    stock_bajo: bool | None = Field(default=None, description="Solo productos con stock bajo")
    requiere_receta: bool | None = Field(default=None, description="Filtrar por receta requerida")

    # Filtros por estado
    estado: str | None = Field(default="Activo", description="Estado del producto")
    forma_farmaceutica: str | None = Field(default=None, description="Forma farmacéutica")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "paracetamol",
                "id_laboratorio": 1,
                "precio_min": 10.0,
                "precio_max": 100.0,
                "stock_bajo": True,
                "estado": "Activo",
            }
        }
    )


class LaboratorioFilters(BaseModel):
    """Filtros para laboratorios"""

    nombre: str | None = Field(default=None, description="Buscar por nombre")
    pais_origen: str | None = Field(default=None, description="Filtrar por país")
    estado: str | None = Field(default="Activo", description="Estado del laboratorio")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"nombre": "Bayer", "pais_origen": "Alemania", "estado": "Activo"}
        }
    )


class SeccionFilters(BaseModel):
    """Filtros para secciones"""

    nombre: str | None = Field(default=None, description="Buscar por nombre")
    ubicacion_fisica: str | None = Field(default=None, description="Filtrar por ubicación")
    estado: str | None = Field(default="Activo", description="Estado de la sección")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Analgésicos",
                "ubicacion_fisica": "Pasillo A",
                "estado": "Activo",
            }
        }
    )


class AlertaFilters(BaseModel):
    """Filtros para alertas"""

    tipo_alerta: str | None = Field(default=None, description="Tipo de alerta")
    prioridad: str | None = Field(default=None, description="Prioridad (Alta, Media, Baja)")
    estado: str | None = Field(default="Activo", description="Estado de la alerta")
    id_producto: int | None = Field(default=None, description="Filtrar por producto")
    id_seccion: int | None = Field(default=None, description="Filtrar por sección")
    fecha_desde: datetime | None = Field(default=None, description="Fecha de creación desde")
    fecha_hasta: datetime | None = Field(default=None, description="Fecha de creación hasta")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"tipo_alerta": "stock_bajo", "prioridad": "Alta", "estado": "Activo"}
        }
    )


class VentaFilters(BaseModel):
    """Filtros para ventas"""

    id_usuario: int | None = Field(default=None, description="Filtrar por usuario")
    id_cliente: int | None = Field(default=None, description="Filtrar por cliente")
    fecha_desde: datetime | None = Field(default=None, description="Fecha desde")
    fecha_hasta: datetime | None = Field(default=None, description="Fecha hasta")
    monto_min: float | None = Field(default=None, ge=0, description="Monto mínimo")
    monto_max: float | None = Field(default=None, ge=0, description="Monto máximo")
    metodo_pago: str | None = Field(default=None, description="Método de pago")
    estado: str | None = Field(default="Activo", description="Estado de la venta")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "fecha_desde": "2024-01-01T00:00:00",
                "fecha_hasta": "2024-12-31T23:59:59",
                "monto_min": 50.0,
                "metodo_pago": "Efectivo",
            }
        }
    )


def apply_text_filter(query, model_field, filter_value: str | None):
    """
    Aplicar filtro de texto con búsqueda parcial (ILIKE)

    Args:
        query: Query de SQLAlchemy
        model_field: Campo del modelo a filtrar
        filter_value: Valor a buscar

    Returns:
        Query modificada
    """
    if filter_value:
        return query.filter(model_field.ilike(f"%{filter_value}%"))
    return query


def apply_exact_filter(query, model_field, filter_value):
    """
    Aplicar filtro exacto

    Args:
        query: Query de SQLAlchemy
        model_field: Campo del modelo a filtrar
        filter_value: Valor exacto a buscar

    Returns:
        Query modificada
    """
    if filter_value is not None:
        return query.filter(model_field == filter_value)
    return query


def apply_range_filter(query, model_field, min_value, max_value):
    """
    Aplicar filtro de rango

    Args:
        query: Query de SQLAlchemy
        model_field: Campo del modelo a filtrar
        min_value: Valor mínimo
        max_value: Valor máximo

    Returns:
        Query modificada
    """
    if min_value is not None:
        query = query.filter(model_field >= min_value)
    if max_value is not None:
        query = query.filter(model_field <= max_value)
    return query


def apply_date_range_filter(
    query, model_field, fecha_desde: datetime | None, fecha_hasta: datetime | None
):
    """
    Aplicar filtro de rango de fechas

    Args:
        query: Query de SQLAlchemy
        model_field: Campo del modelo a filtrar
        fecha_desde: Fecha inicial
        fecha_hasta: Fecha final

    Returns:
        Query modificada
    """
    if fecha_desde:
        query = query.filter(model_field >= fecha_desde)
    if fecha_hasta:
        query = query.filter(model_field <= fecha_hasta)
    return query
