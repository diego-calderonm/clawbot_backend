"""Modelos de respuesta expuestos por la API (no de entrada)."""

from pydantic import BaseModel


class ReportAck(BaseModel):
    """Confirmación devuelta tras aceptar un reporte."""

    report_id: str
    skill_id: str
    security_score: int
    findings_count: int


class ErrorResponse(BaseModel):
    error: str
    message: str
