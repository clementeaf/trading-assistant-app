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
from app.models.psychological_levels import PsychologicalLevelsResponse
from app.models.trading_mode import TradingModeRecommendation
from app.models.trading_recommendation import TradeRecommendation
from app.models.daily_summary import DailySummary, MarketContext
from app.models.market_question import MarketQuestionRequest, MarketQuestionResponse
from app.services.economic_calendar_service import EconomicCalendarService
from app.services.market_analysis_service import MarketAnalysisService
from app.services.market_alignment_service import MarketAlignmentService
from app.services.psychological_levels_service import PsychologicalLevelsService
from app.services.trading_mode_service import TradingModeService
from app.services.trading_advisor_service import TradingAdvisorService
from app.services.technical_analysis_service import TechnicalAnalysisService
from app.services.llm_service import LLMService
from app.utils.validators import CurrencyValidator, InstrumentValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/market-briefing", tags=["Market Briefing"])


def get_economic_calendar_service(
    settings: Settings = Depends(get_settings),
    llm_service: LLMService = Depends(get_llm_service),
    db: Optional[Session] = Depends(get_db)
) -> EconomicCalendarService:
    """
    Dependency para obtener el servicio de calendario económico
    @param settings - Configuración de la aplicación
    @param llm_service - Servicio LLM
    @param db - Sesión de base de datos
    @returns Instancia del servicio de calendario económico
    """
    return EconomicCalendarService(settings, llm_service, db)


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


def get_psychological_levels_service(
    settings: Settings = Depends(get_settings),
    db: Optional[Session] = Depends(get_db)
) -> PsychologicalLevelsService:
    """
    Dependency para obtener el servicio de niveles psicológicos
    @param settings - Configuración de la aplicación
    @param db - Sesión de base de datos
    @returns Instancia del servicio de niveles psicológicos
    """
    return PsychologicalLevelsService(settings, db)


def get_technical_analysis_service(
    settings: Settings = Depends(get_settings),
    db: Optional[Session] = Depends(get_db),
    psychological_levels_service: PsychologicalLevelsService = Depends(get_psychological_levels_service),
    llm_service: LLMService = Depends(get_llm_service)
) -> TechnicalAnalysisService:
    """
    Dependency para obtener el servicio de análisis técnico avanzado
    @param settings - Configuración de la aplicación
    @param db - Sesión de base de datos
    @param psychological_levels_service - Servicio de niveles psicológicos
    @param llm_service - Servicio LLM para detección de patrones
    @returns Instancia del servicio de análisis técnico
    """
    return TechnicalAnalysisService(settings, db, psychological_levels_service, llm_service)


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
    technical_analysis_service: TechnicalAnalysisService = Depends(get_technical_analysis_service),
    llm_service: LLMService = Depends(get_llm_service),
    db: Optional[Session] = Depends(get_db)
) -> TradingAdvisorService:
    """
    Dependency para obtener el servicio de asesoramiento de trading
    @param settings - Configuración de la aplicación
    @param market_analysis_service - Servicio de análisis de mercado
    @param market_alignment_service - Servicio de alineación de mercado
    @param trading_mode_service - Servicio de modo de trading
    @param economic_calendar_service - Servicio de calendario económico
    @param technical_analysis_service - Servicio de análisis técnico
    @param llm_service - Servicio LLM
    @param db - Sesión de base de datos
    @returns Instancia del servicio de asesoramiento de trading
    """
    return TradingAdvisorService(
        settings,
        market_analysis_service,
        market_alignment_service,
        trading_mode_service,
        economic_calendar_service,
        technical_analysis_service,
        llm_service,
        db
    )


