"""
Modelos de datos para análisis de mercado y sesiones de trading
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SessionType(str, Enum):
    """Tipos de sesiones de trading"""
    ASIA = "asia"
    LONDON = "london"
    NEW_YORK = "new_york"


class MarketDirection(str, Enum):
    """Dirección del mercado"""
    BULLISH = "alcista"
    BEARISH = "bajista"
    NEUTRAL = "lateral"


class PriceCandle(BaseModel):
    """Vela de precio (OHLC)"""
    timestamp: datetime = Field(..., description="Timestamp de la vela")
    open: float = Field(..., description="Precio de apertura")
    high: float = Field(..., description="Precio máximo")
    low: float = Field(..., description="Precio mínimo")
    close: float = Field(..., description="Precio de cierre")
    volume: Optional[float] = Field(None, description="Volumen (si está disponible)")


class SessionAnalysis(BaseModel):
    """Análisis de una sesión de trading"""
    session: SessionType = Field(..., description="Tipo de sesión")
    start_time: str = Field(..., description="Hora de inicio (HH:MM UTC)")
    end_time: str = Field(..., description="Hora de fin (HH:MM UTC)")
    open_price: float = Field(..., description="Precio de apertura de la sesión")
    close_price: float = Field(..., description="Precio de cierre de la sesión")
    high: float = Field(..., description="Precio máximo de la sesión")
    low: float = Field(..., description="Precio mínimo de la sesión")
    range_value: float = Field(..., description="Rango de la sesión (high - low)")
    direction: MarketDirection = Field(..., description="Dirección del mercado en la sesión")
    change_percent: float = Field(..., description="Cambio porcentual de la sesión")
    volume_relative: Optional[float] = Field(None, description="Volumen relativo comparado con otras sesiones")
    broke_previous_high: bool = Field(False, description="Si rompió el máximo del día anterior")
    broke_previous_low: bool = Field(False, description="Si rompió el mínimo del día anterior")
    description: str = Field(..., description="Descripción textual de la sesión")


class DailyMarketAnalysis(BaseModel):
    """Análisis completo del día de trading"""
    instrument: str = Field(..., description="Instrumento analizado (ej: XAUUSD)")
    date: str = Field(..., description="Fecha analizada (YYYY-MM-DD)")
    previous_day_close: float = Field(..., description="Cierre del día anterior")
    current_day_close: float = Field(..., description="Cierre del día actual")
    daily_change_percent: float = Field(..., description="Cambio porcentual del día")
    daily_direction: MarketDirection = Field(..., description="Dirección general del día")
    previous_day_high: Optional[float] = Field(None, description="Máximo del día anterior")
    previous_day_low: Optional[float] = Field(None, description="Mínimo del día anterior")
    sessions: list[SessionAnalysis] = Field(..., description="Análisis por sesión")
    summary: str = Field(..., description="Resumen textual del análisis completo")

