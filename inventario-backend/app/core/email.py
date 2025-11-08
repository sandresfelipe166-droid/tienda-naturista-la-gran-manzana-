"""
Cliente de correo simple usando smtplib (stdlib).
Funciona en modo no-op si no hay configuración SMTP.
"""

import smtplib
import ssl
from email.message import EmailMessage
from typing import Any, cast

from app.core.config import settings
from app.core.logging_config import inventario_logger

logger = inventario_logger


class EmailClient:
    def __init__(self):
        self.host: str | None = getattr(settings, "smtp_host", None)
        self.port: int = getattr(settings, "smtp_port", 587)
        self.user: str | None = getattr(settings, "smtp_user", None)
        self.password: str | None = getattr(settings, "smtp_password", None)
        self.use_tls: bool = getattr(settings, "smtp_use_tls", True)
        # Lista de correos destino por defecto
        self.default_recipients: list[str] = getattr(settings, "alert_emails", []) or []

    @property
    def is_configured(self) -> bool:
        return bool(self.host and self.port and self.user and self.password)

    def send_email(
        self,
        subject: str,
        body: str,
        recipients: list[str] | None = None,
        sender: str | None = None,
    ) -> dict[str, Any]:
        """
        Envía un correo de texto plano. Retorna diccionario con status.
        Si no hay configuración SMTP o no hay destinatarios, funciona en modo no-op.
        """
        recipients = recipients if recipients is not None else self.default_recipients
        sender = sender or self.user or "no-reply@example.com"

        if not recipients:
            logger.log_warning("Email send skipped: no recipients configured")
            return {"success": False, "skipped": True, "reason": "no_recipients"}

        if not self.is_configured:
            logger.log_warning("Email send skipped: SMTP not configured")
            return {"success": False, "skipped": True, "reason": "smtp_not_configured"}

        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = ", ".join(recipients)
            msg.set_content(body)

            # Variables tipadas para satisfacer el analizador estático (ya validado is_configured)
            host = cast(str, self.host)
            user = cast(str, self.user)
            password = cast(str, self.password)

            if self.use_tls:
                context = ssl.create_default_context()
                with smtplib.SMTP(host, self.port, timeout=10) as server:
                    server.starttls(context=context)
                    server.login(user, password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(host, self.port, timeout=10) as server:
                    server.login(user, password)
                    server.send_message(msg)

            logger.log_info("Email sent successfully", {"to": recipients, "subject": subject})
            return {"success": True, "sent": True, "to": recipients}
        except Exception as e:
            logger.log_error(e, {"context": "email_send", "to": recipients, "subject": subject})
            return {"success": False, "error": str(e)}


# Instancia global
email_client = EmailClient()
