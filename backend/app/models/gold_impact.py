"""
Modelos para estimación de impacto en Gold
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ImpactDirection(str, Enum):
    """
    Dirección esperada del impacto en Gold
    """
    BULLISH = "alcista"
    BEARISH = "bajista"
    NEUTRAL = "neutral"


class ImpactMagnitude(str, Enum):
    """
    Magnitud esperada del impacto
    """
    VERY_HIGH = "muy_alta"
    HIGH = "alta"
    MEDIUM = "media"
    LOW = "baja"
    VERY_LOW = "muy_baja"


class GoldImpactEstimate(BaseModel):
    """
    Estimación de impacto de un evento en Gold
    """
    probability: float = Field(
        ...,
        description="Probabilidad de impacto (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    direction: ImpactDirection = Field(
        ...,
        description="Dirección esperada del impacto"
    )
    direction_note: Optional[str] = Field(
        None,
        description="Nota condicional sobre la dirección (ej: 'si dato fuerte')"
    )
    magnitude: ImpactMagnitude = Field(
        ...,
        description="Magnitud esperada del impacto"
    )
    magnitude_range: str = Field(
        ...,
        description="Rango de puntos esperados (ej: '50-150 puntos')"
    )
    confidence: float = Field(
        ...,
        description="Confianza en la estimación (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    reasoning: str = Field(
        ...,
        description="Razonamiento de la estimación"
    )
    event_type: str = Field(
        ...,
        description="Tipo de evento detectado (NFP, CPI, FOMC, etc.)"
    )
