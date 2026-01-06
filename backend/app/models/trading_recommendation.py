"""
Modelos de datos para recomendaciones de trading
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TradeDirection(str, Enum):
    """Dirección de la operativa recomendada"""
    BUY = "compra"
    SELL = "venta"
    WAIT = "esperar"


class TradeRecommendation(BaseModel):
    """Recomendación de trading con niveles de precio"""
    # Información temporal
    analysis_date: str = Field(..., description="Fecha del análisis (último día hábil analizado)")
    analysis_datetime: str = Field(..., description="Fecha y hora cuando se generó la recomendación (ISO format)")
    current_datetime: str = Field(..., description="Fecha y hora actual del sistema (ISO format)")
    
    direction: TradeDirection = Field(..., description="Dirección recomendada (compra/venta/esperar)")
    confidence: float = Field(..., description="Nivel de confianza (0.0-1.0)")
    current_price: float = Field(..., description="Precio actual de XAUUSD")
    
    # Niveles de precio
    entry_price: Optional[float] = Field(None, description="Precio de entrada recomendado")
    stop_loss: Optional[float] = Field(None, description="Stop loss recomendado")
    take_profit_1: Optional[float] = Field(None, description="Primer objetivo de take profit")
    take_profit_2: Optional[float] = Field(None, description="Segundo objetivo de take profit (opcional)")
    
    # Rango de precio óptimo
    optimal_entry_range: Optional[dict[str, float]] = Field(
        None,
        description="Rango de precio óptimo para entrada (min, max)"
    )
    
    # Análisis técnico
    support_level: Optional[float] = Field(None, description="Nivel de soporte identificado")
    resistance_level: Optional[float] = Field(None, description="Nivel de resistencia identificado")
    
    # Contexto del mercado
    market_context: str = Field(..., description="Contexto del mercado (risk-on/risk-off/neutral)")
    trading_mode: str = Field(..., description="Modo de trading recomendado (calma/agresivo/etc)")
    
    # Razones y explicación
    reasons: list[str] = Field(..., description="Lista de razones para la recomendación")
    summary: str = Field(..., description="Resumen de la recomendación")
    detailed_explanation: str = Field(..., description="Explicación detallada con análisis")
    
    # Advertencias
    warnings: list[str] = Field(default_factory=list, description="Advertencias importantes (noticias próximas, etc)")

