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
from app.providers.market_data.fred_provider import FredProvider
from app.providers.market_data.mock_market_provider import MockMarketProvider
from app.utils.alignment_analyzer import AlignmentAnalyzer
from app.utils.business_days import BusinessDays

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
                raise ValueError(
                    "Twelve Data provider selected but no API key configured. "
                    "Please set MARKET_DATA_API_KEY environment variable."
                )
            
            logger.info("Using Twelve Data provider for market data (specialized in XAUUSD)")
            return TwelveDataProvider(api_key=settings.market_data_api_key)
        elif provider_name == "alphavantage":
            if not settings.market_data_api_key:
                raise ValueError(
                    "Alpha Vantage provider selected but no API key configured. "
                    "Please set MARKET_DATA_API_KEY environment variable."
                )
            
            logger.info("Using Alpha Vantage provider for market data")
            return AlphaVantageProvider(api_key=settings.market_data_api_key)
        elif provider_name == "mock":
            logger.info("Using Mock provider for market data")
            return MockMarketProvider()
        else:
            raise ValueError(
                f"Unknown market data provider '{provider_name}'. "
                "Supported providers: twelvedata, alphavantage, mock"
            )
    
    async def analyze_dxy_bond_alignment(
        self,
        bond_symbol: str = "US10Y"
    ) -> MarketAlignmentAnalysis:
        """
        Analiza la alineación entre DXY y un bono
        @param bond_symbol - Símbolo del bono (US10Y, US02Y, etc.)
        @returns Análisis de alineación
        """
        # Usar días hábiles (la Fed solo opera en días hábiles)
        today = datetime.now().date()
        yesterday = BusinessDays.get_last_business_day(today)
        day_before = BusinessDays.get_previous_business_day(yesterday)
        
        logger.info(
            f"Analyzing alignment between DXY and {bond_symbol} "
            f"(last business day: {yesterday}, previous: {day_before})"
        )
        
        # Obtener datos de DXY
        # Intentar con fechas más antiguas si no hay datos disponibles
        dxy_yesterday_start = datetime.combine(yesterday, datetime.min.time())
        dxy_yesterday_end = datetime.combine(yesterday, datetime.max.time())
        dxy_day_before_start = datetime.combine(day_before, datetime.min.time())
        dxy_day_before_end = datetime.combine(day_before, datetime.max.time())
        
        # DXY y bonos: intentar con FRED primero (especializado), luego con el proveedor principal
        dxy_provider = self._get_dxy_bond_provider()
        bond_provider = self._get_dxy_bond_provider()
        
        # FRED solo tiene datos en días hábiles, buscar un rango amplio y tomar los últimos disponibles
        # Buscar datos de los últimos 30 días para encontrar los días hábiles más recientes
        range_start = today - timedelta(days=30)
        range_end = today
        
        range_start_dt = datetime.combine(range_start, datetime.min.time())
        range_end_dt = datetime.combine(range_end, datetime.max.time())
        
        try:
            # Obtener todos los datos disponibles en el rango
            dxy_all_candles = await dxy_provider.fetch_historical_candles(
                "DXY", range_start_dt, range_end_dt, "1d"
            )
            bond_all_candles = await bond_provider.fetch_historical_candles(
                bond_symbol, range_start_dt, range_end_dt, "1d"
            )
            
            if not dxy_all_candles or len(dxy_all_candles) < 2:
                raise ValueError("Not enough DXY data available from FRED")
            if not bond_all_candles or len(bond_all_candles) < 2:
                raise ValueError(f"Not enough {bond_symbol} data available from FRED")
            
            # Tomar los dos últimos días disponibles (días hábiles más recientes)
            dxy_yesterday_candles = [dxy_all_candles[-1]]
            dxy_day_before_candles = [dxy_all_candles[-2]]
            bond_yesterday_candles = [bond_all_candles[-1]]
            bond_day_before_candles = [bond_all_candles[-2]]
            
            logger.info(
                f"Using most recent available data: "
                f"DXY from {dxy_all_candles[-1].timestamp.date()}, "
                f"{bond_symbol} from {bond_all_candles[-1].timestamp.date()}"
            )
        except (ValueError, Exception) as e:
            logger.error(f"Could not fetch data from FRED: {str(e)}")
            raise ValueError(
                f"Data is not available from FRED. "
                f"Please verify FRED_API_KEY is correct and data is available. Error: {str(e)}"
            )
        
        if not dxy_yesterday_candles or not dxy_day_before_candles:
            logger.error("Could not fetch DXY data from FRED")
            raise ValueError(
                f"DXY data is not available from FRED. "
                "Please verify FRED_API_KEY is correct and data is available for the requested dates."
            )
        
        if not bond_yesterday_candles or not bond_day_before_candles:
            logger.error(f"Could not fetch {bond_symbol} data from FRED")
            raise ValueError(
                f"{bond_symbol} data is not available from FRED. "
                "Please verify FRED_API_KEY is correct and data is available for the requested dates."
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
    
    def _get_dxy_bond_provider(self) -> MarketDataProvider:
        """
        Obtiene el proveedor adecuado para DXY y bonos
        Prioriza FRED (especializado), luego el proveedor principal
        @returns Proveedor de datos de mercado
        """
        # FRED es especializado en DXY y bonos, tiene prioridad
        if self.settings.fred_api_key:
            logger.info("Using FRED provider for DXY and bonds")
            return FredProvider(api_key=self.settings.fred_api_key)
        
        # Si no hay FRED, intentar con el proveedor principal
        logger.warning(
            "FRED_API_KEY not configured. Attempting to use main provider for DXY/bonds. "
            "This may not work for all providers. Consider configuring FRED_API_KEY."
        )
        return self.provider

