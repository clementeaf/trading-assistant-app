"""
Rutas para el servicio de Market Briefing
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config.settings import Settings, get_settings
from app.db.session import get_db
from app.models.economic_calendar import EventScheduleResponse, HighImpactNewsResponse
from app.models.market_analysis import DailyMarketAnalysis
from app.models.market_alignment import MarketAlignmentAnalysis
from app.models.trading_mode import TradingModeRecommendation
from app.models.trading_recommendation import TradeRecommendation
from app.services.economic_calendar_service import EconomicCalendarService
from app.services.market_analysis_service import MarketAnalysisService
from app.services.market_alignment_service import MarketAlignmentService
from app.services.trading_mode_service import TradingModeService
from app.services.trading_advisor_service import TradingAdvisorService
from app.utils.validators import CurrencyValidator, InstrumentValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/market-briefing", tags=["Market Briefing"])


def get_economic_calendar_service(
    settings: Settings = Depends(get_settings),
    db: Optional[Session] = Depends(get_db)
) -> EconomicCalendarService:
    """
    Dependency para obtener el servicio de calendario económico
    @param settings - Configuración de la aplicación
    @param db - Sesión de base de datos
    @returns Instancia del servicio de calendario económico
    """
    return EconomicCalendarService(settings, db)


def get_market_analysis_service(
    settings: Settings = Depends(get_settings),
    db: Optional[Session] = Depends(get_db)
) -> MarketAnalysisService:
    """
    Dependency para obtener el servicio de análisis de mercado
    @param settings - Configuración de la aplicación
    @param db - Sesión de base de datos
    @returns Instancia del servicio de análisis de mercado
    """
    return MarketAnalysisService(settings, db)


def get_market_alignment_service(
    settings: Settings = Depends(get_settings),
    db: Optional[Session] = Depends(get_db)
) -> MarketAlignmentService:
    """
    Dependency para obtener el servicio de alineación de mercado
    @param settings - Configuración de la aplicación
    @param db - Sesión de base de datos
    @returns Instancia del servicio de alineación de mercado
    """
    return MarketAlignmentService(settings, db)


def get_trading_mode_service(
    settings: Settings = Depends(get_settings),
    economic_calendar_service: EconomicCalendarService = Depends(get_economic_calendar_service),
    market_analysis_service: MarketAnalysisService = Depends(get_market_analysis_service),
    market_alignment_service: MarketAlignmentService = Depends(get_market_alignment_service),
    db: Optional[Session] = Depends(get_db)
) -> TradingModeService:
    """
    Dependency para obtener el servicio de recomendación de modo de trading
    @param settings - Configuración de la aplicación
    @param economic_calendar_service - Servicio de calendario económico
    @param market_analysis_service - Servicio de análisis de mercado
    @param market_alignment_service - Servicio de alineación de mercado
    @param db - Sesión de base de datos
    @returns Instancia del servicio de modo de trading
    """
    return TradingModeService(
        settings,
        economic_calendar_service,
        market_analysis_service,
        market_alignment_service,
        db
    )


def get_trading_advisor_service(
    settings: Settings = Depends(get_settings),
    market_analysis_service: MarketAnalysisService = Depends(get_market_analysis_service),
    market_alignment_service: MarketAlignmentService = Depends(get_market_alignment_service),
    trading_mode_service: TradingModeService = Depends(get_trading_mode_service),
    economic_calendar_service: EconomicCalendarService = Depends(get_economic_calendar_service),
    db: Optional[Session] = Depends(get_db)
) -> TradingAdvisorService:
    """
    Dependency para obtener el servicio de asesoramiento de trading
    @param settings - Configuración de la aplicación
    @param market_analysis_service - Servicio de análisis de mercado
    @param market_alignment_service - Servicio de alineación de mercado
    @param trading_mode_service - Servicio de modo de trading
    @param economic_calendar_service - Servicio de calendario económico
    @param db - Sesión de base de datos
    @returns Instancia del servicio de asesoramiento de trading
    """
    return TradingAdvisorService(
        settings,
        market_analysis_service,
        market_alignment_service,
        trading_mode_service,
        economic_calendar_service,
        db
    )


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
    summary="Obtiene el calendario de eventos económicos de alto impacto del día",
    description="Muestra una lista de noticias de alto impacto con su hora y si afectan al USD."
)
async def get_event_schedule(
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
    Endpoint para obtener el calendario de eventos económicos de alto impacto del día actual.
    @param currency - Moneda para filtrar (opcional, por defecto USD).
    @param service - Servicio de calendario económico.
    @returns Respuesta con el calendario de eventos formateado.
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

        logger.info(f"Fetching event schedule with currency: {validated_currency or 'USD'}")
        result = await service.get_event_schedule_today(currency=validated_currency)
        logger.info(f"Successfully retrieved {result.total_events} events, {result.usd_events_count} affecting USD")
        return result
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
    summary="Obtiene el análisis de mercado del día anterior para un instrumento",
    description="Proporciona un resumen de cómo cerró el instrumento ayer y qué pasó durante las sesiones de trading (Asia, Londres, Nueva York)."
)
async def get_yesterday_analysis(
    instrument: str = Query(
        ...,
        description="Símbolo del instrumento a analizar (ej: XAUUSD, EURUSD, NASDAQ)",
        min_length=3,
        max_length=10,
        pattern="^[A-Z0-9]{3,10}$"
    ),
    service: MarketAnalysisService = Depends(get_market_analysis_service)
) -> DailyMarketAnalysis:
    """
    Endpoint para obtener el análisis de mercado del día anterior.
    @param instrument - Símbolo del instrumento.
    @param service - Servicio de análisis de mercado.
    @returns Análisis completo del día anterior.
    """
    try:
        validated_instrument = InstrumentValidator.validate_instrument(instrument)
        logger.info(f"Fetching yesterday analysis for {validated_instrument}")
        result = await service.analyze_yesterday_sessions(instrument=validated_instrument)
        logger.info(f"Successfully generated analysis for {validated_instrument}")
        return result
    except ValueError as e:
        logger.warning(f"Invalid instrument parameter: {instrument} - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching yesterday analysis for {instrument}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener el análisis del día anterior"
        )


@router.get(
    "/dxy-bond-alignment",
    response_model=MarketAlignmentAnalysis,
    summary="Analiza la alineación entre el DXY y los rendimientos de bonos",
    description="Determina si el DXY y un bono específico (ej: US10Y) están alineados o en conflicto, y el sesgo de mercado."
)
async def get_dxy_bond_alignment(
    bond: str = Query(
        "US10Y",
        description="Símbolo del bono a analizar (ej: US10Y, US02Y, US30Y)",
        min_length=4,
        max_length=5,
        pattern="^US(02|10|30)Y$"
    ),
    service: MarketAlignmentService = Depends(get_market_alignment_service)
) -> MarketAlignmentAnalysis:
    """
    Endpoint para obtener el análisis de alineación entre DXY y bonos.
    @param bond - Símbolo del bono.
    @param service - Servicio de alineación de mercado.
    @returns Análisis de alineación entre DXY y bonos.
    """
    try:
        validated_bond = InstrumentValidator.validate_bond_symbol(bond)
        logger.info(f"Fetching DXY-Bond alignment analysis for {validated_bond}")
        result = await service.analyze_dxy_bond_alignment(bond_symbol=validated_bond)
        logger.info(f"Alignment: {result.alignment}, Bias: {result.market_bias}")
        return result
    except ValueError as e:
        logger.warning(f"Invalid bond symbol parameter: {bond} - {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching DXY-Bond alignment for {bond}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener el análisis de alineación DXY-Bonos"
        )


@router.get(
    "/trading-mode",
    response_model=TradingModeRecommendation,
    summary="Obtiene una recomendación del modo de trading para el día",
    description="Sugiere un modo de trading (Calma, Agresivo, Muy Calma/Observar) basado en noticias, volatilidad y alineación de mercado."
)
async def get_trading_mode_recommendation(
    instrument: str = Query(
        "XAUUSD",
        description="Instrumento principal a analizar (ej: XAUUSD)",
        min_length=3,
        max_length=10,
        pattern="^[A-Z0-9]{3,10}$"
    ),
    bond: str = Query(
        "US10Y",
        description="Símbolo del bono para el análisis de alineación (ej: US10Y, US02Y)",
        min_length=4,
        max_length=5,
        pattern="^US(02|10|30)Y$"
    ),
    time_window_minutes: int = Query(
        120,
        description="Ventana de tiempo en minutos para considerar noticias próximas de alto impacto USD",
        ge=30,
        le=360
    ),
    service: TradingModeService = Depends(get_trading_mode_service)
) -> TradingModeRecommendation:
    """
    Endpoint para obtener una recomendación del modo de trading.
    @param instrument - Instrumento principal a analizar.
    @param bond - Símbolo del bono para el análisis de alineación.
    @param time_window_minutes - Ventana de tiempo para noticias próximas.
    @param service - Servicio de recomendación de modo de trading.
    @returns Recomendación del modo de trading.
    """
    try:
        validated_instrument = InstrumentValidator.validate_instrument(instrument)
        validated_bond = InstrumentValidator.validate_bond_symbol(bond)
        logger.info(f"Fetching trading mode recommendation for {validated_instrument}")
        result = await service.get_trading_mode_recommendation(
            instrument=validated_instrument,
            bond_symbol=validated_bond,
            time_window_minutes=time_window_minutes
        )
        logger.info(f"Trading mode recommendation: {result.mode} (confidence: {result.confidence})")
        return result
    except ValueError as e:
        logger.warning(f"Invalid parameter: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching trading mode recommendation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener la recomendación del modo de trading"
        )


@router.get(
    "/trading-recommendation",
    response_model=TradeRecommendation,
    summary="Obtiene recomendación completa de trading con niveles de precio",
    description="Genera una recomendación de operativa (compra/venta/esperar) con niveles de entrada, stop loss y take profit basado en análisis técnico y fundamental."
)
async def get_trading_recommendation(
    instrument: str = Query(
        "XAUUSD",
        description="Instrumento principal a analizar (ej: XAUUSD)",
        min_length=3,
        max_length=10,
        pattern="^[A-Z0-9]{3,10}$"
    ),
    bond: str = Query(
        "US10Y",
        description="Símbolo del bono para el análisis de alineación (ej: US10Y, US02Y)",
        min_length=4,
        max_length=5,
        pattern="^US(02|10|30)Y$"
    ),
    time_window_minutes: int = Query(
        120,
        description="Ventana de tiempo en minutos para considerar noticias próximas de alto impacto USD",
        ge=30,
        le=360
    ),
    service: TradingAdvisorService = Depends(get_trading_advisor_service)
) -> TradeRecommendation:
    """
    Endpoint para obtener recomendación completa de trading con niveles de precio.
    @param instrument - Instrumento principal a analizar.
    @param bond - Símbolo del bono para el análisis de alineación.
    @param time_window_minutes - Ventana de tiempo para noticias próximas.
    @param service - Servicio de asesoramiento de trading.
    @returns Recomendación de trading con niveles de precio.
    """
    try:
        validated_instrument = InstrumentValidator.validate_instrument(instrument)
        validated_bond = InstrumentValidator.validate_bond_symbol(bond)
        logger.info(f"Fetching trading recommendation for {validated_instrument}")
        result = await service.get_trading_recommendation(
            instrument=validated_instrument,
            bond_symbol=validated_bond,
            time_window_minutes=time_window_minutes
        )
        logger.info(f"Trading recommendation: {result.direction} (confidence: {result.confidence})")
        return result
    except ValueError as e:
        logger.warning(f"Invalid parameter: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching trading recommendation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener la recomendación de trading"
        )
