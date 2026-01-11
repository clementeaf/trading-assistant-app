"""
Modelos para sistema Q&A de preguntas sobre mercado
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class MarketQuestionRequest(BaseModel):
    """Request para pregunta sobre mercado"""
    question: str = Field(
        ...,
        description="Pregunta en lenguaje natural sobre el mercado",
        min_length=3,
        max_length=500
    )
    language: str = Field(
        default="es",
        description="Idioma de la respuesta (es, en)",
        pattern="^(es|en)$"
    )
    include_context: bool = Field(
        default=True,
        description="Si se debe incluir contexto de mercado en la respuesta"
    )


class MarketContext(BaseModel):
    """Contexto de mercado para responder preguntas"""
    current_price: Optional[float] = Field(None, description="Precio actual de Gold")
    daily_change_percent: Optional[float] = Field(None, description="Cambio diario en porcentaje")
    high_impact_news_count: int = Field(0, description="Número de noticias de alto impacto hoy")
    market_bias: Optional[str] = Field(None, description="Sesgo de mercado (RISK_ON, RISK_OFF, NEUTRAL)")
    trading_mode: Optional[str] = Field(None, description="Modo de trading (CALM, AGGRESSIVE, OBSERVE)")
    dxy_price: Optional[float] = Field(None, description="Precio del DXY")
    bond_yield: Optional[float] = Field(None, description="Rendimiento del bono US10Y")
    geopolitical_risk: Optional[str] = Field(None, description="Nivel de riesgo geopolítico")


class MarketQuestionResponse(BaseModel):
    """Response con respuesta a pregunta sobre mercado"""
    question: str = Field(..., description="Pregunta original")
    answer: str = Field(..., description="Respuesta en lenguaje natural")
    confidence: float = Field(..., description="Nivel de confianza de la respuesta (0.0-1.0)")
    sources_used: List[str] = Field(
        default_factory=list,
        description="Fuentes de datos utilizadas para la respuesta"
    )
    related_topics: List[str] = Field(
        default_factory=list,
        description="Temas relacionados que el usuario podría preguntar"
    )
    context: Optional[MarketContext] = Field(
        None,
        description="Contexto de mercado utilizado para la respuesta"
    )
    model_used: str = Field(..., description="Modelo de LLM utilizado")
    tokens_used: Optional[int] = Field(None, description="Número de tokens utilizados")
    response_time_ms: Optional[int] = Field(None, description="Tiempo de respuesta en milisegundos")