def get_llm_service(
    settings: Settings = Depends(get_settings)
) -> LLMService:
    """
    Dependency para obtener el servicio LLM
    @param settings - Configuración de la aplicación
    @returns Instancia del servicio LLM
    """
    return LLMService(settings)


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
    description="Muestra una lista de noticias de alto impacto con su hora, si afectan al USD, y opcionalmente estimación de impacto en Gold."
)
async def get_event_schedule(
    currency: Optional[str] = Query(
        None,
        description="Código de moneda ISO 4217 (ej: USD, EUR). Por defecto USD.",
        min_length=3,
        max_length=3,
        pattern="^[A-Z]{3}$"
    ),
    include_gold_impact: bool = Query(
        True,
        description="Incluir estimación de impacto en Gold para cada evento"
    ),
    include_sentiment: bool = Query(
        False,
        description="Incluir análisis de sentimiento LLM para cada evento (requiere OPENAI_API_KEY)"
    ),
    sentiment_language: str = Query(
        "es",
        description="Idioma para análisis de sentimiento (es, en)",
        pattern="^(es|en)$"
    ),
    service: EconomicCalendarService = Depends(get_economic_calendar_service)
) -> EventScheduleResponse:
    """
    Endpoint para obtener el calendario de eventos económicos de alto impacto del día actual.
    @param currency - Moneda para filtrar (opcional, por defecto USD).
    @param include_gold_impact - Si incluir estimación de impacto en Gold
    @param include_sentiment - Si incluir análisis de sentimiento LLM (opcional)
    @param sentiment_language - Idioma para análisis de sentimiento (es, en)
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

        logger.info(
            f"Fetching event schedule with currency: {validated_currency or 'USD'}, "
            f"include_gold_impact={include_gold_impact}, include_sentiment={include_sentiment}"
        )
        result = await service.get_event_schedule_today(
            currency=validated_currency,
            include_gold_impact=include_gold_impact,
            include_sentiment=include_sentiment,
            sentiment_language=sentiment_language
        )
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
    description="Determina si el DXY y un bono específico (ej: US10Y) están alineados o en conflicto, el sesgo de mercado, y opcionalmente incluye correlación Gold-DXY con proyección de impacto."
)
async def get_dxy_bond_alignment(
    bond: str = Query(
        "US10Y",
        description="Símbolo del bono a analizar (ej: US10Y, US02Y, US30Y)",
        min_length=4,
        max_length=5,
        pattern="^US(02|10|30)Y$"
    ),
    include_gold_correlation: bool = Query(
        True,
        description="Incluir análisis de correlación Gold-DXY"
    ),
    gold_symbol: str = Query(
        "XAUUSD",
        description="Símbolo de Gold a usar para correlación"
    ),
    correlation_days: int = Query(
        30,
        description="Días históricos para calcular correlación",
        ge=7,
        le=90
    ),
    service: MarketAlignmentService = Depends(get_market_alignment_service)
) -> MarketAlignmentAnalysis:
    """
    Endpoint para obtener el análisis de alineación entre DXY y bonos.
    @param bond - Símbolo del bono.
    @param include_gold_correlation - Si incluir correlación Gold-DXY
    @param gold_symbol - Símbolo de Gold
    @param correlation_days - Días para calcular correlación
    @param service - Servicio de alineación de mercado.
    @returns Análisis de alineación entre DXY y bonos con correlación Gold-DXY.
    """
    try:
        validated_bond = InstrumentValidator.validate_bond_symbol(bond)
        logger.info(
            f"Fetching DXY-Bond alignment analysis for {validated_bond} "
            f"(gold_correlation={include_gold_correlation})"
        )
        result = await service.analyze_dxy_bond_alignment(
            bond_symbol=validated_bond,
            include_gold_correlation=include_gold_correlation,
            gold_symbol=gold_symbol,
            correlation_days=correlation_days
        )
        logger.info(f"Alignment: {result.alignment}, Bias: {result.market_bias}")
        
        if result.gold_dxy_correlation:
            logger.info(
                f"Gold-DXY correlation: {result.gold_dxy_correlation.coefficient:.2f} "
                f"({result.gold_dxy_correlation.strength.value})"
            )
        
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
    description="Genera una recomendación de operativa (compra/venta/esperar) con niveles de entrada, stop loss y take profit basado en análisis técnico y fundamental. Opcionalmente incluye justificación generada por LLM."
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
    include_llm_justification: bool = Query(
        False,
        description="Si incluir justificación detallada generada por LLM (requiere OPENAI_API_KEY configurada)"
    ),
    language: str = Query(
        "es",
        description="Idioma para justificación LLM (es, en)",
        pattern="^(es|en)$"
    ),
    service: TradingAdvisorService = Depends(get_trading_advisor_service)
) -> TradeRecommendation:
    """
    Endpoint para obtener recomendación completa de trading con niveles de precio.
    @param instrument - Instrumento principal a analizar.
    @param bond - Símbolo del bono para el análisis de alineación.
    @param time_window_minutes - Ventana de tiempo para noticias próximas.
    @param include_llm_justification - Si incluir justificación LLM (opcional).
    @param language - Idioma para justificación LLM (es, en).
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
            time_window_minutes=time_window_minutes,
            include_llm_justification=include_llm_justification,
            language=language
        )
        logger.info(f"Trading recommendation: {result.direction} (confidence: {result.confidence}, LLM: {include_llm_justification})")
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


