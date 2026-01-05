"""
Servicio para analizar alineación entre DXY y bonos
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.models.market_alignment import MarketAlignmentAnalysis
from app.providers.market_data.base_market_provider import MarketDataProvider
from app.providers.market_data.alpha_vantage_provider import AlphaVantageProvider
from app.providers.market_data.twelve_data_provider import TwelveDataProvider
from app.providers.market_data.mock_market_provider import MockMarketProvider
from app.utils.alignment_analyzer import AlignmentAnalyzer

logger = logging.getLogger(__name__)


class MarketAlignmentService:
    """Servicio para analizar alineación de mercado"""
    
    def __init__(self, settings: Settings, db: Optional[Session] = None):
        """
        Inicializa el servicio de alineación de mercado
        @param settings - Configuración de la aplicación
        @param db - Sesión de base de datos (opcional)
        """
        self.settings = settings
        self.provider = self._create_provider(settings)
        self.db = db
    
    def _create_provider(self, settings: Settings) -> MarketDataProvider:
        """
        Crea el proveedor de datos de mercado
        @param settings - Configuración de la aplicación
        @returns Instancia del proveedor
        """
        provider_name = settings.market_data_provider.lower()
        
        if provider_name == "twelvedata":
            if not settings.market_data_api_key:
                logger.warning(
                    "Twelve Data provider selected but no API key configured. "
                    "Falling back to mock provider."
                )
                return MockMarketProvider()
            
            logger.info("Using Twelve Data provider for market data (specialized in XAUUSD)")
            return TwelveDataProvider(api_key=settings.market_data_api_key)
        elif provider_name == "alphavantage":
            if not settings.market_data_api_key:
                logger.warning(
                    "Alpha Vantage provider selected but no API key configured. "
                    "Falling back to mock provider."
                )
                return MockMarketProvider()
            
            logger.info("Using Alpha Vantage provider for market data")
            return AlphaVantageProvider(api_key=settings.market_data_api_key)
        elif provider_name == "mock":
            logger.info("Using mock provider for market data")
            return MockMarketProvider()
        else:
            logger.warning(
                f"Unknown market data provider '{provider_name}'. Using mock provider."
            )
            return MockMarketProvider()
    
    async def analyze_dxy_bond_alignment(
        self,
        bond_symbol: str = "US10Y"
    ) -> MarketAlignmentAnalysis:
        """
        Analiza la alineación entre DXY y un bono
        @param bond_symbol - Símbolo del bono (US10Y, US02Y, etc.)
        @returns Análisis de alineación
        """
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        day_before = yesterday - timedelta(days=1)
        
        logger.info(f"Analyzing alignment between DXY and {bond_symbol}")
        
        # Obtener datos de DXY
        dxy_yesterday_start = datetime.combine(yesterday, datetime.min.time())
        dxy_yesterday_end = datetime.combine(yesterday, datetime.max.time())
        dxy_day_before_start = datetime.combine(day_before, datetime.min.time())
        dxy_day_before_end = datetime.combine(day_before, datetime.max.time())
        
        # DXY y bonos no están disponibles en Alpha Vantage
        # Usar mock provider para estos instrumentos
        from app.providers.market_data.mock_market_provider import MockMarketProvider
        
        mock_provider = MockMarketProvider()
        
        try:
            dxy_yesterday_candles = await self.provider.fetch_historical_candles(
                "DXY", dxy_yesterday_start, dxy_yesterday_end, "1h"
            )
            dxy_day_before_candles = await self.provider.fetch_historical_candles(
                "DXY", dxy_day_before_start, dxy_day_before_end, "1h"
            )
        except (ValueError, Exception) as e:
            logger.warning(f"Provider does not support DXY, using mock: {str(e)}")
            dxy_yesterday_candles = await mock_provider.fetch_historical_candles(
                "DXY", dxy_yesterday_start, dxy_yesterday_end, "1h"
            )
            dxy_day_before_candles = await mock_provider.fetch_historical_candles(
                "DXY", dxy_day_before_start, dxy_day_before_end, "1h"
            )
        
        try:
            bond_yesterday_candles = await self.provider.fetch_historical_candles(
                bond_symbol, dxy_yesterday_start, dxy_yesterday_end, "1h"
            )
            bond_day_before_candles = await self.provider.fetch_historical_candles(
                bond_symbol, dxy_day_before_start, dxy_day_before_end, "1h"
            )
        except (ValueError, Exception) as e:
            logger.warning(f"Provider does not support {bond_symbol}, using mock: {str(e)}")
            bond_yesterday_candles = await mock_provider.fetch_historical_candles(
                bond_symbol, dxy_yesterday_start, dxy_yesterday_end, "1h"
            )
            bond_day_before_candles = await mock_provider.fetch_historical_candles(
                bond_symbol, dxy_day_before_start, dxy_day_before_end, "1h"
            )
        
        if not dxy_yesterday_candles or not dxy_day_before_candles:
            raise ValueError(f"No data available for DXY")
        
        if not bond_yesterday_candles or not bond_day_before_candles:
            raise ValueError(f"No data available for {bond_symbol}")
        
        # Obtener precios de cierre
        dxy_current = dxy_yesterday_candles[-1].close
        dxy_previous = dxy_day_before_candles[-1].close
        
        bond_current = bond_yesterday_candles[-1].close
        bond_previous = bond_day_before_candles[-1].close
        
        # Analizar alineación
        analysis = AlignmentAnalyzer.analyze_alignment(
            dxy_current=dxy_current,
            dxy_previous=dxy_previous,
            bond_current=bond_current,
            bond_previous=bond_previous,
            bond_symbol=bond_symbol
        )
        
        logger.info(
            f"Alignment analysis: {analysis.alignment.value}, "
            f"bias: {analysis.market_bias.value}"
        )
        
        return analysis

