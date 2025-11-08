"""
Router de notificaciones (email) para alertas del sistema
"""

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.auth_middleware import require_admin
from app.core.logging_config import inventario_logger as logger
from app.models.database import SessionLocal, get_db
from app.models.models import Usuario
from app.services.notification_service import send_stock_bajo_email

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])


@router.post("/stock-bajo/test", response_model=dict)
def enviar_alerta_stock_bajo_test(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
) -> dict[str, Any]:
    """
    Envía un correo con el resumen de productos con stock bajo (ejecución en background).
    Requiere rol admin. Si SMTP no está configurado, se retorna estado 'skipped' (no-op).
    """

    # Importante: abrir una nueva sesión dentro de la tarea en background,
    # ya que la sesión inyectada por dependencia puede cerrarse al finalizar la respuesta.
    def task():
        db_local = SessionLocal()
        try:
            res = send_stock_bajo_email(db_local)
            logger.log_info(
                "Background stock-bajo email task executed",
                {"email_result": res.get("email_result")},
            )
        except Exception as e:
            logger.log_error(e, {"context": "bg_stock_bajo_email"})
        finally:
            db_local.close()

    background_tasks.add_task(task)
    return {
        "success": True,
        "message": "Solicitud de envío de alerta de stock bajo encolada",
        "info": "Si SMTP no está configurado, se realizará no-op",
    }


@router.post("/stock-bajo/programado", response_model=dict)
def programar_alerta_stock_bajo(
    intervalo_horas: int = 24,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
) -> dict[str, Any]:
    """
    Punto de integración para programar alertas (stub). En un siguiente paso
    puede integrarse con APScheduler o un cron externo.
    """
    return {
        "success": True,
        "message": "Programación registrada (stub). Integraremos un scheduler en la siguiente fase.",
        "data": {"intervalo_horas": intervalo_horas},
    }
