"""Dependencias reutilizables por los routers de la API."""

from fastapi import Header

from app.config import get_settings
from app.core.exceptions import InvalidAPIKeyError


async def verify_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> bool:
    """
    Valida la API key enviada por el Report Sender en el header `X-API-Key`.

    Si REPORT_API_KEY no está configurada en el entorno, la verificación
    se omite (modo desarrollo). En producción siempre debe configurarse.
    """
    settings = get_settings()
    if settings.report_api_key:
        if x_api_key != settings.report_api_key:
            raise InvalidAPIKeyError("API key inválida o ausente.")
    return True
