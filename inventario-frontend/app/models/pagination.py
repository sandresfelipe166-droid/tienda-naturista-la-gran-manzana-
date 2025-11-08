"""
Modelos y utilidades para paginación mejorada
"""

from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Parámetros de paginación"""

    page: int = Field(default=1, ge=1, description="Número de página (inicia en 1)")
    size: int = Field(default=50, ge=1, le=100, description="Elementos por página")

    @property
    def skip(self) -> int:
        """Calcular offset para la consulta"""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Alias para size"""
        return self.size


class PaginationMeta(BaseModel):
    """Metadata de paginación"""

    page: int = Field(description="Página actual")
    size: int = Field(description="Elementos por página")
    total: int = Field(description="Total de elementos")
    pages: int = Field(description="Total de páginas")
    has_next: bool = Field(description="Hay página siguiente")
    has_prev: bool = Field(description="Hay página anterior")

    @classmethod
    def create(cls, page: int, size: int, total: int) -> "PaginationMeta":
        """Crear metadata de paginación"""
        pages = ceil(total / size) if size > 0 else 0
        return cls(
            page=page, size=size, total=total, pages=pages, has_next=page < pages, has_prev=page > 1
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """Respuesta paginada genérica"""

    success: bool = True
    message: str = "Datos obtenidos exitosamente"
    data: list[T] = Field(description="Lista de elementos")
    pagination: PaginationMeta = Field(description="Información de paginación")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Datos obtenidos exitosamente",
                "data": [],
                "pagination": {
                    "page": 1,
                    "size": 50,
                    "total": 150,
                    "pages": 3,
                    "has_next": True,
                    "has_prev": False,
                },
            }
        }
    )


class SortParams(BaseModel):
    """Parámetros de ordenamiento"""

    sort_by: str | None = Field(default=None, description="Campo por el cual ordenar")
    order: str = Field(
        default="asc", pattern="^(asc|desc)$", description="Dirección del ordenamiento"
    )

    def is_valid_field(self, model_class, field_name: str) -> bool:
        """Verificar si el campo existe en el modelo"""
        return hasattr(model_class, field_name)


def paginate_query(query, page: int, size: int):
    """
    Aplicar paginación a una query de SQLAlchemy

    Args:
        query: Query de SQLAlchemy
        page: Número de página (inicia en 1)
        size: Elementos por página

    Returns:
        tuple: (items, total)
    """
    total = query.count()
    skip = (page - 1) * size
    items = query.offset(skip).limit(size).all()
    return items, total


def create_paginated_response(
    items: list[T], total: int, page: int, size: int, message: str = "Datos obtenidos exitosamente"
) -> dict:
    """
    Crear respuesta paginada en formato dict

    Args:
        items: Lista de elementos
        total: Total de elementos
        page: Página actual
        size: Elementos por página
        message: Mensaje de respuesta

    Returns:
        dict con estructura de respuesta paginada
    """
    pagination_meta = PaginationMeta.create(page, size, total)

    return {
        "success": True,
        "message": message,
        "data": items,
        "pagination": pagination_meta.model_dump(),
    }
