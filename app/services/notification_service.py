from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.email import email_client
from app.core.logging_config import inventario_logger
from app.models.models import Producto

logger = inventario_logger


def get_stock_bajo_productos(db: Session, limit: int = 50) -> List[Producto]:
    """
    Obtiene productos con stock bajo (stock_actual <= stock_minimo) y estado Activo.
    """
    return (
        db.query(Producto)
        .filter(
            and_(
                Producto.estado == "Activo",
                Producto.stock_actual <= Producto.stock_minimo,
            )
        )
        .order_by(Producto.stock_actual.asc())
        .limit(limit)
        .all()
    )


def build_stock_bajo_summary(db: Session, max_items: int = 20) -> Dict[str, Any]:
    """
    Construye un resumen de productos con stock bajo para enviar por email.
    """
    productos_bajo = get_stock_bajo_productos(db, limit=max_items)

    items = []
    for p in productos_bajo:
        items.append(
            {
                "id_producto": getattr(p, "id_producto", None),
                "nombre": getattr(p, "nombre_producto", ""),
                "stock_actual": getattr(p, "stock_actual", 0),
                "stock_minimo": getattr(p, "stock_minimo", 0),
                "laboratorio": getattr(getattr(p, "laboratorio", None), "nombre_laboratorio", ""),
                "seccion": getattr(getattr(p, "seccion", None), "nombre_seccion", ""),
            }
        )

    summary = {
        "total": len(items),
        "fecha": datetime.utcnow().isoformat(),
        "items": items,
    }
    return summary


def format_stock_bajo_email(summary: Dict[str, Any]) -> str:
    """
    Da formato al cuerpo del correo para el resumen de stock bajo.
    """
    lines = []
    lines.append("Alerta de Stock Bajo - Inventario")
    lines.append(f"Fecha: {summary.get('fecha')}")
    lines.append("")
    lines.append(f"Total de productos con stock bajo: {summary.get('total')}")
    lines.append("")

    items = summary.get("items", []) or []
    if not items:
        lines.append("No hay productos con stock bajo en este momento.")
    else:
        lines.append("Listado (máximo 20 ítems):")
        lines.append("")
        lines.append(
            f"{'ID':<6} {'Nombre':<35} {'Stock':>7} {'Mín':>5}  {'Sección':<15} {'Laboratorio':<20}"
        )
        lines.append("-" * 100)
        for it in items:
            lines.append(
                f"{str(it.get('id_producto') or ''):<6} "
                f"{(it.get('nombre') or '')[:34]:<35} "
                f"{str(it.get('stock_actual') or 0):>7} "
                f"{str(it.get('stock_minimo') or 0):>5}  "
                f"{(it.get('seccion') or '')[:14]:<15} "
                f"{(it.get('laboratorio') or '')[:19]:<20}"
            )

    return "\n".join(lines)


def send_stock_bajo_email(db: Session, recipients: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Genera y envía correo de alerta de stock bajo.
    Si SMTP no está configurado, realiza no-op y retorna estado con skipped.
    """
    summary = build_stock_bajo_summary(db)
    subject = "Alerta: Productos con stock bajo"
    body = format_stock_bajo_email(summary)

    result = email_client.send_email(subject=subject, body=body, recipients=recipients)
    # Log de envío
    status = "sent" if result.get("success") else "skipped"
    logger.log_info(
        "Stock bajo email processed", {"status": status, "meta": {"total": summary.get("total", 0)}}
    )
    return {"summary": summary, "email_result": result}
