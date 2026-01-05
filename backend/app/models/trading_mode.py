"""
Modelos de datos para recomendación de modo de trading
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TradingMode(str, Enum):
    """Modo de trading recomendado"""
    CALM = "calma"
    AGGRESSIVE = "agresivo"
    VERY_CALM = "muy_calma"
    OBSERVE = "observar"


class TradingModeReason(BaseModel):
    """Razón para la recomendación de modo"""
    rule_name: str = Field(..., description="Nombre de la regla aplicada")
    description: str = Field(..., description="Descripción de la razón")
    priority: int = Field(..., description="Prioridad de la razón (mayor = más importante)")


class TradingModeRecommendation(BaseModel):
    """Recomendación de modo de trading"""
    mode: TradingMode = Field(..., description="Modo de trading recomendado")
    confidence: float = Field(..., description="Nivel de confianza (0.0-1.0)")
    reasons: list[TradingModeReason] = Field(..., description="Lista de razones para la recomendación")
    summary: str = Field(..., description="Resumen textual de la recomendación")
    detailed_explanation: str = Field(..., description="Explicación detallada con motivos")

