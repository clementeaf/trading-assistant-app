"""
Modelos de datos para análisis de alineación de mercado
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AlignmentStatus(str, Enum):
    """Estado de alineación entre instrumentos"""
    ALIGNED = "alineados"
    CONFLICT = "conflicto"


class MarketBias(str, Enum):
    """Sesgo del mercado"""
    RISK_OFF = "risk-off"
    RISK_ON = "risk-on"
    MIXED = "mixto"


class InstrumentPrice(BaseModel):
    """Precio de un instrumento en un momento dado"""
    symbol: str = Field(..., description="Símbolo del instrumento (DXY, US10Y, etc.)")
    price: float = Field(..., description="Precio actual")
    previous_price: float = Field(..., description="Precio del día anterior")
    change_percent: float = Field(..., description="Cambio porcentual vs día anterior")
    direction: str = Field(..., description="Dirección del cambio (sube/baja)")


class MarketAlignmentAnalysis(BaseModel):
    """Análisis de alineación entre DXY y bonos"""
    dxy: InstrumentPrice = Field(..., description="Datos del DXY")
    bond: InstrumentPrice = Field(..., description="Datos del bono (US10Y, US02Y, etc.)")
    alignment: AlignmentStatus = Field(..., description="Estado de alineación (alineados/conflicto)")
    market_bias: MarketBias = Field(..., description="Sesgo del mercado (risk-off/risk-on/mixto)")
    summary: str = Field(..., description="Resumen textual del análisis")

