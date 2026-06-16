"""Punto de entrada de la aplicación FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import reports
from app.config import get_settings
from app.core.exceptions import register_exception_handlers

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "Backend de recepción de reportes de auditoría de seguridad "
        "generados por las Agent Skills de ClawBot."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(reports.router, prefix="/api")


@app.get("/", tags=["health"], summary="Estado del servicio")
def root() -> dict:
    return {
        "service": settings.app_name,
        "status": "running",
        "environment": settings.environment,
    }


@app.get("/health", tags=["health"], summary="Health check para Render")
def health() -> dict:
    return {"status": "ok"}