@router.get(
    "/technical-analysis",
    summary="Obtiene análisis técnico avanzado multi-temporalidad (Daily, H4, H1)",
    description="Analiza tendencias, RSI, estructura de precio y soporte/resistencia en múltiples timeframes. Opcionalmente detecta patrones complejos con LLM."
)
async def get_technical_analysis(
    instrument: str = Query(
        "XAUUSD",
        description="Instrumento a analizar (ej: XAUUSD)",
        min_length=3,
        max_length=10,
        pattern="^[A-Z0-9]{3,10}$"
    ),
    include_pattern_detection: bool = Query(
        False,
        description="Si se debe detectar patrones técnicos complejos con LLM (Head & Shoulders, Double Top/Bottom, etc.)"
    ),
    pattern_language: str = Query(
        "es",
        description="Idioma para descripción de patrones (es, en)",
        pattern="^(es|en)$"
    ),
    service: TechnicalAnalysisService = Depends(get_technical_analysis_service)
) -> dict:
    """
    Endpoint para obtener análisis técnico avanzado multi-temporalidad.
    @param instrument - Instrumento a analizar.
    @param include_pattern_detection - Si se debe detectar patrones complejos.
    @param pattern_language - Idioma para descripción de patrones.
    @param service - Servicio de análisis técnico.
    @returns Análisis técnico en Daily, H4 y H1, con patrones opcionales.
    """
    try:
        validated_instrument = InstrumentValidator.validate_instrument(instrument)
        logger.info(f"Fetching technical analysis for {validated_instrument} (patterns={include_pattern_detection})")
        result = await service.analyze_multi_timeframe(
            instrument=validated_instrument,
            include_pattern_detection=include_pattern_detection,
            pattern_language=pattern_language
        )
        logger.info(f"Technical analysis completed for {validated_instrument}")
        return result
    except ValueError as e:
        logger.warning(f"Invalid parameter: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching technical analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener el análisis técnico"
        )


@router.get(
    "/psychological-levels",
    response_model=PsychologicalLevelsResponse,
    summary="Obtiene niveles psicológicos de precio con análisis histórico",
    description="Analiza niveles redondos cercanos al precio actual (ej: 4500, 4550) con histórico de reacciones (rebotes/rupturas) en los últimos 30 días."
)
async def get_psychological_levels(
    instrument: str = Query(
        "XAUUSD",
        description="Instrumento a analizar (ej: XAUUSD)",
        min_length=3,
        max_length=10,
        pattern="^[A-Z0-9]{3,10}$"
    ),
    lookback_days: int = Query(
        30,
        description="Días hacia atrás para analizar histórico de reacciones",
        ge=7,
        le=90
    ),
    max_distance_points: float = Query(
        100.0,
        description="Distancia máxima en puntos desde precio actual para considerar niveles",
        ge=20.0,
        le=500.0
    ),
    service: PsychologicalLevelsService = Depends(get_psychological_levels_service)
) -> PsychologicalLevelsResponse:
    """
    Endpoint para obtener análisis de niveles psicológicos de precio.
    @param instrument - Instrumento a analizar.
    @param lookback_days - Días de histórico a analizar.
    @param max_distance_points - Distancia máxima para niveles.
    @param service - Servicio de niveles psicológicos.
    @returns Análisis completo de niveles psicológicos cercanos.
    """
    try:
        validated_instrument = InstrumentValidator.validate_instrument(instrument)
        logger.info(
            f"Fetching psychological levels for {validated_instrument} "
            f"(lookback: {lookback_days} days, max distance: {max_distance_points} points)"
        )
        result = await service.get_psychological_levels(
            instrument=validated_instrument,
            lookback_days=lookback_days,
            max_distance_points=max_distance_points
        )
        logger.info(
            f"Psychological levels analysis completed for {validated_instrument}: "
            f"{len(result.levels)} levels found"
        )
        return result
    except ValueError as e:
        logger.warning(f"Invalid parameter: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching psychological levels: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno al obtener niveles psicológicos"
        )


