"""
Router para administrar el scheduler (APScheduler)

Endpoints (solo admin):
- GET    /api/v1/scheduler/jobs                 -> Lista los jobs activos
- POST   /api/v1/scheduler/stock-bajo/start     -> Inicia/actualiza el job de stock bajo (intervalo en horas)
- POST   /api/v1/scheduler/stock-bajo/stop      -> Detiene el job de stock bajo
- POST   /api/v1/scheduler/stock-bajo/run-now   -> Ejecuta una corrida inmediata del job de stock bajo
- POST   /api/v1/scheduler/start                -> Arranca el scheduler (si estuviera detenido)
- POST   /api/v1/scheduler/stop                 -> Detiene el scheduler
"""

from typing import Any

from fastapi import APIRouter, Depends, Query

from app.core.auth_middleware import require_admin

# Importar manager del scheduler
from app.core.scheduler import scheduler_manager
from app.models.models import Usuario

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.get("/jobs", response_model=dict[str, Any])
def list_jobs(
    current_user: Usuario = Depends(require_admin),
) -> dict[str, Any]:
    """
    Listar jobs del scheduler.
    """
    jobs = scheduler_manager.get_jobs()
    return {
        "success": True,
        "message": "Jobs listados exitosamente",
        "data": {
            "scheduler_started": scheduler_manager.started,
            "jobs": jobs,
        },
    }


@router.post("/stock-bajo/start", response_model=dict[str, Any])
def start_stock_bajo_job(
    interval_horas: int = Query(..., ge=1, le=168, description="Intervalo en horas (1-168)"),
    current_user: Usuario = Depends(require_admin),
) -> dict[str, Any]:
    """
    Crear o actualizar el job de 'stock bajo' con el intervalo indicado.
    """
    result = scheduler_manager.add_or_update_stock_bajo_job(interval_horas)
    return {
        "success": True,
        "message": "Job de 'stock bajo' creado/actualizado",
        "data": result,
    }


@router.post("/stock-bajo/stop", response_model=dict[str, Any])
def stop_stock_bajo_job(
    current_user: Usuario = Depends(require_admin),
) -> dict[str, Any]:
    """
    Eliminar job de 'stock bajo' si existe.
    """
    removed = scheduler_manager.remove_stock_bajo_job()
    if not removed:
        return {
            "success": True,
            "message": "No había job de 'stock bajo' activo",
            "data": {"removed": False},
        }
    return {
        "success": True,
        "message": "Job de 'stock bajo' detenido",
        "data": {"removed": True},
    }


@router.post("/stock-bajo/run-now", response_model=dict[str, Any])
def run_stock_bajo_now(
    current_user: Usuario = Depends(require_admin),
) -> dict[str, Any]:
    """
    Ejecutar inmediatamente la tarea de 'stock bajo'.
    """
    scheduler_manager.run_stock_bajo_now()
    return {
        "success": True,
        "message": "Job de 'stock bajo' ejecutado inmediatamente",
    }


@router.post("/start", response_model=dict[str, Any])
def start_scheduler(
    current_user: Usuario = Depends(require_admin),
) -> dict[str, Any]:
    """
    Arrancar el scheduler manualmente.
    """
    scheduler_manager.start()
    return {
        "success": True,
        "message": "Scheduler iniciado",
        "data": {"started": scheduler_manager.started},
    }


@router.post("/stop", response_model=dict[str, Any])
def stop_scheduler(
    current_user: Usuario = Depends(require_admin),
) -> dict[str, Any]:
    """
    Detener el scheduler manualmente.
    """
    scheduler_manager.shutdown()
    return {
        "success": True,
        "message": "Scheduler detenido",
        "data": {"started": scheduler_manager.started},
    }
