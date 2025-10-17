"""
Router de exportación de reportes (CSV)
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.core.auth_middleware import get_current_active_user, require_admin
from app.models.database import get_db
from app.models.filters import ProductoFilters
from app.models.models import Usuario
from app.services.report_service import (
    generate_laboratorios_csv,
    generate_productos_csv,
    generate_secciones_csv,
)

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get("/productos.csv")
def export_productos_csv(
    # Filtros (alineados con ProductoFilters)
    nombre: Optional[str] = Query(None, description="Buscar por nombre"),
    codigo_barras: Optional[str] = Query(None, description="Buscar por código de barras"),
    principio_activo: Optional[str] = Query(None, description="Buscar por principio activo"),
    id_laboratorio: Optional[int] = Query(None, description="Filtrar por laboratorio"),
    id_seccion: Optional[int] = Query(None, description="Filtrar por sección"),
    precio_min: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    precio_max: Optional[float] = Query(None, ge=0, description="Precio máximo"),
    stock_min: Optional[int] = Query(None, ge=0, description="Stock mínimo"),
    stock_max: Optional[int] = Query(None, ge=0, description="Stock máximo"),
    stock_bajo: Optional[bool] = Query(None, description="Solo productos con stock bajo"),
    requiere_receta: Optional[bool] = Query(None, description="Filtrar por receta requerida"),
    estado: Optional[str] = Query("Activo", description="Estado del producto"),
    forma_farmaceutica: Optional[str] = Query(None, description="Forma farmacéutica"),
    # Dependencias
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
):
    """
    Exporta productos a CSV aplicando filtros. Restringido a usuarios admin.
    """
    filters = ProductoFilters(
        nombre=nombre,
        codigo_barras=codigo_barras,
        principio_activo=principio_activo,
        id_laboratorio=id_laboratorio,
        id_seccion=id_seccion,
        precio_min=precio_min,
        precio_max=precio_max,
        stock_min=stock_min,
        stock_max=stock_max,
        stock_bajo=stock_bajo,
        requiere_receta=requiere_receta,
        estado=estado,
        forma_farmaceutica=forma_farmaceutica,
    )

    content = generate_productos_csv(db, filters)
    headers = {"Content-Disposition": 'attachment; filename="productos.csv"'}
    return Response(content=content, media_type="text/csv; charset=utf-8", headers=headers)


@router.get("/laboratorios.csv")
def export_laboratorios_csv(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
):
    """
    Exporta laboratorios a CSV. Restringido a usuarios admin.
    """
    content = generate_laboratorios_csv(db)
    headers = {"Content-Disposition": 'attachment; filename="laboratorios.csv"'}
    return Response(content=content, media_type="text/csv; charset=utf-8", headers=headers)


@router.get("/secciones.csv")
def export_secciones_csv(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
):
    """
    Exporta secciones a CSV. Restringido a usuarios admin.
    """
    content = generate_secciones_csv(db)
    headers = {"Content-Disposition": 'attachment; filename="secciones.csv"'}
    return Response(content=content, media_type="text/csv; charset=utf-8", headers=headers)


@router.get("/productos_stock_bajo.csv")
def export_productos_stock_bajo_csv(
    # Filtros relevantes (además de forzar stock_bajo=True)
    nombre: Optional[str] = Query(None, description="Buscar por nombre"),
    codigo_barras: Optional[str] = Query(None, description="Buscar por código de barras"),
    principio_activo: Optional[str] = Query(None, description="Buscar por principio activo"),
    id_laboratorio: Optional[int] = Query(None, description="Filtrar por laboratorio"),
    id_seccion: Optional[int] = Query(None, description="Filtrar por sección"),
    forma_farmaceutica: Optional[str] = Query(None, description="Forma farmacéutica"),
    estado: Optional[str] = Query("Activo", description="Estado del producto"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
):
    """
    Exporta productos con stock bajo a CSV. Restringido a usuarios admin.
    Fuerza stock_bajo=True y aplica demás filtros opcionales.
    """
    filters = ProductoFilters(
        nombre=nombre,
        codigo_barras=codigo_barras,
        principio_activo=principio_activo,
        id_laboratorio=id_laboratorio,
        id_seccion=id_seccion,
        forma_farmaceutica=forma_farmaceutica,
        estado=estado,
        stock_bajo=True,  # Forzado
    )

    content = generate_productos_csv(db, filters)
    headers = {"Content-Disposition": 'attachment; filename="productos_stock_bajo.csv"'}
    return Response(content=content, media_type="text/csv; charset=utf-8", headers=headers)
