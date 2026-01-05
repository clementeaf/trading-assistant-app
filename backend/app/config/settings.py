"""
Configuración de la aplicación
"""
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # API de calendario económico
    economic_calendar_provider: str = Field(
        default="tradingeconomics",
        description="Proveedor de calendario económico (tradingeconomics, mock)"
    )
    economic_calendar_api_key: Optional[str] = Field(
        default=None,
        description="API key para el servicio de calendario económico"
    )
    economic_calendar_api_url: str = Field(
        default="https://api.tradingeconomics.com/calendar",
        description="URL base de la API de calendario económico"
    )
    
    # Configuración de AWS Lambda
    aws_region: str = Field(default="us-east-1", description="Región de AWS")
    stage: str = Field(default="dev", description="Etapa de despliegue")
    
    # Configuración de filtros por defecto
    default_currency: Optional[str] = Field(
        default="USD",
        description="Moneda por defecto para filtrar eventos"
    )
    
    # Configuración de CORS
    frontend_url: Optional[str] = Field(
        default=None,
        description="URL del frontend para CORS"
    )
    
    # Configuración de base de datos
    database_url: Optional[str] = Field(
        default=None,
        description="URL de conexión a PostgreSQL (ej: postgresql://user:pass@host:port/db)"
    )
    
    # Configuración de logging
    log_level: str = Field(
        default="INFO",
        description="Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    # API de datos de mercado
    market_data_provider: str = Field(
        default="twelvedata",
        description="Proveedor de datos de mercado (twelvedata, alphavantage)"
    )
    market_data_api_key: Optional[str] = Field(
        default=None,
        description="API key para el servicio de datos de mercado"
    )
    market_data_api_url: Optional[str] = Field(
        default=None,
        description="URL base de la API de datos de mercado (opcional)"
    )
    
    # FRED API para DXY y bonos (Federal Reserve Economic Data)
    fred_api_key: Optional[str] = Field(
        default=None,
        description="API key para FRED (gratis en https://fred.stlouisfed.org/docs/api/api_key.html)"
    )
    
    class Config:
        """Configuración de Pydantic"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """
    Obtiene la configuración de la aplicación
    @returns Instancia de Settings
    """
    return Settings()

