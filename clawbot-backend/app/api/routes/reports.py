"""
Endpoints relacionados con la recepción y consulta de reportes de seguridad.

POST /api/reports                    -> Report Sender envía un reporte.
GET  /api/reports                    -> Lista todos los reportes en memoria.
GET  /api/reports/pending            -> Lista solo los no procesados por APEX.
GET  /api/reports/{id}               -> Detalle de un reporte.
POST /api/reports/{id}/acknowledge   -> APEX marca un reporte como procesado.
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
    Si el JSON no cumple el formato, se responde 422 con el detalle
    de los campos inválidos.
    """
    result = await service.process_report(report)
    return ReportAck(**result)


@router.get(
    "",
    dependencies=[Depends(verify_api_key)],
    summary="Lista todos los reportes almacenados",
)
async def list_reports(service: ReportService = Depends(get_report_service)) -> list[dict]:
    return await service.list_reports()


@router.get(
    "/pending",
    dependencies=[Depends(verify_api_key)],
    summary="Lista los reportes pendientes de procesar por APEX",
)
async def list_pending(service: ReportService = Depends(get_report_service)) -> list[dict]:
    """
    Devuelve únicamente los reportes que todavía no fueron procesados
    por Oracle APEX. APEX debe llamar este endpoint en su Automation,
    procesar cada reporte e inmediatamente llamar /acknowledge para
    marcarlo como procesado y evitar duplicados.
    """
    return await service.list_pending()


@router.post(
    "/{report_id}/acknowledge",
    dependencies=[Depends(verify_api_key)],
    summary="APEX marca un reporte como ya procesado",
)
async def acknowledge_report(
    report_id: str,
    service: ReportService = Depends(get_report_service),
) -> dict:
    """
    APEX llama este endpoint después de insertar correctamente un reporte
    en Oracle. Evita que el mismo reporte sea procesado dos veces.
    """
    success = await service.acknowledge(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reporte no encontrado.")
    return {"report_id": report_id, "acknowledged": True}


@router.get(
    "/{report_id}",
    dependencies=[Depends(verify_api_key)],
    summary="Obtiene el detalle de un reporte por ID",
)
async def get_report(
    report_id: str,
    service: ReportService = Depends(get_report_service),
) -> dict:
    report = await service.get_report(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Reporte no encontrado.")
    return report