@router.get(
    "/daily-summary",
    response_model=DailySummary,
    summary="Genera resumen ejecutivo diario del mercado con LLM",
    description="Resumen en lenguaje natural combinando noticias, análisis técnico, macro context y recomendaciones. Generado por GPT-4."
)
async def get_daily_summary(
    instrument: str = Query(
        "XAUUSD",
        description="Instrumento a analizar (ej: XAUUSD)",
        min_length=3,
        max_length=10,
        pattern="^[A-Z0-9]{3,10}$"
    ),
    language: str = Query(
        "es",
        description="Idioma del resumen (es, en)",
        pattern="^(es|en)$"
    ),
    detail_level: str = Query(
        "standard",
        description="Nivel de detalle (brief, standard, detailed)",
        pattern="^(brief|standard|detailed)$"
    ),
    economic_calendar_service: EconomicCalendarService = Depends(get_economic_calendar_service),
    market_analysis_service: MarketAnalysisService = Depends(get_market_analysis_service),
    market_alignment_service: MarketAlignmentService = Depends(get_market_alignment_service),
    trading_mode_service: TradingModeService = Depends(get_trading_mode_service),
    llm_service: LLMService = Depends(get_llm_service)
) -> DailySummary:
    """
    Endpoint para generar resumen ejecutivo diario usando LLM (GPT-4).
    Combina todos los análisis del sistema en un resumen legible de 200-300 palabras.
    
    @param instrument - Instrumento a analizar
    @param language - Idioma del resumen (es, en)
    @param detail_level - Nivel de detalle (brief, standard, detailed)
    @param economic_calendar_service - Servicio de calendario económico
    @param market_analysis_service - Servicio de análisis de mercado
    @param market_alignment_service - Servicio de alineación macro
    @param trading_mode_service - Servicio de modo de trading
    @param llm_service - Servicio LLM
    @returns Resumen ejecutivo generado por LLM
    """
    try:
        validated_instrument = InstrumentValidator.validate_instrument(instrument)
        logger.info(f"Generating daily summary for {validated_instrument} (language: {language}, detail: {detail_level})")
        
        # 1. Obtener análisis de ayer
        yesterday_analysis = await market_analysis_service.analyze_yesterday_sessions(instrument=validated_instrument)
        
        # 2. Obtener noticias de alto impacto
        news = await economic_calendar_service.get_high_impact_news_today()
        
        # 3. Obtener alineación DXY-Bonds con correlación Gold
        alignment = await market_alignment_service.analyze_dxy_bond_alignment(
            bond_symbol="US10Y",
            include_gold_correlation=True,
            gold_symbol=validated_instrument,
            correlation_days=30
        )
        
        # 4. Obtener modo de trading
        trading_mode = await trading_mode_service.get_trading_mode_recommendation(
            instrument=validated_instrument,
            bond_symbol="US10Y",
            time_window_minutes=120
        )
        
        # 5. Obtener precio actual (del análisis de ayer)
        current_price = yesterday_analysis.close_price  # Aproximación (último cierre)
        
        # 6. Construir contexto para LLM
        context = MarketContext(
            high_impact_news_count=news.count,
            geopolitical_risk_level=news.geopolitical_risk.level if news.geopolitical_risk else "LOW",
            market_bias=alignment.market_bias,
            trading_mode=trading_mode.mode,
            gold_dxy_correlation=alignment.gold_dxy_correlation.coefficient if alignment.gold_dxy_correlation else None
        )
        
        # 7. Generar resumen con LLM
        summary = await llm_service.generate_daily_summary(
            context=context,
            yesterday_close=yesterday_analysis.close_price,
            yesterday_change_percent=yesterday_analysis.change_percent,
            current_price=current_price,
            language=language,
            detail_level=detail_level
        )
        
        logger.info(
            f"Daily summary generated successfully for {validated_instrument} "
            f"(sentiment: {summary.market_sentiment}, action: {summary.recommended_action}, "
            f"confidence: {summary.confidence_level:.2f})"
        )
        
        return summary
        
    except ValueError as e:
        logger.warning(f"Invalid parameter: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating daily summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al generar resumen diario: {str(e)}"
        )


