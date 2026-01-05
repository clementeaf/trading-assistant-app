"""
Modelos de datos para el calendario económico
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ImpactLevel(str, Enum):
    """Niveles de impacto de eventos económicos"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EconomicEvent(BaseModel):
    """Modelo de evento económico"""
    date: datetime = Field(..., description="Fecha y hora del evento")
    importance: ImpactLevel = Field(..., description="Nivel de importancia del evento")
    currency: str = Field(..., description="Moneda relacionada (USD, EUR, etc.)")
    description: str = Field(..., description="Descripción del evento (NFP, CPI, FOMC, PMI...)")
    country: Optional[str] = Field(None, description="País relacionado")
    actual: Optional[float] = Field(None, description="Valor actual si está disponible")
    forecast: Optional[float] = Field(None, description="Valor pronosticado")
    previous: Optional[float] = Field(None, description="Valor anterior")


class HighImpactNewsResponse(BaseModel):
    """Respuesta del servicio de noticias de alto impacto para XAUUSD"""
    has_high_impact_news: bool = Field(..., description="Indica si hay noticias de alto impacto hoy para XAUUSD")
    count: int = Field(..., description="Cantidad de noticias de alto impacto para XAUUSD")
    events: list[EconomicEvent] = Field(..., description="Lista de eventos de alto impacto relevantes para XAUUSD")
    summary: str = Field(..., description="Resumen textual de las noticias relevantes para XAUUSD")
    instrument: str = Field(default="XAUUSD", description="Instrumento financiero al que aplican las noticias")

