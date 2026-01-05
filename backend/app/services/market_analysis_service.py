"""
Servicio para analizar datos de mercado y sesiones de trading
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.models.market_analysis import DailyMarketAnalysis, PriceCandle, SessionType
from app.providers.market_data.base_market_provider import MarketDataProvider
from app.providers.market_data.mock_market_provider import MockMarketProvider
from app.utils.market_analyzer import MarketAnalyzer
from app.utils.trading_sessions import TradingSessions

logger = logging.getLogger(__name__)


class MarketAnalysisService:
    """Servicio para analizar datos de mercado"""
    
    def __init__(self, settings: Settings, db: Optional[Session] = None):
        """
        Inicializa el servicio de análisis de mercado
        @param settings - Configuración de la aplicación
        @param db - Sesión de base de datos (opcional)
        """
        self.settings = settings
        self.provider = self._create_provider(settings)
        self.db = db
    
    def _create_provider(self, settings: Settings) -> MarketDataProvider:
        """
        Crea el proveedor de datos de mercado según la configuración
        @param settings - Configuración de la aplicación
        @returns Instancia del proveedor
        """
        # Por ahora solo mock, se puede extender con APIs reales
        logger.info("Using mock provider for market data")
        return MockMarketProvider()
    
    async def analyze_yesterday_sessions(
        self,
        instrument: str = "XAUUSD"
    ) -> DailyMarketAnalysis:
        """
        Analiza el cierre de ayer y las sesiones de trading
        @param instrument - Instrumento a analizar (por defecto XAUUSD)
        @returns Análisis completo del día
        """
        yesterday = datetime.now().date() - timedelta(days=1)
        day_before = yesterday - timedelta(days=1)
        
        logger.info(f"Analyzing {instrument} for {yesterday}")
        
        # Obtener datos del día anterior (para calcular cierre)
        day_before_start = datetime.combine(day_before, datetime.min.time())
        day_before_end = datetime.combine(day_before, datetime.max.time())
        
        # Obtener datos de ayer
        yesterday_start = datetime.combine(yesterday, datetime.min.time())
        yesterday_end = datetime.combine(yesterday, datetime.max.time())
        
        # Obtener velas del día anterior y de ayer
        day_before_candles = await self.provider.fetch_historical_candles(
            instrument, day_before_start, day_before_end, "1h"
        )
        yesterday_candles = await self.provider.fetch_historical_candles(
            instrument, yesterday_start, yesterday_end, "1h"
        )
        
        if not yesterday_candles:
            raise ValueError(f"No data available for {instrument} on {yesterday}")
        
        # Calcular cierres
        previous_close = day_before_candles[-1].close if day_before_candles else yesterday_candles[0].open
        current_close = yesterday_candles[-1].close
        
        # Calcular máximos y mínimos del día anterior
        previous_day_high = max(c.high for c in day_before_candles) if day_before_candles else None
        previous_day_low = min(c.low for c in day_before_candles) if day_before_candles else None
        
        # Agrupar velas por sesión
        sessions_analysis = []
        
        for session_type in [SessionType.ASIA, SessionType.LONDON, SessionType.NEW_YORK]:
            session_candles = self._filter_candles_by_session(yesterday_candles, session_type)
            
            if session_candles:
                session_analysis = MarketAnalyzer.analyze_session(
                    session_type,
                    session_candles,
                    previous_day_high,
                    previous_day_low
                )
                sessions_analysis.append(session_analysis)
        
        # Calcular dirección general del día
        daily_direction = MarketAnalyzer.calculate_direction(
            yesterday_candles[0].open,
            current_close
        )
        
        daily_change_percent = (
            ((current_close - previous_close) / previous_close) * 100
            if previous_close > 0 else 0
        )
        
        # Generar resumen
        summary = MarketAnalyzer.generate_daily_summary(
            instrument,
            yesterday.isoformat(),
            previous_close,
            current_close,
            sessions_analysis
        )
        
        return DailyMarketAnalysis(
            instrument=instrument,
            date=yesterday.isoformat(),
            previous_day_close=previous_close,
            current_day_close=current_close,
            daily_change_percent=round(daily_change_percent, 2),
            daily_direction=daily_direction,
            previous_day_high=previous_day_high,
            previous_day_low=previous_day_low,
            sessions=sessions_analysis,
            summary=summary
        )
    
    def _filter_candles_by_session(
        self,
        candles: list[PriceCandle],
        session: SessionType
    ) -> list[PriceCandle]:
        """
        Filtra velas que pertenecen a una sesión específica
        @param candles - Lista de velas
        @param session - Tipo de sesión
        @returns Velas filtradas por sesión
        """
        session_candles: list[PriceCandle] = []
        
        for candle in candles:
            candle_session = TradingSessions.get_session_for_time(candle.timestamp)
            if candle_session == session:
                session_candles.append(candle)
        
        return session_candles