@router.post(
    "/ask",
    response_model=MarketQuestionResponse,
    summary="Pregunta sobre el mercado en lenguaje natural",
    description="Responde preguntas del usuario sobre Gold/XAU/USD usando contexto de mercado actual."
)
async def ask_market_question(
    request: MarketQuestionRequest,
    instrument: str = Query(
        "XAUUSD",
        description="Instrumento sobre el que preguntar",
        pattern="^[A-Z0-9]{3,10}$"
    ),
    economic_calendar_service: EconomicCalendarService = Depends(get_economic_calendar_service),
    market_alignment_service: MarketAlignmentService = Depends(get_market_alignment_service),
    trading_mode_service: TradingModeService = Depends(get_trading_mode_service),
    llm_service: LLMService = Depends(get_llm_service),
    settings: Settings = Depends(get_settings)
) -> MarketQuestionResponse:
    """
    Endpoint para responder preguntas sobre el mercado en lenguaje natural
    @param request - Pregunta del usuario
    @param instrument - Instrumento a consultar
    @returns Respuesta con análisis y sugerencias
    """
    import time
    start_time = time.time()
    
    try:
        validated_instrument = InstrumentValidator.validate_instrument(instrument)
        logger.info(f"Processing question for {validated_instrument}: '{request.question[:50]}...'")
        
        # Construir contexto de mercado
        context_dict: dict[str, any] = {}
        
        if request.include_context:
            try:
                # Obtener noticias de alto impacto
                try:
                    high_impact_news = await economic_calendar_service.get_high_impact_news_today()
                    context_dict["high_impact_news_count"] = len(high_impact_news.events)
                    if high_impact_news.geopolitical_risk:
                        context_dict["geopolitical_risk"] = high_impact_news.geopolitical_risk.level
                except Exception:
                    context_dict["high_impact_news_count"] = 0
                
                # Obtener alineación de mercado
                try:
                    alignment = await market_alignment_service.analyze_dxy_bond_alignment(
                        gold_symbol=validated_instrument
                    )
                    context_dict["market_bias"] = alignment.market_bias
                    if alignment.dxy_current:
                        context_dict["dxy_price"] = alignment.dxy_current
                    if alignment.bond_yield_current:
                        context_dict["bond_yield"] = alignment.bond_yield_current
                except Exception:
                    pass
                
                # Obtener modo de trading
                try:
                    trading_mode = await trading_mode_service.get_trading_mode_recommendation(
                        instrument=validated_instrument
                    )
                    context_dict["trading_mode"] = trading_mode.mode
                except Exception:
                    pass
                
                logger.info(f"Context built with {len(context_dict)} data points")
            except Exception as context_error:
                logger.error(f"Error building context: {str(context_error)}")
        
        # Responder pregunta con LLM
        answer_data = await llm_service.answer_market_question(
            question=request.question,
            context=context_dict,
            language=request.language
        )
        
        # Calcular tiempo de respuesta
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Construir respuesta
        response = MarketQuestionResponse(
            question=request.question,
            answer=answer_data["answer"],
            confidence=answer_data.get("confidence", 0.5),
            sources_used=answer_data.get("sources_used", []),
            related_topics=answer_data.get("related_topics", []),
            context=None if not request.include_context else context_dict,
            model_used=settings.openai_model,
            tokens_used=answer_data.get("tokens_used"),
            response_time_ms=response_time_ms
        )
        
        logger.info(
            f"Question answered (confidence: {response.confidence:.2f}, time: {response_time_ms}ms)"
        )
        
        return response
        
    except ValueError as e:
        logger.warning(f"Invalid parameter: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error answering question: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to answer market question")

