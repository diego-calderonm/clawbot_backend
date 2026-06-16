"""
Punto único de "wiring" del repositorio de reportes.

Cuando se implemente Oracle en la siguiente etapa, este es el ÚNICO
archivo que deberá cambiar: se sustituirá InMemoryReportRepository por
OracleReportRepository. Routers y servicios no necesitarán ningún cambio.
"""

from functools import lru_cache

from app.repositories.base import ReportRepository
from app.repositories.memory import InMemoryReportRepository


@lru_cache
def get_report_repository() -> ReportRepository:
    return InMemoryReportRepository()
