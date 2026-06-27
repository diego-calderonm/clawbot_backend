"""
Capa de servicios: contiene la lógica de negocio relacionada con los
reportes, desacoplada de FastAPI y de la implementación de persistencia.
"""

from app.models.report import SecurityReport
from app.repositories.base import ReportRepository


class ReportService:
    def __init__(self, repository: ReportRepository) -> None:
        self._repository = repository

    async def process_report(self, report: SecurityReport) -> dict:
        report_id = await self._repository.save(report)
        return {
            "report_id": report_id,
            "skill_id": report.skill.id,
            "security_score": report.summary.security_score,
            "findings_count": len(report.findings),
        }

    async def list_reports(self) -> list[dict]:
        return await self._repository.list_all()

    async def get_report(self, report_id: str) -> dict | None:
        return await self._repository.get_by_id(report_id)

    async def list_pending(self) -> list[dict]:
        """Devuelve solo los reportes que APEX todavía no procesó."""
        return await self._repository.list_pending()

    async def acknowledge(self, report_id: str) -> bool:
        """
        Marca un reporte como procesado por APEX.
        Devuelve False si el reporte no existe.
        """
        return await self._repository.mark_as_processed(report_id)
