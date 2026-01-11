"""
Servicio de análisis técnico avanzado multi-temporalidad
Analiza Daily, H4, H1 con RSI, tendencias y estructura de precio
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.models.market_analysis import MarketDirection, PriceCandle
from app.providers.market_data.base_market_provider import MarketDataProvider
from app.providers.market_data.twelve_data_provider import TwelveDataProvider
from app.providers.market_data.alpha_vantage_provider import AlphaVantageProvider
from app.providers.market_data.mock_market_provider import MockMarketProvider
from app.repositories.market_data_repository import MarketDataRepository
from app.services.psychological_levels_service import PsychologicalLevelsService
from app.utils.business_days import BusinessDays
from app.utils.technical_analysis import TechnicalAnalysis

logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    """Servicio de análisis técnico avanzado"""
    
    def __init__(
        self,
        settings: Settings,
        db: Optional[Session] = None,
        psychological_levels_service: Optional[PsychologicalLevelsService] = None,
        llm_service: Optional[LLMService] = None
    ):
        """
        Inicializa el servicio de análisis técnico
        @param settings - Configuración de la aplicación
        @param db - Sesión de base de datos (opcional)
        @param psychological_levels_service - Servicio de niveles (opcional)
        @param llm_service - Servicio LLM para detección de patrones (opcional)
        """
        self.settings = settings
        self.provider = self._create_provider(settings)
        self.db = db
        self.market_data_repo = MarketDataRepository(db)
        self.psychological_levels_service = psychological_levels_service
        self.llm_service = llm_service
    
    def _create_provider(self, settings: Settings) -> MarketDataProvider:
        """
        Crea el proveedor de datos de mercado
        @param settings - Configuración de la aplicación
        @returns Instancia del proveedor
        """
        provider_name = settings.market_data_provider.lower()
        
        if provider_name == "twelvedata":
            if not settings.market_data_api_key:
                raise ValueError(
                    "Twelve Data provider selected but no API key configured. "
                    "Please set MARKET_DATA_API_KEY environment variable."
                )
            logger.info("Using Twelve Data provider for technical analysis")
            return TwelveDataProvider(api_key=settings.market_data_api_key)
        elif provider_name == "alphavantage":
            if not settings.market_data_api_key:
                raise ValueError(
                    "Alpha Vantage provider selected but no API key configured. "
                    "Please set MARKET_DATA_API_KEY environment variable."
                )
            logger.info("Using Alpha Vantage provider for technical analysis")
            return AlphaVantageProvider(api_key=settings.market_data_api_key)
        elif provider_name == "mock":
            logger.info("Using Mock provider for technical analysis")
            return MockMarketProvider()
        else:
            raise ValueError(
                f"Unknown market data provider '{provider_name}'. "
                "Supported providers: twelvedata, alphavantage, mock"
            )
    
    async def analyze_multi_timeframe(
        self,
        instrument: str = "XAUUSD"
    ) -> dict:
        """
        Realiza análisis técnico en múltiples temporalidades (Daily, H4, H1)
        @param instrument - Instrumento a analizar
        @returns Diccionario con análisis de cada timeframe
        """
        logger.info(f"Starting multi-timeframe analysis for {instrument}")
        
        # Obtener último día hábil
        today = datetime.now().date()
        last_business_day = BusinessDays.get_last_business_day(today)
        
        # Calcular rangos de fechas para cada timeframe
        # Daily: últimos 30 días
        daily_start = datetime.combine(last_business_day - timedelta(days=30), datetime.min.time())
        daily_end = datetime.combine(last_business_day, datetime.max.time())
        
        # H4: últimos 20 días (para tener suficientes velas H4)
        h4_start = datetime.combine(last_business_day - timedelta(days=20), datetime.min.time())
        h4_end = datetime.now()
        
        # H1: últimos 7 días (para tener suficientes velas H1)
        h1_start = datetime.combine(last_business_day - timedelta(days=7), datetime.min.time())
        h1_end = datetime.now()
        
        # Obtener datos de cada timeframe (primero de BD, luego de API si es necesario)
        daily_candles = await self._get_candles_with_cache(
            instrument, daily_start, daily_end, "1day", "Daily"
        )
        h4_candles = await self._get_candles_with_cache(
            instrument, h4_start, h4_end, "4h", "H4"
        )
        h1_candles = await self._get_candles_with_cache(
            instrument, h1_start, h1_end, "1h", "H1"
        )
        
        logger.info(
            f"Fetched candles: Daily={len(daily_candles)}, H4={len(h4_candles)}, H1={len(h1_candles)}"
        )
        
        # Análisis Daily
        try:
            daily_analysis = self._analyze_timeframe(
                daily_candles, "Daily", instrument
            )
        except Exception as e:
            logger.error(f"Error analyzing Daily timeframe: {str(e)}", exc_info=True)
            daily_analysis = {"timeframe": "Daily", "error": str(e)}
        
        # Análisis H4
        try:
            h4_analysis = self._analyze_timeframe(
                h4_candles, "H4", instrument, rsi_zones=[55, 50, 45]
            )
        except Exception as e:
            logger.error(f"Error analyzing H4 timeframe: {str(e)}", exc_info=True)
            h4_analysis = {"timeframe": "H4", "error": str(e)}
        
        # Análisis H1 (confirmación)
        try:
            h1_analysis = self._analyze_timeframe(
                h1_candles, "H1", instrument
            )
        except Exception as e:
            logger.error(f"Error analyzing H1 timeframe: {str(e)}", exc_info=True)
            h1_analysis = {"timeframe": "H1", "error": str(e)}
        
        try:
            summary = self._generate_summary(daily_analysis, h4_analysis, h1_analysis)
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            summary = "Error generating summary"
        
        # Obtener últimas velas para el chart (priorizar H4, luego H1, luego Daily)
        chart_candles_source = []
        if h4_candles and len(h4_candles) > 0:
            sorted_h4 = sorted(h4_candles, key=lambda c: c.timestamp)
            chart_candles_source = sorted_h4[-50:]  # Últimas 50 velas H4
            logger.info(f"Using {len(chart_candles_source)} H4 candles for chart")
        elif h1_candles and len(h1_candles) > 0:
            sorted_h1 = sorted(h1_candles, key=lambda c: c.timestamp)
            chart_candles_source = sorted_h1[-100:]  # Últimas 100 velas H1 (más velas porque son más pequeñas)
            logger.info(f"Using {len(chart_candles_source)} H1 candles for chart (H4 not available)")
        elif daily_candles and len(daily_candles) > 0:
            sorted_daily = sorted(daily_candles, key=lambda c: c.timestamp)
            chart_candles_source = sorted_daily[-50:]  # Últimas 50 velas Daily
            logger.info(f"Using {len(chart_candles_source)} Daily candles for chart (H4 and H1 not available)")
        else:
            logger.warning(f"No candles available for chart. H4={len(h4_candles)}, H1={len(h1_candles)}, Daily={len(daily_candles)}")
        
        chart_candles_data = [
            {
                "timestamp": c.timestamp.isoformat(),
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume
            }
            for c in chart_candles_source
        ]
        
        logger.info(f"Returning {len(chart_candles_data)} chart candles")
        
        return {
            "instrument": instrument,
            "analysis_date": last_business_day.isoformat(),
            "daily": daily_analysis,
            "h4": h4_analysis,
            "h1": h1_analysis,
            "summary": summary,
            "chart_candles": chart_candles_data
        }
    
    async def _get_candles_with_cache(
        self,
        instrument: str,
        start_date: datetime,
        end_date: datetime,
        interval: str,
        timeframe_name: str
    ) -> list[PriceCandle]:
        """
        Obtiene velas desde BD o API, usando BD como caché
        @param instrument - Instrumento a analizar
        @param start_date - Fecha de inicio
        @param end_date - Fecha de fin
        @param interval - Intervalo de las velas
        @param timeframe_name - Nombre del timeframe para logging
        @returns Lista de velas
        """
        # Mapear intervalos para BD (usar formato estándar)
        interval_mapping = {
            "1day": "1d",
            "4h": "4h",
            "1h": "1h"
        }
        db_interval = interval_mapping.get(interval, interval)
        logger.info(f"Fetching {timeframe_name} candles: interval={interval}, db_interval={db_interval}, start={start_date}, end={end_date}")
        
        # Intentar obtener de BD primero
        db_candles = []
        if self.db:
            try:
                db_models = self.market_data_repo.get_candles(
                    instrument, start_date, end_date, db_interval
                )
                db_candles = self.market_data_repo.convert_to_price_candles(db_models)
                logger.info(f"Retrieved {len(db_candles)} {timeframe_name} candles from database")
            except Exception as e:
                logger.warning(f"Error retrieving {timeframe_name} candles from DB: {str(e)}")
        
        # Verificar si necesitamos actualizar desde API
        needs_update = False
        if not db_candles:
            needs_update = True
            logger.info(f"No {timeframe_name} candles in DB, will fetch from API")
        else:
            # Verificar si la última vela es reciente
            latest_candle = max(db_candles, key=lambda c: c.timestamp)
            time_since_last = datetime.now() - latest_candle.timestamp
            
            # Para H4, actualizar si la última vela tiene más de 5 horas
            # Para H1, actualizar si la última vela tiene más de 2 horas
            # Para Daily, actualizar si la última vela tiene más de 1 día
            update_thresholds = {
                "H4": timedelta(hours=5),
                "H1": timedelta(hours=2),
                "Daily": timedelta(days=1)
            }
            threshold = update_thresholds.get(timeframe_name, timedelta(hours=4))
            
            if time_since_last > threshold:
                needs_update = True
                logger.info(
                    f"{timeframe_name} candles are {time_since_last} old, "
                    f"updating from API (threshold: {threshold})"
                )
        
        # Si necesitamos actualizar, obtener de API y guardar en BD
        if needs_update:
            try:
                api_candles = await self.provider.fetch_historical_candles(
                    instrument, start_date, end_date, interval
                )
                logger.info(f"Fetched {len(api_candles)} {timeframe_name} candles from API")
                
                # Guardar en BD
                if self.db and api_candles:
                    try:
                        self.market_data_repo.save_candles(
                            instrument, api_candles, db_interval
                        )
                        logger.info(f"Saved {len(api_candles)} {timeframe_name} candles to database")
                    except Exception as e:
                        logger.warning(f"Error saving {timeframe_name} candles to DB: {str(e)}")
                
                return api_candles
            except Exception as e:
                logger.warning(f"Could not fetch {timeframe_name} candles from API: {str(e)}")
                # Si falla la API pero tenemos datos en BD, usar esos
                if db_candles:
                    logger.info(f"Using {len(db_candles)} cached {timeframe_name} candles from DB")
                    return db_candles
                return []
        
        # Usar datos de BD
        return db_candles
    
    def _analyze_timeframe(
        self,
        candles: list[PriceCandle],
        timeframe: str,
        instrument: str,
        rsi_zones: Optional[list[float]] = None
    ) -> dict:
        """
        Analiza un timeframe específico
        @param candles - Lista de velas
        @param timeframe - Nombre del timeframe (Daily, H4, H1)
        @param instrument - Instrumento analizado
        @param rsi_zones - Zonas objetivo de RSI (opcional)
        @returns Diccionario con análisis del timeframe
        """
        if not candles:
            return {
                "timeframe": timeframe,
                "error": "No data available"
            }
        
        sorted_candles = sorted(candles, key=lambda c: c.timestamp)
        current_price = sorted_candles[-1].close
        
        # Identificar tendencia
        trend = TechnicalAnalysis.identify_trend(sorted_candles)
        
        # Calcular RSI (solo para H4 según requerimientos)
        rsi = None
        rsi_zone = None
        if timeframe == "H4" and rsi_zones:
            rsi = TechnicalAnalysis.calculate_rsi(sorted_candles)
            if rsi is not None:
                rsi_zone = TechnicalAnalysis.check_rsi_zone(rsi, rsi_zones)
        
        # Calcular EMAs (50, 100, 200) para todos los timeframes
        emas = TechnicalAnalysis.calculate_emas(sorted_candles, periods=[50, 100, 200])
        
        # Análisis de impulso (solo para H4)
        impulse_direction = None
        impulse_distance = 0.0
        impulse_strong = False
        if timeframe == "H4":
            impulse_direction, impulse_distance, impulse_strong = TechnicalAnalysis.analyze_impulse_strength(
                sorted_candles, lookback=2
            )
        
        # Soporte y resistencia
        support, resistance = TechnicalAnalysis.find_support_resistance(sorted_candles)
        
        # Verificar proximidad a niveles
        near_support = False
        near_resistance = False
        if support:
            near_support = TechnicalAnalysis.is_price_near_level(current_price, support)
        if resistance:
            near_resistance = TechnicalAnalysis.is_price_near_level(current_price, resistance)
            
        # Análisis de niveles psicológicos (si el servicio está disponible)
        psychological_context = None
        retests = []
        if self.psychological_levels_service:
            try:
                # Usar las velas ya obtenidas para analizar niveles
                # Convertir PriceCandle a formato esperado si es necesario
                # Nota: analyze_levels_from_candles espera list[PriceCandle]
                psych_analysis = self.psychological_levels_service.analyze_levels_from_candles(
                    instrument=instrument,
                    current_price=current_price,
                    candles=sorted_candles,  # Usar velas ordenadas
                    max_distance_points=100.0 if timeframe == "H4" else 50.0  # Ajustar distancia por TF
                )
                
                # Convertir a dict para serialización JSON
                psychological_context = {
                    "nearest_support": psych_analysis.nearest_support.dict() if psych_analysis.nearest_support else None,
                    "nearest_resistance": psych_analysis.nearest_resistance.dict() if psych_analysis.nearest_resistance else None,
                    "strongest_support": psych_analysis.strongest_support.dict() if psych_analysis.strongest_support else None,
                    "strongest_resistance": psych_analysis.strongest_resistance.dict() if psych_analysis.strongest_resistance else None
                }
                
                # Detectar retesteos
                levels_to_check = []
                if psych_analysis.nearest_support:
                    levels_to_check.append(psych_analysis.nearest_support.level)
                if psych_analysis.nearest_resistance:
                    levels_to_check.append(psych_analysis.nearest_resistance.level)
                
                retests = self._detect_retests(sorted_candles, levels_to_check)
                
            except Exception as e:
                logger.warning(f"Error analyzing psychological levels for {timeframe}: {str(e)}")
        
        return {
            "timeframe": timeframe,
            "current_price": round(current_price, 2),
            "trend": trend.value,
            "rsi": rsi,
            "rsi_zone": rsi_zone,
            "impulse_direction": impulse_direction.value if impulse_direction else None,
            "impulse_distance_percent": impulse_distance,
            "impulse_strong": impulse_strong,
            "support": support,
            "resistance": resistance,
            "near_support": near_support,
            "near_resistance": near_resistance,
            "psychological_context": psychological_context,
            "retests": retests,
            "ema_50": emas.get(50),
            "ema_100": emas.get(100),
            "ema_200": emas.get(200),
            "candles_count": len(sorted_candles),
            "last_candle_time": sorted_candles[-1].timestamp.isoformat() if sorted_candles else None
        }

    def _detect_retests(
        self,
        candles: list[PriceCandle],
        levels: list[float],
        lookback: int = 5
    ) -> list[dict]:
        """
        Detecta retesteos recientes de niveles clave con análisis de patrones
        @param candles - Velas ordenadas
        @param levels - Niveles a verificar
        @param lookback - Cuántas velas atrás mirar
        @returns Lista de retesteos detectados con probabilidades
        """
        from app.utils.retest_detector import RetestDetector
        
        retests = []
        if not candles or not levels:
            return retests
            
        recent_candles = candles[-lookback:]
        tolerance = 5.0  # Tolerancia en puntos
        
        for level in levels:
            for i, candle in enumerate(recent_candles):
                # Verificar si tocó el nivel
                touched = (candle.low - tolerance <= level <= candle.high + tolerance)
                
                if touched:
                    # Detectar patrón de vela
                    previous_candle = recent_candles[i - 1] if i > 0 else None
                    pattern = RetestDetector.detect_candle_pattern(candle, previous_candle)
                    
                    # Determinar tipo de nivel
                    is_support_retest = candle.close > level and candle.low <= level + tolerance
                    is_resistance_retest = candle.close < level and candle.high >= level - tolerance
                    
                    # Calcular distancia del precio al nivel
                    price_distance_percent = ((candle.close - level) / level) * 100
                    
                    # Calcular probabilidad de rebote
                    level_type = "support" if is_support_retest else "resistance"
                    level_strength = 0.7  # Por defecto, se puede mejorar con histórico
                    
                    bounce_probability = RetestDetector.calculate_bounce_probability(
                        level_type=level_type,
                        pattern=pattern,
                        price_distance=price_distance_percent,
                        level_strength=level_strength
                    )
                    
                    if is_support_retest:
                        retests.append({
                            "level": level,
                            "type": "support_retest",
                            "candles_ago": len(recent_candles) - 1 - i,
                            "candle_time": candle.timestamp.isoformat(),
                            "pattern": pattern.value,
                            "bounce_probability": round(bounce_probability, 2),
                            "price_at_retest": round(candle.close, 2),
                            "description": self._format_retest_description(
                                level, "soporte", pattern, bounce_probability
                            )
                        })
                    elif is_resistance_retest:
                        retests.append({
                            "level": level,
                            "type": "resistance_retest",
                            "candles_ago": len(recent_candles) - 1 - i,
                            "candle_time": candle.timestamp.isoformat(),
                            "pattern": pattern.value,
                            "bounce_probability": round(bounce_probability, 2),
                            "price_at_retest": round(candle.close, 2),
                            "description": self._format_retest_description(
                                level, "resistencia", pattern, bounce_probability
                            )
                        })
                        
        return retests
    
    def _format_retest_description(
        self,
        level: float,
        level_type: str,
        pattern: str,
        probability: float
    ) -> str:
        """
        Formatea descripción de retesteo
        @param level - Nivel retesteado
        @param level_type - Tipo de nivel
        @param pattern - Patrón detectado
        @param probability - Probabilidad de rebote
        @returns Descripción textual
        """
        pattern_names = {
            "pin_bar_alcista": "pin bar alcista",
            "pin_bar_bajista": "pin bar bajista",
            "envolvente_alcista": "envolvente alcista",
            "envolvente_bajista": "envolvente bajista",
            "martillo": "martillo",
            "estrella_fugaz": "estrella fugaz",
            "doji": "doji",
            "ninguno": "sin patrón claro"
        }
        
        pattern_text = pattern_names.get(pattern, pattern)
        prob_percent = int(probability * 100)
        
        return (
            f"Retesteo de {level_type} en {level:.0f} con {pattern_text}. "
            f"Probabilidad de rebote: {prob_percent}%"
        )
    
    def _generate_summary(
        self,
        daily_analysis: dict,
        h4_analysis: dict,
        h1_analysis: dict
    ) -> str:
        """
        Genera un resumen del análisis multi-temporalidad
        @param daily_analysis - Análisis diario
        @param h4_analysis - Análisis H4
        @param h1_analysis - Análisis H1
        @returns Resumen textual
        """
        parts: list[str] = []
        
        # Tendencia diaria
        if "trend" in daily_analysis:
            trend_text = {
                "alcista": "Alcista",
                "bajista": "Bajista",
                "lateral": "Lateral"
            }.get(daily_analysis["trend"], daily_analysis["trend"])
            parts.append(f"Tendencia Diaria: {trend_text}")
        
        # Análisis H4
        if "trend" in h4_analysis:
            h4_trend = {
                "alcista": "Alcista",
                "bajista": "Bajista",
                "lateral": "Lateral"
            }.get(h4_analysis["trend"], h4_analysis["trend"])
            parts.append(f"H4: {h4_trend}")
            
            if h4_analysis.get("rsi") is not None:
                parts.append(f"RSI H4: {h4_analysis['rsi']}")
                if h4_analysis.get("rsi_zone"):
                    parts.append(f"RSI en zona: {h4_analysis['rsi_zone']}")
            
            if h4_analysis.get("impulse_strong"):
                impulse_dir = h4_analysis.get("impulse_direction", "N/A")
                parts.append(f"Impulso H4: {impulse_dir} (fuerte, {h4_analysis.get('impulse_distance_percent', 0)}%)")
        
        # Confirmación H1
        if "trend" in h1_analysis:
            h1_trend = {
                "alcista": "Alcista",
                "bajista": "Bajista",
                "lateral": "Lateral"
            }.get(h1_analysis["trend"], h1_analysis["trend"])
            parts.append(f"H1: {h1_trend} (confirmación)")
        
        return " | ".join(parts)

