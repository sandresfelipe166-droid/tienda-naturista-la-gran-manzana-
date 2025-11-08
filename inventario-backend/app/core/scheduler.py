"""
Scheduler de tareas en segundo plano (APScheduler - AsyncIOScheduler)

- Programa y administra tareas periódicas como el envío de alertas de stock bajo.
- Integración con FastAPI mediante inicialización en lifespan (main.py).
"""

from __future__ import annotations

from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.core.logging_config import inventario_logger
from app.models.database import SessionLocal
from app.services.notification_service import send_stock_bajo_email

logger = inventario_logger


STOCK_BAJO_JOB_ID = "stock_bajo_email_job"


def _stock_bajo_job() -> None:
    """
    Tarea programada: envía email de alerta de stock bajo.
    Abre y cierra su propia sesión de DB.
    """
    db = SessionLocal()
    try:
        result = send_stock_bajo_email(db)
        logger.log_info(
            "Scheduled job executed: stock_bajo_email",
            {
                "email_result": result.get("email_result", {}),
                "total_items": result.get("summary", {}).get("total", 0),
            },
        )
    except Exception as e:
        logger.log_error(e, {"context": "scheduler_stock_bajo_job"})
    finally:
        db.close()


class SchedulerManager:
    def __init__(self):
        self.scheduler: AsyncIOScheduler | None = None
        self.started: bool = False

    def start(self) -> None:
        """
        Inicia el scheduler si no está iniciado.
        """
        if self.started:
            return
        tz = getattr(settings, "scheduler_timezone", "UTC")
        logger.log_info("Starting AsyncIOScheduler", {"timezone": tz})

        self.scheduler = AsyncIOScheduler(
            timezone=tz,
            job_defaults={
                "coalesce": True,  # agrupar ejecuciones si hubo retraso
                "max_instances": 1,  # evitar concurrencia múltiple del mismo job
                "misfire_grace_time": 30,
            },
        )
        # Asegurar a Pylance/Type checker que no es None
        assert self.scheduler is not None
        self.scheduler.start()
        self.started = True

    def shutdown(self) -> None:
        """
        Apaga el scheduler si está iniciado.
        """
        if self.scheduler and self.started:
            try:
                self.scheduler.shutdown(wait=False)
                logger.log_info("AsyncIOScheduler stopped")
            except Exception as e:
                logger.log_error(e, {"context": "scheduler_shutdown"})
        self.started = False
        self.scheduler = None

    def ensure_started(self) -> None:
        if not self.started:
            self.start()

    def add_or_update_stock_bajo_job(self, interval_hours: int) -> dict[str, Any]:
        """
        Crea o actualiza el job de stock_bajo con el intervalo especificado.
        """
        self.ensure_started()
        assert self.scheduler is not None

        # Si existe, lo removemos para reprogramar
        try:
            self.scheduler.remove_job(STOCK_BAJO_JOB_ID)
        except Exception:
            pass

        trigger = IntervalTrigger(
            hours=int(interval_hours), timezone=getattr(settings, "scheduler_timezone", "UTC")
        )
        job = self.scheduler.add_job(
            _stock_bajo_job, trigger, id=STOCK_BAJO_JOB_ID, replace_existing=True
        )

        logger.log_info("Scheduled/Updated stock_bajo job", {"interval_hours": interval_hours})
        return {
            "job_id": job.id,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "interval_hours": interval_hours,
        }

    def remove_stock_bajo_job(self) -> bool:
        """
        Elimina el job de stock_bajo si existe.
        """
        if not self.started or not self.scheduler:
            return False
        try:
            self.scheduler.remove_job(STOCK_BAJO_JOB_ID)
            logger.log_info("Removed stock_bajo job")
            return True
        except Exception:
            return False

    def run_stock_bajo_now(self) -> None:
        """
        Ejecuta inmediatamente la tarea de stock bajo una vez.
        """
        _stock_bajo_job()

    def get_jobs(self) -> list[dict[str, Any]]:
        """
        Devuelve listado de jobs con información básica.
        """
        if not self.started or not self.scheduler:
            return []
        jobs_info: list[dict[str, Any]] = []
        for job in self.scheduler.get_jobs():
            jobs_info.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger),
                }
            )
        return jobs_info


# Instancia global del scheduler manager
scheduler_manager = SchedulerManager()

__all__ = ["scheduler_manager", "SchedulerManager", "STOCK_BAJO_JOB_ID"]
