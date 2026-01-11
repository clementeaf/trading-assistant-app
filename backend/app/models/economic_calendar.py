"""
Modelos de datos para el calendario económico
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.models.gold_impact import GoldImpactEstimate
from app.models.geopolitical_risk import GeopoliticalRisk


class ImpactLevel(str, Enum):
    """Niveles de impacto de eventos económicos"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EventType(str, Enum):
    """Tipos de eventos económicos categorizados por importancia para XAU/USD"""
    
    # Tier 1: Máximo impacto (mueven mercados globalmente)
    FOMC = "fomc"                          # Decisiones de tasas Fed + conferencia
    NFP = "nfp"                            # Non-Farm Payrolls
    CPI = "cpi"                            # Consumer Price Index (inflación)
    
    # Tier 2: Alto impacto
    UNEMPLOYMENT = "unemployment"          # Tasa de desempleo
    PCE = "pce"                           # Personal Consumption Expenditures (favorito Fed)
    GDP = "gdp"                           # Producto Interno Bruto
    RETAIL_SALES = "retail_sales"         # Ventas minoristas
    PPI = "ppi"                           # Producer Price Index
    
    # Tier 3: Impacto medio-alto
    PMI = "pmi"                           # Purchasing Managers Index
    ISM_MANUFACTURING = "ism_manufacturing"  # ISM Manufacturing
    ISM_SERVICES = "ism_services"         # ISM Services
    JOLTS = "jolts"                       # Job Openings
    ADP_EMPLOYMENT = "adp"                # ADP Employment Report
    
    # Tier 4: Impacto medio
    JOBLESS_CLAIMS = "jobless_claims"     # Initial Jobless Claims
    DURABLE_GOODS = "durable_goods"       # Durable Goods Orders
    HOUSING_STARTS = "housing_starts"     # Housing Starts
    CONSUMER_CONFIDENCE = "consumer_confidence"  # Consumer Confidence Index
    
    # Otros bancos centrales
    ECB = "ecb"                           # European Central Bank
    BOE = "boe"                           # Bank of England
    BOJ = "boj"                           # Bank of Japan
    
    # Geopolítica y otros
    GEOPOLITICAL = "geopolitical"         # Eventos geopolíticos
    TREASURY_AUCTION = "treasury_auction" # Subastas de bonos
    FED_SPEECH = "fed_speech"             # Discursos de miembros Fed
    
    # Sin clasificar
    OTHER = "other"                       # Otros eventos


class NewsSentiment(str, Enum):
    """Sentimiento de noticia para Gold"""
    BULLISH = "bullish"      # Positivo para Gold (alza esperada)
    BEARISH = "bearish"      # Negativo para Gold (baja esperada)
    NEUTRAL = "neutral"      # Sin dirección clara


class EconomicEvent(BaseModel):
    """Modelo de evento económico"""
    date: datetime = Field(..., description="Fecha y hora del evento")
    importance: ImpactLevel = Field(..., description="Nivel de importancia del evento")
    currency: str = Field(..., description="Moneda relacionada (USD, EUR, etc.)")
    description: str = Field(..., description="Descripción del evento (NFP, CPI, FOMC, PMI...)")
    country: Optional[str] = Field(None, description="País relacionado")
    actual: Optional[float] = Field(None, description="Valor actual si está disponible")
    forecast: Optional[float] = Field(None, description="Valor pronosticado")
    previous: Optional[float] = Field(None, description="Valor anterior")
    event_type: EventType = Field(default=EventType.OTHER, description="Tipo categorizado de evento")


class HighImpactNewsResponse(BaseModel):
    """Respuesta del servicio de noticias de alto impacto para XAUUSD"""
    has_high_impact_news: bool = Field(..., description="Indica si hay noticias de alto impacto hoy para XAUUSD")
    count: int = Field(..., description="Cantidad de noticias de alto impacto para XAUUSD")
    events: list[EconomicEvent] = Field(..., description="Lista de eventos de alto impacto relevantes para XAUUSD")
    summary: str = Field(..., description="Resumen textual de las noticias relevantes para XAUUSD")
    instrument: str = Field(default="XAUUSD", description="Instrumento financiero al que aplican las noticias")
    
    # Riesgo geopolítico
    geopolitical_risk: Optional[GeopoliticalRisk] = Field(
        None,
        description="Análisis de riesgo geopolítico basado en eventos"
    )


class EventScheduleItem(BaseModel):
    """Item individual del calendario de eventos"""
    time: str = Field(..., description="Hora del evento en formato HH:MM (UTC)")
    description: str = Field(..., description="Descripción del evento (NFP, CPI, FOMC, PMI...)")
    currency: str = Field(..., description="Moneda relacionada (USD, EUR, etc.)")
    impact: str = Field(..., description="Nivel de impacto (Alto impacto, Medio impacto, Bajo impacto)")
    affects_usd: bool = Field(..., description="Indica si el evento afecta al USD")
    full_description: str = Field(..., description="Descripción completa formateada: 'HH:MM – Descripción – Moneda – Impacto'")
    
    # Campos nuevos para múltiples zonas horarias
    timezones: dict[str, str] = Field(
        default_factory=dict,
        description="Hora del evento en múltiples zonas horarias: {'UTC': '10:30', 'ET': '05:30', 'PT': '02:30'}"
    )
    formatted_time: Optional[str] = Field(
        None,
        description="Hora formateada para display: '10:30 UTC (05:30 ET, 02:30 PT)'"
    )
    
    # Impacto estimado en Gold
    gold_impact: Optional[GoldImpactEstimate] = Field(
        None,
        description="Estimación de impacto del evento en Gold (probabilidad, dirección, magnitud)"
    )
    
    # Sentimiento de la noticia para Gold (generado por LLM)
    sentiment: Optional[NewsSentiment] = Field(
        None,
        description="Sentimiento de la noticia para Gold: BULLISH (positivo), BEARISH (negativo), NEUTRAL"
    )


class EventScheduleResponse(BaseModel):
    """Respuesta del calendario de eventos con horarios"""
    date: str = Field(..., description="Fecha de los eventos (YYYY-MM-DD)")
    events: list[EventScheduleItem] = Field(..., description="Lista de eventos ordenados por hora")
    usd_events_count: int = Field(..., description="Cantidad de eventos que afectan al USD")
    total_events: int = Field(..., description="Cantidad total de eventos")


class UpcomingEvent(BaseModel):
    """Evento económico futuro con información de countdown"""
    event: EconomicEvent = Field(..., description="Datos del evento económico")
    days_until: int = Field(..., description="Días hasta el evento")
    hours_until: Optional[int] = Field(None, description="Horas hasta el evento (si es <48h)")
    is_today: bool = Field(..., description="Si el evento es hoy")
    is_tomorrow: bool = Field(..., description="Si el evento es mañana")
    is_this_week: bool = Field(..., description="Si el evento es esta semana")
    tier: int = Field(..., description="Tier de importancia (1=máximo, 5=bajo)")
    typical_time_et: str = Field(default="Variable", description="Hora típica de publicación en ET")


class UpcomingEventsResponse(BaseModel):
    """Respuesta con eventos económicos futuros"""
    events: list[UpcomingEvent] = Field(..., description="Lista de eventos futuros")
    total_events: int = Field(..., description="Total de eventos encontrados")
    next_high_impact: Optional[UpcomingEvent] = Field(None, description="Próximo evento de alto impacto (Tier 1-2)")
    days_range: int = Field(..., description="Rango de días consultado")
    summary: str = Field(..., description="Resumen de los próximos eventos importantes")

