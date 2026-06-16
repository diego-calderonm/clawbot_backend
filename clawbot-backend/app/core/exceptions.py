"""Excepciones personalizadas del dominio y sus manejadores HTTP."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class InvalidAPIKeyError(Exception):
    """Se lanza cuando el Report Sender no envía una API key válida."""


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "message": "El reporte enviado no cumple con el esquema esperado.",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(InvalidAPIKeyError)
    async def invalid_api_key_handler(
        request: Request, exc: InvalidAPIKeyError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "unauthorized",
                "message": str(exc) or "API key inválida o ausente.",
            },
        )
