"""
Modelos para análisis de patrones técnicos complejos
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PatternType(str, Enum):
    """Tipos de patrones técnicos detectables"""
    HEAD_SHOULDERS = "head_and_shoulders"
    INVERSE_HEAD_SHOULDERS = "inverse_head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIPLE_TOP = "triple_top"
    TRIPLE_BOTTOM = "triple_bottom"
    ASCENDING_TRIANGLE = "ascending_triangle"
    DESCENDING_TRIANGLE = "descending_triangle"
    SYMMETRICAL_TRIANGLE = "symmetrical_triangle"
    RISING_WEDGE = "rising_wedge"
    FALLING_WEDGE = "falling_wedge"
    FLAG = "flag"
    PENNANT = "pennant"
    CUP_AND_HANDLE = "cup_and_handle"
    ROUNDING_BOTTOM = "rounding_bottom"
    NONE = "none"  # No pattern detected


class PatternStatus(str, Enum):
    """Estado de formación del patrón"""
    FORMING = "forming"        # Patrón en formación (no confirmado)
    CONFIRMED = "confirmed"    # Patrón confirmado (roto nivel clave)
    COMPLETED = "completed"    # Patrón completado (objetivo alcanzado)


class PatternBias(str, Enum):
    """Sesgo direccional del patrón"""
    BULLISH = "bullish"      # Patrón alcista
    BEARISH = "bearish"      # Patrón bajista
    NEUTRAL = "neutral"      # Sin sesgo claro


class PatternAnalysis(BaseModel):
    """Análisis de patrón técnico complejo detectado por LLM"""
    
    pattern_type: PatternType = Field(
        description="Tipo de patrón detectado"
    )
    
    status: PatternStatus = Field(
        description="Estado de formación del patrón (forming, confirmed, completed)"
    )
    
    bias: PatternBias = Field(
        description="Sesgo direccional del patrón (bullish, bearish, neutral)"
    )
    
    confidence: float = Field(
        description="Confianza en la detección (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    
    description: str = Field(
        description="Descripción del patrón en lenguaje natural (100-150 palabras)"
    )
    
    key_levels: dict[str, float] = Field(
        description="Niveles clave del patrón (neckline, breakout, target, invalidation)",
        default_factory=dict
    )
    
    timeframe: str = Field(
        description="Timeframe donde se detectó (H1, H4, Daily)"
    )
    
    implications: str = Field(
        description="Implicaciones operativas del patrón (qué hacer)"
    )
