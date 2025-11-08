import logging

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Response
from sqlalchemy.orm import Session

from app.core.auth_middleware import require_product_read, require_product_write
from app.models.database import get_db
from app.models.schemas import (
    MessageResponse,
    SeccionBase,
    SeccionCreate,
    SeccionCreateResponse,
    SeccionPaginatedResponse,
    SeccionResponse,
    SeccionUpdate,
)
from app.services import SeccionService
from app.utils import crear_respuesta

router = APIRouter(prefix="/secciones", tags=["Secciones"])
logger = logging.getLogger(__name__)


@router.get("", response_model=SeccionPaginatedResponse)
async def listar_secciones(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    nombre_seccion: str | None = Query(None),
    estado: str | None = Query("Activo"),
    _: dict = Depends(require_product_read()),
):
    try:
        filtros = {
            k: v
            for k, v in {"nombre_seccion": nombre_seccion, "estado": estado}.items()
            if v is not None
        }

        secciones, total = SeccionService.listar(db, page, size, filtros)
        total_pages = (total + size - 1) // size

        secciones_data = [SeccionBase.model_validate(s) for s in secciones]
        return SeccionPaginatedResponse(
            success=True,
            message=f"Se encontraron {total} secciones",
            data=secciones_data,
            pagination={
                "page": page,
                "size": size,
                "total": total,
                "pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
            filters_applied=filtros,
        )
    except Exception as e:
        logger.error(f"Error en endpoint listar_secciones: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{id_seccion}", response_model=SeccionResponse)
async def obtener_seccion(
    id_seccion: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_read()),
):
    seccion = SeccionService.obtener_por_id(db, id_seccion)
    if not seccion:
        raise HTTPException(status_code=404, detail="Sección no encontrada")
    seccion_data = SeccionBase.model_validate(seccion)
    return crear_respuesta(message="Sección encontrada", data=seccion_data)


@router.post("", response_model=SeccionCreateResponse)
async def crear_seccion(
    seccion: SeccionCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_write()),
    response: Response = None,
):
    try:
        seccion_data = seccion.model_dump()
        nuevo_id = SeccionService.crear(db, seccion_data)
        if response is not None:
            response.headers["Location"] = f"/api/v1/secciones/{nuevo_id}"
        return crear_respuesta(message="Sección creada exitosamente", data={"id_seccion": nuevo_id})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{id_seccion}", response_model=MessageResponse)
async def actualizar_seccion(
    id_seccion: int = Path(..., gt=0),
    seccion: SeccionUpdate = Body(...),
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_write()),
):
    try:
        updates = seccion.model_dump(exclude_unset=True)
        if not SeccionService.actualizar(db, id_seccion, updates):
            raise HTTPException(status_code=404, detail="Sección no encontrada")
        return crear_respuesta(message="Sección actualizada exitosamente")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{id_seccion}", response_model=MessageResponse)
async def eliminar_seccion(
    id_seccion: int = Path(..., gt=0),
    modo: str = Query("logico", pattern="^(logico|fisico)$"),
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_write()),
):
    try:
        if not SeccionService.eliminar(db, id_seccion, modo):
            raise HTTPException(status_code=404, detail="Sección no encontrada")
        return crear_respuesta(
            message=f"Sección {'eliminada' if modo == 'fisico' else 'desactivada'} exitosamente"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
