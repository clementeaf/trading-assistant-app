"""
Proveedor de datos de mercado usando Twelve Data API
Especializado en metales preciosos como XAUUSD
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx

from app.models.market_analysis import PriceCandle
from app.providers.market_data.base_market_provider import MarketDataProvider

logger = logging.getLogger(__name__)


class TwelveDataProvider(MarketDataProvider):
    """Proveedor de datos de mercado usando Twelve Data API - Especializado en XAUUSD"""
    
    BASE_URL = "https://api.twelvedata.com"
    
    # Mapeo de instrumentos a símbolos de Twelve Data
    # Twelve Data usa símbolos específicos para metales preciosos
    INSTRUMENT_MAPPING = {
        "XAUUSD": "XAU/USD",  # Oro en Twelve Data
        "DXY": "DXY",  # Dollar Index
        "US10Y": "US10Y",  # Bono 10 años
        "US02Y": "US02Y",  # Bono 2 años
        "US30Y": "US30Y",  # Bono 30 años
        "NASDAQ": "IXIC",  # Nasdaq Composite Index
    }
    
    # Mapeo de intervalos
    INTERVAL_MAPPING = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "1h": "1h",
        "4h": "4h",
        "1d": "1day",
    }
    
    def __init__(self, api_key: str):
        """
        Inicializa el proveedor de Twelve Data
        @param api_key - API key de Twelve Data
        """
        if not api_key:
            raise ValueError("Twelve Data API key is required")
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
        Obtiene velas históricas para un instrumento usando Twelve Data
        @param instrument - Símbolo del instrumento (ej: XAUUSD)
        @param start_date - Fecha de inicio
        @param end_date - Fecha de fin
        @param interval - Intervalo de las velas (1h, 15m, etc.)
        @returns Lista de velas de precio
        """
        instrument_upper = instrument.upper()
        symbol = self.INSTRUMENT_MAPPING.get(instrument_upper, instrument_upper)
        
        # Twelve Data es especializado en metales preciosos, ideal para XAUUSD
        interval_mapped = self.INTERVAL_MAPPING.get(interval.lower(), "1h")
        
        candles: list[PriceCandle] = []
        
        try:
            candles = await self._fetch_time_series(
                symbol, start_date, end_date, interval_mapped, instrument_upper
            )
            
            # Filtrar por rango de fechas
            filtered_candles = [
                candle for candle in candles
                if start_date <= candle.timestamp <= end_date
            ]
            
            logger.info(
                f"Fetched {len(filtered_candles)} candles for {instrument} "
                f"from Twelve Data (interval: {interval})"
            )
            
            return sorted(filtered_candles, key=lambda x: x.timestamp)
            
        except Exception as e:
            logger.error(f"Error fetching data from Twelve Data: {str(e)}")
            raise ValueError(f"Failed to fetch market data from Twelve Data: {str(e)}")
    
    async def _fetch_time_series(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str,
        original_instrument: str
    ) -> list[PriceCandle]:
        """
        Obtiene datos de time series de Twelve Data
        @param symbol - Símbolo del instrumento
        @param start_date - Fecha de inicio
        @param end_date - Fecha de fin
        @param interval - Intervalo mapeado
        @returns Lista de velas
        """
        # Twelve Data API endpoint para time series
        # Formato: /time_series?symbol=XAU/USD&interval=1h&apikey=xxx&start_date=...&end_date=...
        
        params = {
            "symbol": symbol,
            "interval": interval,
            "apikey": self.api_key,
            "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
            "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
            "format": "JSON",
            "outputsize": "5000"  # Máximo permitido
        }
        
        response = await self.client.get(f"{self.BASE_URL}/time_series", params=params)
        response.raise_for_status()
        data = response.json()
        
        # Verificar errores de API
        if "status" in data and data["status"] == "error":
            error_message = data.get("message", "Unknown error")
            if "rate limit" in error_message.lower() or "quota" in error_message.lower():
                raise ValueError(f"Twelve Data API rate limit: {error_message}")
            raise ValueError(f"Twelve Data API error: {error_message}")
        
        # Twelve Data devuelve los datos en "values" o directamente como array
        if "values" in data:
            time_series = data["values"]
        elif "data" in data:
            time_series = data["data"]
        elif isinstance(data, list):
            time_series = data
        else:
            # Intentar encontrar datos en cualquier clave que contenga valores
            time_series = None
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    if isinstance(value[0], dict) and "datetime" in value[0]:
                        time_series = value
                        break
            
            if not time_series:
                logger.warning(f"Available keys in Twelve Data response: {list(data.keys())}")
                raise ValueError("No time series data found in Twelve Data response")
        
        candles: list[PriceCandle] = []
        
        for item in time_series:
            try:
                # Twelve Data formato: {"datetime": "2024-01-01 10:00:00", "open": "2650.0", "high": "2655.0", "low": "2648.0", "close": "2652.0", "volume": "1000"}
                timestamp_str = item.get("datetime") or item.get("time")
                if not timestamp_str:
                    continue
                
                # Parsear timestamp (formato puede variar)
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
                    except ValueError:
                        try:
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d")
                        except ValueError:
                            logger.warning(f"Could not parse timestamp: {timestamp_str}")
                            continue
                
                # Extraer valores OHLC
                open_price = float(item.get("open", 0))
                high_price = float(item.get("high", 0))
                low_price = float(item.get("low", 0))
                close_price = float(item.get("close", 0))
                volume = float(item.get("volume", 0))
                
                if open_price == 0 or high_price == 0 or low_price == 0 or close_price == 0:
                    logger.warning(f"Invalid price data in candle: {item}")
                    continue
                
                candles.append(PriceCandle(
                    timestamp=timestamp,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    volume=volume
                ))
            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"Error parsing candle data: {item}, error: {str(e)}")
                continue
        
        return candles

