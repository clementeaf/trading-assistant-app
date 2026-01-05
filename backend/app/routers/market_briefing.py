"""
Router para el servicio de briefing de mercado
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.config.settings import Settings, get_settings
from app.models.economic_calendar import EventScheduleResponse, HighImpactNewsResponse
from app.models.market_analysis import DailyMarketAnalysis
from app.services.economic_calendar_service import EconomicCalendarService
from app.services.market_analysis_service import MarketAnalysisService
from app.utils.schedule_formatter import ScheduleFormatter
from app.utils.validators import CurrencyValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/market-briefing", tags=["Market Briefing"])


def get_economic_calendar_service(
    settings: Settings = Depends(get_settings)
) -> EconomicCalendarService:
    """
    Dependency para obtener el servicio de calendario económico
    @param settings - Configuración de la aplicación
    @returns Instancia del servicio de calendario económico
    """
    return EconomicCalendarService(settings)


def get_market_analysis_service(
    settings: Settings = Depends(get_settings)
) -> MarketAnalysisService:
    """
    Dependency para obtener el servicio de análisis de mercado
    @param settings - Configuración de la aplicación
    @returns Instancia del servicio de análisis de mercado
    """
    return MarketAnalysisService(settings)


@router.get(
    "/high-impact-news",
    response_model=HighImpactNewsResponse,
    summary="Obtiene noticias de alto impacto para XAUUSD del día",
    description="Verifica si hay noticias económicas de alto impacto hoy relevantes para XAUUSD (NFP, CPI, Fed, PMI...)"
)
async def get_high_impact_news_today(
    currency: Optional[str] = Query(
        None,
        description="Código de moneda ISO 4217 (ej: USD, EUR). Por defecto USD.",
        min_length=3,
        max_length=3,
        pattern="^[A-Z]{3}$"
    ),
    service: EconomicCalendarService = Depends(get_economic_calendar_service)
) -> HighImpactNewsResponse:
    """
    Endpoint para obtener noticias de alto impacto del día actual relevantes para XAUUSD
    @param currency - Moneda para filtrar (opcional, por defecto USD). Debe ser código ISO 4217 de 3 letras.
    @param service - Servicio de calendario económico
    @returns Respuesta con noticias de alto impacto relevantes para XAUUSD
    """
    try:
        validated_currency = None
        if currency:
            try:
                validated_currency = CurrencyValidator.validate_currency(currency)
            except ValueError as e:
                logger.warning(f"Invalid currency parameter: {currency} - {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=str(e)
                )
        
        logger.info(f"Fetching high impact news for XAUUSD with currency: {validated_currency or 'USD'}")
        result = await service.get_high_impact_news_today(currency=validated_currency)
        logger.info(f"Successfully retrieved {result.count} high impact events for XAUUSD")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching high impact news for XAUUSD: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener noticias de alto impacto para XAUUSD"
        )


@router.get(
    "/event-schedule",
    response_model=EventScheduleResponse,
    summary="Obtiene el calendario de eventos del día con horarios",
    description="Devuelve una lista de eventos económicos del día con sus horarios, indicando cuáles afectan al USD"
)
async def get_event_schedule_today(
    currency: Optional[str] = Query(
        None,
        description="Código de moneda ISO 4217 (ej: USD, EUR). Por defecto USD.",
        min_length=3,
        max_length=3,
        pattern="^[A-Z]{3}$"
    ),
    service: EconomicCalendarService = Depends(get_economic_calendar_service)
) -> EventScheduleResponse:
    """
    Endpoint para obtener el calendario de eventos del día con horarios
    @param currency - Moneda para filtrar (opcional, por defecto USD). Debe ser código ISO 4217 de 3 letras.
    @param service - Servicio de calendario económico
    @returns Respuesta con calendario de eventos formateado
    """
    try:
        from datetime import date
        
        validated_currency = None
        if currency:
            try:
                validated_currency = CurrencyValidator.validate_currency(currency)
            except ValueError as e:
                logger.warning(f"Invalid currency parameter: {currency} - {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=str(e)
                )
        
        logger.info(f"Fetching event schedule with currency: {validated_currency or 'USD'}")
        events = await service.get_event_schedule_today(currency=validated_currency)
        
        formatted_events = ScheduleFormatter.format_events(events)
        usd_events_count = sum(1 for event in formatted_events if event.affects_usd)
        
        logger.info(f"Successfully retrieved {len(formatted_events)} events, {usd_events_count} affecting USD")
        
        return EventScheduleResponse(
            date=date.today().isoformat(),
            events=formatted_events,
            usd_events_count=usd_events_count,
            total_events=len(formatted_events)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching event schedule: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener el calendario de eventos"
        )


@router.get(
    "/yesterday-analysis",
    response_model=DailyMarketAnalysis,
    summary="Analiza el cierre de ayer y las sesiones de trading",
    description="Analiza cómo cerró el instrumento ayer, las sesiones de Asia, Londres y NY, y genera un resumen"
)
async def get_yesterday_analysis(
    instrument: str = Query(
        "XAUUSD",
        description="Instrumento a analizar (ej: XAUUSD, EURUSD, NASDAQ)",
        min_length=3,
        max_length=10
    ),
    service: MarketAnalysisService = Depends(get_market_analysis_service)
) -> DailyMarketAnalysis:
    """
    Endpoint para obtener análisis del cierre de ayer y sesiones de trading
    @param instrument - Instrumento a analizar (por defecto XAUUSD)
    @param service - Servicio de análisis de mercado
    @returns Análisis completo del día anterior
    """
    try:
        logger.info(f"Fetching yesterday analysis for {instrument}")
        result = await service.analyze_yesterday_sessions(instrument=instrument)
        logger.info(f"Successfully generated analysis for {instrument}")
        return result
    except ValueError as e:
        logger.warning(f"Invalid request: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching yesterday analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener el análisis del día anterior"
        )

