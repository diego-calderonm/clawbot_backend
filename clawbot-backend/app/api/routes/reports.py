"""
Endpoints relacionados con la recepción y consulta de reportes de seguridad.

POST /api/reports      -> usado por el Report Sender para enviar un reporte.
GET  /api/reports       -> listado temporal (solo desarrollo, en memoria).
GET  /api/reports/{id}  -> detalle temporal (solo desarrollo, en memoria).

Los endpoints GET serán reemplazados/ampliados en la etapa final del
proyecto, cuando consulten Oracle Database en lugar del repositorio en
memoria, pensados para ser consumidos por Oracle APEX.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import verify_api_key
from app.models.report import SecurityReport
from app.models.response import ReportAck
from app.repositories.dependency import get_report_repository
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


def get_report_service() -> ReportService:
    return ReportService(get_report_repository())


@router.post(
    "",
    response_model=ReportAck,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
    summary="Recibe un reporte generado por una Agent Skill",
)
async def receive_report(
    report: SecurityReport,
    service: ReportService = Depends(get_report_service),
) -> ReportAck:
    """
    Recibe y valida un reporte JSON enviado por el Report Sender.

    La validación del esquema la realiza FastAPI/Pydantic automáticamente
    a partir del modelo `SecurityReport`. Si el JSON no cumple el formato,
    se responde 422 con el detalle de los campos inválidos.
    """
    result = await service.process_report(report)
    return ReportAck(**result)


@router.get(
    "",
    dependencies=[Depends(verify_api_key)],
    summary="[Temporal] Lista los reportes almacenados en memoria",
)
async def list_reports(service: ReportService = Depends(get_report_service)) -> list[dict]:
    return await service.list_reports()


@router.get(
    "/{report_id}",
    dependencies=[Depends(verify_api_key)],
    summary="[Temporal] Obtiene el detalle de un reporte por ID",
)
async def get_report(
    report_id: str,
    service: ReportService = Depends(get_report_service),
) -> dict:
    report = await service.get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Reporte no encontrado.")
    return report
