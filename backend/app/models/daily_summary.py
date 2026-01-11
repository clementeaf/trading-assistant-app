"""
Modelos para resumen ejecutivo diario generado por LLM
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MarketContext(BaseModel):
    """Contexto de mercado simplificado para el resumen"""
    high_impact_news_count: int = Field(description="Cantidad de noticias de alto impacto hoy")
    geopolitical_risk_level: str = Field(description="Nivel de riesgo geopolítico (LOW, MEDIUM, HIGH, CRITICAL)")
    market_bias: str = Field(description="Sesgo de mercado (RISK_ON, RISK_OFF, MIXED)")
    trading_mode: str = Field(description="Modo de trading recomendado (CALM, AGGRESSIVE, OBSERVE)")
    gold_dxy_correlation: Optional[float] = Field(None, description="Correlación Gold-DXY (-1 a 1)")


class DailySummary(BaseModel):
    """Resumen ejecutivo diario del mercado generado por LLM"""
    
    summary: str = Field(
        description="Resumen ejecutivo en lenguaje natural (200-300 palabras)"
    )
    
    key_points: list[str] = Field(
        description="3-5 puntos clave del día",
        min_length=3,
        max_length=5
    )
    
    market_sentiment: str = Field(
        description="Sentimiento general del mercado (BULLISH, BEARISH, NEUTRAL)"
    )
    
    recommended_action: str = Field(
        description="Acción recomendada para hoy (TRADE_ACTIVELY, TRADE_CAUTIOUSLY, OBSERVE)"
    )
    
    confidence_level: float = Field(
        description="Nivel de confianza del análisis (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    
    context: MarketContext = Field(
        description="Contexto de mercado usado para generar el resumen"
    )
    
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de generación del resumen"
    )
    
    model_used: str = Field(
        default="gpt-4-turbo-preview",
        description="Modelo LLM usado para generar el resumen"
    )
    
    tokens_used: Optional[int] = Field(
        None,
        description="Tokens usados en la generación (para tracking de costos)"
    )


class DailySummaryRequest(BaseModel):
    """Request para generar resumen diario (parámetros opcionales)"""
    
    instrument: str = Field(
        default="XAUUSD",
        description="Instrumento a analizar"
    )
    
    language: str = Field(
        default="es",
        description="Idioma del resumen (es, en)"
    )
    
    detail_level: str = Field(
        default="standard",
        description="Nivel de detalle (brief, standard, detailed)"
    )
