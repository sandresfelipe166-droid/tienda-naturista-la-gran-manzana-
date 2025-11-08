"""
Servicio de notificaciones: Email + WebSocket en tiempo real.

Integra notificaciones por email y WebSocket con circuit breaker y retry.
"""
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.circuit_breaker import email_circuit_breaker
from app.core.email import email_client
from app.core.logging_config import inventario_logger
from app.core.retry import retry_decorator
from app.core.websocket_manager import ws_manager
from app.models.models import Alerta, Lote, Producto

logger = inventario_logger


def get_stock_bajo_productos(db: Session, limit: int = 50) -> list[Producto]:
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


def build_stock_bajo_summary(db: Session, max_items: int = 20) -> dict[str, Any]:
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


def format_stock_bajo_email(summary: dict[str, Any]) -> str:
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


def send_stock_bajo_email(db: Session, recipients: list[str] | None = None) -> dict[str, Any]:
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


# ============================================================================
# NUEVAS FUNCIONES: WebSocket + Circuit Breaker + Retry
# ============================================================================


@retry_decorator(max_attempts=3, base_delay=1.0)
async def check_and_notify_low_stock(db: Session, dias_vencimiento: int = 30):
    """
    Verificar stock bajo y enviar notificaciones en tiempo real vía WebSocket.
    
    Esta función se ejecuta periódicamente (por scheduler) y:
    1. Detecta productos con stock bajo
    2. Envía notificaciones WebSocket a clientes conectados
    3. Opcionalmente envía emails (con circuit breaker)
    """
    try:
        # Buscar alertas activas de stock bajo
        alertas_stock_bajo = (
            db.query(Alerta)
            .join(Producto)
            .filter(
                and_(
                    Alerta.tipo_alerta == "stock_bajo",
                    Alerta.activo == True,  # noqa: E712
                    Alerta.nivel_criticidad.in_(["alto", "critico"])
                )
            )
            .all()
        )
        
        if not alertas_stock_bajo:
            return
        
        # Enviar notificaciones WebSocket
        for alerta in alertas_stock_bajo:
            await ws_manager.broadcast_alert(
                alert_type="stock_bajo",
                title=f"Stock Bajo: {alerta.producto.nombre}",
                message=f"Stock actual: {alerta.producto.stock} unidades. "
                        f"Mínimo requerido: {alerta.umbral_min or 10}",
                data={
                    "producto_id": alerta.producto_id,
                    "producto_nombre": alerta.producto.nombre,
                    "stock_actual": alerta.producto.stock,
                    "umbral_min": alerta.umbral_min,
                    "nivel_criticidad": alerta.nivel_criticidad,
                },
                severity="warning" if alerta.nivel_criticidad == "alto" else "error"
            )
        
        logger.log_info(
            f"Notificadas {len(alertas_stock_bajo)} alertas de stock bajo vía WebSocket"
        )
    
    except Exception as e:
        logger.log_error(e)
        raise


@retry_decorator(max_attempts=3, base_delay=1.0)
async def check_and_notify_expired_products(db: Session, dias_vencimiento: int = 30):
    """
    Verificar productos próximos a vencer y enviar notificaciones.
    
    Args:
        db: Sesión de base de datos
        dias_vencimiento: Días antes de vencimiento para alertar
    """
    try:
        fecha_limite = datetime.now() + timedelta(days=dias_vencimiento)
        
        # Buscar lotes próximos a vencer
        lotes_por_vencer = (
            db.query(Lote)
            .join(Producto)
            .filter(
                and_(
                    Lote.fecha_vencimiento <= fecha_limite,
                    Lote.fecha_vencimiento >= datetime.now(),
                    Lote.cantidad_restante > 0
                )
            )
            .all()
        )
        
        if not lotes_por_vencer:
            return
        
        # Agrupar por nivel de urgencia
        urgente = []
        critico = []
        
        for lote in lotes_por_vencer:
            dias_restantes = (lote.fecha_vencimiento - datetime.now()).days
            
            if dias_restantes <= 7:
                critico.append(lote)
            elif dias_restantes <= 15:
                urgente.append(lote)
        
        # Notificar productos críticos (vencen en 7 días o menos)
        for lote in critico:
            await ws_manager.broadcast_alert(
                alert_type="producto_expirado",
                title=f"CRÍTICO: {lote.producto.nombre} vence pronto",
                message=f"Lote #{lote.lote_id} vence el {lote.fecha_vencimiento.strftime('%Y-%m-%d')}. "
                        f"Quedan {lote.cantidad_restante} unidades.",
                data={
                    "lote_id": lote.lote_id,
                    "producto_id": lote.producto_id,
                    "producto_nombre": lote.producto.nombre,
                    "cantidad_restante": lote.cantidad_restante,
                    "fecha_vencimiento": lote.fecha_vencimiento.isoformat(),
                    "dias_restantes": (lote.fecha_vencimiento - datetime.now()).days,
                },
                severity="critical"
            )
        
        # Notificar productos urgentes (vencen en 7-15 días)
        for lote in urgente:
            await ws_manager.broadcast_alert(
                alert_type="producto_proximo_vencer",
                title=f"Urgente: {lote.producto.nombre} próximo a vencer",
                message=f"Lote #{lote.lote_id} vence el {lote.fecha_vencimiento.strftime('%Y-%m-%d')}",
                data={
                    "lote_id": lote.lote_id,
                    "producto_id": lote.producto_id,
                    "producto_nombre": lote.producto.nombre,
                    "cantidad_restante": lote.cantidad_restante,
                    "fecha_vencimiento": lote.fecha_vencimiento.isoformat(),
                    "dias_restantes": (lote.fecha_vencimiento - datetime.now()).days,
                },
                severity="warning"
            )
        
        logger.log_info(
            f"Notificados {len(critico)} productos críticos y {len(urgente)} urgentes vía WebSocket"
        )
    
    except Exception as e:
        logger.log_error(e)
        raise


@email_circuit_breaker
async def send_email_alert_with_circuit_breaker(to: str, subject: str, body: str):
    """
    Enviar email con protección de circuit breaker.
    
    Si el servicio de email falla repetidamente, el circuit breaker
    se abre y rechaza las peticiones rápidamente (fail-fast).
    """
    result = email_client.send_email(subject=subject, body=body, recipients=[to])
    logger.log_info(f"Email enviado a {to}: {subject}")
    return result


async def broadcast_inventory_update(
    update_type: str,
    producto_id: int,
    producto_nombre: str,
    data: dict
):
    """
    Enviar notificación de actualización de inventario en tiempo real.
    
    Args:
        update_type: Tipo de actualización (entrada, salida, venta, ajuste)
        producto_id: ID del producto
        producto_nombre: Nombre del producto
        data: Datos adicionales
    """
    await ws_manager.broadcast({
        "type": "inventory_update",
        "update_type": update_type,
        "producto_id": producto_id,
        "producto_nombre": producto_nombre,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    })

