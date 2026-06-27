"""
Implementación temporal del repositorio, usada mientras no existe la
conexión a Oracle Database (próxima etapa del proyecto).

IMPORTANTE: esta implementación no persiste datos entre reinicios del
proceso y no es apta para producción. Sirve para:
  1. Validar de punta a punta el flujo POST /api/reports.
  2. Probar el backend localmente antes de tener Oracle disponible.
"""

import uuid
from datetime import datetime, timezone

from app.models.report import SecurityReport
from app.repositories.base import ReportRepository


class InMemoryReportRepository(ReportRepository):
    def __init__(self) -> None:
        self._reports: dict[str, dict] = {}

    async def save(self, report: SecurityReport) -> str:
        report_id = str(uuid.uuid4())
        self._reports[report_id] = {
            "report_id": report_id,
            "received_at": datetime.now(timezone.utc).isoformat(),
            "processed": False,
            "processed_at": None,
            "data": report.model_dump(mode="json"),
        }
        return report_id

    async def list_all(self) -> list[dict]:
        return list(self._reports.values())

    async def get_by_id(self, report_id: str) -> dict | None:
        return self._reports.get(report_id)

    async def list_pending(self) -> list[dict]:
        return [r for r in self._reports.values() if not r["processed"]]

    async def mark_as_processed(self, report_id: str) -> bool:
        if report_id not in self._reports:
            return False
        self._reports[report_id]["processed"] = True
        self._reports[report_id]["processed_at"] = datetime.now(timezone.utc).isoformat()
        return True
