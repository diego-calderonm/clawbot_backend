"""
Interfaz (puerto) que define cómo se persisten los reportes.

El resto de la aplicación (servicios, routers) depende ÚNICAMENTE de esta
abstracción, nunca de una implementación concreta. Esto permite que en la
siguiente etapa agreguemos `OracleReportRepository` sin modificar ni una
línea de `app/services` o `app/api`.
"""

from abc import ABC, abstractmethod

from app.models.report import SecurityReport


class ReportRepository(ABC):
    @abstractmethod
    async def save(self, report: SecurityReport) -> str:
        """Persiste un reporte y devuelve su identificador único."""
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> list[dict]:
        """Devuelve todos los reportes almacenados (uso temporal/desarrollo)."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, report_id: str) -> dict | None:
        """Devuelve un reporte por su identificador, o None si no existe."""
        raise NotImplementedError
