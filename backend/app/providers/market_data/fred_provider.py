"""
Proveedor de datos de mercado usando FRED API (Federal Reserve Economic Data)
Especializado en DXY y bonos del Tesoro de EE.UU.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx

from app.models.market_analysis import PriceCandle
from app.providers.market_data.base_market_provider import MarketDataProvider

logger = logging.getLogger(__name__)


class FredProvider(MarketDataProvider):
    """Proveedor de datos usando FRED API - Especializado en DXY y bonos"""
    
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
    
    # Mapeo de instrumentos a series ID de FRED
    # FRED usa series IDs específicos para cada indicador
    SERIES_MAPPING = {
        "DXY": "DTWEXBGS",  # Trade Weighted U.S. Dollar Index: Broad
        "US10Y": "DGS10",  # 10-Year Treasury Constant Maturity Rate
        "US02Y": "DGS2",  # 2-Year Treasury Constant Maturity Rate
        "US30Y": "DGS30",  # 30-Year Treasury Constant Maturity Rate
        "US05Y": "DGS5",  # 5-Year Treasury Constant Maturity Rate
    }
    
    def __init__(self, api_key: str):
        """
        Inicializa el proveedor de FRED
        @param api_key - API key de FRED (gratis en https://fred.stlouisfed.org/docs/api/api_key.html)
        """
        if not api_key:
            raise ValueError("FRED API key is required")
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """
        Obtiene o crea el cliente HTTP
        @returns Cliente HTTP asíncrono
        """
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def fetch_historical_candles(
        self,
        instrument: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h"
    ) -> list[PriceCandle]:
        """
        Obtiene velas históricas para un instrumento usando FRED
        @param instrument - Símbolo del instrumento (ej: DXY, US10Y)
        @param start_date - Fecha de inicio
        @param end_date - Fecha de fin
        @param interval - Intervalo de las velas (FRED solo soporta diario)
        @returns Lista de velas de precio
        """
        instrument_upper = instrument.upper()
        series_id = self.SERIES_MAPPING.get(instrument_upper)
        
        if not series_id:
            raise ValueError(
                f"FRED does not support instrument '{instrument}'. "
                f"Supported instruments: {list(self.SERIES_MAPPING.keys())}"
            )
        
        # FRED solo proporciona datos diarios
        # Para intervalos intradía, usamos el valor diario para todas las horas
        if interval not in ["1d", "1day", "daily"]:
            logger.warning(
                f"FRED only provides daily data. Using daily values for interval '{interval}'"
            )
        
        candles: list[PriceCandle] = []
        
        try:
            candles = await self._fetch_fred_data(
                series_id, start_date, end_date, instrument_upper
            )
            
            logger.info(
                f"Fetched {len(candles)} candles for {instrument} from FRED "
                f"(series: {series_id})"
            )
            
            return sorted(candles, key=lambda x: x.timestamp)
            
        except Exception as e:
            logger.error(f"Error fetching data from FRED: {str(e)}")
            raise ValueError(f"Failed to fetch market data from FRED: {str(e)}")
    
    async def _fetch_fred_data(
        self,
        series_id: str,
        start_date: datetime,
        end_date: datetime,
        original_instrument: str
    ) -> list[PriceCandle]:
        """
        Obtiene datos de FRED API
        @param series_id - ID de la serie en FRED
        @param start_date - Fecha de inicio
        @param end_date - Fecha de fin
        @returns Lista de velas
        """
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start_date.strftime("%Y-%m-%d"),
            "observation_end": end_date.strftime("%Y-%m-%d"),
            "sort_order": "asc"
        }
        
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Verificar errores de API
        if "error_code" in data:
            error_message = data.get("error_message", "Unknown error")
            raise ValueError(f"FRED API error: {error_message}")
        
        # FRED devuelve los datos en "observations"
        observations = data.get("observations", [])
        
        if not observations:
            raise ValueError(f"No data available for series {series_id} in the specified date range")
        
        candles: list[PriceCandle] = []
        
        for obs in observations:
            try:
                # FRED formato: {"date": "2024-01-01", "value": "104.5"}
                date_str = obs.get("date")
                value_str = obs.get("value")
                
                if not date_str or not value_str:
                    continue
                
                # FRED usa "." para valores faltantes
                if value_str == ".":
                    continue
                
                # Parsear fecha
                try:
                    timestamp = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    logger.warning(f"Could not parse date: {date_str}")
                    continue
                
                # Parsear valor
                try:
                    price = float(value_str)
                except ValueError:
                    logger.warning(f"Could not parse value: {value_str}")
                    continue
                
                # FRED proporciona un solo valor por día (cierre)
                # Para crear una vela OHLC, usamos el mismo valor para todos
                candles.append(PriceCandle(
                    timestamp=timestamp,
                    open=price,
                    high=price,
                    low=price,
                    close=price,
                    volume=0.0  # FRED no proporciona volumen
                ))
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"Error parsing observation: {obs}, error: {str(e)}")
                continue
        
        return candles

