import logging

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, Response
from sqlalchemy.orm import Session

from app.core.auth_middleware import require_product_read, require_product_write
from app.models.database import get_db
from app.models.schemas import (
    LaboratorioBase,
    LaboratorioCreate,
    LaboratorioCreateResponse,
    LaboratorioPaginatedResponse,
    LaboratorioResponse,
    LaboratorioUpdate,
    MessageResponse,
)
from app.services import LaboratorioService
from app.utils import crear_respuesta

router = APIRouter(prefix="/laboratorios", tags=["Laboratorios"])
logger = logging.getLogger(__name__)


@router.get("", response_model=LaboratorioPaginatedResponse)
async def listar_laboratorios(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    nombre_laboratorio: str | None = Query(None),
    estado: str | None = Query("Activo"),
    _: dict = Depends(require_product_read()),
):
    try:
        filtros = {
            k: v
            for k, v in {"nombre_laboratorio": nombre_laboratorio, "estado": estado}.items()
            if v is not None
        }

        laboratorios, total = LaboratorioService.listar(db, page, size, filtros)
        total_pages = (total + size - 1) // size

        laboratorios_data = [LaboratorioBase.model_validate(lab) for lab in laboratorios]
        return LaboratorioPaginatedResponse(
            success=True,
            message=f"Se encontraron {total} laboratorios",
            data=laboratorios_data,
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
        logger.error(f"Error en endpoint listar_laboratorios: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{id_laboratorio}", response_model=LaboratorioResponse)
async def obtener_laboratorio(
    id_laboratorio: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_read()),
):
    laboratorio = LaboratorioService.obtener_por_id(db, id_laboratorio)
    if not laboratorio:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
    laboratorio_data = LaboratorioBase.model_validate(laboratorio)
    return crear_respuesta(message="Laboratorio encontrado", data=laboratorio_data)


@router.post("", response_model=LaboratorioCreateResponse)
async def crear_laboratorio(
    laboratorio: LaboratorioCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_write()),
    response: Response = None,  # type: ignore[assignment]
):
    laboratorio_data = laboratorio.model_dump()
    nuevo_id = LaboratorioService.crear(db, laboratorio_data)
    if response is not None:
        response.headers["Location"] = f"/api/v1/laboratorios/{nuevo_id}"
    return crear_respuesta(
        message="Laboratorio creado exitosamente", data={"id_laboratorio": nuevo_id}
    )


@router.put("/{id_laboratorio}", response_model=MessageResponse)
async def actualizar_laboratorio(
    id_laboratorio: int = Path(..., gt=0),
    laboratorio: LaboratorioUpdate = Body(...),
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_write()),
):
    try:
        updates = laboratorio.model_dump(exclude_unset=True)
        if not LaboratorioService.actualizar(db, id_laboratorio, updates):
            raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
        return crear_respuesta(message="Laboratorio actualizado exitosamente")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{id_laboratorio}", response_model=MessageResponse)
async def eliminar_laboratorio(
    id_laboratorio: int = Path(..., gt=0),
    modo: str = Query("logico", pattern="^(logico|fisico)$"),
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_write()),
):
    if not LaboratorioService.eliminar(db, id_laboratorio, modo):
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
    return crear_respuesta(
        message=f"Laboratorio {'eliminado' if modo == 'fisico' else 'desactivado'} exitosamente"
    )
