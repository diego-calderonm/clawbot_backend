"""
Configuración centralizada del backend.

Todas las variables de entorno de la aplicación se definen y validan aquí.
En las siguientes etapas se agregarán aquí las variables de conexión a
Oracle Database (ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN, etc.).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Información general de la aplicación
    app_name: str = "ClawBot Backend"
    environment: str = "development"

    # Seguridad del endpoint de ingesta de reportes.
    # Si se deja vacío, la validación de API key queda deshabilitada
    # (útil solo para desarrollo local, nunca en producción).
    report_api_key: str | None = None

    # CORS: lista separada por comas, o "*" para permitir todos los orígenes.
    # Oracle APEX deberá agregarse aquí cuando se conozca su dominio final.
    allowed_origins: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        if self.allowed_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia cacheada de Settings (evita releer .env en cada request)."""
    return Settings()
