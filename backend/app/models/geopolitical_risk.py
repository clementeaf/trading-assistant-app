"""
Modelos para análisis de riesgo geopolítico
"""
from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class GeopoliticalRiskLevel(str, Enum):
    """
    Nivel de riesgo geopolítico
    """
    LOW = "bajo"
    MEDIUM = "medio"
    HIGH = "alto"
    CRITICAL = "crítico"


class GeopoliticalRisk(BaseModel):
    """
    Análisis de riesgo geopolítico
    """
    score: float = Field(
        ...,
        description="Score de riesgo geopolítico (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    level: GeopoliticalRiskLevel = Field(
        ...,
        description="Nivel de riesgo (bajo/medio/alto/crítico)"
    )
    factors: list[str] = Field(
        ...,
        description="Factores de riesgo detectados (keywords, regiones)"
    )
    description: str = Field(
        ...,
        description="Descripción textual del riesgo"
    )
    last_updated: datetime = Field(
        ...,
        description="Timestamp de última actualización"
    )
