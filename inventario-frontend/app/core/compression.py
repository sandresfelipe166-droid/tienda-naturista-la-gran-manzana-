"""
Middleware de compresión Brotli/Gzip para respuestas HTTP.
Reduce el tamaño de respuestas hasta 80% para JSON.
"""
import brotli
import gzip
from typing import Callable

from fastapi import Request, Response
from starlette.datastructures import Headers, MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware para comprimir respuestas HTTP con Brotli (preferido) o Gzip.
    
    Características:
    - Brotli quality 4 (balance velocidad/compresión)
    - Gzip level 6 (default óptimo)
    - Solo comprime respuestas > min_size bytes
    - Respeta Content-Type comprimibles
    - No comprime si ya está comprimido
    """

    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = 500,  # Solo comprimir si > 500 bytes
        compressible_types: tuple = (
            "text/",
            "application/json",
            "application/javascript",
            "application/xml",
        ),
    ):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compressible_types = compressible_types

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Skip si ya está comprimido
        if response.headers.get("Content-Encoding"):
            return response

        # Skip si Content-Type no es comprimible
        content_type = response.headers.get("Content-Type", "")
        if not any(content_type.startswith(ct) for ct in self.compressible_types):
            return response

        # Leer body original
        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        # Skip si es muy pequeño
        if len(body) < self.minimum_size:
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        # Detectar encoding aceptado por cliente
        accept_encoding = request.headers.get("Accept-Encoding", "").lower()

        compressed_body = body
        encoding = None

        # Preferir Brotli (mejor compresión, más rápido en quality 4)
        if "br" in accept_encoding:
            compressed_body = brotli.compress(body, quality=4)
            encoding = "br"
        # Fallback a Gzip
        elif "gzip" in accept_encoding:
            compressed_body = gzip.compress(body, compresslevel=6)
            encoding = "gzip"

        # Si no se comprimió o compresión no es efectiva, retornar original
        if not encoding or len(compressed_body) >= len(body):
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        # Crear respuesta comprimida
        headers = MutableHeaders(response.headers)
        headers["Content-Encoding"] = encoding
        headers["Content-Length"] = str(len(compressed_body))
        headers["Vary"] = "Accept-Encoding"

        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=dict(headers),
            media_type=response.media_type,
        )
