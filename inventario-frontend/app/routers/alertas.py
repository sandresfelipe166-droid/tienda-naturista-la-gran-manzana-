import logging

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.core.auth_middleware import require_product_read, require_product_write
from app.models.database import get_db
from app.models.schemas import (
    AlertaBase,
    AlertaCreate,
    AlertaCreateResponse,
    AlertaPaginatedResponse,
    AlertaResponse,
    AlertaUpdate,
    MessageResponse,
)
from app.services import AlertaService
from app.utils import crear_respuesta

router = APIRouter(prefix="/alertas", tags=["Alertas"])
logger = logging.getLogger(__name__)


@router.get("", response_model=AlertaPaginatedResponse)
async def listar_alertas(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    tipo_alerta: str | None = Query(None),
    prioridad: str | None = Query(None),
    id_producto: int | None = Query(None),
    id_seccion: int | None = Query(None),
    estado: str | None = Query("Activo"),
    _: dict = Depends(require_product_read()),
):
    try:
        filtros = {
            k: v
            for k, v in {
                "tipo_alerta": tipo_alerta,
                "prioridad": prioridad,
                "id_producto": id_producto,
                "id_seccion": id_seccion,
                "estado": estado,
            }.items()
            if v is not None
        }

        alertas, total = AlertaService.listar(db, page, size, filtros)
        total_pages = (total + size - 1) // size

        alertas_data = [AlertaBase.model_validate(a) for a in alertas]
        return AlertaPaginatedResponse(
            success=True,
            message=f"Se encontraron {total} alertas",
            data=alertas_data,
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
        logger.error(f"Error en endpoint listar_alertas: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{id_alerta}", response_model=AlertaResponse)
async def obtener_alerta(
    id_alerta: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_read()),
):
    alerta = AlertaService.obtener_por_id(db, id_alerta)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    alerta_data = AlertaBase.model_validate(alerta)
    return crear_respuesta(message="Alerta encontrada", data=alerta_data)


@router.post("", response_model=AlertaCreateResponse)
async def crear_alerta(
    alerta: AlertaCreate, db: Session = Depends(get_db), _: dict = Depends(require_product_write())
):
    try:
        alerta_data = alerta.model_dump()
        nuevo_id = AlertaService.crear(db, alerta_data)
        resp = crear_respuesta(message="Alerta creada exitosamente", data={"id_alerta": nuevo_id})
        # Optional Location header (no contract change)
        resp.headers["Location"] = f"/api/v1/alertas/{nuevo_id}"
        return resp
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.put("/{id_alerta}", response_model=MessageResponse)
async def actualizar_alerta(
    id_alerta: int = Path(..., gt=0),
    alerta: AlertaUpdate = Body(...),
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_write()),
):
    try:
        updates = alerta.model_dump(exclude_unset=True)
        if not AlertaService.actualizar(db, id_alerta, updates):
            raise HTTPException(status_code=404, detail="Alerta no encontrada")
        return crear_respuesta(message="Alerta actualizada exitosamente")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{id_alerta}", response_model=MessageResponse)
async def eliminar_alerta(
    id_alerta: int = Path(..., gt=0),
    modo: str = Query("logico", pattern="^(logico|fisico)$"),
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_write()),
):
    if not AlertaService.eliminar(db, id_alerta, modo):
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    return crear_respuesta(
        message=f"Alerta {'eliminada' if modo == 'fisico' else 'desactivada'} exitosamente"
    )
