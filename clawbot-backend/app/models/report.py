"""
Esquema estándar de reportes generados por las Agent Skills de ClawBot.

Este modelo es intencionalmente agnóstico a la skill que generó el reporte:
cualquier skill (security_ports, security_updates, security_firewall, o
futuras skills de usuarios/procesos/logs/servicios, etc.) debe producir un
JSON que cumpla con esta estructura para ser aceptado por el backend.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class Priority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AgentInfo(BaseModel):
    name: str
    version: str


class SkillInfo(BaseModel):
    id: str = Field(..., description="Identificador único de la skill, ej: security_ports")
    name: str
    category: str


class ExecutionInfo(BaseModel):
    timestamp: datetime
    hostname: str
    os: str
    duration_ms: int = Field(..., ge=0)


class SummaryInfo(BaseModel):
    status: HealthStatus
    security_score: int = Field(..., ge=0, le=100)
    critical: int = Field(0, ge=0)
    high: int = Field(0, ge=0)
    medium: int = Field(0, ge=0)
    low: int = Field(0, ge=0)
    info: int = Field(0, ge=0)


class Finding(BaseModel):
    id: str
    severity: Severity
    title: str
    description: str
    resource: str
    status: str
    details: dict[str, Any] = Field(default_factory=dict)


class Recommendation(BaseModel):
    priority: Priority
    title: str
    description: str


class SecurityReport(BaseModel):
    """Reporte completo enviado por el Report Sender al backend."""

    report_version: str
    agent: AgentInfo
    skill: SkillInfo
    execution: ExecutionInfo
    summary: SummaryInfo
    findings: list[Finding] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("report_version")
    @classmethod
    def validate_report_version(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("report_version no puede estar vacío.")
        return value
