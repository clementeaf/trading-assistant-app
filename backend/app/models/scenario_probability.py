"""
Modelos para probabilidades por escenario de trading
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ScenarioType(str, Enum):
    """Tipos de escenarios de trading"""
    BREAKOUT_BULLISH = "breakout_alcista"
    BREAKOUT_BEARISH = "breakout_bajista"
    RETEST_SUPPORT = "retesteo_soporte"
    RETEST_RESISTANCE = "retesteo_resistencia"
    CONSOLIDATION = "consolidacion"
    TREND_CONTINUATION = "continuacion_tendencia"
    TREND_REVERSAL = "reversion_tendencia"


class ScenarioProbability(BaseModel):
    """Probabilidad de un escenario específico"""
    
    scenario: ScenarioType = Field(..., description="Tipo de escenario")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probabilidad del escenario (0-1)")
    confidence: str = Field(..., description="Nivel de confianza (bajo, medio, alto)")
    factors: dict[str, float] = Field(
        default_factory=dict,
        description="Factores que contribuyen a la probabilidad"
    )
    explanation: str = Field(..., description="Explicación del escenario y probabilidad")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario": "breakout_alcista",
                "probability": 0.72,
                "confidence": "alto",
                "factors": {
                    "weekly_trend": 0.20,
                    "daily_confirmation": 0.15,
                    "level_strength": 0.12,
                    "pattern_quality": 0.10,
                    "convergence": 0.15
                },
                "explanation": "Alta probabilidad de breakout alcista por convergencia Weekly-Daily"
            }
        }


class ScenarioAnalysis(BaseModel):
    """Análisis completo de escenarios para una operación"""
    
    instrument: str = Field(..., description="Instrumento analizado")
    current_price: float = Field(..., description="Precio actual")
    timestamp: str = Field(..., description="Timestamp del análisis")
    
    primary_scenario: ScenarioProbability = Field(
        ..., description="Escenario principal (mayor probabilidad)"
    )
    alternative_scenarios: list[ScenarioProbability] = Field(
        default_factory=list,
        description="Escenarios alternativos ordenados por probabilidad"
    )
    
    convergence_strength: float = Field(
        ..., ge=0.0, le=1.0,
        description="Fuerza de convergencia multi-timeframe (0-1)"
    )
    market_context: dict = Field(
        default_factory=dict,
        description="Contexto de mercado (tendencias por TF, niveles clave, etc)"
    )
    
    summary: str = Field(..., description="Resumen del análisis de escenarios")
    
    class Config:
        json_schema_extra = {
            "example": {
                "instrument": "XAUUSD",
                "current_price": 4520.50,
                "timestamp": "2026-01-11T15:30:00Z",
                "primary_scenario": {
                    "scenario": "breakout_alcista",
                    "probability": 0.72,
                    "confidence": "alto",
                    "factors": {},
                    "explanation": "..."
                },
                "alternative_scenarios": [],
                "convergence_strength": 0.85,
                "market_context": {
                    "weekly_trend": "alcista",
                    "daily_trend": "alcista",
                    "key_resistance": 4550.0,
                    "key_support": 4500.0
                },
                "summary": "Escenario principal: Breakout alcista (72%). Convergencia fuerte Weekly-Daily."
            }
        }


class ConfidenceLevel(str, Enum):
    """Niveles de confianza para probabilidades"""
    LOW = "bajo"        # 0.0 - 0.5
    MEDIUM = "medio"    # 0.5 - 0.7
    HIGH = "alto"       # 0.7 - 1.0


def get_confidence_level(probability: float) -> ConfidenceLevel:
    """
    Obtiene el nivel de confianza basado en la probabilidad
    @param probability - Probabilidad (0-1)
    @returns Nivel de confianza
    """
    if probability >= 0.7:
        return ConfidenceLevel.HIGH
    elif probability >= 0.5:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.LOW
